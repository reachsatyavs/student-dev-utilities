# Phase A: Build the Test environment (A1 to A9)

> **Flow diagram:** see all steps A1 to F4 on one page in [FLOW.md](FLOW.md).

Copy and run the blocks in order. Replace every `<placeholder>` first.
**Where** each block runs is shown at the top of it: your **laptop**, the **EC2 ops instance**, or **Jenkins**.

Result of Phase A:

| Account | Region | What runs there |
|---|---|---|
| Test-Prod | eu-west-1 (Ireland) | EKS `hub` (VPC 10.100.0.0/16), platform Jenkins, app stack `test-live`, Aurora primary |
| Test-DR | eu-west-2 (London) | EKS `hub` (VPC 10.101.0.0/16), platform Jenkins, app stack `test-live` (scaled to 0), its own Aurora |

Later (Phase B) adds the Aurora secondary VPC 10.200.0.0/16 in the Test-Prod account.

---

## Inputs sheet: fill this in once

| Input | Example | Your value |
|---|---|---|
| Management account CLI profile (on your laptop) | `mgmt` | |
| Email for the Test-Prod account (unique, never used in AWS) | `aws-test-prod@yourco.com` | |
| Email for the Test-DR account | `aws-test-dr@yourco.com` | |
| Parent DNS domain you control | `yourco.com` | |
| Test-Prod sub-domain | `tprd.yourco.com` | |
| Test-DR sub-domain | `tdr.yourco.com` | |
| Git host (SSH) | `git.yourco.com` | |
| Platform repo (SSH URL) | `git@git.yourco.com:ops/<platform-repo>.git` | |
| Platform branch | `master` (or `<adopt-secret-branch>`) | |
| App repo (SSH URL) | `git@git.yourco.com:ops/<app-repo>.git` | |
| Docker repo (SSH URL) | `git@git.yourco.com:ops/docker.git` | |
| Scripts repo (with `cli-aurora-migration/`) | `git@…:…/migration-scripts.git` | |
| Artifact repository (Nexus) user / password | from your vendor | |
| Your laptop's public IP | `curl -s https://checkip.amazonaws.com` | |
| App nickname (namespace) | `test-live` | |

---

## A1. Create the AWS accounts (laptop, about 30 min)

**Needs:** CLI access to the AWS Organizations **management** account. If someone else creates accounts for you, skip to "Profiles" and ask them for the two account IDs.

```bash
# laptop
export AWS_PROFILE=mgmt

aws organizations create-account --email <test-prod-email> --account-name "Test-Prod"
aws organizations create-account --email <test-dr-email>   --account-name "Test-DR"

# Wait until both say SUCCEEDED, and note the AccountId of each
aws organizations list-create-account-status --states IN_PROGRESS SUCCEEDED FAILED \
  --query 'CreateAccountStatuses[].{Name:AccountName,State:State,Id:AccountId}' --output table
```

**Profiles.** Add these to `~/.aws/config` on your laptop. They log you into each new account through the role that Organizations creates:

```ini
[profile testprod-admin]
role_arn = arn:aws:iam::<TEST_PROD_ACCOUNT_ID>:role/OrganizationAccountAccessRole
source_profile = mgmt
region = eu-west-1

[profile testdr-admin]
role_arn = arn:aws:iam::<TEST_DR_ACCOUNT_ID>:role/OrganizationAccountAccessRole
source_profile = mgmt
region = eu-west-2
```

```bash
# laptop: each must print the new account ID
aws sts get-caller-identity --profile testprod-admin
aws sts get-caller-identity --profile testdr-admin
```

**vCPU quota.** Each cluster runs 3 or more `m6a.2xlarge` nodes (8 vCPU each), and builds need more. New accounts often start lower, so ask for 96:

```bash
# laptop
aws service-quotas request-service-quota-increase --service-code ec2 --quota-code L-1216C47A \
  --desired-value 96 --region eu-west-1 --profile testprod-admin
aws service-quotas request-service-quota-increase --service-code ec2 --quota-code L-1216C47A \
  --desired-value 96 --region eu-west-2 --profile testdr-admin
```

**IAM user for the platform bootstrap**, one per account. The bootstrap needs an access key. `AdministratorAccess` is the simple choice **for Test only**; for Production use the policy from the platform docs.

```bash
# laptop: Test-Prod
aws iam create-user --user-name platform-bootstrap --profile testprod-admin
aws iam attach-user-policy --user-name platform-bootstrap \
  --policy-arn arn:aws:iam::aws:policy/AdministratorAccess --profile testprod-admin
aws iam create-access-key --user-name platform-bootstrap --profile testprod-admin   # save AccessKeyId + SecretAccessKey

# laptop: Test-DR
aws iam create-user --user-name platform-bootstrap --profile testdr-admin
aws iam attach-user-policy --user-name platform-bootstrap \
  --policy-arn arn:aws:iam::aws:policy/AdministratorAccess --profile testdr-admin
aws iam create-access-key --user-name platform-bootstrap --profile testdr-admin     # save AccessKeyId + SecretAccessKey
```

Keep the two key pairs in a password manager. They are needed in A2 and A3/A4.

---

## A2. The EC2 ops instance (laptop, then EC2, about 30 min)

**Size:** `t3.large` (2 vCPU, 8 GB RAM), **50 GB gp3** disk, Amazon Linux 2023, in the **Test-Prod** account, eu-west-1.
The bootstrap container runs Terraform and builds one Docker image, so this is enough. Use `t3.xlarge` if the image build is slow.
Only one bootstrap can run at a time on it, because the container name is fixed (`kubernetes-bootstrap`).

### Create it (laptop)

```bash
# laptop
export AWS_PROFILE=testprod-admin AWS_REGION=eu-west-1
MYIP="$(curl -s https://checkip.amazonaws.com)/32"

aws ec2 create-key-pair --key-name ops-host --key-type ed25519 \
  --query KeyMaterial --output text > ops-host.pem && chmod 400 ops-host.pem

VPC=$(aws ec2 describe-vpcs --filters Name=isDefault,Values=true --query 'Vpcs[0].VpcId' --output text)
SG=$(aws ec2 create-security-group --group-name ops-host-ssh --description "SSH from my IP" \
  --vpc-id "$VPC" --query GroupId --output text)
aws ec2 authorize-security-group-ingress --group-id "$SG" --protocol tcp --port 22 --cidr "$MYIP"

AMI=$(aws ssm get-parameter --name /aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64 \
  --query Parameter.Value --output text)

ID=$(aws ec2 run-instances --image-id "$AMI" --instance-type t3.large --key-name ops-host \
  --security-group-ids "$SG" \
  --block-device-mappings 'DeviceName=/dev/xvda,Ebs={VolumeSize=50,VolumeType=gp3}' \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=ops-host}]' \
  --query 'Instances[0].InstanceId' --output text)
aws ec2 wait instance-running --instance-ids "$ID"

# Fixed public IP, so it can be whitelisted for Jenkins/Nexus
EIP=$(aws ec2 allocate-address --query AllocationId --output text)
aws ec2 associate-address --instance-id "$ID" --allocation-id "$EIP"
OPS_IP=$(aws ec2 describe-addresses --allocation-ids "$EIP" --query 'Addresses[0].PublicIp' --output text)
echo "ssh -i ops-host.pem ec2-user@$OPS_IP"
```

### Install the tools (EC2)

```bash
# EC2: after ssh-ing in
sudo dnf install -y git jq tmux docker unzip mariadb105    # mariadb105 = mysql client (optional)
sudo systemctl enable --now docker
sudo usermod -aG docker ec2-user

# docker compose v2 (+ buildx). Also usable as the old "docker-compose" command.
sudo mkdir -p /usr/local/lib/docker/cli-plugins
sudo curl -fsSL https://github.com/docker/compose/releases/download/v2.29.7/docker-compose-linux-x86_64 \
  -o /usr/local/lib/docker/cli-plugins/docker-compose
sudo curl -fsSL https://github.com/docker/buildx/releases/download/v0.17.1/buildx-v0.17.1.linux-amd64 \
  -o /usr/local/lib/docker/cli-plugins/docker-buildx
sudo chmod +x /usr/local/lib/docker/cli-plugins/*
sudo ln -sf /usr/local/lib/docker/cli-plugins/docker-compose /usr/local/bin/docker-compose

# kubectl: pick the version of your EKS cluster (check after A3 with: aws eks describe-cluster ... --query cluster.version)
KUBECTL_VERSION=v1.31.0
curl -fsSLO "https://dl.k8s.io/release/${KUBECTL_VERSION}/bin/linux/amd64/kubectl"
sudo install -m 0755 kubectl /usr/local/bin/kubectl && rm kubectl

exit    # log out and back in, so the docker group applies
```

```bash
# EC2: check (aws CLI v2 comes with Amazon Linux 2023)
aws --version && docker version --format '{{.Server.Version}}' && docker-compose version \
  && kubectl version --client && jq --version && git --version
```

### AWS profiles on the EC2 (EC2)

```bash
# EC2: use the platform-bootstrap keys from A1
aws configure --profile testprod     # key + secret of Test-Prod, region eu-west-1, output json
aws configure --profile testdr       # key + secret of Test-DR,  region eu-west-2, output json
aws sts get-caller-identity --profile testprod
aws sts get-caller-identity --profile testdr
```

### SSH keys (EC2)

```bash
# EC2
# 1) Git key: platform and Jenkins clone your repos with it.
#    RSA in PEM format, no passphrase (platform does not support one; older Jenkins Git clients need PEM).
ssh-keygen -t rsa -b 4096 -m PEM -f ~/.ssh/platform_git -N "" -C platform-git
cat ~/.ssh/platform_git.pub     # add this key to the platform, app and Docker repos on your Git host

# 2) Key for the EKS nodes
ssh-keygen -t rsa -b 4096 -f ~/.ssh/eks_nodes -N "" -C eks-nodes

# 3) Git host key, needed in the bootstrap settings
ssh-keyscan <git-host> 2>/dev/null | grep -E 'ssh-(rsa|ed25519)' | head -1

# Check the Git key works
GIT_SSH_COMMAND="ssh -i ~/.ssh/platform_git" git ls-remote <platform-repo-ssh-url> | head -3
```

### Variables used in the next steps (EC2)

```bash
# EC2: add to ~/.bashrc so every new terminal has them
cat >> ~/.bashrc <<'EOF'
export TP_REGION=eu-west-1 DR_REGION=eu-west-2
export TP_PROFILE=testprod DR_PROFILE=testdr
export CLUSTER=hub NICK=test-live
export DB_SECRET=<db-secret-name>   # the app's DB secret in namespace $NICK (see local name map)
EOF
source ~/.bashrc
```

---

## A3. Bootstrap the platform in Test-Prod (EC2, 1 to 2 hours)

```bash
# EC2
mkdir -p ~/platform && cd ~/platform
GIT_SSH_COMMAND="ssh -i ~/.ssh/platform_git" git clone -b <platform-branch> <platform-repo-ssh-url> testprod
cd testprod && ls docker-compose.yml     # must exist
```

Create the settings file. It overrides values in `docker-compose.yml`.

```bash
# EC2: in ~/platform/testprod. Replace every <...>
cat > docker-compose.override.yml <<'EOF'
version: '2.1'
services:
  kubernetes-bootstrap:
    environment:
      TF_VAR_aws_access_key_id: "<test-prod platform-bootstrap access key id>"
      TF_VAR_aws_secret_access_key: "<test-prod platform-bootstrap secret key>"
      TF_VAR_aws_region: "eu-west-1"
      TF_VAR_domain: "<tprd.yourco.com>"
      TF_VAR_aws_backend_s3_bucket: "platform-<test-prod-account-id>-tf-backend"
      TF_VAR_aws_backend_dynamodb_table: "platform-tfstate-euw1"
      TF_VAR_aws_iam_role_name: "Platform-Infra-Mgmt-euw1"
      aws_eks_ssh_key: "<contents of ~/.ssh/eks_nodes.pub>"
      <ARTIFACT_REPO_USER_VAR>: "<nexus user>"
      <ARTIFACT_REPO_PASSWORD_VAR>: "<nexus password>"
      TF_VAR_jenkins_allowed_cidr: "<laptop-ip>/32,<OPS_IP>/32"
      TF_VAR_nexus_allowed_cidr: "<laptop-ip>/32,<OPS_IP>/32"
      TF_VAR_git_credential_username: "git"
      TF_VAR_git_ssh_host_key: "<one line from ssh-keyscan>"
      <PLATFORM_REPO_URL_VAR>: "<platform-repo-ssh-url>"
      <PLATFORM_REPO_BRANCH_VAR>: "<platform-branch>"
      <APP_REPO_URL_VAR>: "<app-repo-ssh-url>"
      TF_VAR_docker_repo_url: "<docker-repo-ssh-url>"
      TF_VAR_kubernetes_cluster_name: "hub"
      TF_VAR_aws_kubernetes_cluster_vpc_cidr: "10.100.0.0/16"
      TF_VAR_aws_remote_peering_vpc_id: ""
      aws_eks_instance_type: "m6a.2xlarge"
      TF_VAR_rebuild_nodegroups: "true"
      TF_VAR_bootstrap_mode: "setup"
      TF_VAR_letsencrypt_email: "<your email>"
    volumes:
      - /home/ec2-user/.ssh/platform_git:/secrets/git_id_rsa
EOF
chmod 600 docker-compose.override.yml
docker-compose config -q && echo "settings OK"
```

Run it inside `tmux`, so it survives a dropped SSH session:

```bash
# EC2
tmux new -s platform-testprod
cd ~/platform/testprod
docker-compose build
docker-compose up --force-recreate 2>&1 | tee bootstrap-$(date +%Y%m%d-%H%M).log
# detach: Ctrl-b then d    re-attach: tmux attach -t platform-testprod
```

**DNS: do this as soon as the hosted zone exists**, in a second terminal. The certificate and the Jenkins URL depend on it.

```bash
# EC2: name servers of the new zone
ZONE=$(aws route53 list-hosted-zones-by-name --dns-name <tprd.yourco.com> \
  --query 'HostedZones[0].Id' --output text --profile $TP_PROFILE)
aws route53 get-hosted-zone --id "$ZONE" --query DelegationSet.NameServers --profile $TP_PROFILE
```

Add an **NS record** for `tprd.yourco.com` with those 4 name servers in the parent zone `yourco.com`, wherever that zone is hosted. Check with `dig NS tprd.yourco.com +short`.

**After it finishes:**

```bash
# EC2: next runs must NOT rebuild all nodes
sed -i 's/TF_VAR_rebuild_nodegroups: "true"/TF_VAR_rebuild_nodegroups: "false"/' docker-compose.override.yml

# Print outputs (Jenkins URL etc.): run once in "show" mode, then set it back to "setup"
sed -i 's/TF_VAR_bootstrap_mode: "setup"/TF_VAR_bootstrap_mode: "show"/' docker-compose.override.yml
docker-compose up --force-recreate
sed -i 's/TF_VAR_bootstrap_mode: "show"/TF_VAR_bootstrap_mode: "setup"/' docker-compose.override.yml
```

**Done when:** `<test-prod-jenkins-url>` opens. The Jenkins user names and passwords are described on the platform "credentials" docs page.

---

## A4. Bootstrap the platform in Test-DR (EC2, 1 to 2 hours)

Same as A3, in its own folder, after A3 has finished.

```bash
# EC2
cd ~/platform
GIT_SSH_COMMAND="ssh -i ~/.ssh/platform_git" git clone -b <platform-branch> <platform-repo-ssh-url> testdr
cd testdr
cp ../testprod/docker-compose.override.yml .
```

Change **only these lines** in `~/platform/testdr/docker-compose.override.yml`. Also put back `rebuild_nodegroups: "true"`, since this is the first run:

| Setting | Test-DR value |
|---|---|
| `TF_VAR_aws_access_key_id` / `TF_VAR_aws_secret_access_key` | the **Test-DR** platform-bootstrap keys |
| `TF_VAR_aws_region` | `eu-west-2` |
| `TF_VAR_domain` | `<tdr.yourco.com>` |
| `TF_VAR_aws_backend_s3_bucket` | `platform-<test-dr-account-id>-tf-backend` |
| `TF_VAR_aws_backend_dynamodb_table` | `platform-tfstate-euw2` |
| `TF_VAR_aws_iam_role_name` | `Platform-Infra-Mgmt-euw2` |
| `TF_VAR_aws_kubernetes_cluster_vpc_cidr` | `10.101.0.0/16` (must not overlap the secondary VPC 10.200.0.0/16 it will be peered with) |
| `TF_VAR_rebuild_nodegroups` | `"true"` (first run) |

```bash
# EC2
docker-compose config -q && echo "settings OK"
tmux new -s platform-testdr
cd ~/platform/testdr
docker-compose build
docker-compose up --force-recreate 2>&1 | tee bootstrap-$(date +%Y%m%d-%H%M).log
```

Do the DNS delegation for `tdr.yourco.com` (as in A3, with `--profile $DR_PROFILE`). Afterwards set `rebuild_nodegroups` to `"false"`.

---

## A5. kubectl access to both clusters (EC2, 5 min)

```bash
# EC2
aws eks update-kubeconfig --name $CLUSTER --region $TP_REGION --profile $TP_PROFILE --alias testprod
aws eks update-kubeconfig --name $CLUSTER --region $DR_REGION --profile $DR_PROFILE --alias testdr

kubectl --context testprod get nodes
kubectl --context testdr   get nodes
kubectl --context testprod -n default get pods | grep -i jenkins     # Jenkins runs in "default"

aws eks describe-cluster --name $CLUSTER --region $TP_REGION --profile $TP_PROFILE --query cluster.version
# if this differs from your kubectl by more than one minor version, reinstall kubectl (A2)
```

Clone the migration scripts now. `scale-smc.sh` is used in A7, the rest in Phase B.

```bash
# EC2
cd ~ && GIT_SSH_COMMAND="ssh -i ~/.ssh/platform_git" git clone <scripts-repo-ssh-url> migration-scripts
ls ~/migration-scripts/cli-aurora-migration/scripts/
```

---

## A6. Test-Prod: app + Aurora (Jenkins, half a day)

**Where:** the Test-Prod platform Jenkins (`<test-prod-jenkins-url>`).

Run these jobs in order, with nickname `test-live` everywhere. The reference run used **`<build-and-deploy-job>`**, which may do all of it in one run. Check its parameters first.

| # | Job | Key inputs |
|---|---|---|
| 1 | Build the Jenkins agents / app images (the build jobs in the build view) | app branch |
| 2 | **`<create-database-job>`** | `kubernetesNickname=test-live`, type **Aurora MySQL**, engine **8.0 / Aurora 3.08.x** (supports Global Database), instance **db.r6g.large** |
| 3 | ActiveMQ deploy job | `kubernetesNickname=test-live` |
| 4 | `<data-load-job>` | `kubernetesNickname=test-live`, the data set to load |
| 5 | `<deploy-stack-job>` | `kubernetesNickname=test-live`, sizing (e.g. `prod-small`), environment name |

Check from the EC2:

```bash
# EC2
kubectl --context testprod -n $NICK get pods                 # all Running / Ready

aws rds describe-db-clusters --region $TP_REGION --profile $TP_PROFILE \
  --query 'DBClusters[].{Id:DBClusterIdentifier,Version:EngineVersion,Status:Status,Endpoint:Endpoint}' --output table

# The engine version must support Global Database (paste the Version from above)
aws rds describe-db-engine-versions --engine aurora-mysql --region $TP_REGION --profile $TP_PROFILE \
  --query "DBEngineVersions[?SupportsGlobalDatabases && EngineVersion=='<version>'].EngineVersion" --output text
```

**Done when:** `<test-prod-admin-ui-url>` and the storefront work. Note the **Aurora cluster ID**; it is the "primary cluster" in Phase B.

---

## A7. Test-DR: app + its own Aurora, then scale to 0 (Jenkins + EC2, half a day)

**Where:** the Test-DR platform Jenkins. Run the **same jobs as A6**, with nickname `test-live`. This mirrors today's Production DR, which has its own Aurora cluster. Then stop it:

```bash
# EC2
kubectl config use-context testdr
~/migration-scripts/cli-aurora-migration/scripts/scale-smc.sh $NICK down
kubectl -n $NICK get deploy        # all app deployments at 0/0
```

**Done when:** all app deployments in Test-DR are at 0. Their replica counts are saved in annotations, so `scale-smc.sh $NICK up` restores them.

---

## A8. Test data in Test-Prod (browser + EC2, 15 min)

1. In the **storefront** (`<test-prod-storefront-url>`), add an item to the cart and place 2 or 3 orders.
2. In the **admin UI** (`<test-prod-admin-ui-url>`), change something visible, such as a product name or a setting. Write down what you changed.
3. Record row counts, to compare after each drill:

```bash
# EC2: DB name/user/password come from the app DB secret
kubectl config use-context testprod
S=$DB_SECRET
DBH=$(kubectl -n $NICK get secret $S -o go-template='{{.data.<HOST_KEY> | base64decode}}')
DBN=$(kubectl -n $NICK get secret $S -o go-template='{{.data.<DB_NAME_KEY> | base64decode}}')
DBU=$(kubectl -n $NICK get secret $S -o go-template='{{.data.<DB_USER_KEY> | base64decode}}')

kubectl -n $NICK run mysql-client --image=mysql:8.0 --restart=Never -- sleep infinity
kubectl -n $NICK wait --for=condition=Ready pod/mysql-client
kubectl -n $NICK exec -it mysql-client -- mysql -h "$DBH" -u "$DBU" -p "$DBN" \
  -e "SELECT COUNT(*) AS orders FROM <orders-table>;"     # enter the <DB_PASS_KEY> value when asked
```

(`<orders-table>` is the usual app orders table. If the name differs, run `SHOW TABLES LIKE '%ORDER%';` first.)

---

## A9. DMS: skip it

The reference run did not include DMS either. For this Test:

- DMS isn't needed to prove the new design, because Global Database replaces it.
- It would need its own network path between the two accounts.

The only Production step it would rehearse is "stop the DMS task", which is a single command on the day.

---

## Phase A checklist

- [ ] A1 Two accounts, admin profiles working, quota requests submitted, `platform-bootstrap` keys saved
- [ ] A2 EC2 `ops-host` running with tools, AWS profiles `testprod` / `testdr`, SSH keys added to Git
- [ ] A3 Test-Prod bootstrap done, DNS delegated, Jenkins reachable, `rebuild_nodegroups` set to false
- [ ] A4 Test-DR bootstrap done, DNS delegated, Jenkins reachable, `rebuild_nodegroups` set to false
- [ ] A5 `kubectl --context testprod|testdr get nodes` both work; scripts repo cloned
- [ ] A6 Test-Prod app works; Aurora cluster ID noted; engine supports Global Database
- [ ] A7 Test-DR deployed and scaled to 0
- [ ] A8 Orders and an admin UI change made; order count recorded

Cost note: from A3 onwards, two EKS clusters, their nodes and two Aurora clusters run around the clock. Tear down with bootstrap mode `cleanup` when testing is done.

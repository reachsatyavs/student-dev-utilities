# Phases B to F: Global Database, DR repoint, drills, rollback, cleanup

> **Flow diagram:** see all steps A1 to F4 on one page in [FLOW.md](FLOW.md).

Continues from [Phase A](PHASE-A-build-test-environment.md). Run the blocks in order and replace every `<placeholder>`.
**Where** each block runs: the **EC2 ops instance** (most of it), **Jenkins**, or a **browser**.

The commands follow the tested reference run, adjusted for Test:

| Phase | What | Downtime in Test-Prod |
|---|---|---|
| B | New London VPC (Test-Prod account), peering to Test-DR, Aurora Global Database | None |
| C | Point the Test-DR app stack at the London secondary | None |
| D | Drills: planned failover, failback, disaster failover, rebuild | Yes, during each drill |
| E | Rollback: back to a single-region Aurora | None |
| F | Delete everything | — |

---

## Before you start (EC2)

```bash
# EC2: variables from Phase A must be set
source ~/.bashrc
echo "$TP_REGION $DR_REGION $TP_PROFILE $DR_PROFILE $CLUSTER $NICK"

# Working folder and test config, copied from the "mock" config of the reference run
cd ~/migration-scripts
cp -r cli-aurora-migration/config/mock cli-aurora-migration/config/test
ls cli-aurora-migration/config/test/          # 1-vpc-config.env  2-migration-config.env

# A log of start/end times for every step, to measure downtime and RTO
mark() { echo "$(date -u +%FT%TZ)  $*" | tee -a ~/drill-log.txt; }
declare -f mark >> ~/.bashrc
```

Values used below (from Phase A):

| Name | Value |
|---|---|
| Test-Prod EKS VPC | `10.100.0.0/16` (eu-west-1) |
| Test-DR EKS VPC | `10.101.0.0/16` (eu-west-2) |
| New Aurora secondary VPC (Test-Prod account) | `10.200.0.0/16` (eu-west-2) |
| Primary Aurora cluster ID | from A6, e.g. `aurora-test-live` |

---

## Phase B: Network and Global Database (EC2, about 1 day, no downtime)

### B1. Fill in the VPC config (EC2)

```bash
# EC2: values you need for the file
DR_VPC_ID=$(aws eks describe-cluster --name $CLUSTER --region $DR_REGION --profile $DR_PROFILE \
  --query cluster.resourcesVpcConfig.vpcId --output text)
DR_ACCT=$(aws sts get-caller-identity --profile $DR_PROFILE --query Account --output text)
echo "DR EKS VPC: $DR_VPC_ID   DR account: $DR_ACCT"

vi cli-aurora-migration/config/test/1-vpc-config.env
```

Set these values. Keep the key names as they are in the file.

| Setting | Value |
|---|---|
| Region | `eu-west-2` |
| VPC name | `aurora-db-secondary-vpc` |
| VPC CIDR | `10.200.0.0/16` |
| Availability Zones | `eu-west-2a,eu-west-2b,eu-west-2c` |
| Application (DR EKS) VPC ID | `$DR_VPC_ID` from above |
| Application VPC CIDR | `10.101.0.0/16` |
| Application account ID | `$DR_ACCT` from above |
| Name of the DB subnet group / security group | any clear name, e.g. `test-aurora-secondary-…` |

### B2. Create the secondary VPC in the Test-Prod account (EC2, about 10 min)

```bash
# EC2: one terminal = Test-Prod account
export AWS_PROFILE=$TP_PROFILE
aws sts get-caller-identity --query Account --output text     # must be the Test-Prod account
cd ~/migration-scripts

cli-aurora-migration/scripts/1-create-secondary-vpc.sh --config cli-aurora-migration/config/test/1-vpc-config.env --dry-run
cli-aurora-migration/scripts/1-create-secondary-vpc.sh --config cli-aurora-migration/config/test/1-vpc-config.env
# answer "yes"
```

**Done when:** the output ends with "VPC Infrastructure Created Successfully!" and prints `SECONDARY_SUBNET_IDS`, `SECONDARY_VPC_SECURITY_GROUPS` and `SECONDARY_DB_SUBNET_GROUP`. Copy those three lines.

### B3. Fill in the migration config (EC2)

```bash
# EC2: the primary cluster ID and its settings
aws rds describe-db-clusters --region $TP_REGION \
  --query 'DBClusters[].{Id:DBClusterIdentifier,Version:EngineVersion,Members:DBClusterMembers[].DBInstanceIdentifier}' --output json

vi cli-aurora-migration/config/test/2-migration-config.env
```

| Setting | Value |
|---|---|
| `SECONDARY_SUBNET_IDS` | from B2, **spaces changed to commas** |
| `SECONDARY_VPC_SECURITY_GROUPS` | from B2 |
| `SECONDARY_DB_SUBNET_GROUP` | from B2 |
| Primary cluster ID / region | the A6 cluster, `eu-west-1` |
| Global cluster ID | primary ID + `-global` (e.g. `aurora-test-live-global`) |
| Secondary cluster ID / region | primary ID + `-secondary`, `eu-west-2` |
| Secondary instance class / count | `db.r6g.large`, `2` |
| `CREATE_SNAPSHOT` | `true` (a safety snapshot before converting) |
| KMS key for eu-west-2 | empty = AWS-managed key (fine for Test) |

### B4. Check the London prerequisites (EC2, 2 min)

```bash
# EC2 (Test-Prod terminal)
cli-aurora-migration/scripts/2-prepare-secondary-region.sh --config cli-aurora-migration/config/test/2-migration-config.env
```

**Done when:** "All prerequisites are met!"

### B5. VPC peering: Test-Prod secondary VPC to Test-DR EKS VPC (EC2, two terminals, 15 min)

**Terminal 1, Test-Prod account:**

```bash
# EC2 terminal 1
export AWS_PROFILE=$TP_PROFILE
cd ~/migration-scripts
cli-aurora-migration/scripts/3-setup-vpc-peering.sh --config cli-aurora-migration/config/test/1-vpc-config.env --dry-run
cli-aurora-migration/scripts/3-setup-vpc-peering.sh --config cli-aurora-migration/config/test/1-vpc-config.env
# answer "yes"; it then PAUSES and prints an accept command with a pcx-... ID
```

**Terminal 2, Test-DR account.** Run when terminal 1 pauses:

```bash
# EC2 terminal 2
export AWS_PROFILE=$DR_PROFILE
source ~/.bashrc
PCX=<pcx-id printed in terminal 1>

aws ec2 accept-vpc-peering-connection --vpc-peering-connection-id $PCX --region $DR_REGION
```

Press **Enter** in terminal 1. When it pauses again and asks for routes in the application account, add a route in **every** route table of the DR EKS VPC (terminal 2):

```bash
# EC2 terminal 2
DR_VPC_ID=$(aws eks describe-cluster --name $CLUSTER --region $DR_REGION \
  --query cluster.resourcesVpcConfig.vpcId --output text)
for RT in $(aws ec2 describe-route-tables --region $DR_REGION \
              --filters Name=vpc-id,Values=$DR_VPC_ID --query 'RouteTables[].RouteTableId' --output text); do
  aws ec2 create-route --region $DR_REGION --route-table-id $RT \
    --destination-cidr-block 10.200.0.0/16 --vpc-peering-connection-id $PCX && echo "route added: $RT"
done
```

Press **Enter** in terminal 1 again.

**Done when:** terminal 1 shows "VPC Peering Setup Complete!"

### B6. Create the Global Database and the London secondary (EC2, 30 to 45 min, no downtime)

```bash
# EC2 terminal 1 (Test-Prod), inside tmux: it runs for a while
tmux new -s global-db
export AWS_PROFILE=$TP_PROFILE
cd ~/migration-scripts
mark "B6 start"
cli-aurora-migration/scripts/4-migrate-aurora-to-global.sh --config cli-aurora-migration/config/test/2-migration-config.env --dry-run
cli-aurora-migration/scripts/4-migrate-aurora-to-global.sh --config cli-aurora-migration/config/test/2-migration-config.env
# answer "yes" at each prompt
mark "B6 end"
```

**Done when:** "Migration completed successfully!" and "Global cluster has 2 members", with Ireland as Writer and London as Reader.

### B7. Check (EC2 + browser)

```bash
# EC2
aws rds describe-global-clusters --region $TP_REGION --profile $TP_PROFILE \
  --query 'GlobalClusters[].GlobalClusterMembers[].{Cluster:DBClusterArn,Writer:IsWriter,Sync:SynchronizationStatus}' --output table

# Replication lag in London over the last 30 min (milliseconds; normally well under 1000)
START=$(date -u -d '-30 min' +%FT%TZ)
aws cloudwatch get-metric-statistics --region $DR_REGION --profile $TP_PROFILE \
  --namespace AWS/RDS --metric-name AuroraGlobalDBReplicationLag \
  --dimensions Name=DBClusterIdentifier,Value=<secondary-cluster-id> \
  --start-time $START --end-time $(date -u +%FT%TZ) --period 300 --statistics Average Maximum --output table
```

Browser: Test-Prod admin UI and storefront still work.

**Jenkins option:** B4 and B6 can run as **Pipeline 2** (`aurora-migration-test/jenkins/Jenkinsfile.aurora-global-setup`). Do B1 to B5 by hand at least once first.

---

## Phase C: Point Test-DR at the secondary (EC2 + Jenkins, half a day)

### C1. Collect the values for the DR repoint (EC2)

The secondary already has all users and data: they replicate from Ireland. So DR uses **the same DB name, users and passwords as Test-Prod**.

```bash
# EC2: secondary cluster endpoint (the writer endpoint, NOT cluster-ro)
aws rds describe-db-clusters --region $DR_REGION --profile $TP_PROFILE \
  --db-cluster-identifier <secondary-cluster-id> --query 'DBClusters[0].Endpoint' --output text

# Credentials from the Test-Prod secret. Shown on screen only: don't save them in a file or a ticket.
kubectl config use-context testprod
S=$DB_SECRET
for K in <ROOT_USER_KEY> <ROOT_PASS_KEY> <DB_NAME_KEY> <DB_USER_KEY> <DB_PASS_KEY>; do
  printf '%-16s ' "$K"; kubectl -n $NICK get secret $S -o go-template="{{.data.$K | base64decode}}"; echo
done
```

### C2. Check the network path from Test-DR (EC2, 2 min)

```bash
# EC2
kubectl config use-context testdr
JPOD=$(kubectl -n default get pods -o name | grep -i jenkins | head -1)
kubectl -n default exec -it $JPOD -- bash -c \
  'timeout 5 bash -c "echo > /dev/tcp/<secondary-endpoint>/3306" && echo "CONNECTED" || echo "NO CONNECTION"'
```

**Done when:** `CONNECTED`. If not, check the B5 routes and the secondary security group (MySQL from `10.101.0.0/16`).

### C3. Back up the Test-DR DB secret (EC2)

```bash
# EC2
kubectl config use-context testdr
mkdir -p ~/backups && chmod 700 ~/backups
kubectl -n $NICK get secret $DB_SECRET -o yaml > ~/backups/dr-mysql-secret.ORIG.yml
chmod 600 ~/backups/dr-mysql-secret.ORIG.yml
kubectl -n $NICK get secret $DB_SECRET -o go-template='{{.data.<HOST_KEY> | base64decode}}'; echo
# note this hostname: it is Test-DR's own Aurora (from A7), needed for the rollback in Phase E
```

### C4. Run `<use-existing-database-job>` (Jenkins, Test-DR)

**Where:** Test-DR platform Jenkins. Values from C1:

| Parameter | Value |
|---|---|
| `deleteDatabase` | unchecked |
| `adoptExistingDatabaseSecret` | **checked** |
| `databaseType` | `mysql` |
| `databaseRootUsername` / `databaseRootPassword` | `<ROOT_USER_KEY>` / `<ROOT_PASS_KEY>` |
| `databaseServerUrl` | secondary cluster endpoint (C1) |
| `databaseName` | `<DB_NAME_KEY>` |
| `databaseUsername` / `databasePassword` | `<DB_USER_KEY>` / `<DB_PASS_KEY>` |
| `kubernetesNickname` | `test-live` |
| `<BRANCH_PARAMETER>` | `<adopt-secret-branch>`, until the adopt-existing-secret feature is released |

### C5. Check the secret now points at the secondary (EC2)

```bash
# EC2
kubectl config use-context testdr
for K in <HOST_KEY> <DB_NAME_KEY> <DB_USER_KEY>; do
  printf '%-16s ' "$K"; kubectl -n $NICK get secret $DB_SECRET -o go-template="{{.data.$K | base64decode}}"; echo
done
# <HOST_KEY> must be the secondary endpoint
kubectl -n $NICK get deploy        # still all 0/0: the secondary is read-only until a failover
```

---

## Phase D: Drills (EC2 + browser, 1 to 2 days, Test only)

Every drill uses the same pattern. Watch the active side: `watch kubectl get pods -n $NICK`.

**Before each drill**, take an order count on the side that is currently live (A8 commands, using its context).

### D1. Planned failover: Ireland to London (about 30 min, no data loss)

```bash
# EC2
cd ~/migration-scripts
export AWS_PROFILE=$TP_PROFILE            # the Global Database is in the Test-Prod account
mark "D1 start: scale down Test-Prod"
kubectl config use-context testprod
cli-aurora-migration/scripts/scale-smc.sh $NICK down

mark "D1 DB failover start"
cli-aurora-migration/scripts/6-failover-to-secondary.sh --config cli-aurora-migration/config/test/2-migration-config.env --planned --dry-run
cli-aurora-migration/scripts/6-failover-to-secondary.sh --config cli-aurora-migration/config/test/2-migration-config.env --planned
mark "D1 DB failover end"

kubectl config use-context testdr
cli-aurora-migration/scripts/scale-smc.sh $NICK up
watch kubectl get pods -n $NICK           # wait for all Running/Ready, then Ctrl-C
mark "D1 London app up"
```

**Verify (browser):** Test-DR storefront (`<test-dr-storefront-url>`): add to cart. Test-DR admin UI: edit a value. The order count matches the count taken before the drill.

### D2. Data-pop while failed over (Jenkins, Test only)

This proves Jenkins jobs work against London while it is the writer. **It replaces the data**, so take a new order count afterwards.

```bash
# EC2
kubectl config use-context testdr
cli-aurora-migration/scripts/scale-smc.sh $NICK down
```

In **Test-DR Jenkins**, run `<data-load-job>` (`kubernetesNickname=test-live`). Then:

```bash
# EC2
cli-aurora-migration/scripts/scale-smc.sh $NICK up
```

### D3. Optional performance test

As in the reference run: in Jenkins, run `<deploy-stack-job>` with environment `perf`, sizing `prod-small`, HPA on, and the load-test CIDRs on the ingress. Run the load test against London, then repeat on Ireland after D4 as a baseline. In the reference run, the load test was tuned for eu-west-1.

### D4. Failback: London to Ireland (about 30 min)

```bash
# EC2: take an order count in London first (A8 commands with context testdr)
export AWS_PROFILE=$TP_PROFILE
mark "D4 start: scale down London"
kubectl config use-context testdr
cli-aurora-migration/scripts/scale-smc.sh $NICK down

mark "D4 DB failback start"
cli-aurora-migration/scripts/7-failback-to-primary.sh --config cli-aurora-migration/config/test/2-migration-config.env --dry-run
#   the dry run must say: "Detected: POST-PLANNED FAILOVER"
cli-aurora-migration/scripts/7-failback-to-primary.sh --config cli-aurora-migration/config/test/2-migration-config.env
mark "D4 DB failback end"

kubectl config use-context testprod
cli-aurora-migration/scripts/scale-smc.sh $NICK up
watch kubectl get pods -n $NICK
mark "D4 Ireland app up"
```

**Verify:** Test-Prod admin UI and storefront work. The admin change and orders made in London are visible in Ireland, and the order count matches London's.

### D5. Disaster failover (Test only, about 15 min)

This simulates losing Ireland. London is **detached** from the global cluster and becomes a standalone writer. The global cluster is then broken until D6.

```bash
# EC2
export AWS_PROFILE=$TP_PROFILE
mark "D5 start"
kubectl config use-context testprod
cli-aurora-migration/scripts/scale-smc.sh $NICK down     # in a real disaster Ireland might be unreachable

cli-aurora-migration/scripts/6-failover-to-secondary.sh --config cli-aurora-migration/config/test/2-migration-config.env --disaster --dry-run
cli-aurora-migration/scripts/6-failover-to-secondary.sh --config cli-aurora-migration/config/test/2-migration-config.env --disaster
mark "D5 London promoted"

kubectl config use-context testdr
cli-aurora-migration/scripts/scale-smc.sh $NICK up
watch kubectl get pods -n $NICK
mark "D5 London app up"
```

**Verify:** Test-DR storefront and admin UI work. Make a new order in London; it should come back to Ireland in D6.

### D6. Rebuild after the disaster (30 to 60 min)

**Warning:** this **deletes the Ireland cluster**, whose data is stale, recreates it from London's data, and makes Ireland the writer again.

```bash
# EC2: both sides down, so nothing is connected to either database
export AWS_PROFILE=$TP_PROFILE
kubectl config use-context testprod && cli-aurora-migration/scripts/scale-smc.sh $NICK down
kubectl config use-context testdr   && cli-aurora-migration/scripts/scale-smc.sh $NICK down

mark "D6 rebuild start"
cli-aurora-migration/scripts/7-failback-to-primary.sh --config cli-aurora-migration/config/test/2-migration-config.env --dry-run
#   the dry run must say: "Detected: POST-DISASTER FAILOVER"
cli-aurora-migration/scripts/7-failback-to-primary.sh --config cli-aurora-migration/config/test/2-migration-config.env
#   answer "yes", including "Delete old primary cluster ...? (Required for rebuild)"
mark "D6 rebuild end"

kubectl config use-context testprod && cli-aurora-migration/scripts/scale-smc.sh $NICK up
watch kubectl get pods -n $NICK
mark "D6 Ireland app up"
```

**Verify:**

```bash
# EC2: Ireland Writer + London Reader again
aws rds describe-global-clusters --region $TP_REGION \
  --query 'GlobalClusters[].GlobalClusterMembers[].{Cluster:DBClusterArn,Writer:IsWriter}' --output table
```

Test-Prod admin UI and storefront work, and the order made in London in D5 is there.

**Check the DR secret after D6.** The secondary keeps its name, so its endpoint should be unchanged. Run C5 again; `<HOST_KEY>` must still resolve.

### Drill results (fill in from `~/drill-log.txt`)

| Drill | App down (scale-down to app up) | DB switch time | Lag before | Data correct? | Manual surprises |
|---|---|---|---|---|---|
| D1 planned failover | | | | | |
| D4 failback | | | | | |
| D5 disaster failover | | | | | |
| D6 rebuild | | | | | |

**Jenkins option:** D1, D4, D5 and D6 can run as **Pipeline 3** (`Jenkinsfile.aurora-dr-drill`, with `ACTION=planned-failover`, `failback` or `disaster-failover`). Do each drill by hand once first.

---

## Phase E: Rollback test (EC2 + Jenkins, half a day)

This proves you can undo the whole change: Test-Prod goes back to a single-region Aurora, and Test-DR goes back to its own Aurora.

### E1. Point Test-DR back at its own Aurora (Jenkins + EC2)

Do this first, because E2 deletes the secondary.

```bash
# EC2
kubectl config use-context testdr
cd ~/migration-scripts && cli-aurora-migration/scripts/scale-smc.sh $NICK down
# Original DR values (Test-DR's own Aurora), decoded from the C3 backup. Shown on screen only.
for K in <HOST_KEY> <ROOT_USER_KEY> <ROOT_PASS_KEY> <DB_NAME_KEY> <DB_USER_KEY> <DB_PASS_KEY>; do
  printf '%-16s ' "$K"; grep "^  $K:" ~/backups/dr-mysql-secret.ORIG.yml | awk '{print $2}' | base64 -d; echo
done
```

In **Test-DR Jenkins**, run `<use-existing-database-job>` again. Use the **C3 hostname** (Test-DR's own Aurora) and the **original DR credentials**, decoded from the backup file, with `adoptExistingDatabaseSecret` checked.

Using the job, rather than `kubectl apply` of the backup, keeps the job's own record of the secret in step with Kubernetes.

```bash
# EC2: check
kubectl -n $NICK get secret $DB_SECRET -o go-template='{{.data.<HOST_KEY> | base64decode}}'; echo
```

### E2. Remove the Global Database (EC2, 20 to 30 min)

```bash
# EC2 (Test-Prod)
export AWS_PROFILE=$TP_PROFILE
cd ~/migration-scripts
cli-aurora-migration/scripts/5-rollback-aurora-global.sh --config cli-aurora-migration/config/test/2-migration-config.env --level 2 --dry-run
cli-aurora-migration/scripts/5-rollback-aurora-global.sh --config cli-aurora-migration/config/test/2-migration-config.env --level 2
# type ROLLBACK when asked. It snapshots the secondary first, then deletes it and the global cluster.
```

**Done when:** `aws rds describe-global-clusters --region $TP_REGION` returns an empty list, and Test-Prod admin UI and storefront still work.

### E3. Remove the peering and DR routes (EC2, two terminals)

```bash
# EC2 terminal 2 (Test-DR): remove the routes to 10.200.0.0/16
export AWS_PROFILE=$DR_PROFILE
DR_VPC_ID=$(aws eks describe-cluster --name $CLUSTER --region $DR_REGION --query cluster.resourcesVpcConfig.vpcId --output text)
for RT in $(aws ec2 describe-route-tables --region $DR_REGION --filters Name=vpc-id,Values=$DR_VPC_ID \
              --query 'RouteTables[].RouteTableId' --output text); do
  aws ec2 delete-route --region $DR_REGION --route-table-id $RT --destination-cidr-block 10.200.0.0/16 2>/dev/null \
    && echo "route removed: $RT"
done
```

```bash
# EC2 terminal 1 (Test-Prod): delete the peering
export AWS_PROFILE=$TP_PROFILE
PCX=$(aws ec2 describe-vpc-peering-connections --region $DR_REGION \
  --filters Name=status-code,Values=active Name=accepter-vpc-info.cidr-block,Values=10.101.0.0/16 \
  --query 'VpcPeeringConnections[0].VpcPeeringConnectionId' --output text)
echo $PCX
aws ec2 delete-vpc-peering-connection --region $DR_REGION --vpc-peering-connection-id $PCX
```

### E4. Delete the secondary VPC (EC2, about 10 min)

```bash
# EC2 terminal 1 (Test-Prod)
cli-aurora-migration/scripts/cleanup-delete-secondary-vpc.sh --region $DR_REGION --vpc-name aurora-db-secondary-vpc
```

### E5. Check you are back to the start

```bash
# EC2
aws rds describe-db-clusters --region $TP_REGION --profile $TP_PROFILE \
  --query 'DBClusters[].{Id:DBClusterIdentifier,Global:GlobalClusterIdentifier}' --output table   # Global empty
aws ec2 describe-vpcs --region $DR_REGION --profile $TP_PROFILE \
  --filters Name=cidr,Values=10.200.0.0/16 --query 'Vpcs[].VpcId'                               # []
```

Optional: run Phases B to D again (this time with Pipelines 2 and 3) to prove the steps can be repeated.

---

## Phase F: Delete everything (EC2 + Jenkins, half a day)

Aurora in two regions, EKS, nodes and NAT gateways cost money every hour. Do this as soon as testing is finished.

### F1. Remove what the Jenkins jobs created, in each region (Jenkins)

In **Test-DR Jenkins**, then **Test-Prod Jenkins**:

1. `<deploy-stack-job>`: **delete**, `kubernetesNickname=test-live`
2. The ActiveMQ job: **delete**
3. `<create-database-job>` (or `<use-existing-database-job>`): with **`deleteDatabase` checked**

If a delete job fails on Aurora, delete Aurora from the EC2 instead:

```bash
# EC2: only if F1.3 failed. Example for one cluster; repeat for each.
aws rds describe-db-clusters --region <region> --profile <profile> \
  --query 'DBClusters[].{Id:DBClusterIdentifier,Members:DBClusterMembers[].DBInstanceIdentifier}'
aws rds delete-db-instance --region <region> --profile <profile> --db-instance-identifier <instance-id>   # each instance
aws rds delete-db-cluster  --region <region> --profile <profile> --db-cluster-identifier <cluster-id> --skip-final-snapshot
```

### F2. Tear down the platform in each account (EC2, about 1 hour each)

```bash
# EC2: Test-DR first
cd ~/platform/testdr
sed -i 's/TF_VAR_bootstrap_mode: "setup"/TF_VAR_bootstrap_mode: "cleanup"/' docker-compose.override.yml
docker-compose up --force-recreate 2>&1 | tee cleanup-$(date +%Y%m%d-%H%M).log

# then Test-Prod
cd ~/platform/testprod
sed -i 's/TF_VAR_bootstrap_mode: "setup"/TF_VAR_bootstrap_mode: "cleanup"/' docker-compose.override.yml
docker-compose up --force-recreate 2>&1 | tee cleanup-$(date +%Y%m%d-%H%M).log
```

If "cleanup" refuses because other Terraform workspaces exist, F1 missed something. As a last resort, use mode `force-cleanup` and set `TF_VAR_approve_force_cleanup: "true"`.

### F3. Leftovers that cost money (EC2)

```bash
# EC2: run for each profile/region pair: testprod+eu-west-1, testprod+eu-west-2, testdr+eu-west-2
P=testprod; R=eu-west-1
aws rds describe-db-clusters          --profile $P --region $R --query 'DBClusters[].DBClusterIdentifier'
aws rds describe-db-cluster-snapshots --profile $P --region $R --snapshot-type manual --query 'DBClusterSnapshots[].DBClusterSnapshotIdentifier'
aws ec2 describe-nat-gateways         --profile $P --region $R --filter Name=state,Values=available --query 'NatGateways[].NatGatewayId'
aws ec2 describe-addresses            --profile $P --region $R --query 'Addresses[].{Ip:PublicIp,Alloc:AllocationId}'
aws eks list-clusters                 --profile $P --region $R

# delete manual snapshots you no longer need (e.g. the E2 pre-rollback snapshot)
aws rds delete-db-cluster-snapshot --profile $P --region $R --db-cluster-snapshot-identifier <snapshot-id>
```

### F4. DNS, ops instance, users, accounts (laptop)

```bash
# laptop
# 1) Remove the NS records for tprd.<domain> and tdr.<domain> from the parent zone.

# 2) Terminate the ops EC2 and release its Elastic IP
export AWS_PROFILE=testprod-admin AWS_REGION=eu-west-1
ID=$(aws ec2 describe-instances --filters Name=tag:Name,Values=ops-host Name=instance-state-name,Values=running \
  --query 'Reservations[0].Instances[0].InstanceId' --output text)
ALLOC=$(aws ec2 describe-addresses --filters Name=instance-id,Values=$ID --query 'Addresses[0].AllocationId' --output text)
aws ec2 terminate-instances --instance-ids $ID && aws ec2 wait instance-terminated --instance-ids $ID
aws ec2 release-address --allocation-id $ALLOC

# 3) Delete the platform-bootstrap users' access keys (in each account)
for P in testprod-admin testdr-admin; do
  for K in $(aws iam list-access-keys --user-name platform-bootstrap --profile $P --query 'AccessKeyMetadata[].AccessKeyId' --output text); do
    aws iam delete-access-key --user-name platform-bootstrap --access-key-id $K --profile $P
  done
done

# 4) Optional: close the Test accounts (management account; they stay suspended for 90 days)
aws organizations close-account --account-id <TEST_PROD_ACCOUNT_ID> --profile mgmt
aws organizations close-account --account-id <TEST_DR_ACCOUNT_ID>   --profile mgmt
```

---

## Checklist

- [ ] B1–B3 configs filled in (`config/test/`)
- [ ] B4 London prerequisites met
- [ ] B5 peering active, routes in every DR route table
- [ ] B6 global cluster with 2 members; B7 lag under 1 s, Test-Prod unaffected
- [ ] C2 Test-DR reaches the secondary on 3306
- [ ] C3 DR secret backed up; C4–C5 DR secret points at the secondary
- [ ] D1 planned failover; D2 data-pop in London; D4 failback; data correct each time
- [ ] D5 disaster failover; D6 rebuild; global cluster healthy again
- [ ] Drill results table filled in
- [ ] E1–E5 rollback done, back to the starting state
- [ ] F1–F4 everything deleted; no clusters, snapshots, NAT gateways or Elastic IPs left

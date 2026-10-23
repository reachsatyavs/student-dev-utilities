# Inputs by step: what each step needs, and where it comes from

[Test plan](README.md) · **Inputs by step** · [Flow](02-FLOW.md) · [Phase A](03-PHASE-A-build-test-environment.md) · [Phases B to F](04-PHASE-B-to-F-global-db-drills-cleanup.md)

Companion to [Phase A](03-PHASE-A-build-test-environment.md) and [Phases B to F](04-PHASE-B-to-F-global-db-drills-cleanup.md).

How to use it:

1. Collect everything in **Part 1** before you start A1.
2. Before each step, check its **Needs** in **Part 2**. Each input either comes from Part 1, or is an output of an earlier step (shown as "from A2", "from B6", and so on).
3. Write each new value into the **register** in **Part 3** as soon as a step produces it.

Never write passwords or secret keys in this document or the register. Keep them in a password manager, and note only *where* they are.

---

## Part 1: Collect before A1

| # | Input | Example | Get it from | First needed |
|---|---|---|---|---|
| P1 | Access to the AWS Organizations **management** account (a CLI profile) | profile `mgmt` | Cloud governance / AWS admin | A1 |
| P2 | Two **unique e-mail addresses**, never used for AWS before | `aws-test-prod@yourco.com`, `aws-test-dr@yourco.com` | You / IT (mail aliases) | A1 |
| P3 | Account names | `Test-Prod`, `Test-DR` | You | A1 |
| P4 | Regions | primary `eu-west-1`, DR `eu-west-2` | Agreed design | A1 |
| P5 | Budget approval: two EKS clusters, Aurora in two regions, NAT gateways, for 1–2 weeks | — | Cloud governance / manager | A1 |
| P6 | Network ranges, agreed not to overlap anything they will be peered with | Test-Prod EKS `10.100.0.0/16`, Test-DR EKS `10.101.0.0/16`, Aurora secondary `10.200.0.0/16` | Network team | A3, A4, B1 |
| P7 | Your laptop's public IP | `curl -s https://checkip.amazonaws.com` | You | A2, A3 |
| P8 | Parent DNS domain, and the right to add NS records to it | `yourco.com` | DNS team | A3, A4 |
| P9 | Sub-domain names | `tprd.yourco.com`, `tdr.yourco.com` | You (agreed with DNS team) | A3, A4 |
| P10 | Git host and the three repo URLs (SSH): platform, app, Docker | `git@git.yourco.com:ops/<platform-repo>.git` | Platform / dev team | A2, A3 |
| P11 | Platform repo branch to bootstrap from | `master` | Platform team / vendor | A3 |
| P12 | The right to add an SSH key to those three repos | — | Git admin | A2 |
| P13 | Migration scripts repo URL (with `cli-aurora-migration/`) and access to it | — | Team that ran the reference run | A5 |
| P14 | Artifact repository (Nexus) user and password | — | Your vendor | A3 |
| P15 | E-mail for certificate expiry alerts | `ops@yourco.com` | You | A3 |
| P16 | Sizes | ops EC2 `t3.large` + 50 GB; EKS nodes `m6a.2xlarge`; Aurora `db.r6g.large` | Agreed design | A2, A3, A6, B3 |
| P17 | Aurora engine version that supports Global Database | Aurora MySQL 3.08.x (MySQL 8.0) | DBA (checked in A6) | A6 |
| P18 | App nickname / namespace (same in both regions) | `test-live` | You | A6 |
| P19 | Jenkins job names and parameters for your platform version (`<create-database-job>`, `<deploy-stack-job>`, `<data-load-job>`, `<use-existing-database-job>`, `<build-and-deploy-job>`) | see the local name map | Platform Jenkins / platform team | A6 |
| P20 | Branch with the adopt-existing-secret feature, if not yet released | `<adopt-secret-branch>` | Platform team / vendor | C4 |

---

## Part 2: Step by step

### Phase A: Build the Test environment

| Step | Needs (from where) | Produces (used in) |
|---|---|---|
| **A1** Create accounts, profiles, quotas, bootstrap users | P1, P2, P3, P4 | **Test-Prod account ID**, **Test-DR account ID** (A1 profiles, A3, A4, B1, F4); laptop profiles `testprod-admin`, `testdr-admin` (A2, F4); quota request IDs; **two platform-bootstrap access keys** (password manager → A2, A3, A4) |
| **A2** Ops EC2, tools, profiles, SSH keys | `testprod-admin` profile (A1); laptop IP (P7); access keys (A1); Git host (P10); right to add keys (P12) | **ops-host key file** `*.pem` (to log in); **ops IP** (A3/A4 allowed CIDRs); instance ID + Elastic IP allocation ID (F4); EC2 profiles `testprod`, `testdr` (all later steps); **Git SSH key** (public key → Git admin; private key → A3/A4); **EKS node key** (A3/A4); **Git host key line** (A3/A4) |
| **A3** Bootstrap Test-Prod | Test-Prod access key (A1); account ID (A1, for the bucket name); EKS node public key, Git host key, ops IP, Git key path (A2); domain (P8, P9); CIDR `10.100.0.0/16` (P6); repos + branch (P10, P11); Nexus login (P14); laptop IP (P7); alert e-mail (P15); node size (P16) | EKS cluster `hub` in eu-west-1; **Route53 zone name servers** (→ DNS team: NS record in parent zone); **Test-Prod Jenkins URL** and **Jenkins logins** (A6); Terraform state bucket and table (F2); settings file `~/platform/testprod/docker-compose.override.yml` (F2) |
| **A4** Bootstrap Test-DR | Same as A3, with: Test-DR access key and account ID (A1); `tdr` sub-domain (P9); CIDR `10.101.0.0/16` (P6) | EKS cluster `hub` in eu-west-2; name servers (→ DNS team); **Test-DR Jenkins URL** and logins (A7, C4); settings file `~/platform/testdr/…` (F2) |
| **A5** kubectl access, scripts repo | Cluster name and regions (A3, A4); EC2 profiles (A2); scripts repo URL (P13) | kubectl contexts **`testprod`**, **`testdr`** (A7 onward); **EKS version** (→ kubectl version check); scripts at `~/migration-scripts` (A7, B onward) |
| **A6** Test-Prod: app + Aurora (Jenkins) | Test-Prod Jenkins URL + login (A3); nickname (P18); job names (P19); engine version (P17); Aurora size (P16) | **Primary Aurora cluster ID** and **engine version** (B3); **app DB secret name** (`$DB_SECRET`, A8, C1); **admin UI URL**, **storefront URL** (A8, B7, D) |
| **A7** Test-DR: app + own Aurora, scale to 0 | Test-DR Jenkins (A4); nickname (P18); job names (P19); `testdr` context and scripts (A5) | DR's own **Aurora cluster ID / hostname** (C3, E1, F1); DR app deployed and scaled to 0, replica counts saved in annotations (D1) |
| **A8** Test data | Admin UI + storefront URLs (A6); `$DB_SECRET` (A6); `testprod` context (A5) | **Baseline order count**; note of the admin change made (D1, D4) |
| **A9** DMS | — (skipped) | — |

### Phase B: Network and Global Database

| Step | Needs (from where) | Produces (used in) |
|---|---|---|
| **B1** Fill `1-vpc-config.env` | **DR EKS VPC ID** (lookup command in B1, uses A4 + A5); **Test-DR account ID** (A1); CIDRs (P6); region and AZs (P4) | Filled `config/test/1-vpc-config.env` (B2, B5); chosen **secondary VPC name** (E4) |
| **B2** Create secondary VPC (script 1) | `testprod` profile (A2); B1 file | **Secondary VPC ID**; **3 subnet IDs** (`SECONDARY_SUBNET_IDS`), **security group ID** (`SECONDARY_VPC_SECURITY_GROUPS`), **DB subnet group** (`SECONDARY_DB_SUBNET_GROUP`) (all → B3); NAT gateway ID (F3); resource tracking file |
| **B3** Fill `2-migration-config.env` | The three `SECONDARY_*` values (B2); **primary cluster ID** + engine version (A6); instance class and count (P16) | Filled `config/test/2-migration-config.env` (B4, B6, D, E2); chosen **global cluster ID** and **secondary cluster ID** (B6, B7, C1) |
| **B4** Check London (script 2) | B3 file | "All prerequisites are met" (go-ahead for B5) |
| **B5** Peering (script 3, two terminals) | `testprod` + `testdr` profiles (A2); B1 file; DR EKS VPC ID (B1) | **Peering ID `pcx-…`** (E3); routes in every DR EKS route table (E3) |
| **B6** Global Database (script 4) | B3 file; B4 and B5 done | **Global cluster** (B7, D, E2); **secondary cluster ARN**; **secondary endpoint** (writer) and reader endpoint (C1, C2); pre-migration snapshot if `CREATE_SNAPSHOT=true` (F3); log and state files |
| **B7** Check | Secondary cluster ID (B3); admin UI + storefront URLs (A6) | **Replication lag baseline** (D, drill results); confirmation that Test-Prod is unaffected |

### Phase C: Point Test-DR at the secondary

| Step | Needs (from where) | Produces (used in) |
|---|---|---|
| **C1** Collect values | **Secondary endpoint** (B6); **Test-Prod DB secret** values: root user and password, DB name, app user and password (`$DB_SECRET`, A6) | Values for C4 (on screen only, never saved) |
| **C2** Network check | Secondary endpoint (B6); `testdr` context (A5); Jenkins pod in `default` | "CONNECTED" (go-ahead for C4) |
| **C3** Back up DR secret | `testdr` context (A5); `$DB_SECRET` (A6) | **Backup file** `~/backups/dr-mysql-secret.ORIG.yml` and **DR's own Aurora hostname** (E1) |
| **C4** `<use-existing-database-job>` (Jenkins) | C1 values; nickname (P18); Test-DR Jenkins (A4); `<adopt-secret-branch>` (P20) | DR secret pointing at the secondary (C5, D) |
| **C5** Check | `testdr` context; secondary endpoint (B6) | Confirmation; DR app still at 0 |

### Phase D: Drills

| Step | Needs (from where) | Produces (used in) |
|---|---|---|
| **D1** Planned failover | B3 config; contexts and scripts (A5); baseline count (A8); storefront/admin UI URLs (A6, A4) | Drill log times (results table); London is writer; count check |
| **D2** Data load in London | Test-DR Jenkins (A4); `<data-load-job>` (P19) | **New baseline order count** (D4) |
| **D3** Performance test (optional) | Perf settings and load-test CIDRs (load-test team); `<deploy-stack-job>` (P19) | Perf results (London, then Ireland) |
| **D4** Failback | B3 config; London order count (taken before D4) | Drill log times; Ireland is writer again; count check |
| **D5** Disaster failover | B3 config | Drill log times; London standalone writer; a test order made in London (D6) |
| **D6** Rebuild | B3 config; both apps scaled down | Rebuilt global cluster; D5 order present in Ireland; DR secret re-checked (C5) |

### Phase E: Rollback

| Step | Needs (from where) | Produces (used in) |
|---|---|---|
| **E1** DR back to its own Aurora | **Backup file** and **DR's own hostname** (C3); Test-DR Jenkins (A4) | DR secret on DR's own Aurora |
| **E2** Remove Global Database (script 5) | B3 config; E1 done | **Pre-rollback snapshot ID** (F3); Test-Prod back to single region |
| **E3** Remove peering and routes | **Peering ID** (B5, or the lookup in E3); DR EKS VPC ID (B1) | Peering and routes gone |
| **E4** Delete secondary VPC | **Secondary VPC name** (B1) | VPC gone (F3 checks) |
| **E5** Check | — | Confirmation: back to the starting state |

### Phase F: Delete everything

| Step | Needs (from where) | Produces (used in) |
|---|---|---|
| **F1** Delete app, broker, databases (Jenkins) | Both Jenkins URLs (A3, A4); nickname (P18); job names (P19); cluster IDs (A6, A7) if done by hand | Jenkins-created resources gone (go-ahead for F2) |
| **F2** Bootstrap `cleanup` | Settings files (A3, A4) | EKS clusters, VPCs, DNS zones gone |
| **F3** Leftovers | Snapshot IDs (B6, E2); profiles (A2) | Nothing left that costs money |
| **F4** DNS, EC2, keys, accounts | Parent DNS zone (P8); ops instance and Elastic IP (A2); account IDs (A1) | NS records removed; ops EC2 and IP released; access keys deleted; accounts closed (optional) |

---

## Part 3: Values register (fill in as you go)

Write values here as each step produces them. **No passwords or secret keys:** for those, write only where they are stored.

| Value | Produced at | Used at | Your value |
|---|---|---|---|
| Test-Prod account ID | A1 | A3, B1, F4 | |
| Test-DR account ID | A1 | A4, B1, F4 | |
| Test-Prod bootstrap access key | A1 | A2, A3 | stored in: |
| Test-DR bootstrap access key | A1 | A2, A4 | stored in: |
| Ops EC2 instance ID | A2 | F4 | |
| Ops Elastic IP / allocation ID | A2 | A3, A4, F4 | |
| Git host key line | A2 | A3, A4 | |
| Test-Prod name servers (delegated?) | A3 | DNS | |
| Test-Prod Jenkins URL | A3 | A6, F1 | |
| Test-DR name servers (delegated?) | A4 | DNS | |
| Test-DR Jenkins URL | A4 | A7, C4, E1, F1 | |
| EKS version | A5 | kubectl check | |
| Primary Aurora cluster ID | A6 | B3 | |
| Aurora engine version (supports Global DB?) | A6 | B3 | |
| App DB secret name (`$DB_SECRET`) | A6 | A8, C1, C3 | |
| Admin UI / storefront URLs (Test-Prod) | A6 | A8, B7, D | |
| Admin UI / storefront URLs (Test-DR) | A7 | D | |
| DR's own Aurora cluster ID / hostname | A7 / C3 | E1, F1 | |
| Baseline order count | A8 | D1 | |
| DR EKS VPC ID | B1 | B1, B5, E3 | |
| Secondary VPC name / ID | B1 / B2 | E4 | |
| Secondary subnet IDs | B2 | B3 | |
| Secondary security group ID | B2 | B3 | |
| Secondary DB subnet group | B2 | B3 | |
| Global cluster ID | B3 | B6, D, E2 | |
| Secondary cluster ID | B3 | B6, B7, C1 | |
| Peering ID (`pcx-…`) | B5 | E3 | |
| Secondary endpoint (writer) | B6 | C1, C2, C4, C5 | |
| Replication lag baseline | B7 | D | |
| DR secret backup file location | C3 | E1 | |
| Pre-migration snapshot ID (if any) | B6 | F3 | |
| Pre-rollback snapshot ID | E2 | F3 | |

---

**Next:** [Flow](02-FLOW.md)

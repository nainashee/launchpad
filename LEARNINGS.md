# LaunchPad — Learnings

## Session 1 — April 21, 2026

### What I built

Today I set up the Week 1 infrastructure for LaunchPad using ___________. The resources I created were:

1. An _______ bucket named `___________` with all _______ access blocked
2. A _____________ distribution that serves files from the bucket using _______ _______ _______ (OAC)
3. An _______ certificate for the domain `___________`
4. DNS records in _____________ pointing the subdomain to CloudFront

The Terraform state file is stored remotely in a separate S3 bucket called `___________` with _____________ enabled on it.

By the end, I had a live page at `https://___________`.

### What tripped me up

The biggest issue was a _______ in my `variables.tf`. I had typed `___________` instead of `___________`. This caused the ACM certificate to stay stuck in `___________` status because the validation CNAME was generated for the wrong domain.

I initially tried to debug using `nslookup` through my work DNS server (`___________`), but it cached a "___________" response. The fix was to test against _____________ public DNS at IP `_______` which bypasses the corporate DNS chain entirely.

The actual fix was:
1. Correct the domain in ___________
2. Delete the old _______ record in Cloudflare
3. Run `___________` to recreate the cert
4. Add the _______ validation record in Cloudflare
5. Wait for the cert status to change from `___________` to `___________`
6. Run `___________` again to create CloudFront

### What I understand now

**Why Terraform uses multiple resources for one S3 bucket:**
An S3 bucket and its public access block are two separate _______ _______ on AWS's side, so Terraform models them as ___________ that reference each other using the _______ attribute.

**The CloudFront + ACM chicken-and-egg problem:**
CloudFront won't accept a certificate that is still in _______ status. You have to validate the cert via _______ first by adding a _______ record, wait for it to be _______, then CloudFront can be created.

**Why ACM certs must be in us-east-1:**
CloudFront is a _______ service, and it reads certificates only from the _______ region. That's why we created a second Terraform _______ with an _______ of `us_east_1`.

**What Origin Access Control does:**
The S3 bucket is completely _______. OAC lets CloudFront _______ every request to S3 using _______ (AWS's request signing protocol). Without it, CloudFront gets "_______ _______" from the bucket.

**The DNS validation flow:**
ACM gives you a _______ record → you add it to your DNS provider → AWS checks that the record _______ → cert status changes to _______ → you can now attach it to CloudFront.

**DynamoDB lock table (didn't use, but learned about):**
A lock table prevents two people from running `terraform _______` at the same time. It works by writing a _______ to a DynamoDB table. If someone else tries to apply, Terraform sees the lock and _______. I skipped it because I'm working _______ on this project.

---

## Session 2 — April 24, 2026

### What I built

Today I added the data and compute layers to LaunchPad:

1. **3 DynamoDB tables** using `PAY_PER_REQUEST` billing:
   - `launchpad-profile` — stores user info and master resume location
   - `launchpad-applications` — tracks job applications with a GSI on `followUpDate` for daily reminders
   - `launchpad-jobs` — Phase 2 cache for scraped job postings with a 30-day TTL

2. **5 Lambda functions** in Python 3.12, each with its own IAM role:
   - `launchpad-tailor-resume` — 512MB / 60s timeout (Bedrock + S3 + DynamoDB)
   - `launchpad-decode-job` — 256MB / 30s (Bedrock only)
   - `launchpad-generate-outreach` — 256MB / 30s (Bedrock + DynamoDB profile read)
   - `launchpad-mock-interview` — 256MB / 30s (Bedrock only)
   - `launchpad-tracker` — 128MB / 10s (DynamoDB CRUD only)

3. **Assets S3 bucket** — `launchpad-assets-989126024881` for storing resumes and prompt templates

### What tripped me up

**Terraform backend doesn't use the provider profile.**
The `provider.tf` has `profile = "launchpad"` but the S3 backend ignores that. Terraform reads the backend using the default AWS credential chain. The fix is to always prefix commands with `AWS_PROFILE=launchpad` in the terminal.

**S3 bucket names are globally unique across all AWS accounts.**
I tried to create a bucket called `launchpad-assets` but got a `BucketAlreadyExists` 409 error — someone else in the world already owns that name. The fix was to append the AWS account ID to guarantee uniqueness: `launchpad-assets-989126024881`. I got the account ID using the `data "aws_caller_identity" "current"` data source in Terraform.

**The AWS provider v6 `hash_key` deprecation warning.**
Terraform v6 shows a warning saying `hash_key is deprecated. Use key_schema instead.` But when you actually try to use `key_schema` blocks, Terraform throws an error saying they're not supported. The warning points to a future version. Safe to ignore for now — the config is valid and works.

**The `archive` provider isn't installed by default.**
When I added `data "archive_file"` resources to zip the Lambda code, Terraform threw a "Missing required provider" error. The fix was to run `terraform init` again to install the `hashicorp/archive` provider.

### What I understand now

**Why each Lambda needs its own IAM role:**
Least privilege — if `tailor-resume` gets compromised, the attacker can only access Bedrock and the resumes S3 prefix. They can't read DynamoDB or touch other functions. The `tracker` function, for example, has zero Bedrock access because it doesn't need it.

**Why `PAY_PER_REQUEST` over provisioned capacity:**
Provisioned capacity bills you 24/7 for reserved read/write units even when nothing is happening. At personal usage scale (a few requests per day), `PAY_PER_REQUEST` costs fractions of a cent per month vs a fixed $X/month for provisioned.

**What a GSI (Global Secondary Index) is:**
DynamoDB can only query efficiently on the primary key. A GSI creates a second index on a different attribute, letting you query on that attribute without scanning the whole table. The `followUpDate` GSI on the applications table lets the daily reminder Lambda ask "which applications need a follow-up today?" without reading every row.

**What TTL does in DynamoDB:**
TTL is a built-in expiry mechanism. You store a Unix timestamp in the `ttl` attribute of each item. DynamoDB automatically deletes the item within 48 hours after that timestamp passes — no cron job needed. Used on the `launchpad-jobs` table so old scraped job postings don't accumulate forever.

**How Terraform zips Lambda code:**
The `data "archive_file"` data source creates a `.zip` file from a local Python file at plan/apply time. Terraform tracks the zip's SHA256 hash in `source_code_hash` — so if the Python code changes, Terraform knows to re-upload the Lambda on the next apply.

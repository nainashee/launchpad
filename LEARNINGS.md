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

---

### API Gateway (same session)

#### What I built

An HTTP API Gateway with 9 routes wired to the 5 Lambda functions:
- `POST /tailor-resume`, `POST /decode-job`, `POST /outreach`, `POST /interview`
- `POST /applications`, `GET /applications`, `GET /applications/{id}`, `PUT /applications/{id}`, `DELETE /applications/{id}`

Live URL: `https://zh1gkhvulc.execute-api.us-east-1.amazonaws.com`

Tested end-to-end with curl and got a real response from the Lambda through API Gateway.

#### What I understand now

**The four things needed to wire API Gateway to a Lambda:**
1. `aws_apigatewayv2_integration` — tells API Gateway which Lambda ARN to call
2. `aws_apigatewayv2_route` — maps a `METHOD /path` to an integration
3. `aws_lambda_permission` — grants API Gateway the IAM permission to invoke the Lambda
4. `aws_apigatewayv2_stage` — the deployment unit; `$default` with `auto_deploy = true` means every `terraform apply` automatically goes live

**What `payload_format_version = "2.0"` means:**
There are two formats for how API Gateway packages the HTTP request before sending it to Lambda. Version 2.0 is simpler and cheaper — it uses a cleaner JSON structure. The Lambda handlers use `event.get("requestContext", {}).get("http", {}).get("method")` which is the v2.0 path.

**Why CORS is configured on the API, not the Lambda:**
CORS (Cross-Origin Resource Sharing) is enforced by the browser. When the React frontend (on `jobs.naindigital.com`) calls the API (on `execute-api.amazonaws.com`), the browser first sends a preflight `OPTIONS` request. API Gateway handles these automatically when you set `cors_configuration` — the Lambda never even sees them.

**What `source_arn = "${execution_arn}/*/*"` means:**
The `/*/*/*` pattern is `{api}/{stage}/{route}`. Using `/*/*` (any stage, any route) means the same permission covers all routes pointing to that Lambda, so you don't need one permission per route.

---

## Session 3 — April 27, 2026

### What I built

Today I completed the Phase 1 frontend and CI/CD pipeline:

1. **React frontend** — scaffolded with Vite, 4 screens wired to the live API Gateway:
   - Dashboard — stats grid, recent applications table, quick action cards
   - Tailor Resume — textarea → POST `/tailor-resume` → display result
   - Job Decoder — textarea → POST `/decode-job` → display analysis + fit score
   - Applications — full CRUD table with modal form (add / edit / delete)

2. **Earthy light UI theme** — cream background (`#faf7f2`), forest greens, warm browns, Lora serif headings, Inter body. Design tokens in CSS custom properties so the whole palette is controlled from one place.

3. **Mobile responsive nav** — horizontal links on desktop, hamburger menu below 600px that animates to an X and reveals a full-width drawer.

4. **GitHub Actions CI/CD** — `.github/workflows/deploy.yml` triggers on push to `main` when `frontend/` changes. Builds the app, syncs to S3 with `--delete`, then invalidates CloudFront. `index.html` gets `no-cache` headers; all other assets get 1-year immutable cache.

5. **CORS fix** — API Gateway `cors_configuration` only allowed the production domain. Added `http://localhost:5173` so the dev server can call the live API without CORS errors.

### What tripped me up

**CORS works in curl but not in the browser.**
`curl` doesn't enforce CORS — it just sends the request and gets the response. The browser sends a preflight `OPTIONS` request first and checks for `Access-Control-Allow-Origin` in the response. Our API Gateway had CORS configured, but only for `https://jobs.naindigital.com`. Adding `http://localhost:5173` to `allow_origins` and running `terraform apply` fixed it immediately.

**Vite can't scaffold into a non-empty directory.**
Running `npm create vite@latest .` in an existing folder (even with just a `.gitkeep`) fails with "Operation cancelled." The workaround is to scaffold into a temp folder (`frontend-tmp`) and then copy everything over.

**`index.html` must never be cached at the CDN.**
Static assets (JS, CSS) get content-hash filenames from Vite (e.g. `index-DpbLTSKt.js`), so they're safe to cache forever. But `index.html` always has the same filename — if CloudFront caches it, users get the old version of the app even after a new deploy. Solved by uploading `index.html` separately with `Cache-Control: no-cache, no-store, must-revalidate`.

### What I understand now

**How Vite handles cache-busting:**
Vite fingerprints every JS and CSS file in `dist/assets/` with a content hash (e.g. `index-DpbLTSKt.js`). If you change a single line of code, the hash changes and the browser treats it as a brand-new file. This is why you can safely set a 1-year cache on those files — the URL itself changes when the content changes.

**Why `npm ci` instead of `npm install` in CI:**
`npm install` can update `package-lock.json` if there are floating version ranges. `npm ci` always installs the exact versions pinned in `package-lock.json` and fails if there's a mismatch. This makes CI builds reproducible — you get the exact same dependency tree every time.

**How the S3 + CloudFront deploy pipeline works:**
`aws s3 sync dist/ s3://bucket --delete` uploads new/changed files and removes files that no longer exist. CloudFront then needs to be told to stop serving its cached copies — that's the invalidation step (`/*` clears everything). Without it, users could get a mix of old and new files until CloudFront's TTL expires naturally.

**Why React Router needs a CloudFront fallback.**
React Router handles routing in the browser — `/tailor`, `/decode` etc. are not real files in S3. If a user bookmarks `jobs.naindigital.com/tailor` and loads it directly, CloudFront asks S3 for a file at `/tailor`, gets a 404, and returns that to the user. The fix (Phase next) is to configure a CloudFront custom error response that returns `index.html` with a 200 for all 404s, letting React Router take over.

**CSS custom properties for design tokens:**
Instead of hardcoding colours throughout the CSS, all design values live in `:root { --green-700: #3d6b4a; ... }`. Every component references `var(--green-700)`. To retheme the whole app you change one block. It also makes dark mode trivial to add later — just redefine the variables inside a `@media (prefers-color-scheme: dark)` block.

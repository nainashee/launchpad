# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

LaunchPad is an AI-powered job search automation tool built on AWS serverless. It tailors resumes, decodes job descriptions, generates outreach messages, supports mock interviews, and tracks applications — all via Claude on Bedrock.

- **Domain:** jobs.naindigital.com
- **Owner:** Hussain Ashfaque (nain.ashee@gmail.com)
- **Repo:** github.com/nainashee/launchpad
- **Target cost:** <$5/month at personal usage scale

## Architecture

### Stack

| Layer | Technology |
|---|---|
| Compute | AWS Lambda (Python) |
| Infrastructure | Terraform (all resources, no console clicks) |
| Frontend | React → S3 + CloudFront |
| Auth | AWS Cognito (Phase 3) |
| AI | Amazon Bedrock (Claude) — IAM auth, no API keys |
| Database | DynamoDB (3 tables) |
| Storage | S3 (resumes, prompts, job cache) |
| API | API Gateway HTTP API (not REST — cheaper, simpler) |
| Scheduling | EventBridge cron |
| Queuing | SQS with DLQ (Phase 2) |
| Email | SES |
| Orchestration | Step Functions (Phase 3) |
| Observability | CloudWatch + X-Ray (Phase 2) |
| CI/CD | GitHub Actions |

### Lambda Functions

**Phase 1 — Core AI tools (all live)**

1. **tailor-resume** — Bedrock call to tailor master resume against a job description; writes output to S3
2. **decode-job** — AI analysis of a job posting to extract fit signals and requirements
3. **generate-outreach** — Drafts LinkedIn/email outreach messages from job + profile context
4. **mock-interview** — Multi-turn interview prep using Bedrock
5. **tracker** — CRUD operations on the Applications DynamoDB table

**Phase 2 — Onboarding + live job search (planned)**

6. **profile-api** — Profile CRUD, presigned S3 upload URL, parse-resume trigger (128MB / 15s)
7. **parse-resume** — Bedrock PDF extraction: skills, roles, experience + preference suggestions (256MB / 60s)
8. **job-scraper** — Fetches jobs from Adzuna, deduplicates, writes to DynamoDB, publishes to SQS (256MB / 60s)
9. **job-ranker** — SQS-triggered; scores each job per user via Bedrock, writes to job-rankings table (256MB / 60s)
10. **jobs-api** — Serves ranked job results to frontend with optional score filtering (128MB / 15s)
11. **email-digest** — Daily SES email with top job matches + overdue follow-up reminders (256MB / 30s)

### DynamoDB Tables

**Profile** (single-item per user)
- PK: `userId`
- Phase 1 fields: `email`, `targetTitles`, `skills`, `masterResumeS3Key`, `githubUsername`, `linkedInUrl`
- Phase 2 additions: `name`, `parsedRoles`, `yearsExperience`, `suggestedTargetTitles`, `suggestedSkills`, `suggestedIndustries`, `parseStatus` (pending/complete/failed), `parsedAt`, `onboardingComplete`

**Applications**
- PK: `userId`, SK: `applicationId` (ULID)
- Fields: `companyName`, `roleTitle`, `status`, `appliedDate`, `followUpDate`, `tailoredResumeKey`, `fitScore` (0–10)
- GSI on `followUpDate` for daily reminders

**Jobs** (global scraped postings cache — Phase 2)
- PK: `source`, SK: `jobId`
- Fields: `title`, `company`, `description`, `location`, `url`, `salary`, `scrapedAt`, `ttl` (30-day TTL)
- No per-user data lives here — fit scores are in the JobRankings table

**JobRankings** (per-user fit scores — Phase 2)
- PK: `userId`, SK: `jobId`
- Fields: `fitScore` (0–10), `fitSummary`, `rankedAt`, `source`, `title`, `company`, `location`, `url`, `ttl`
- GSI: `fitScore-index` (PK: `userId`, SK: `fitScore`) — powers "top jobs for this user" queries
- Separation rationale: jobs are global; scores are personal. One jobs table + one rankings table supports multiple users without conflating the two.

### S3 Buckets

| Bucket | Purpose |
|---|---|
| `launchpad-frontend-jobs` | Static React app, served via CloudFront + OAC |
| `launchpad-assets-<account-id>` | Resumes, prompt templates, job cache (private) |

**Assets bucket layout:**
```
launchpad-assets-<account-id>/
  resumes/{userId}/master.pdf       # uploaded master resume (PDF)
  resumes/{userId}/tailored-*.txt   # Bedrock-tailored resume outputs
  prompts/                          # Bedrock prompt templates
  job-cache/                        # raw scraped job data (Phase 2)
```

> Note: The assets bucket name includes the AWS account ID to guarantee global S3 uniqueness.
> Resume upload uses presigned S3 PUT URLs — PDF never passes through Lambda (avoids 6MB payload limit).

## Development Phases

**Phase 1 (Weeks 1–4 — MVP):** React frontend, 5 core Lambdas, 3 DynamoDB tables, API Gateway, GitHub Actions CI/CD, Bedrock AI integration.

Phase 1 checklist:
- [x] Terraform base infrastructure (S3, CloudFront, ACM, DNS)
- [x] DynamoDB tables
- [x] Lambda function skeletons + IAM roles
- [x] API Gateway HTTP API + 9 routes
- [x] React frontend — 5 screens (landing + 4 app screens), earthy light theme, mobile responsive
- [x] GitHub Actions CI/CD — build → S3 sync → CloudFront invalidation
- [x] Firebase Google auth — landing page, AuthContext, protected routes
- [x] Bedrock AI integration — all 5 Lambda functions live and tested

**Phase 2 (Weeks 5–10 — Live Job Search):** User onboarding + profile creation, resume parsing, live job scraping (Adzuna), per-user AI job ranking via SQS, SES email digest, X-Ray tracing.

Security hardening (pre-Phase 2, complete ✅):
- [x] **S-1** — `launchpad-auth` Lambda Layer: Firebase JWT verification + structured logging utility (`PyJWT`, `cryptography`, `requests`) built for Linux/x86_64 via `layers/auth/build.sh`
- [x] **S-2** — Firebase JWT verification on all 5 Phase 1 Lambdas — `userId` derived from verified token, never from request body or query string
- [x] **S-3** — Structured JSON logging on every Lambda exit path (`userId`, `endpoint`, `timestamp`, `result`) — queryable via CloudWatch Logs Insights
- [x] **S-4** — Input size limits on all Bedrock Lambdas (decode-job: 8K, tailor-resume: 8K, outreach: 5K, interview: 8K JD + 3K message)
- [x] **S-5** — CORS locked from `*` to `https://jobs.naindigital.com` in all Lambda responses
- [x] **S-6** — API Gateway route-level throttling: 0.5/s burst 2 (decode, outreach), 0.3/s burst 1 (tailor), 1/s burst 3 (interview); default 20/s burst 50
- [x] **S-7** — Frontend axios interceptors: auto-attach `Authorization: Bearer <token>` on every request; auto-retry once on 401 with force-refreshed token
- [x] **S-8** — `FIREBASE_PROJECT_ID` env var on all Lambdas; `firebase_project_id` variable in Terraform
- [ ] **S-9** — Per-user daily quota table (`launchpad-usage`) — deferred to Phase 2 Step 0a, wired into `profile-api`
- [ ] **S-10** — S3 presigned URL restrictions (content-type, size, 5-min expiry) — deferred to Phase 2 Step 0b
- [ ] **S-11** — Reserved Lambda concurrency — deferred until AWS Support grants concurrency limit increase (current account limit: 10)

Phase 2 checklist:
- [ ] **0a** — `profile-api` Lambda + 4 new API routes (GET/PUT /profile, POST /profile/upload-url, POST /profile/parse-resume) + `launchpad-usage` quota table
- [ ] **0b** — Presigned S3 upload URL flow + S3 CORS config for direct browser upload + upload restrictions (PDF only, 5MB, 5-min expiry)
- [ ] **0c** — `parse-resume` Lambda (Bedrock PDF extraction + preference suggestions) + extend Profile table schema in Terraform
- [ ] **0d** — `/profile` frontend screen (upload → spinner → suggestions form → confirm)
- [ ] **1** — Adzuna developer account + test API call
- [ ] **2** — `launchpad-job-rankings` DynamoDB table + GSI in Terraform
- [ ] **3** — `job-scraper` Lambda + EventBridge cron rule (reads all profiles, queries Adzuna, publishes per-user SQS messages)
- [ ] **4** — SQS queue + DLQ in Terraform
- [ ] **5** — `job-ranker` Lambda (SQS trigger, Bedrock scoring, writes to job-rankings table)
- [ ] **6** — `jobs-api` Lambda + GET /jobs + GET /jobs/{jobId} routes
- [ ] **7** — `/jobs` frontend screen (ranked cards with Quick Apply / Tailor & Apply / Decode buttons)
- [ ] **8** — `email-digest` Lambda + SES verified sender + EventBridge cron
- [ ] **9** — X-Ray tracing across all Lambdas

**Phase 3 (Weeks 11–16 — Full Automation):** Step Functions one-click-apply workflow, Cognito OAuth, cost dashboard.

## Infrastructure Conventions

- **All AWS resources defined in Terraform** — no manual console changes ever
- **Terraform state** stored in S3 backend with DynamoDB lock table
- **Least-privilege IAM** — each Lambda gets its own role with only the permissions it needs
- **No hardcoded secrets** — credentials via IAM roles; config via environment variables from Terraform outputs

## Commands

```bash
# Auth layer — rebuild before terraform apply on a new machine or after changing auth.py
bash layers/auth/build.sh

# Terraform — always prefix with AWS_PROFILE=launchpad (backend requires it)
cd infra/
AWS_PROFILE=launchpad terraform init
AWS_PROFILE=launchpad terraform plan
AWS_PROFILE=launchpad terraform apply

# Lambda (Python)
cd functions/<function-name>/
python -m pytest tests/

# Frontend (React + Vite)
cd frontend/
npm install
npm run dev        # local dev server at localhost:5173
npm run build      # production build → dist/
npm run lint       # ESLint

# CI/CD
# GitHub Actions handles deploy on push to main

# CloudWatch Logs Insights — useful abuse/debug queries
# All Lambda logs share this JSON shape: {userId, endpoint, timestamp, result, ...}
# Query example — auth failures in last 24h:
#   fields userId, endpoint, timestamp, reason
#   | filter result = "auth_error"
#   | sort timestamp desc
#   | limit 50
```

## Live Endpoints

**API Gateway base URL:** `https://zh1gkhvulc.execute-api.us-east-1.amazonaws.com`

**Phase 1 routes (live):**

| Method | Route | Lambda |
|---|---|---|
| POST | `/tailor-resume` | launchpad-tailor-resume |
| POST | `/decode-job` | launchpad-decode-job |
| POST | `/outreach` | launchpad-generate-outreach |
| POST | `/interview` | launchpad-mock-interview |
| POST | `/applications` | launchpad-tracker |
| GET | `/applications` | launchpad-tracker |
| GET | `/applications/{id}` | launchpad-tracker |
| PUT | `/applications/{id}` | launchpad-tracker |
| DELETE | `/applications/{id}` | launchpad-tracker |

**Phase 2 routes (planned):**

| Method | Route | Lambda |
|---|---|---|
| GET | `/profile` | launchpad-profile-api |
| PUT | `/profile` | launchpad-profile-api |
| POST | `/profile/upload-url` | launchpad-profile-api |
| POST | `/profile/parse-resume` | launchpad-profile-api |
| GET | `/jobs` | launchpad-jobs-api |
| GET | `/jobs/{jobId}` | launchpad-jobs-api |

Test any route with curl:
```bash
curl -s -X POST https://zh1gkhvulc.execute-api.us-east-1.amazonaws.com/decode-job \
  -H "Content-Type: application/json" \
  -d '{"jobDescription": "..."}'
```

## Frontend Architecture

```
frontend/src/
  api.js                        # axios client — all API Gateway calls live here
  firebase.js                   # Firebase app init + auth + GoogleAuthProvider
  context/AuthContext.jsx        # onAuthStateChanged, signInWithGoogle, signOut
  components/Nav.jsx/.css       # sticky nav, hamburger at <600px
  pages/
    Landing.jsx/.css            # public landing page + Google sign-in button
    Dashboard.jsx/.css          # stats grid + recent applications + quick actions
    TailorResume.jsx            # POST /tailor-resume
    JobDecoder.jsx              # POST /decode-job
    Applications.jsx/.css       # full CRUD — POST/GET/PUT/DELETE /applications
    Outreach.jsx                # POST /outreach — generate LinkedIn/email messages
    Profile.jsx                 # Phase 2: upload resume, review AI suggestions, confirm preferences
    Jobs.jsx                    # Phase 2: browse ranked jobs, Quick Apply / Tailor & Apply / Decode
  App.jsx                       # React Router — routes, ProtectedRoute wrapper
  index.css                     # design tokens + global styles (earthy light theme)
```

**Phase 2 frontend flows:**

- **Profile onboarding** (`/profile`): 3-step flow — upload PDF → spinner while Bedrock parses → editable chip form with AI-suggested titles/skills → Save → sets `onboardingComplete: true`
- **Jobs feed** (`/jobs`): ranked cards showing `fitScore`, `fitSummary`, company, title. Buttons: "Quick Apply" (pre-fills tracker), "Tailor & Apply" (calls tailor-resume then tracker), "Decode" (calls decode-job)
- **Onboarding gate**: Dashboard checks `onboardingComplete` on mount; redirects to `/profile` if false

**Theme:** Lora (serif headings) + Inter (body), warm cream background, forest green CTAs, brown text hierarchy.

**CI/CD flow:** push to `main` → `.github/workflows/deploy.yml` → `npm ci` + `npm run build` → `aws s3 sync dist/ s3://launchpad-frontend-jobs --delete` → CloudFront invalidation on `E325QX646NP0EU`. Assets cached 1 year; `index.html` never cached.

**CORS:** `localhost:5173` and `https://jobs.naindigital.com` both allowed in API Gateway `cors_configuration`.

## Key Design Decisions

- **Lambda over EC2** — no idle cost, auto-scales, pay-per-invocation
- **DynamoDB over RDS** — serverless, no connection pool management, single-table-friendly access patterns
- **HTTP API over REST API** — ~70% cheaper, sufficient for this use case
- **Bedrock over direct Anthropic API** — native IAM auth (no API key rotation), stays within AWS billing
- **Terraform over CDK/SAM** — explicit, portable, teaches cloud fundamentals
- **Vite over CRA** — faster dev server, smaller bundles, modern default
- **Presigned S3 URL for resume upload** — avoids Lambda's 6MB payload limit; PDF never passes through API Gateway or Lambda
- **Separate job-rankings table from jobs table** — jobs are global (one copy per jobId); fit scores are personal (one per userId+jobId). Conflating them breaks multi-user support
- **Async parse-resume via Lambda invoke** — resume parsing takes 10–20s; returning 202 immediately and polling `GET /profile` avoids API Gateway's 30s timeout and gives better UX
- **SQS decouples scraper from ranker** — scraper writes at burst speed; ranker processes at steady pace; each can fail/retry independently
- **Adzuna as first job source** — free tier (250 req/day), clean REST API, no scraping ToS risk. LinkedIn scraping explicitly avoided.
- **Firebase JWT verified on backend, not just frontend** — `userId` is always extracted from the verified token; never trusted from request body or query string. Closes the impersonation gap where any caller could claim any userId.
- **Lambda Layer for shared auth** — `launchpad-auth` layer carries `PyJWT` + `cryptography` + `requests` built for Linux/x86_64. All Lambdas import `verify_firebase_jwt()` and `log_request()` from it. Rebuild with `bash layers/auth/build.sh` before any `terraform apply` on a new machine.
- **Structured logging over custom log infra** — every Lambda emits one `logger.info(json.dumps({...}))` line per invocation. CloudWatch Logs Insights queries handle abuse detection and debugging with zero extra cost or infrastructure.

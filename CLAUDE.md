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

### Five Core Lambda Functions (Phase 1)

1. **tailor-resume** — Bedrock call to tailor master resume against a job description; writes output to S3
2. **decode-job** — AI analysis of a job posting to extract fit signals and requirements
3. **generate-outreach** — Drafts LinkedIn/email outreach messages from job + profile context
4. **mock-interview** — Multi-turn interview prep using Bedrock
5. **tracker** — CRUD operations on the Applications DynamoDB table

### DynamoDB Tables

**Profile** (single-item per user)
- PK: `userId`
- Fields: `email`, `targetTitles`, `skills`, `masterResumeS3Key`, `githubUsername`, `linkedInUrl`

**Applications**
- PK: `userId`, SK: `applicationId` (ULID)
- Fields: `companyName`, `roleTitle`, `status`, `appliedDate`, `followUpDate`, `tailoredResumeKey`, `fitScore` (0–10)
- GSI on `followUpDate` for daily reminders

**Jobs** (Phase 2 — scraped postings cache)
- PK: `source`, SK: `jobId`
- Fields: `title`, `company`, `description`, `scrapedAt`, `ttl` (30-day TTL)

### S3 Buckets

| Bucket | Purpose |
|---|---|
| `launchpad-frontend-jobs` | Static React app, served via CloudFront + OAC |
| `launchpad-assets-<account-id>` | Resumes, prompt templates, job cache (private) |

**Assets bucket layout:**
```
launchpad-assets-<account-id>/
  resumes/          # master + tailored PDFs
  prompts/          # Bedrock prompt templates
  job-cache/        # raw scraped job data (Phase 2)
```

> Note: The assets bucket name includes the AWS account ID to guarantee global S3 uniqueness.

## Development Phases

**Phase 1 (Weeks 1–4 — MVP):** React frontend, 5 core Lambdas, 3 DynamoDB tables, API Gateway, GitHub Actions CI/CD, Bedrock AI integration.

Phase 1 checklist:
- [x] Terraform base infrastructure (S3, CloudFront, ACM, DNS)
- [x] DynamoDB tables
- [x] Lambda function skeletons + IAM roles
- [x] API Gateway HTTP API + 9 routes
- [x] React frontend — 4 screens, earthy light theme, mobile responsive
- [x] GitHub Actions CI/CD — build → S3 sync → CloudFront invalidation
- [ ] Bedrock AI integration in Lambda functions

**Phase 2 (Weeks 5–10 — Live Job Search):** EventBridge scraper, Adzuna/Greenhouse/Lever/Indeed integrations, AI ranker with SQS, SES email digest, GitHub API integration, X-Ray tracing.

**Phase 3 (Weeks 11–16 — Full Automation):** Step Functions one-click-apply workflow, Cognito OAuth, cost dashboard.

## Infrastructure Conventions

- **All AWS resources defined in Terraform** — no manual console changes ever
- **Terraform state** stored in S3 backend with DynamoDB lock table
- **Least-privilege IAM** — each Lambda gets its own role with only the permissions it needs
- **No hardcoded secrets** — credentials via IAM roles; config via environment variables from Terraform outputs

## Commands

```bash
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
```

## Live Endpoints

**API Gateway base URL:** `https://zh1gkhvulc.execute-api.us-east-1.amazonaws.com`

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
  components/Nav.jsx/.css       # sticky nav, hamburger at <600px
  pages/
    Dashboard.jsx/.css          # stats grid + recent applications + quick actions
    TailorResume.jsx            # POST /tailor-resume
    JobDecoder.jsx              # POST /decode-job
    Applications.jsx/.css       # full CRUD — POST/GET/PUT/DELETE /applications
  App.jsx                       # React Router — 4 routes
  index.css                     # design tokens + global styles (earthy light theme)
```

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

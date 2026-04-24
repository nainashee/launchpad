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

**Phase 1 (Weeks 1–4 — MVP):** Static frontend, 5 core Lambdas, 3 DynamoDB tables, API Gateway, GitHub Actions CI/CD, CloudWatch.

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

# Frontend (React) — not scaffolded yet
cd frontend/
npm install
npm run dev        # local dev server
npm run build      # production build
npm run test       # unit tests
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

## Key Design Decisions

- **Lambda over EC2** — no idle cost, auto-scales, pay-per-invocation
- **DynamoDB over RDS** — serverless, no connection pool management, single-table-friendly access patterns
- **HTTP API over REST API** — ~70% cheaper, sufficient for this use case
- **Bedrock over direct Anthropic API** — native IAM auth (no API key rotation), stays within AWS billing
- **Terraform over CDK/SAM** — explicit, portable, teaches cloud fundamentals

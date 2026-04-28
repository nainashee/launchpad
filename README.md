# LaunchPad — Archived

> **This project has been archived.** The AWS infrastructure has been decommissioned and the app is no longer live. The code is preserved here as a record of the work completed.

---

AI-powered job search automation built on AWS serverless. Users could tailor resumes, decode job descriptions, generate outreach messages, practice mock interviews, and track applications — all powered by Claude on Amazon Bedrock.

## What Was Built

**Phase 1 — MVP (complete)**
- Terraform-managed AWS infrastructure from scratch (S3, CloudFront, ACM, Route53, API Gateway, DynamoDB, Lambda, IAM)
- 5 Python Lambda functions each with least-privilege IAM roles
- API Gateway HTTP API with 9 routes
- React + Vite frontend (5 screens, earthy light theme, mobile responsive)
- GitHub Actions CI/CD — auto-deploy on push to main
- Firebase Google authentication with protected routes
- Amazon Bedrock (Claude) integration across all AI endpoints

**Security hardening (complete)**
- Firebase JWT verification on every Lambda — `userId` always derived from verified token, never trusted from request body
- Shared Lambda Layer (`launchpad-auth`) carrying PyJWT + cryptography built for Linux/x86_64
- API Gateway route-level throttling (0.3–1 req/s on Bedrock endpoints)
- Input size limits on all AI endpoints
- CORS locked to production domain
- Frontend axios interceptor — auto-attaches Bearer token, auto-retries on 401

**Phase 2 — partially started**
- `profile-api` Lambda (GET/PUT /profile + presigned S3 upload URL)
- `launchpad-usage` DynamoDB table for per-user quota tracking

## Tech Stack

| Layer | Technology |
|---|---|
| Compute | AWS Lambda (Python 3.12) |
| AI | Amazon Bedrock (Claude Haiku) |
| Database | DynamoDB |
| Storage | S3 |
| Frontend | React + Vite → S3 + CloudFront |
| API | API Gateway HTTP API |
| Auth | Firebase Authentication (Google) |
| Infrastructure | Terraform |
| CI/CD | GitHub Actions |

## Key Things Learned

- How Terraform manages AWS infrastructure as code — state, plan, apply, destroy
- Lambda + API Gateway wiring — integrations, routes, permissions, payload format v2.0
- IAM least-privilege — each Lambda gets its own role scoped to only what it needs
- Lambda Layers — building Linux-compatible Python packages, correct zip structure (`python/` prefix)
- DynamoDB access patterns — single-table design, GSIs, TTL
- Presigned S3 URLs — direct browser-to-S3 uploads bypassing Lambda payload limits
- Firebase JWT verification on the backend — closing the userId impersonation gap
- CloudFront SPA routing — custom error responses for React Router
- Structured logging — queryable JSON logs in CloudWatch Logs Insights

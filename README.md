# LaunchPad

AI-powered job search automation built on AWS serverless.

## Tech Stack

| Layer | Technology |
|---|---|
| Compute | AWS Lambda (Python) |
| AI | Amazon Bedrock (Claude) |
| Database | DynamoDB |
| Storage | S3 |
| Frontend | React + CloudFront |
| API | API Gateway (HTTP) |
| Infrastructure | Terraform |
| CI/CD | GitHub Actions |

## Status

**Phase 1 — MVP** ✅ complete

- [x] Terraform base infrastructure (S3, CloudFront, ACM, DNS)
- [x] DynamoDB tables (Profile, Applications, Jobs)
- [x] 5 core Lambda functions + IAM roles
- [x] API Gateway HTTP API (9 routes, fully wired)
- [x] React frontend (5 screens, earthy light theme, mobile responsive)
- [x] GitHub Actions CI/CD — auto-deploy on push to main
- [x] Firebase Google auth — landing page + protected routes
- [x] Bedrock AI integration — all 5 Lambdas live

**Security hardening** ✅ complete (pre-Phase 2)

- [x] Firebase JWT verification on all Lambdas — backend validates every request, `userId` never trusted from body
- [x] `launchpad-auth` Lambda Layer — shared `PyJWT` + structured logging utility across all functions
- [x] API Gateway route throttling — 0.3–1 req/s on all Bedrock endpoints
- [x] Input size limits on all AI endpoints
- [x] CORS locked to `https://jobs.naindigital.com`
- [x] Frontend axios interceptor — auto-attaches Bearer token, auto-retries on 401

**Phase 2 — Live Job Search** 🚧 in progress

- [ ] `profile-api` Lambda + per-user quota table (`launchpad-usage`)
- [ ] Resume upload: presigned S3 URL + PDF restrictions (type, size, expiry)
- [ ] `parse-resume` Lambda — Bedrock PDF extraction: skills, roles, experience, preference suggestions
- [ ] `/profile` frontend screen — upload → AI parses → confirm preferences
- [ ] `launchpad-job-rankings` DynamoDB table (per-user fit scores, separate from global jobs)
- [ ] `job-scraper` Lambda — Adzuna integration, EventBridge daily cron
- [ ] `job-ranker` Lambda — SQS-triggered, Bedrock scoring per user
- [ ] `jobs-api` Lambda — ranked job feed with score filtering
- [ ] `/jobs` frontend screen — ranked cards with Quick Apply / Tailor & Apply / Decode
- [ ] `email-digest` Lambda — SES daily email (top matches + follow-up reminders)
- [ ] X-Ray tracing

## API

**Base URL:** `https://zh1gkhvulc.execute-api.us-east-1.amazonaws.com`

**Phase 1 (live):**

| Method | Route | Function |
|---|---|---|
| POST | `/tailor-resume` | Tailor resume against a job description |
| POST | `/decode-job` | Extract signals from a job posting |
| POST | `/outreach` | Draft LinkedIn/email outreach |
| POST | `/interview` | Mock interview (multi-turn) |
| POST | `/applications` | Create a job application |
| GET | `/applications` | List all applications |
| GET | `/applications/{id}` | Get a single application |
| PUT | `/applications/{id}` | Update application status |
| DELETE | `/applications/{id}` | Delete an application |

**Phase 2 (planned):**

| Method | Route | Function |
|---|---|---|
| GET | `/profile` | Read user profile |
| PUT | `/profile` | Update profile preferences |
| POST | `/profile/upload-url` | Get presigned S3 URL for resume upload |
| POST | `/profile/parse-resume` | Trigger async resume parsing |
| GET | `/jobs` | List ranked job matches for user |
| GET | `/jobs/{jobId}` | Get full job detail |

## Infrastructure

| Resource | Name |
|---|---|
| Frontend bucket | `launchpad-frontend-jobs` |
| Assets bucket | `launchpad-assets-989126024881` |
| CloudFront | `d1j38znc7w4uld.cloudfront.net` |
| DynamoDB | `launchpad-profile`, `launchpad-applications`, `launchpad-jobs`, `launchpad-job-rankings` *(Phase 2)* |
| Phase 1 Lambdas | `launchpad-tailor-resume`, `launchpad-decode-job`, `launchpad-generate-outreach`, `launchpad-mock-interview`, `launchpad-tracker` |
| Phase 2 Lambdas | `launchpad-profile-api`, `launchpad-parse-resume`, `launchpad-job-scraper`, `launchpad-job-ranker`, `launchpad-jobs-api`, `launchpad-email-digest` |

## Auth & Security

Google sign-in via Firebase Authentication. Firebase issues a signed JWT on login; every API call sends it as `Authorization: Bearer <token>`. All Lambda functions verify the JWT signature against Firebase's public keys before processing any request — `userId` is always derived from the verified token, never from the request body.

**Security layers:**
- Identity: Firebase JWT verified on every Lambda
- Rate limiting: API Gateway route-level throttling (0.3–1 req/s on AI endpoints)
- Input validation: size limits on all Bedrock inputs
- Logging: structured JSON per invocation, queryable in CloudWatch Logs Insights

## Frontend

Built in React (Vite), served via S3 + CloudFront:

| Screen | Route | Phase | Purpose |
|---|---|---|---|
| Landing | `/` | 1 | Public page — Google sign-in |
| Dashboard | `/dashboard` | 1 | Stats overview, recent applications, quick actions |
| Tailor Resume | `/tailor` | 1 | Paste JD → Claude tailors your resume |
| Job Decoder | `/decode` | 1 | Paste JD → Claude extracts fit signals + score |
| Applications | `/applications` | 1 | Full CRUD tracker (add / edit / delete) |
| Outreach | `/outreach` | 1 | Generate LinkedIn/email outreach messages |
| Profile | `/profile` | 2 | Upload resume → AI parses → confirm preferences |
| Jobs | `/jobs` | 2 | Browse AI-ranked job matches, apply or tailor |

- Light earthy theme — cream background, greens and browns, Lora + Inter fonts
- Mobile responsive with hamburger nav below 600px
- Protected routes redirect unauthenticated users to landing page
- Phase 2: Dashboard redirects to `/profile` if onboarding not complete

## CI/CD

Push to `main` → GitHub Actions builds `frontend/` → syncs to S3 → invalidates CloudFront.
Assets are cached for 1 year; `index.html` is never cached so deploys are instant.

## Live App

[jobs.naindigital.com](https://jobs.naindigital.com)

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
- [x] React frontend (4 screens, earthy light theme, mobile responsive)
- [x] GitHub Actions CI/CD — auto-deploy on push to main
- [x] Firebase Google auth — landing page + protected routes
- [x] Bedrock AI integration — all 5 Lambdas live

## API

**Base URL:** `https://zh1gkhvulc.execute-api.us-east-1.amazonaws.com`

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

## Infrastructure

| Resource | Name |
|---|---|
| Frontend bucket | `launchpad-frontend-jobs` |
| Assets bucket | `launchpad-assets-989126024881` |
| CloudFront | `d1j38znc7w4uld.cloudfront.net` |
| DynamoDB | `launchpad-profile`, `launchpad-applications`, `launchpad-jobs` |
| Lambdas | `launchpad-tailor-resume`, `launchpad-decode-job`, `launchpad-generate-outreach`, `launchpad-mock-interview`, `launchpad-tracker` |

## Auth

Google sign-in via Firebase Authentication. Users land on a public page, sign in with Google, and are routed to the dashboard. Firebase UID is used as `userId` in all API calls.

## Frontend

**5 screens** built in React (Vite), served via S3 + CloudFront:

| Screen | Route | Purpose |
|---|---|---|
| Landing | `/` | Public page — Google sign-in |
| Dashboard | `/dashboard` | Stats overview, recent applications, quick actions |
| Tailor Resume | `/tailor` | Paste JD → Claude tailors your resume |
| Job Decoder | `/decode` | Paste JD → Claude extracts fit signals + score |
| Applications | `/applications` | Full CRUD tracker (add / edit / delete) |

- Light earthy theme — cream background, greens and browns, Lora + Inter fonts
- Mobile responsive with hamburger nav below 600px
- Protected routes redirect unauthenticated users to landing page

## CI/CD

Push to `main` → GitHub Actions builds `frontend/` → syncs to S3 → invalidates CloudFront.
Assets are cached for 1 year; `index.html` is never cached so deploys are instant.

## Live App

[jobs.naindigital.com](https://jobs.naindigital.com)

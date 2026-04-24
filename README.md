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

**Phase 1 — MVP** (in progress)

- [x] Terraform base infrastructure (S3, CloudFront, ACM, DNS)
- [x] DynamoDB tables (Profile, Applications, Jobs)
- [x] 5 core Lambda functions (skeletons + IAM roles)
- [x] API Gateway HTTP API (9 routes, fully wired)
- [ ] React frontend
- [ ] GitHub Actions CI/CD pipeline
- [ ] Bedrock AI integration

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

## Live App

[jobs.naindigital.com](https://jobs.naindigital.com) *(frontend coming soon)*

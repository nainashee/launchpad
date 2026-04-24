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
- [x] 5 core Lambda functions (skeletons with IAM roles)
- [ ] API Gateway HTTP API + routes
- [ ] React frontend
- [ ] GitHub Actions CI/CD pipeline
- [ ] Bedrock AI integration

## Infrastructure

| Resource | Name |
|---|---|
| Frontend bucket | `launchpad-frontend-jobs` |
| Assets bucket | `launchpad-assets-989126024881` |
| CloudFront | `d1j38znc7w4uld.cloudfront.net` |
| DynamoDB | `launchpad-profile`, `launchpad-applications`, `launchpad-jobs` |
| Lambdas | `launchpad-tailor-resume`, `launchpad-decode-job`, `launchpad-generate-outreach`, `launchpad-mock-interview`, `launchpad-tracker` |

## Live App

[jobs.naindigital.com](https://jobs.naindigital.com) *(coming soon)*

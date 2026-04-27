variable "project_name" {
  description = "Project name used for resource naming"
  type        = string
  default     = "launchpad"
}

variable "domain_name" {
  description = "Root domain"
  type        = string
  default     = "naindigital.com"
}

variable "subdomain" {
  description = "Subdomain for the job board"
  type        = string
  default     = "jobs"
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "firebase_project_id" {
  description = "Firebase project ID — used by Lambdas to verify JWT audience/issuer"
  type        = string
  default     = "launchpad-93064"
}
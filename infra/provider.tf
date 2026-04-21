provider "aws" {
  region  = var.aws_region
  profile = "launchpad"
}

provider "aws" {
  alias   = "us_east_1"
  region  = "us-east-1"
  profile = "launchpad"
}
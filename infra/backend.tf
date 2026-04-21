terraform {
  backend "s3" {
    bucket = "launchpad-terraform-state-hussain"
    key    = "launchpad/terraform.tfstate"
    region = "us-east-1"
  }
}

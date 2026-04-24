# ---------------------------------------------------------------------------
# Profile table — one item per user, stores resume metadata and preferences
# ---------------------------------------------------------------------------
resource "aws_dynamodb_table" "profile" {
  name         = "${var.project_name}-profile"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "userId"

  attribute {
    name = "userId"
    type = "S"
  }

  tags = {
    Project = var.project_name
  }
}

# ---------------------------------------------------------------------------
# Applications table — tracks every job application
# GSI on followUpDate so the daily reminder job can query due follow-ups
# ---------------------------------------------------------------------------
resource "aws_dynamodb_table" "applications" {
  name         = "${var.project_name}-applications"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "userId"
  range_key    = "applicationId"

  attribute {
    name = "userId"
    type = "S"
  }

  attribute {
    name = "applicationId"
    type = "S"
  }

  attribute {
    name = "followUpDate"
    type = "S"
  }

  global_secondary_index {
    name            = "followUpDate-index"
    hash_key        = "followUpDate"
    projection_type = "ALL"
  }

  tags = {
    Project = var.project_name
  }
}

# ---------------------------------------------------------------------------
# Jobs table — Phase 2 cache for scraped job postings (30-day TTL)
# ---------------------------------------------------------------------------
resource "aws_dynamodb_table" "jobs" {
  name         = "${var.project_name}-jobs"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "source"
  range_key    = "jobId"

  attribute {
    name = "source"
    type = "S"
  }

  attribute {
    name = "jobId"
    type = "S"
  }

  ttl {
    attribute_name = "ttl"
    enabled        = true
  }

  tags = {
    Project = var.project_name
  }
}

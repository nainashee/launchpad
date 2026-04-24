# ---------------------------------------------------------------------------
# Zip each function's handler.py for deployment
# ---------------------------------------------------------------------------
data "archive_file" "tailor_resume" {
  type        = "zip"
  source_file = "${path.module}/../functions/tailor-resume/handler.py"
  output_path = "${path.module}/../functions/tailor-resume/handler.zip"
}

data "archive_file" "decode_job" {
  type        = "zip"
  source_file = "${path.module}/../functions/decode-job/handler.py"
  output_path = "${path.module}/../functions/decode-job/handler.zip"
}

data "archive_file" "generate_outreach" {
  type        = "zip"
  source_file = "${path.module}/../functions/generate-outreach/handler.py"
  output_path = "${path.module}/../functions/generate-outreach/handler.zip"
}

data "archive_file" "mock_interview" {
  type        = "zip"
  source_file = "${path.module}/../functions/mock-interview/handler.py"
  output_path = "${path.module}/../functions/mock-interview/handler.zip"
}

data "archive_file" "tracker" {
  type        = "zip"
  source_file = "${path.module}/../functions/tracker/handler.py"
  output_path = "${path.module}/../functions/tracker/handler.zip"
}

# ---------------------------------------------------------------------------
# Shared assume-role policy — lets Lambda service assume these roles
# ---------------------------------------------------------------------------
data "aws_iam_policy_document" "lambda_assume_role" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

# ---------------------------------------------------------------------------
# tailor-resume — needs Bedrock + S3 (read master, write tailored) + DynamoDB profile read
# ---------------------------------------------------------------------------
resource "aws_iam_role" "tailor_resume" {
  name               = "${var.project_name}-tailor-resume"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json
}

resource "aws_iam_role_policy_attachment" "tailor_resume_basic" {
  role       = aws_iam_role.tailor_resume.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy" "tailor_resume_inline" {
  name = "tailor-resume-inline"
  role = aws_iam_role.tailor_resume.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "BedrockInvoke"
        Effect = "Allow"
        Action = ["bedrock:InvokeModel"]
        Resource = "arn:aws:bedrock:${var.aws_region}::foundation-model/*"
      },
      {
        Sid    = "S3Assets"
        Effect = "Allow"
        Action = ["s3:GetObject", "s3:PutObject"]
        Resource = "${aws_s3_bucket.assets.arn}/resumes/*"
      },
      {
        Sid    = "DynamoDBProfileRead"
        Effect = "Allow"
        Action = ["dynamodb:GetItem"]
        Resource = aws_dynamodb_table.profile.arn
      }
    ]
  })
}

resource "aws_lambda_function" "tailor_resume" {
  function_name    = "${var.project_name}-tailor-resume"
  role             = aws_iam_role.tailor_resume.arn
  filename         = data.archive_file.tailor_resume.output_path
  source_code_hash = data.archive_file.tailor_resume.output_base64sha256
  runtime          = "python3.12"
  handler          = "handler.handler"
  timeout          = 60
  memory_size      = 512

  environment {
    variables = {
      ASSETS_BUCKET = aws_s3_bucket.assets.id
      PROFILE_TABLE = aws_dynamodb_table.profile.name
    }
  }
}

# ---------------------------------------------------------------------------
# decode-job — needs Bedrock only
# ---------------------------------------------------------------------------
resource "aws_iam_role" "decode_job" {
  name               = "${var.project_name}-decode-job"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json
}

resource "aws_iam_role_policy_attachment" "decode_job_basic" {
  role       = aws_iam_role.decode_job.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy" "decode_job_inline" {
  name = "decode-job-inline"
  role = aws_iam_role.decode_job.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "BedrockInvoke"
        Effect = "Allow"
        Action = ["bedrock:InvokeModel"]
        Resource = "arn:aws:bedrock:${var.aws_region}::foundation-model/*"
      }
    ]
  })
}

resource "aws_lambda_function" "decode_job" {
  function_name    = "${var.project_name}-decode-job"
  role             = aws_iam_role.decode_job.arn
  filename         = data.archive_file.decode_job.output_path
  source_code_hash = data.archive_file.decode_job.output_base64sha256
  runtime          = "python3.12"
  handler          = "handler.handler"
  timeout          = 30
  memory_size      = 256

  environment {
    variables = {
      ASSETS_BUCKET = aws_s3_bucket.assets.id
    }
  }
}

# ---------------------------------------------------------------------------
# generate-outreach — needs Bedrock + DynamoDB profile read
# ---------------------------------------------------------------------------
resource "aws_iam_role" "generate_outreach" {
  name               = "${var.project_name}-generate-outreach"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json
}

resource "aws_iam_role_policy_attachment" "generate_outreach_basic" {
  role       = aws_iam_role.generate_outreach.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy" "generate_outreach_inline" {
  name = "generate-outreach-inline"
  role = aws_iam_role.generate_outreach.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "BedrockInvoke"
        Effect = "Allow"
        Action = ["bedrock:InvokeModel"]
        Resource = "arn:aws:bedrock:${var.aws_region}::foundation-model/*"
      },
      {
        Sid    = "DynamoDBProfileRead"
        Effect = "Allow"
        Action = ["dynamodb:GetItem"]
        Resource = aws_dynamodb_table.profile.arn
      }
    ]
  })
}

resource "aws_lambda_function" "generate_outreach" {
  function_name    = "${var.project_name}-generate-outreach"
  role             = aws_iam_role.generate_outreach.arn
  filename         = data.archive_file.generate_outreach.output_path
  source_code_hash = data.archive_file.generate_outreach.output_base64sha256
  runtime          = "python3.12"
  handler          = "handler.handler"
  timeout          = 30
  memory_size      = 256

  environment {
    variables = {
      PROFILE_TABLE = aws_dynamodb_table.profile.name
    }
  }
}

# ---------------------------------------------------------------------------
# mock-interview — needs Bedrock only
# ---------------------------------------------------------------------------
resource "aws_iam_role" "mock_interview" {
  name               = "${var.project_name}-mock-interview"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json
}

resource "aws_iam_role_policy_attachment" "mock_interview_basic" {
  role       = aws_iam_role.mock_interview.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy" "mock_interview_inline" {
  name = "mock-interview-inline"
  role = aws_iam_role.mock_interview.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "BedrockInvoke"
        Effect = "Allow"
        Action = ["bedrock:InvokeModel"]
        Resource = "arn:aws:bedrock:${var.aws_region}::foundation-model/*"
      }
    ]
  })
}

resource "aws_lambda_function" "mock_interview" {
  function_name    = "${var.project_name}-mock-interview"
  role             = aws_iam_role.mock_interview.arn
  filename         = data.archive_file.mock_interview.output_path
  source_code_hash = data.archive_file.mock_interview.output_base64sha256
  runtime          = "python3.12"
  handler          = "handler.handler"
  timeout          = 30
  memory_size      = 256
}

# ---------------------------------------------------------------------------
# tracker — needs DynamoDB CRUD on applications table only
# ---------------------------------------------------------------------------
resource "aws_iam_role" "tracker" {
  name               = "${var.project_name}-tracker"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json
}

resource "aws_iam_role_policy_attachment" "tracker_basic" {
  role       = aws_iam_role.tracker.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy" "tracker_inline" {
  name = "tracker-inline"
  role = aws_iam_role.tracker.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "DynamoDBApplicationsCRUD"
        Effect = "Allow"
        Action = [
          "dynamodb:PutItem",
          "dynamodb:GetItem",
          "dynamodb:UpdateItem",
          "dynamodb:DeleteItem",
          "dynamodb:Query"
        ]
        Resource = [
          aws_dynamodb_table.applications.arn,
          "${aws_dynamodb_table.applications.arn}/index/*"
        ]
      }
    ]
  })
}

resource "aws_lambda_function" "tracker" {
  function_name    = "${var.project_name}-tracker"
  role             = aws_iam_role.tracker.arn
  filename         = data.archive_file.tracker.output_path
  source_code_hash = data.archive_file.tracker.output_base64sha256
  runtime          = "python3.12"
  handler          = "handler.handler"
  timeout          = 10
  memory_size      = 128

  environment {
    variables = {
      APPLICATIONS_TABLE = aws_dynamodb_table.applications.name
    }
  }
}

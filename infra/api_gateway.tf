# ---------------------------------------------------------------------------
# HTTP API — the public HTTPS endpoint for the frontend to call
# ---------------------------------------------------------------------------
resource "aws_apigatewayv2_api" "main" {
  name          = "${var.project_name}-api"
  protocol_type = "HTTP"

  cors_configuration {
    allow_origins = [
      "https://${var.subdomain}.${var.domain_name}",
      "http://localhost:5173",
    ]
    allow_methods = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    allow_headers = ["Content-Type", "Authorization"]
    max_age       = 300
  }
}

# ---------------------------------------------------------------------------
# Default stage — auto-deploys on every Terraform apply
# Route-level throttling caps request rates before Lambda is invoked.
# Bedrock routes are tighter (expensive); CRUD routes are looser (cheap).
# ---------------------------------------------------------------------------
resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.main.id
  name        = "$default"
  auto_deploy = true

  default_route_settings {
    throttling_rate_limit  = 20
    throttling_burst_limit = 50
  }

  route_settings {
    route_key              = "POST /decode-job"
    throttling_rate_limit  = 0.5
    throttling_burst_limit = 2
  }

  route_settings {
    route_key              = "POST /tailor-resume"
    throttling_rate_limit  = 0.3
    throttling_burst_limit = 1
  }

  route_settings {
    route_key              = "POST /outreach"
    throttling_rate_limit  = 0.5
    throttling_burst_limit = 2
  }

  route_settings {
    route_key              = "POST /interview"
    throttling_rate_limit  = 1
    throttling_burst_limit = 3
  }
}

# ---------------------------------------------------------------------------
# Integrations — tells API Gateway which Lambda to invoke
# ---------------------------------------------------------------------------
resource "aws_apigatewayv2_integration" "tailor_resume" {
  api_id                 = aws_apigatewayv2_api.main.id
  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.tailor_resume.invoke_arn
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_integration" "decode_job" {
  api_id                 = aws_apigatewayv2_api.main.id
  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.decode_job.invoke_arn
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_integration" "generate_outreach" {
  api_id                 = aws_apigatewayv2_api.main.id
  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.generate_outreach.invoke_arn
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_integration" "mock_interview" {
  api_id                 = aws_apigatewayv2_api.main.id
  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.mock_interview.invoke_arn
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_integration" "tracker" {
  api_id                 = aws_apigatewayv2_api.main.id
  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.tracker.invoke_arn
  payload_format_version = "2.0"
}

# ---------------------------------------------------------------------------
# Routes — maps HTTP method + path to an integration
# ---------------------------------------------------------------------------
resource "aws_apigatewayv2_route" "tailor_resume" {
  api_id    = aws_apigatewayv2_api.main.id
  route_key = "POST /tailor-resume"
  target    = "integrations/${aws_apigatewayv2_integration.tailor_resume.id}"
}

resource "aws_apigatewayv2_route" "decode_job" {
  api_id    = aws_apigatewayv2_api.main.id
  route_key = "POST /decode-job"
  target    = "integrations/${aws_apigatewayv2_integration.decode_job.id}"
}

resource "aws_apigatewayv2_route" "generate_outreach" {
  api_id    = aws_apigatewayv2_api.main.id
  route_key = "POST /outreach"
  target    = "integrations/${aws_apigatewayv2_integration.generate_outreach.id}"
}

resource "aws_apigatewayv2_route" "mock_interview" {
  api_id    = aws_apigatewayv2_api.main.id
  route_key = "POST /interview"
  target    = "integrations/${aws_apigatewayv2_integration.mock_interview.id}"
}

resource "aws_apigatewayv2_route" "tracker_create" {
  api_id    = aws_apigatewayv2_api.main.id
  route_key = "POST /applications"
  target    = "integrations/${aws_apigatewayv2_integration.tracker.id}"
}

resource "aws_apigatewayv2_route" "tracker_list" {
  api_id    = aws_apigatewayv2_api.main.id
  route_key = "GET /applications"
  target    = "integrations/${aws_apigatewayv2_integration.tracker.id}"
}

resource "aws_apigatewayv2_route" "tracker_get" {
  api_id    = aws_apigatewayv2_api.main.id
  route_key = "GET /applications/{id}"
  target    = "integrations/${aws_apigatewayv2_integration.tracker.id}"
}

resource "aws_apigatewayv2_route" "tracker_update" {
  api_id    = aws_apigatewayv2_api.main.id
  route_key = "PUT /applications/{id}"
  target    = "integrations/${aws_apigatewayv2_integration.tracker.id}"
}

resource "aws_apigatewayv2_route" "tracker_delete" {
  api_id    = aws_apigatewayv2_api.main.id
  route_key = "DELETE /applications/{id}"
  target    = "integrations/${aws_apigatewayv2_integration.tracker.id}"
}

# ---------------------------------------------------------------------------
# Lambda permissions — allows API Gateway to invoke each function
# ---------------------------------------------------------------------------
resource "aws_lambda_permission" "tailor_resume" {
  statement_id  = "AllowAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.tailor_resume.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.main.execution_arn}/*/*"
}

resource "aws_lambda_permission" "decode_job" {
  statement_id  = "AllowAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.decode_job.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.main.execution_arn}/*/*"
}

resource "aws_lambda_permission" "generate_outreach" {
  statement_id  = "AllowAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.generate_outreach.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.main.execution_arn}/*/*"
}

resource "aws_lambda_permission" "mock_interview" {
  statement_id  = "AllowAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.mock_interview.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.main.execution_arn}/*/*"
}

resource "aws_lambda_permission" "tracker" {
  statement_id  = "AllowAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.tracker.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.main.execution_arn}/*/*"
}

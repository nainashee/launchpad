resource "aws_acm_certificate" "frontend" {
  provider          = aws.us_east_1
  domain_name       = "${var.subdomain}.${var.domain_name}"
  validation_method = "DNS"

  lifecycle {
    create_before_destroy = true
  }
}
output "cloudfront_distribution_id" {
  description = "CloudFront distribution ID for cache invalidation"
  value       = aws_cloudfront_distribution.frontend.id
}

output "cloudfront_domain_name" {
  description = "CloudFront domain name"
  value       = aws_cloudfront_distribution.frontend.domain_name
}

output "acm_validation_records" {
  description = "DNS records to add in Cloudflare for certificate validation"
  value = {
    for dvo in aws_acm_certificate.frontend.domain_validation_options : dvo.domain_name => {
      type  = dvo.resource_record_type
      name  = dvo.resource_record_name
      value = dvo.resource_record_value
    }
  }
}

output "s3_bucket_name" {
  description = "S3 bucket name for deploying files"
  value       = aws_s3_bucket.frontend.id
}

output "api_url" {
  description = "API Gateway base URL — append route paths to call the backend"
  value       = aws_apigatewayv2_stage.default.invoke_url
}
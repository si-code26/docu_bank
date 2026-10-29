resource "aws_cloudfront_distribution" "docubank" {
  enabled    = true
  web_acl_id = aws_wafv2_web_acl.docubank.arn   # attach WAF at the edge

  origin {
    domain_name = aws_lb.docubank.dns_name   # your existing ALB
    origin_id   = "docubank-alb"

    custom_origin_config {
      http_port                = 80
      https_port                = 443
      origin_protocol_policy    = "http-only"   # ALB listener is on port 80 currently
      origin_ssl_protocols      = ["TLSv1.2"]
    }
  }

  default_cache_behavior {
    target_origin_id       = "docubank-alb"
    viewer_protocol_policy = "redirect-to-https"  # http->https at the edge
    allowed_methods        = ["GET", "HEAD", "OPTIONS", "PUT", "POST", "PATCH", "DELETE"]
    cached_methods          = ["GET", "HEAD"]

    forwarded_values {
      query_string = true
      headers      = ["Authorization", "Content-Type"]  # pass through JWT + body type
      cookies {
        forward = "none"
      }
    }

    min_ttl     = 0
    default_ttl = 0   # API responses shouldn't be cached by default
    max_ttl     = 0
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    cloudfront_default_certificate = true   # uses the free *.cloudfront.net cert
  }
}

output "cloudfront_domain" {
  value = aws_cloudfront_distribution.docubank.domain_name
}

output "cloudfront_distribution_id" {
  value = aws_cloudfront_distribution.docubank.id
}
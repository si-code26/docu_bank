resource "aws_wafv2_web_acl" "docubank" {
  name  = "docubank-waf"
  scope = "CLOUDFRONT"   # REGIONAL for ALB/API Gateway; CLOUDFRONT is a different scope

  # CLOUDFRONT-scoped WAF must be created in us-east-1 regardless of
  # where the rest of your infra lives — add this if not already set:
  provider = aws.us_east_1

  default_action {
    allow {}
  }

  rule {
    name     = "rate-limit"
    priority = 1

    action {
      block {}
    }

    statement {
      rate_based_statement {
        limit              = 2000   # requests per 5-min window, per IP
        aggregate_key_type = "IP"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "docubank-rate-limit"
      sampled_requests_enabled   = true
    }
  }

  rule {
    name     = "aws-managed-common"
    priority = 2

    override_action {
      none {}
    }

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesCommonRuleSet"
        vendor_name = "AWS"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "docubank-common-rules"
      sampled_requests_enabled   = true
    }
  }

  visibility_config {
    cloudwatch_metrics_enabled = true
    metric_name                = "docubank-waf"
    sampled_requests_enabled   = true
  }
}

# NOTE: no aws_wafv2_web_acl_association resource here anymore —
# WAF now attaches directly to CloudFront via web_acl_id in cloudfront.tf.
# If you still have an aws_wafv2_web_acl_association.alb block in ANY
# other .tf file (alb.tf, security.tf, etc.), delete it — run:
#   grep -rn "aws_wafv2_web_acl_association" infra/*.tf
# to confirm it's gone from every file.
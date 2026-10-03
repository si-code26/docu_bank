resource "aws_s3_bucket" "uploads" {
  bucket = "docubank-uploads-${data.aws_caller_identity.current.account_id}"
  # account ID suffix makes the name globally unique (S3 bucket names are global)
}

data "aws_caller_identity" "current" {}

resource "aws_sqs_queue" "ingest" {
  name                       = "docubank-ingest"
  visibility_timeout_seconds = 120   # matches your worker's processing time budget
  message_retention_seconds  = 86400 # 1 day
}
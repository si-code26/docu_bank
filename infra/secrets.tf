data "aws_secretsmanager_secret" "openai_key" {
  name = "docubank/openai-api-key"
}

data "aws_secretsmanager_secret" "langfuse_public_key" {
  name = "docubank/langfuse-public-key"
}

data "aws_secretsmanager_secret" "langfuse_secret_key" {
  name = "docubank/langfuse-secret-key"
}
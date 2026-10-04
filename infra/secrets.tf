data "aws_secretsmanager_secret" "openai_key" {
  name = "docubank/openai-api-key"
}
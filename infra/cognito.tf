# infra/cognito.tf
resource "aws_cognito_user_pool" "docubank" {
  name = "docubank-users"

  password_policy {
    minimum_length    = 8
    require_lowercase = true
    require_numbers   = true
    require_symbols   = false
    require_uppercase = true
  }

  auto_verified_attributes = ["email"]
}

resource "aws_cognito_user_pool_client" "docubank" {
  name         = "docubank-client"
  user_pool_id = aws_cognito_user_pool.docubank.id

  explicit_auth_flows = ["ALLOW_USER_PASSWORD_AUTH", "ALLOW_REFRESH_TOKEN_AUTH"]

  generate_secret = false  # public client (frontend), PKCE flow
}
# infra/ecs.tf

resource "aws_ecs_cluster" "docubank" {
  name = "docubank-cluster"
}

# Execution role: lets ECS itself pull images from ECR + write logs
# (different from a TASK role, which is what your app code uses to call AWS services — that's file #3 in the plan)
resource "aws_iam_role" "ecs_execution" {
  name = "docubank-ecs-execution-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "ecs-tasks.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_execution" {
  role       = aws_iam_role.ecs_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_cloudwatch_log_group" "api" {
  name              = "/ecs/docubank-api"
  retention_in_days = 7
}

resource "aws_cloudwatch_log_group" "worker" {
  name              = "/ecs/docubank-worker"
  retention_in_days = 7
}
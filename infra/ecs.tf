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

resource "aws_ecs_task_definition" "api" {
  family                   = "docubank-api"
  requires_compatibilities = ["FARGATE"]
  network_mode              = "awsvpc"
  cpu                        = "256"
  memory                     = "512"
  execution_role_arn         = aws_iam_role.ecs_execution.arn

  container_definitions = jsonencode([
    {
      name      = "api"
      image     = "833068513702.dkr.ecr.us-east-1.amazonaws.com/docubank-api:latest"
      essential = true
      portMappings = [{ containerPort = 8000, protocol = "tcp" }]
      environment = [
        { name = "DATABASE_URL", value = "postgresql+asyncpg://docubank:${var.db_password}@${aws_db_instance.docubank.address}:5432/docubank" },
        { name = "OPENAI_API_KEY", value = var.openai_api_key },
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.api.name
          "awslogs-region"        = "us-east-1"
          "awslogs-stream-prefix" = "api"
        }
      }
    }
  ])
}
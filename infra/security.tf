# ALB security group: allows inbound HTTP from the internet
resource "aws_security_group" "alb" {
  name   = "docubank-alb-sg"
  vpc_id = aws_vpc.docubank.id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = { Name = "docubank-alb-sg" }
}

# ECS tasks security group: only accepts traffic FROM the ALB
resource "aws_security_group" "ecs" {
  name   = "docubank-ecs-sg"
  vpc_id = aws_vpc.docubank.id

  ingress {
    from_port       = 8000
    to_port         = 8000
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = { Name = "docubank-ecs-sg" }
}

# RDS security group: only accepts traffic FROM ECS tasks
resource "aws_security_group" "rds" {
  name   = "docubank-rds-sg"
  vpc_id = aws_vpc.docubank.id

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.ecs.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = { Name = "docubank-rds-sg" }
}
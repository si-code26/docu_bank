resource "aws_lb" "docubank" {
  name               = "docubank-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = [aws_subnet.public_a.id, aws_subnet.public_b.id]

  tags = { Name = "docubank-alb" }
}

resource "aws_lb_target_group" "api" {
  name        = "docubank-api-tg"
  port        = 8000
  protocol    = "HTTP"
  vpc_id      = aws_vpc.docubank.id
  target_type = "ip"   # Fargate tasks are targeted by IP, not instance ID

  health_check {
    path                = "/health"
    healthy_threshold   = 2
    unhealthy_threshold = 3
    interval            = 30
    timeout             = 5
  }

  tags = { Name = "docubank-api-tg" }
}

resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.docubank.arn
  port               = 80
  protocol           = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.api.arn
  }
}
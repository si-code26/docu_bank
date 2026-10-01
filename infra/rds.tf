resource "aws_db_subnet_group" "docubank" {
  name       = "docubank-db-subnet-group"
  subnet_ids = [aws_subnet.private_a.id, aws_subnet.private_b.id]
  tags = { Name = "docubank-db-subnet-group" }
}

resource "aws_db_instance" "docubank" {
  identifier             = "docubank-db"
  engine                 = "postgres"
  engine_version         = "16"
  instance_class         = "db.t3.micro"       # free-tier eligible
  allocated_storage      = 20
  db_name                = "docubank"
  username               = "docubank"
  password                = var.db_password      # never hardcode — see below
  db_subnet_group_name    = aws_db_subnet_group.docubank.name
  vpc_security_group_ids  = [aws_security_group.rds.id]
  publicly_accessible     = true
  skip_final_snapshot     = true                  # fine for dev; false for real prod
  tags = { Name = "docubank-db" }
}
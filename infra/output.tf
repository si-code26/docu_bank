output "db_endpoint" {
  value = aws_db_instance.docubank.address
}

output "vpc_id" {
  value = aws_vpc.docubank.id
}
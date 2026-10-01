output "db_endpoint" {
  value = aws_db_instance.docubank.address
}

output "vpc_id" {
  value = aws_vpc.docubank.id
}

output "alb_dns" {
  value = aws_lb.docubank.dns_name
}
resource "aws_eip" "nat" {
  domain = "vpc"
  tags = { Name = "docubank-nat-eip" }
}

resource "aws_nat_gateway" "docubank" {
  allocation_id = aws_eip.nat.id
  subnet_id     = aws_subnet.public_a.id   # NAT lives in a public subnet
  tags = { Name = "docubank-nat" }
  depends_on    = [aws_internet_gateway.docubank]
}

# private route table: route outbound traffic through the NAT
resource "aws_route_table" "private" {
  vpc_id = aws_vpc.docubank.id
  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.docubank.id
  }
  tags = { Name = "docubank-private-rt" }
}

resource "aws_route_table_association" "private_a" {
  subnet_id      = aws_subnet.private_a.id
  route_table_id = aws_route_table.private.id
}

resource "aws_route_table_association" "private_b" {
  subnet_id      = aws_subnet.private_b.id
  route_table_id = aws_route_table.private.id
}
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}

# --- VPC: your isolated network in AWS ---
resource "aws_vpc" "docubank" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true
  tags = { Name = "docubank-vpc" }
}

# --- Public subnets (ALB lives here — needs internet access) ---
resource "aws_subnet" "public_a" {
  vpc_id                  = aws_vpc.docubank.id
  cidr_block               = "10.0.1.0/24"
  availability_zone        = "us-east-1a"
  map_public_ip_on_launch  = true
  tags = { Name = "docubank-public-a" }
}

resource "aws_subnet" "public_b" {
  vpc_id                  = aws_vpc.docubank.id
  cidr_block               = "10.0.2.0/24"
  availability_zone        = "us-east-1b"
  map_public_ip_on_launch  = true
  tags = { Name = "docubank-public-b" }
}

# --- Private subnets (RDS + ECS tasks live here — no direct internet) ---
resource "aws_subnet" "private_a" {
  vpc_id            = aws_vpc.docubank.id
  cidr_block         = "10.0.11.0/24"
  availability_zone  = "us-east-1a"
  tags = { Name = "docubank-private-a" }
}

resource "aws_subnet" "private_b" {
  vpc_id            = aws_vpc.docubank.id
  cidr_block         = "10.0.12.0/24"
  availability_zone  = "us-east-1b"
  tags = { Name = "docubank-private-b" }
}

# --- Internet Gateway (public subnets' door to the internet) ---
resource "aws_internet_gateway" "docubank" {
  vpc_id = aws_vpc.docubank.id
  tags = { Name = "docubank-igw" }
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.docubank.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.docubank.id
  }
  tags = { Name = "docubank-public-rt" }
}

resource "aws_route_table_association" "public_a" {
  subnet_id      = aws_subnet.public_a.id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table_association" "public_b" {
  subnet_id      = aws_subnet.public_b.id
  route_table_id = aws_route_table.public.id
}
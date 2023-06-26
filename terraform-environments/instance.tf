terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.16"
    }
  }
  required_version = ">= 1.2.0"
}

resource "aws_security_group" "ec2_security" {
  name        = "ec2_security"
  description = "Give correct security for ec2"
  #tanis vpc = vpc-0bfb64215145a3e13
  vpc_id      = "vpc-0698eb109e6e2afd5"

  ingress {
    from_port        = 8080
    to_port          = 8080
    protocol         = "tcp"
    cidr_blocks      = ["0.0.0.0/0"]
  }
  
  ingress {
    from_port        = 22
    to_port          = 22
    protocol         = "SSH"
    cidr_blocks      = ["0.0.0.0/0"]
  }

  ingress {
    from_port        = 80
    to_port          = 80
    protocol         = "HTTPS"
    cidr_blocks      = ["0.0.0.0/0"]
  }
  tags = {
    Name = "ec2_security"
  }
 }

resource "aws_instance" "app_server" {
  # creates ec2 instance
  ami = "ami-090e0fc566929d98b"
  instance_type = "t2.micro"
  vpc_security_group_ids  =["ec2_security"]
  tags = {
    Name = "TeamHenrique"
  }
  region = "us-east-1"
}










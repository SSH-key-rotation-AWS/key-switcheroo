# AWS Quickstart
# Configure the AWS provider
variable "drp_username" {
  type    = string
  default = "rocketskates"
}

variable "drp_password" {
  type    = string
  default = "r0cketsk8ts"
}

variable "drp_id" {
  type    = string
  default = "!default!"
}

variable "drp_version" {
  type    = string
  default = "tip"
}

variable "ssh_pub_key" {
  type = string
  default = "~/.ssh/id_rsa.pub"
}

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 3.50.0"
    }
  }
  required_version = ">= 1.0"
}

resource "aws_key_pair" "drp_install" {
  key_name_prefix = "drp-"
  public_key = chomp(file(var.ssh_pub_key))
}

locals {
  drp_id            = var.drp_id != "!default!" ? "--drp-id=${var.drp_id}" : ""
  cloud_init_script = <<-EOT
  #!/bin/bash
  value=$(curl -sfL http://169.254.169.254/latest/meta-data/public-ipv4)
  curl -fsSL get.rebar.digital/stable | sudo bash -s -- install --universal --version=${var.drp_version} --ipaddr=$value --remove-rocketskates --drp-password=${var.drp_password} --drp-user=${var.drp_username} ${local.drp_id}
  EOT
}

resource "aws_security_group" "digitalrebar_server" {

  name_prefix = "drp_server"
  description = "Digital Rebar Install"
  ingress {
    description = "ssh"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  ingress {
    description = "drp_ports"
    from_port   = 8090
    to_port     = 8092
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  tags = {
    Name = "digitalrebar"
  }
}

resource "aws_instance" "drp_server" {
  ami           = data.aws_ami.amazon_linux.id
  instance_type = "t2.micro"
  tags = {
    Name = "Digital_Rebar"
  }
  key_name        = aws_key_pair.drp_install.key_name
  security_groups = [aws_security_group.digitalrebar_server.name]
  user_data       = local.cloud_init_script
}

output "drp_credentials" {
  value       = "export RS_KEY=${var.drp_username}:${var.drp_password}"
  description = "export of DRP credentials"
}

output "drp_manager" {
  value       = "export RS_ENDPOINT=https://${aws_instance.drp_server.public_ip}:8092"
  description = "export of URL of DRP"
}

data "aws_ami" "amazon_linux" {
  filter {
    name      = "name"
    values    = ["amzn2-ami-hvm*x86_64*ebs*"]
  }
  most_recent = true
  owners      = ["amazon"]
}

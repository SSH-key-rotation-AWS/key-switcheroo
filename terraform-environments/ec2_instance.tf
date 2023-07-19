resource "aws_security_group" "security" {
  name        = "ec2_security"
  description = "Give correct security for ec2"
  #tanis vpc = vpc-0bfb64215145a3e13
  vpc_id      = "vpc-0bfb64215145a3e13"

  ingress {
    from_port        = 8080
    to_port          = 8080
    protocol         = "tcp"
    cidr_blocks      = ["0.0.0.0/0"]
  }

  ingress {
    from_port        = 22
    to_port          = 22
    protocol         = "tcp"
    cidr_blocks      = ["0.0.0.0/0"]
  }

  ingress {
    from_port        = 80
    to_port          = 80
    protocol         = "tcp"
    cidr_blocks      = ["0.0.0.0/0"]
  }

  egress {
    from_port        = 0
    to_port          = 0
    protocol         = "-1"
    cidr_blocks      = ["0.0.0.0/0"]
  }

  tags = {
    Name = "ec2_security"
  }
}

data "aws_secretsmanager_secret" "credentials_and_keys" {
  name = credentials_and_keys
}

locals {
  inline_user_data = <<-EOT
    #!/bin/bash
    export JENKINS_LOGIN=${data.aws_secretsmanager_secret.jenkins_login.secret_string}
    export GITHUB_PAT=${data.aws_secretsmanager_secret.key-switcheroo_github_pat.secret_string}
    export GITHUB_LOGIN=${data.aws_secretsmanager_secret.github_login.secret_string}
    export PYPI_KEY=${data.aws_secretsmanager_secret.pypi_api_token.secret_string}
  EOT

  external_script = file("${path.module}/startup.sh")
}

resource "aws_instance" "app_server" {
  # creates ec2 instance
  ami = "ami-053b0d53c279acc90"
  instance_type = "t2.micro"
  vpc_security_group_ids  = [aws_security_group.security.id]
  tags = {
    Name = "KeySwitcheroo"
  }
  user_data = "${local.external_script}\n${local.inline_user_data}"

  provisioner "file" {
    source = "${path.module}/setup.groovy"
    destination = "~/setup.groovy"
  }

  provisioner "file" {
    source = "${path.module}/config.xml"
    destination = "~/config.xml"
  }

  provisioner "file" {
    source = "${path.module}/github_credentials.xml"
    destination = "~/github_credentials.xml"
  }
}
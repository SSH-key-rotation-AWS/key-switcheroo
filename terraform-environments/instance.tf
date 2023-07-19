resource "aws_security_group" "security" {
  name        = "ec2_security2"
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

# data "aws_secretsmanager_secret" "jenkins_login" {
#   secret_id = jenkins_login
# }

# data "aws_secretsmanager_secret" "key-switcheroo_github_pat" {
#   secret_id = key-switcheroo_github_pat
# }

# data "aws_secretsmanager_secret" "github_login" {
#   secret_id = github_login
# }

# data "aws_secretsmanager_secret" "pypi_api_token" {
#   secret_id = pypi_api_token
# }

# locals {
#   inline_user_data = <<-EOT
#     #!/bin/bash
#     export JENKINS_LOGIN=${data.aws_secretsmanager_secret.jenkins_login.secret_string}
#     export GITHUB_PAT=${data.aws_secretsmanager_secret.key-switcheroo_github_pat.secret_string}
#     export GITHUB_LOGIN=${data.aws_secretsmanager_secret.github_login.secret_string}
#     export PYPI_KEY=${data.aws_secretsmanager_secret.pypi_api_token.secret_string}
#   EOT

#   external_script = file("${path.module}/startup.sh")
# }

resource "tls_private_key" "pk" {
  algorithm = "RSA"
  rsa_bits  = 4096
}

resource "aws_key_pair" "kp" {
  key_name   = "key"
  public_key = tls_private_key.pk.public_key_openssh
}

resource "aws_instance" "app_server" {
  # creates ec2 instance
  ami = "ami-053b0d53c279acc90"
  instance_type = "t2.micro"
  key_name = "key"
  vpc_security_group_ids  = [aws_security_group.security.id]
  tags = {
    Name = "KeySwitcheroo"
  }
  user_data = file("startup.sh")

  connection {
    type        = "ssh"
    user        = "ec2-user"
    private_key = tls_private_key.pk.private_key_pem
    host        = self.public_ip
  }

  # provisioner "remote-exec" {
  #   inline = [
  #     "/bin/sudo /bin/chmod 777 /var/lib/cloud/instance"
  #   ]
  # }

  provisioner "file" {
    source = "${path.module}/setup.groovy"
    destination = "/var/lib/cloud/instance/setup.groovy"
  }

  provisioner "file" {
    source = "${path.module}/config.xml"
    destination = "/var/lib/cloud/instance/config.xml"
  }

  provisioner "file" {
    source = "${path.module}/github_credentials.xml"
    destination = "/var/lib/cloud/instance/github_credentials.xml"
  }
}
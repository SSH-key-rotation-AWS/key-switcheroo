resource "aws_security_group" "security" {
  name        = "ec2_security"
  description = "Give correct security for ec2"
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

data "aws_secretsmanager_secret" "jenkins_username" {
  name = "jenkins_username"
}

data "aws_secretsmanager_secret_version" "jenkins_username" {
  secret_id = data.aws_secretsmanager_secret.jenkins_username.id
}

data "aws_secretsmanager_secret" "jenkins_password" {
  name = "jenkins_password"
}

data "aws_secretsmanager_secret_version" "jenkins_password" {
  secret_id = data.aws_secretsmanager_secret.jenkins_password.id
}

data "aws_secretsmanager_secret" "key-switcheroo_github_pat" {
  name = "key-switcheroo_github_pat"
}

data "aws_secretsmanager_secret_version" "key-switcheroo_github_pat" {
  secret_id = data.aws_secretsmanager_secret.key-switcheroo_github_pat.id
}

data "aws_secretsmanager_secret" "pypi_api_token" {
  name = "pypi_api_token"
}

data "aws_secretsmanager_secret_version" "pypi_api_token" {
  secret_id = data.aws_secretsmanager_secret.pypi_api_token.id
}

data "aws_secretsmanager_secret" "aws_access_key" {
  name = "aws_access_key"
}

data "aws_secretsmanager_secret_version" "aws_access_key" {
  secret_id = data.aws_secretsmanager_secret.aws_access_key.id
}

data "aws_secretsmanager_secret" "aws_secret_access_key" {
  name = "aws_secret_access_key"
}

data "aws_secretsmanager_secret_version" "aws_secret_access_key" {
  secret_id = data.aws_secretsmanager_secret.aws_secret_access_key.id
}

data "aws_secretsmanager_secret" "github_username" {
  name = "github_username"
}

data "aws_secretsmanager_secret_version" "github_username" {
  secret_id = data.aws_secretsmanager_secret.github_username.id
}

resource "tls_private_key" "pk" {
  algorithm = "RSA"
  rsa_bits  = 4096
}

resource "aws_key_pair" "kp" {
  key_name   = "key"
  public_key = tls_private_key.pk.public_key_openssh
}

resource "aws_instance" "app_server" {
  ami = "ami-053b0d53c279acc90"
  instance_type = "t2.small"
  key_name = "key"
  vpc_security_group_ids  = [aws_security_group.security.id]
  tags = {
    Name = "KeySwitcheroo"
  }
  user_data = base64encode(templatefile("./startup.sh", {
    JENKINS_USERNAME="${data.aws_secretsmanager_secret_version.jenkins_username.secret_string}", 
    JENKINS_PASSWORD="${data.aws_secretsmanager_secret_version.jenkins_password.secret_string}", 
    GITHUB_PAT="${data.aws_secretsmanager_secret_version.key-switcheroo_github_pat.secret_string}",
    AWS_ACCESS_KEY="${data.aws_secretsmanager_secret_version.aws_access_key.secret_string}",
    AWS_SECRET_ACCESS_KEY="${data.aws_secretsmanager_secret_version.aws_secret_access_key.secret_string}",
    GITHUB_USERNAME="${data.aws_secretsmanager_secret_version.github_username.secret_string}",
    PYPI_API_TOKEN="${data.aws_secretsmanager_secret_version.pypi_api_token.secret_string}",
    HOST_1_IP="${resource.aws_instance.baremetal-host-1.public_ip}",
    HOST_2_IP="${resource.aws_instance.baremetal-host-2.public_ip}",
    PRIVATE_KEY="${resource.tls_private_key.key_pair.private_key_pem}"
  }))

  connection {
    type        = "ssh"
    user        = "ubuntu"
    private_key = tls_private_key.pk.private_key_pem
    host        = self.public_ip
  }

  provisioner "file" {
    source = "${path.module}/setup.groovy"
    destination = "setup.groovy"
  }

  provisioner "file" {
    source = "${path.module}/config.xml"
    destination = "config.xml"
  }

  provisioner "file" {
    source = "${path.module}/github_credentials.xml"
    destination = "github_credentials.xml"
  }

  provisioner "file" {
    source = "${path.module}/aws_secret_access_key.xml"
    destination = "aws-secret-access-key.xml"
  }

  provisioner "file" {
    source = "${path.module}/aws_access_key.xml"
    destination = "aws-access-key.xml"
  }

  provisioner "file" {
    source = "${path.module}/pypi_api_token.xml"
    destination = "pypi_api_token.xml"
  }

  provisioner "file" {
    source = "${path.module}/github_pat.xml"
    destination = "github_pat.xml"
  }

  provisioner "file" {
    source = "${path.module}/org.jenkinsci.plugins.github_branch_source.GitHubConfiguration.xml"
    destination = "org.jenkinsci.plugins.github_branch_source.GitHubConfiguration.xml"
  }

  provisioner "file" {
    source = "${path.module}/host_1_ip.xml"
    destination = "host_1_ip.xml"
  }

  provisioner "file" {
    source = "${path.module}/host_2_ip.xml"
    destination = "host_2_ip.xml"
  }

  provisioner "file" {
    source = "${path.module}/private_key.xml"
    destination = "private_key.xml"
  }

  provisioner "remote-exec" {
    inline = [
      "/bin/sudo /bin/mv ~/setup.groovy /setup.groovy",
      "/bin/sudo /bin/mv ~/config.xml /config.xml",
      "/bin/sudo /bin/mv ~/github_credentials.xml /github_credentials.xml",
      "/bin/sudo /bin/mv ~/aws-secret-access-key.xml /aws-secret-access-key.xml",
      "/bin/sudo /bin/mv ~/aws-access-key.xml /aws-access-key.xml",
      "/bin/sudo /bin/mv ~/pypi_api_token.xml /pypi_api_token.xml",
      "/bin/sudo /bin/mv ~/github_pat.xml /github_pat.xml",
      "/bin/sudo /bin/mv ~/org.jenkinsci.plugins.github_branch_source.GitHubConfiguration.xml /org.jenkinsci.plugins.github_branch_source.GitHubConfiguration.xml",
      "/bin/sudo /bin/mv ~/host_1_ip.xml /host_1_ip.xml",
      "/bin/sudo /bin/mv ~/host_2_ip.xml /host_2_ip.xml",
      "/bin/sudo /bin/mv ~/private_key.xml /private_key.xml"
    ]
  }
}
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
    Name = "ec2_security2"
  }
}

# data "aws_secretsmanager_secret" "jenkins_login" {
#   secret_id = jenkins_login
# }

# data "aws_secretsmanager_secret" "key-switcheroo_github_pat" {
#   secret_id = key-switcheroo_github_pat
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

# resource "tls_private_key" "pk" {
#   algorithm = "RSA"
#   rsa_bits  = 4096
# }

# resource "aws_key_pair" "kp" {
#   key_name   = "key"
#   public_key = tls_private_key.pk.public_key_openssh
# }

# variable "instance_profile_name" {
#   type    = string
#   default = "secrets-manager"
# }

# variable "iam_policy_name" {
#   # same name as aws's built in policy - not neccasary
#   type    = string
#   default = "SecretsManagerReadWrite"
# }

# variable "role_name" {
#   # role is different than one that exists on aws
#   type    = string
#   default = "ec2-secrets-access-terraform-role"
# }

# # Create an IAM policy
# resource "aws_iam_policy" "secrets_policy" {
#   name = var.iam_policy_name

#   policy = jsonencode({
#     # copied the policy code from aws 
#     "Version": "2012-10-17",
#     "Statement": [
#         {
#             "Action": [
#                 "secretsmanager:*",
#                 "cloudformation:CreateChangeSet",
#                 "cloudformation:DescribeChangeSet",
#                 "cloudformation:DescribeStackResource",
#                 "cloudformation:DescribeStacks",
#                 "cloudformation:ExecuteChangeSet",
#                 "ec2:DescribeSecurityGroups",
#                 "ec2:DescribeSubnets",
#                 "ec2:DescribeVpcs",
#                 "kms:DescribeKey",
#                 "kms:ListAliases",
#                 "kms:ListKeys",
#                 "lambda:ListFunctions",
#                 "rds:DescribeDBClusters",
#                 "rds:DescribeDBInstances",
#                 "redshift:DescribeClusters",
#                 "tag:GetResources"
#             ],
#             "Effect": "Allow",
#             "Resource": "*"
#         },
#         {
#             "Action": [
#                 "lambda:AddPermission",
#                 "lambda:CreateFunction",
#                 "lambda:GetFunction",
#                 "lambda:InvokeFunction",
#                 "lambda:UpdateFunctionConfiguration"
#             ],
#             "Effect": "Allow",
#             "Resource": "arn:aws:lambda:*:*:function:SecretsManager*"
#         },
#         {
#             "Action": [
#                 "serverlessrepo:CreateCloudFormationChangeSet",
#                 "serverlessrepo:GetApplication"
#             ],
#             "Effect": "Allow",
#             "Resource": "arn:aws:serverlessrepo:*:*:applications/SecretsManager*"
#         },
#         {
#             "Action": [
#                 "s3:GetObject"
#             ],
#             "Effect": "Allow",
#             "Resource": [
#                 "arn:aws:s3:::awsserverlessrepo-changesets*",
#                 "arn:aws:s3:::secrets-manager-rotation-apps-*/*"
#             ]
#         }
#     ]
# })
# }

# # Create an IAM role
# resource "aws_iam_role" "secrets_role" {
#   name = var.role_name

#   assume_role_policy = jsonencode({
#     Version = "2012-10-17"
#     Statement = [
#       {
#         Effect = "Allow"
#         Principal = {
#           Service = "ec2.amazonaws.com"
#         }
#         Action = "sts:AssumeRole"
#       }
#     ]
#   })
# }

# # Attach the IAM policy to the IAM role
# resource "aws_iam_policy_attachment" "attach_secrets" {
#   name = "Policy Attachement"
#   policy_arn = aws_iam_policy.secrets_policy.arn
#   roles       = [aws_iam_role.secrets_role.name]
# }

# # Create an IAM instance profile
# resource "aws_iam_instance_profile" "secrets" {
#   name = var.instance_profile_name
#   role = aws_iam_role.secrets_role.name
# }

# locals {
#   inline_user_data = <<-EOT
#     #!/bin/bash
#     echo "${file("${path.module}/github_pat_secret.py")}" > ~/github_pat_secret.py
#     echo "${file("${path.module}/jenkins_login_secret.py")}" > ~/jenkins_login_secret.py
#     echo "${file("${path.module}/pypi_api_secret.py")}" > ~/pypi_api_secret.py
#     echo "${file("${path.module}/config.xml")}" > ~/config.xml
#     echo "${file("${path.module}/setup.groovy")}" > ~/setup.groovy
#     echo "${file("${path.module}/github_credentials.xml")}" > ~/github_credentials.xml
#   EOT

#   external_script = file("${path.module}/startup.sh")
# }

resource "aws_instance" "app_server" {
  # creates ec2 instance
  ami = "ami-053b0d53c279acc90"
  instance_type = "t2.micro"
  # key_name = "key"
  vpc_security_group_ids  = [aws_security_group.security.id]
  #iam_instance_profile = aws_iam_instance_profile.secrets.name
  tags = {
    Name = "KeySwitcheroo"
  }
  user_data = file("startup.sh")

  # connection {
  #   type        = "ssh"
  #   user        = "ubuntu"
  #   private_key = tls_private_key.pk.private_key_pem
  #   host        = self.public_ip
  # }

  # provisioner "remote-exec" {
  #   inline = [
  #     "/bin/sudo /bin/chmod 777 /"
  #   ]
  # }

  # provisioner "file" {
  #   source = "${path.module}/setup.groovy"
  #   destination = "/setup.groovy"
  # }

  # provisioner "file" {
  #   source = "${path.module}/config.xml"
  #   destination = "/config.xml"
  # }

  # provisioner "file" {
  #   source = "${path.module}/github_credentials.xml"
  #   destination = "/github_credentials.xml"
  # }
}
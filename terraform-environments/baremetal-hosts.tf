resource "aws_security_group" "allow_ingress" {
  name        = "allow_ingress"
  description = "Give correct security for baremetal hosts"
  #tanis vpc 
  # vpc_id      = "vpc-0bfb64215145a3e13"
  vpc_id      = "vpc-0698eb109e6e2afd5"


  ingress {
    from_port        = 22
    to_port          = 22
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
    Name = "allow_ingress"
  }
 }


# Generates a secure private key and encodes it as PEM
resource "tls_private_key" "key_pair" {
  algorithm = "RSA"
  rsa_bits  = 4096
}
# Create the Key Pair 
resource "aws_key_pair" "demo_key_pair" {
  key_name   = "linux-key-pair"  
  public_key = tls_private_key.key_pair.public_key_openssh
}
# Save file
resource "local_file" "ssh_key" {
  filename = "keys/${aws_key_pair.demo_key_pair.key_name}.pem"
  content  = tls_private_key.key_pair.private_key_pem
}


# Set permissions on the private key file
resource "null_resource" "set_permissions" {
  triggers = {
    ssh_key_filename = local_file.ssh_key.filename
  }
  provisioner "local-exec" {
    command = "chmod 400 ${local_file.ssh_key.filename}"
  }
}


locals {
    USERNAME = var.username
}

# role creation section

variable "instance_profile_name" {
  type    = string
  default = "secrets-manager"
}

variable "iam_policy_name" {
  # same name as aws's built in policy - not neccasary
  type    = string
  default = "SecretsManagerReadWrite"
}

variable "role_name" {
  # role is different than one that exists on aws
  type    = string
  default = "ec2-secrets-access-terraform-role"
}

# Create an IAM policy
resource "aws_iam_policy" "secrets_policy" {
  name = var.iam_policy_name

  policy = jsonencode({
    # copied the policy code from aws 
    "Version": "2012-10-17",
    "Statement": [
        {
            "Action": [
                "secretsmanager:*",
                "cloudformation:CreateChangeSet",
                "cloudformation:DescribeChangeSet",
                "cloudformation:DescribeStackResource",
                "cloudformation:DescribeStacks",
                "cloudformation:ExecuteChangeSet",
                "ec2:DescribeSecurityGroups",
                "ec2:DescribeSubnets",
                "ec2:DescribeVpcs",
                "kms:DescribeKey",
                "kms:ListAliases",
                "kms:ListKeys",
                "lambda:ListFunctions",
                "rds:DescribeDBClusters",
                "rds:DescribeDBInstances",
                "redshift:DescribeClusters",
                "tag:GetResources"
            ],
            "Effect": "Allow",
            "Resource": "*"
        },
        {
            "Action": [
                "lambda:AddPermission",
                "lambda:CreateFunction",
                "lambda:GetFunction",
                "lambda:InvokeFunction",
                "lambda:UpdateFunctionConfiguration"
            ],
            "Effect": "Allow",
            "Resource": "arn:aws:lambda:*:*:function:SecretsManager*"
        },
        {
            "Action": [
                "serverlessrepo:CreateCloudFormationChangeSet",
                "serverlessrepo:GetApplication"
            ],
            "Effect": "Allow",
            "Resource": "arn:aws:serverlessrepo:*:*:applications/SecretsManager*"
        },
        {
            "Action": [
                "s3:GetObject"
            ],
            "Effect": "Allow",
            "Resource": [
                "arn:aws:s3:::awsserverlessrepo-changesets*",
                "arn:aws:s3:::secrets-manager-rotation-apps-*/*"
            ]
        }
    ]
})
}

# Create an IAM role
resource "aws_iam_role" "secrets_role" {
  name = var.role_name

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })
}

# Attach the IAM policy to the IAM role
resource "aws_iam_policy_attachment" "attach_secrets" {
  name = "Policy Attachement"
  policy_arn = aws_iam_policy.secrets_policy.arn
  roles       = [aws_iam_role.secrets_role.name]
}

# Create an IAM instance profile
resource "aws_iam_instance_profile" "secrets" {
  name = var.instance_profile_name
  role = aws_iam_role.secrets_role.name
}



# create the hosts
resource "aws_instance" "baremetal-host-1" {
  ami = "ami-053b0d53c279acc90"
  instance_type = "t2.micro"     
  key_name      = aws_key_pair.demo_key_pair.key_name
  vpc_security_group_ids  =[aws_security_group.allow_ingress.id]
  iam_instance_profile = aws_iam_instance_profile.secrets.name
  tags = {
    Name = "host-1"
  }
     user_data = base64encode(templatefile("${path.module}/hosts-user-data.sh", {
      USERNAME=local.USERNAME
     }))

}

resource "aws_instance" "baremetal-host-2" {
  ami = "ami-053b0d53c279acc90"
  instance_type = "t2.micro"      
  key_name      = aws_key_pair.demo_key_pair.key_name
  vpc_security_group_ids  =[aws_security_group.allow_ingress.id]
  tags = {
    Name = "host-2"
  }
  user_data = base64encode(templatefile("${path.module}/hosts-user-data.sh", {
      USERNAME=local.USERNAME
     }))
}
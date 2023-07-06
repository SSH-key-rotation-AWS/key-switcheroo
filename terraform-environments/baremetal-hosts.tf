# resource "null_resource" "ssh_keygen" {
#   provisioner "local-exec" {
#     command = "rm keys/mykey keys/mykey.pub"
#     working_dir = "${path.module}"
#   }
#   provisioner "local-exec" {
#     command = "ssh-keygen -t rsa -b 1024 -f keys/mykey -N 'PASSWORD'"
#     working_dir = "${path.module}"
#   }
# }

# variable "key_pair_name" {
#   type    = string
#   default = "terraform key pair"
# }

# data "local_file" "example" {
#   filename = "keys/mykey.pub"
# }

# locals {
#   output = data.local_file.example.content
# }


resource "aws_security_group" "allow_ingress" {
  name        = "allow_ingress"
  description = "Give correct security for baremetal hosts"
  #tanis vpc = vpc-0bfb64215145a3e13
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











# resource "aws_key_pair" "demo_key_pair" {
#   key_name   = var.key_pair_name
#   # public_key = "${data.external.multiple_commands.result}"
#   public_key = "${local.output}"
# }


data "template_file" "user_data" {
  template = <<-EOT
    #!/bin/bash

    #add user
    sudo adduser ${var.username}

    # Service setup
    sudo yum update -y
    
    #install python3.11
    sudo yum install gcc openssl-devel bzip2-devel libffi-devel zlib-devel -y 
    wget https://www.python.org/ftp/python/3.11.4/Python-3.11.4.tgz 
    tar xzf Python-3.11.4.tgz 
    cd Python-3.11.4 
    sudo ./configure --enable-optimizations 
    sudo make altinstall 
    sudo rm -f /opt/Python-3.11.4.tgz 

    sudo yum install -y ssh python3.11-pip

    # test installation of pycryptome to ensure pip is installed 
    sudo pip3 install pycryptome

  EOT
}


resource "aws_instance" "baremetal-host-1" {
  ami = "ami-090e0fc566929d98b"
  instance_type = "t2.micro"      # Update with your desired instance type
  user_data = data.template_file.user_data.rendered
  key_name      = aws_key_pair.demo_key_pair.key_name
  vpc_security_group_ids  =[aws_security_group.allow_ingress.id]
  tags = {
    Name = "host-1"
  }
}

resource "aws_instance" "baremetal-host-2" {
  ami = "ami-090e0fc566929d98b"
  instance_type = "t2.micro"      # Update with your desired instance type
  user_data = data.template_file.user_data.rendered
  key_name      = aws_key_pair.demo_key_pair.key_name
  vpc_security_group_ids  =[aws_security_group.allow_ingress.id]
  tags = {
    Name = "host-2"
  }
}
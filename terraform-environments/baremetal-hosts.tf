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
  filename = "${aws_key_pair.demo_key_pair.key_name}.pem"
  content  = tls_private_key.key_pair.private_key_pem
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
    sudo apt-get update
    sudo apt-get install -y ssh python3.11 python3.11-pip

    # test installation of pycryptome to ensure pip is installed 
    sudo pip3 install pycryptome"

  EOT
}


resource "aws_instance" "baremetal-host-1" {
  ami = "ami-090e0fc566929d98b"
  instance_type = "t2.micro"      # Update with your desired instance type
  user_data = data.template_file.user_data.rendered
  key_name      = aws_key_pair.demo_key_pair.key_name
  tags = {
    Name = "host-1"
  }
}

resource "aws_instance" "baremetal-host-2" {
  ami = "ami-090e0fc566929d98b"
  instance_type = "t2.micro"      # Update with your desired instance type
  user_data = data.template_file.user_data.rendered
  key_name      = aws_key_pair.demo_key_pair.key_name
  tags = {
    Name = "host-2"
  }
}
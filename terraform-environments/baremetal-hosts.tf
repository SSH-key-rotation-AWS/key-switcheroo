# data "template_file" "user_data" {
#   template = file("../host_user_data.sh")
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
  tags = {
    Name = "host-1"
  }
}

resource "aws_instance" "baremetal-host-2" {
  ami = "ami-090e0fc566929d98b"
  instance_type = "t2.micro"      # Update with your desired instance type
  user_data = data.template_file.user_data.rendered
  tags = {
    Name = "host-2"
  }
}
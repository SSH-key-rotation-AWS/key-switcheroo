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

resource "aws_instance" "baremetal-host-1" {
  ami = "ami-053b0d53c279acc90"
  instance_type = "t2.micro"      # Update with your desired instance type
  user_data = file("hosts-user-data.sh")
  key_name      = aws_key_pair.demo_key_pair.key_name
  vpc_security_group_ids  =[aws_security_group.allow_ingress.id]
  tags = {
    Name = "host-1"
  }
}

resource "aws_instance" "baremetal-host-2" {
  ami = "ami-053b0d53c279acc90"
  instance_type = "t2.micro"      # Update with your desired instance type
  key_name      = aws_key_pair.demo_key_pair.key_name
  vpc_security_group_ids  =[aws_security_group.allow_ingress.id]
  tags = {
    Name = "host-2"
  }
      user_data = file("hosts-user-data.sh")
}
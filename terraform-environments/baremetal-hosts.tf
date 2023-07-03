
resource "aws_instance" "baremetal-host-1" {
  ami = "ami-090e0fc566929d98b"
  instance_type = "t2.micro"      # Update with your desired instance type
  # key_name      = "your_key_pair"  # Update with your EC2 key pair name
  tags = {
    Name = "test-instance"
  }
}

resource "aws_instance" "baremetal-host-2" {
  ami = "ami-090e0fc566929d98b"
  instance_type = "t2.micro"      # Update with your desired instance type
  # key_name      = "your_key_pair"  # Update with your EC2 key pair name
  tags = {
    Name = "test-instance-2"
  }
}
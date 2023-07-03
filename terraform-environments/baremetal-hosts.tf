data "template_file" "user_data" {
  template = file("../host_user_data.sh")
}

resource "aws_instance" "baremetal-host-1" {
  ami = "ami-090e0fc566929d98b"
  instance_type = "t2.micro"      # Update with your desired instance type
  user_data = data.template_file.user_data.rendered
  tags = {
    Name = "test-instance"
  }
}

resource "aws_instance" "baremetal-host-2" {
  ami = "ami-090e0fc566929d98b"
  instance_type = "t2.micro"      # Update with your desired instance type
  user_data = data.template_file.user_data.rendered
  tags = {
    Name = "test-instance-2"
  }
}
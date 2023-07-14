resource "aws_security_group" "security" {
  name        = "ec2_security"
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

resource "aws_instance" "app_server" {
  # creates ec2 instance
  ami = "ami-053b0d53c279acc90"
  instance_type = "t2.micro"
  vpc_security_group_ids  =[aws_security_group.security.id]
  tags = {
    Name = "KeySwitcheroo"
  }
  user_data = file("startup.sh")
} 
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.16"
    }
  }

  required_version = ">= 1.2.0"
}

provider "aws" {
    access_key = "${var.aws_access_key}"
    secret_key = "${var.aws_secret_key}"
    region = "${var.region}"
}

resource "aws_s3_bucket" "example" {
  bucket = "${var.bucket_name}"
    acl = "${var.acl_value}"   

#   tags = {
#     Name        = "My bucket"
#     Environment = "Dev"
#   }
 }


# module "s3" {
#     source = "<../s3_folder/bucket.tf>"
#     #bucket name should be unique
#     bucket_name = "<Bucket-name>"       
# }

# provider "aws" {
#     access_key = "${var.aws_access_key}"
#     secret_key = "${var.aws_secret_key}"
#     region = "${var.region}"
# }

# module "s3" {
#     source = "../s3_folder/bucket.tf"
#     #bucket name should be unique
#     bucket_name = "<production_bucket1>"       
# }

# resource "aws_instance" "app_server" {
#   ami           = "ami-090e0fc566929d98b"
#   instance_type = "t2.micro"

#   tags = {
#     Name = "TeamHenrique"
#   }
# }




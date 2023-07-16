terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.16"
    }
  }

  required_version = ">= 1.2.0"
}

# resource "random_id" "suffix" {
#   byte_length = 8
# }


provider "aws" {
    region = "${var.region}"
}

resource "aws_s3_bucket" "production" {
    # bucket = "production-bucket-${random_id.suffix.hex}"
  bucket = "production-bucket-key-switcheroo"
    # acl = "${var.acl_value}"   
    acl = "private"
 }

 resource "aws_s3_bucket" "testing" {
  bucket = "testing-bucket-key-switcheroo"
  # bucket = "testing-bucket-${random_id.2suffix.hex}"
    # acl = "${var.acl_value}"   
    acl = "private"
 }

# resource "aws_s3_bucket_versioning" "test-bucket-versioning" {
#   bucket = "testing-bucket-key-switcheroo"
#   versioning_configuration {
#   status = var.versioning
#   }
# }


# resource "aws_s3_bucket_versioning" "production-bucket-versioning" {
#   bucket = "production-bucket-key-switcheroo"
#   versioning_configuration {
#   status = var.versioning
#   }
# }
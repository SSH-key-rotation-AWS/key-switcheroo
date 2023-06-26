terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.16"
    }
  }

  required_version = ">= 1.2.0"
}

resource "random_id" "suffix" {
  byte_length = 8
}

provider "aws" {
    # access_key = "${var.aws_access_key}"
    # secret_key = "${var.aws_secret_key}"
    # shared_credentials_file = "/home/isaacsoffer/.aws/credentials"
    # shared_credentials_file = "${var.credentials_directory}/credentials"
    region = "${var.region}"
}

resource "aws_s3_bucket" "production" {
  bucket = "production-bucket-${random_id.suffix.hex}"
  # bucket = "${var.bucket_name}"
    acl = "${var.acl_value}"   
 }

 resource "aws_s3_bucket" "testing" {
  bucket = "testing-bucket-${random_id.suffix.hex}"
  # bucket = "${var.bucket_name}"
    acl = "${var.acl_value}"   
 }





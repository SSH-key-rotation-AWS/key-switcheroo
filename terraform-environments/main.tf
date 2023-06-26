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
    region = "${var.region}"
}

resource "aws_s3_bucket" "production" {
    bucket = "production-bucket-${random_id.suffix.hex}"
  # bucket = "production-bucket-team-henrique"
    acl = "${var.acl_value}"   
 }

 resource "aws_s3_bucket" "testing" {
  # bucket = "testing-bucket-team-henrique"
  bucket = "testing-bucket-${random_id.suffix.hex}"
    acl = "${var.acl_value}"   
 }

 
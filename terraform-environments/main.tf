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
    region = "${var.region}"
}

resource "aws_s3_bucket" "production" {
  bucket = "production-bucket-team-henrique"
    acl = "${var.acl_value}"   
 }

 resource "aws_s3_bucket" "testing" {
  bucket = "testing-bucket-team-henrique"
    acl = "${var.acl_value}"   
 }

 
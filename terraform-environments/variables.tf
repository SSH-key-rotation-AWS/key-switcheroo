# variable "bucket_name" {}

variable "acl_value" {

    default = "private"

}

# variable "aws_access_key" {}

# variable "aws_secret_key" {}

# variable "credentials_directory" {}

variable "region" {

    default = "us-east-1"

}

variable "versioning" {
type = string
description = "(Optional) A state of versioning."
default = "Disabled"
}
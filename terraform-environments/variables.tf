variable "acl_value" {
    default = "private"
}

variable "region" {
    default = "us-east-1"
}

variable "versioning" {
type = string
description = "(Optional) A state of versioning."
default = "Disabled"
}


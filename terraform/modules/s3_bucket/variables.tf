variable "bucket_name" {
  type        = string
  description = "The name of the S3 bucket"
}

variable "acl" {
  type        = string
  default     = "private"
  description = "The ACL to apply to the bucket"
}

variable "tags" {
  type        = map(string)
  default     = {}
  description = "Tags to assign to the bucket"
}

variable "table_name" {
  type        = string
  description = "Name of the DynamoDB table"
}

variable "hash_key" {
  type        = string
  description = "Hash key for the DynamoDB table"
}

variable "hash_key_type" {
  type        = string
  default     = "S" # String
  description = "Type of the hash key (S = String, N = Number, B = Binary)"
}

variable "sort_key" {
  type = object({
    name = string
    type = string
  })
  default = null
  description = "Sort key configuration for the DynamoDB table"
}


variable "sort_key_enabled" {
  type    = bool
  default = false
  description = "Flag to enable or disable sort key"
}

variable "billing_mode" {
  type    = string
  default = "PAY_PER_REQUEST"
  description = "Billing mode (PAY_PER_REQUEST or PROVISIONED)"
}

variable "ttl_attribute_name" {
  type        = string
  default     = ""
  description = "TTL attribute name (empty string to disable)"
}

variable "ttl_attribute_enabled" {
  type        = bool
  default     = false
  description = "Enable TTL on the table"
}

variable "tags" {
  type        = map(string)
  default     = {}
  description = "Tags to assign to the table"
}


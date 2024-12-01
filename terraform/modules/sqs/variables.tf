variable "queue_name" {
  type        = string
  description = "The name of the SQS queue"
}

variable "visibility_timeout" {
  type        = number
  description = "The visibility timeout for the queue in seconds"
  default     = 30
}

variable "message_retention" {
  type        = number
  description = "The message retention period for the queue in seconds"
  default     = 345600  # 4 days
}

variable "dlq_retention" {
  type        = number
  description = "The message retention period for the DLQ in seconds"
  default     = 604800  # 7 days
}

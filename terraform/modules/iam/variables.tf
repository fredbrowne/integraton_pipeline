variable "role_name" {
  type        = string
  description = "Name of the IAM role"
}

variable "sqs_queue_arn" {
  type        = string
  description = "ARN of the SQS queue"
}
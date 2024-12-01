variable "function_name" {
  type        = string
  description = "Name of the Lambda function"
}

variable "role_arn" {
  type        = string
  description = "IAM Role ARN for the Lambda"
}

variable "sqs_queue_url" {
  type        = string
  description = "SQS queue URL"
  default     = null
}

variable "lambda_zip_path" {
  type        = string
  description = "Path to the Lambda deployment package"
}

variable "max_batch_size" {
  type        = number
  default     = 100
}

variable "dynamo_table_name" {
  type        = string
  description = "Name of the DynamoDB table for storing enriched data"
  default     = null
}

variable "s3_bucket_name" {
  type        = string
  default     = null
  description = "The S3 bucket name for storing aggregated data (optional)"
}

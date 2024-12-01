variable "state_machine_name" {
  type        = string
  description = "Name of the Step Functions state machine"
}

variable "role_arn" {
  type        = string
  description = "IAM role for Step Functions"
}

variable "worker_lambda_arn" {
  type        = string
  description = "ARN of the worker Lambda"
}

variable "check_completion_lambda_arn" {
  type        = string
  description = "ARN of the completion-check Lambda"
}

variable "aggregation_lambda_arn" {
  type        = string
  description = "ARN of the aggregation Lambda"
}

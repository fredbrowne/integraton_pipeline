variable "api_name" {
  type        = string
  description = "Name of the API Gateway"
}

variable "routes" {
  description = "Map of routes to Lambda ARNs"
  type        = map(string)
}


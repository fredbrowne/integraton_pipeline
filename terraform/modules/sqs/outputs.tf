output "sqs_queue_url" {
  value = aws_sqs_queue.main_queue.id
}

output "sqs_queue_arn" {
  value = aws_sqs_queue.main_queue.arn
}

output "sqs_dlq_url" {
  value = aws_sqs_queue.dlq.id
}
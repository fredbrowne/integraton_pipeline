output "s3_aggregation_bucket_name" {
  value = aws_s3_bucket.this.bucket
}

output "s3_aggregation_bucket_arn" {
  value = aws_s3_bucket.this.arn
}
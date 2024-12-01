resource "aws_lambda_function" "this" {
  function_name = var.function_name
  role          = var.role_arn
  handler       = "app.lambda_handler"
  runtime       = "python3.9"
  timeout       = 10

  environment {
    variables = merge(
      {
        SQS_QUEUE_URL = var.sqs_queue_url
        MAX_BATCH_SIZE    = var.max_batch_size
      },
      var.sqs_queue_arn != null ? { SQS_QUEUE_ARN = var.sqs_queue_arn } : {},
      var.dynamo_table_name != null ? { DYNAMO_TABLE_NAME = var.dynamo_table_name } : {},
      var.s3_bucket_name != null ? { S3_BUCKET_NAME = var.s3_bucket_name } : {}
    )
  }


  filename         = var.lambda_zip_path
  source_code_hash = filebase64sha256(var.lambda_zip_path)
}

resource "aws_lambda_event_source_mapping" "sqs_trigger" {
  count             = var.function_name == "worker_lambda" ? 1 : 0
  event_source_arn  = var.sqs_queue_arn
  function_name     = aws_lambda_function.this.arn
  batch_size        = 10   # Adjust batch size as needed
  enabled           = true
}
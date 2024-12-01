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
      var.dynamo_table_name != null ? { DYNAMO_TABLE_NAME = var.dynamo_table_name } : {},
      var.s3_bucket_name != null ? { S3_BUCKET_NAME = var.s3_bucket_name } : {}
    )
  }


  filename         = var.lambda_zip_path
  source_code_hash = filebase64sha256(var.lambda_zip_path)
}


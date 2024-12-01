
module "api_gateway" {
  source   = "./modules/api_gateway"
  api_name = "ContactEnrichmentAPI"

  routes = {
    "POST /process"   = module.lambda_split_batches.lambda_arn
    "GET /status/{id}" = module.lambda_check_completion.lambda_arn
  }
}

module "sqs" {
  source               = "./modules/sqs"
  queue_name           = "split-batch-queue"
  visibility_timeout   = 30
  message_retention    = 345600
  dlq_retention        = 604800
}

module "lambda_split_batches" {
  source           = "./modules/lambda"
  function_name    = "split_batches"
  role_arn         = module.iam.lambda_role_arn
  sqs_queue_url    = module.sqs.sqs_queue_url
  lambda_zip_path  = "../lambdas/deployment/split_batches.zip"
  max_batch_size   = 100
}

module "lambda_worker" {
  source            = "./modules/lambda"
  function_name     = "worker_lambda"
  role_arn          = module.iam.lambda_role_arn
  sqs_queue_url     = module.sqs.sqs_queue_url
  lambda_zip_path   = "../lambdas/deployment/worker.zip"
  dynamo_table_name = module.dynamodb.dynamo_table_name
}

module "lambda_aggregation" {
  source           = "./modules/lambda"
  function_name    = "aggregation_lambda"
  role_arn         = module.iam.lambda_role_arn
  lambda_zip_path  = "../lambdas/deployment/aggregate_results.zip"
  sqs_queue_url    = module.sqs.sqs_queue_url
  dynamo_table_name = module.dynamodb.dynamo_table_name
  s3_bucket_name    = module.s3_aggregation_output.s3_aggregation_bucket_name
}

module "lambda_check_completion" {
  source           = "./modules/lambda"
  function_name    = "check_completion_lambda"
  role_arn         = module.iam.lambda_role_arn
  lambda_zip_path  = "../lambdas/deployment/check_completion.zip"
}


module "dynamodb" {
  source       = "./modules/dynamodb"
  table_name   = "EnrichedData"
  hash_key     = "id"
  billing_mode = "PAY_PER_REQUEST"
  tags = {
    Environment = "dev"
  }
}

module "step_functions" {
  source                      = "./modules/step_functions"
  state_machine_name          = "DataProcessingStateMachine"
  role_arn                    = module.iam.step_functions_role_arn
  worker_lambda_arn           = module.lambda_worker.lambda_arn
  check_completion_lambda_arn = module.lambda_check_completion.lambda_arn
  aggregation_lambda_arn      = module.lambda_aggregation.lambda_arn
}


module "s3_aggregation_output" {
  source      = "./modules/s3_bucket"
  bucket_name = "data-enrichment-aggregated-output"
  acl         = "private"
  tags = {
    Environment = "dev"
  }
}

module "iam" {
  source         = "./modules/iam"
  role_name      = "lambda_execution_role"
  sqs_queue_arn  = module.sqs.sqs_queue_arn
}
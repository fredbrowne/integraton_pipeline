resource "aws_sfn_state_machine" "this" {
  name     = var.state_machine_name
  role_arn = var.role_arn
  definition = jsonencode({
    Comment: "Orchestrate batch processing and aggregation",
    StartAt: "Initialize",
    States: {
      "Initialize": {
        "Type": "Pass",
        "Result": {
          "request_id": "uuid-12345",
          "expected_batches": 10
        },
        "ResultPath": "$.metadata",
        "Next": "Process Batches"
      },
      "Process Batches": {
        "Type": "Map",
        "ItemsPath": "$.batches",
        "Iterator": {
          "StartAt": "Invoke Worker",
          "States": {
            "Invoke Worker": {
              "Type": "Task",
              "Resource": var.worker_lambda_arn,
              "Next": "Worker Completed"
            },
            "Worker Completed": {
              "Type": "Pass",
              "End": true
            }
          }
        },
        "Next": "Wait for Completion"
      },
      "Wait for Completion": {
        "Type": "Wait",
        "Seconds": 10,
        "Next": "Check Completion"
      },
      "Check Completion": {
        "Type": "Task",
        "Resource": var.check_completion_lambda_arn,
        "ResultPath": "$.completion_status",
        "Next": "Aggregation Decision"
      },
      "Aggregation Decision": {
        "Type": "Choice",
        "Choices": [
          {
            "Variable": "$.completion_status",
            "StringEquals": "completed",
            "Next": "Run Aggregation"
          }
        ],
        "Default": "Wait for Completion"
      },
      "Run Aggregation": {
        "Type": "Task",
        "Resource": var.aggregation_lambda_arn,
        "End": true
      }
    }
  })
}

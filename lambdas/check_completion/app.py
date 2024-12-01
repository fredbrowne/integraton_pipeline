import os
import boto3
import json
from botocore.exceptions import ClientError

dynamodb = boto3.resource("dynamodb")
control_table_name = os.environ.get("CONTROL_TABLE_NAME", "DefaultControlTable")

def lambda_handler(event, context):
    """
    Check if all batches for a request are processed.
    """
    try:
        request_id = event.get("request_id")
        if not request_id:
            raise KeyError("Missing 'request_id' in event payload.")

        table = dynamodb.Table(control_table_name)
        response = table.get_item(Key={"request_id": request_id})

        item = response.get("Item")
        if not item:
            return {
                "statusCode": 404,
                "body": json.dumps({"error": f"Request ID '{request_id}' not found."}),
            }

        expected_batches = int(item["expected_batches"])
        processed_batches = int(item["processed_batches"])
        status = "completed" if processed_batches >= expected_batches else "incomplete"

        return {
            "statusCode": 200,
            "body": json.dumps({"status": status}),
        }

    except KeyError as e:
        print(f"KeyError: {str(e)}")
        return {
            "statusCode": 400,
            "body": json.dumps({"error": str(e)}),
        }

    except ClientError as e:
        print(f"ClientError: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "DynamoDB client error."}),
        }

    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": f"Internal server error: {str(e)}"}),
        }

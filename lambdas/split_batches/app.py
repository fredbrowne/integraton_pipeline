import os
import json

from .batch_splitter import BatchSplitter
from .sqs_queue import SQSQueue
from .control_table import DynamoDBControlTable
from .request_processor import RequestProcessor


def lambda_handler(event, context):
    """
    Main Lambda handler function.
    Args:
        event (dict): The Lambda event payload.
        context (LambdaContext): Runtime information for the Lambda function.
    Returns:
        dict: HTTP response indicating success or failure.
    """
    try:
        payload = json.loads(event["body"])
        batch_splitter = BatchSplitter(batch_size=100)
        sqs_queue = SQSQueue(queue_url=os.environ["SQS_QUEUE_URL"])
        dynamodb_table = DynamoDBControlTable(table_name=os.environ["DYNAMO_TABLE_NAME"])

        processor = RequestProcessor(
            sqs_queue=sqs_queue, 
            batch_splitter=batch_splitter,
            dynamodb_table=dynamodb_table
            )

        result = processor.process(payload)

        return {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "message": "Contacts successfully split into batches and queued.",
                    **result,
                }
            ),
        }

    except KeyError as e:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": f"Missing field: {str(e)}"}),
        }

    except Exception as e:
        print(f"Error: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Internal server error"}),
        }
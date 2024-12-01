import json
import os
from .batch_processor import BatchProcessor
from .dynamodb import DynamoDBClient
from .provider_factory import ProviderFactory

# Initialize components
dynamo_client = DynamoDBClient(table_name=os.environ["DYNAMO_TABLE_NAME"])
provider_factory = ProviderFactory()
batch_processor = BatchProcessor(dynamo_client=dynamo_client, provider_factory=provider_factory)

def lambda_handler(event, context):
    """
    Main Lambda handler for processing SQS messages.
    """
    try:
        for record in event["Records"]:
            body = json.loads(record["body"])
            batch = body["batch"]

            batch_processor.process_batch(batch)
    except Exception as e:
        print(f"Error processing SQS message: {e}")
        raise

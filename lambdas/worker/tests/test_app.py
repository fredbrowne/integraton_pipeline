import json
import pytest
from moto import mock_aws
import boto3
from lambdas.worker.app import lambda_handler
from lambdas.worker.dynamodb import DynamoDBClient

@pytest.fixture
def dynamodb_setup(monkeypatch):
    """
    Mock DynamoDB setup for testing.
    """
    with mock_aws():
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        table_name = "EnrichedData"

        # Create the mock table
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST",
        )

        monkeypatch.setenv("DYNAMO_TABLE_NAME", table_name)
        yield {
            "table_name": table_name,
            "table": table,
        }


@pytest.fixture
def sqs_setup(monkeypatch):
    """
    Mock SQS setup for testing.
    """
    with mock_aws():
        sqs = boto3.client("sqs", region_name="us-east-1")
        queue = sqs.create_queue(QueueName="test-queue")
        queue_url = queue["QueueUrl"]

        # Mock the environment variable
        monkeypatch.setenv("SQS_QUEUE_URL", queue_url)

        yield {
            "queue_url": queue_url,
            "sqs_client": sqs,
        }


def test_lambda_handler(dynamodb_setup, sqs_setup):
    """
    Test the Lambda handler function.
    """
    # Mock SQS payload
    sqs_setup["sqs_client"].send_message(
        QueueUrl=sqs_setup["queue_url"],
        MessageBody=json.dumps(
            {
                "batch": [
                    {"id": "1", "first_name": "John", "last_name": "Doe", "company_domain": "example.com"},
                    {"id": "2", "first_name": "Jane", "last_name": "Smith", "company_domain": "example.org"},
                ]
            }
        ),
    )

    # Mock event
    mock_event = {
        "Records": [
            {
                "body": json.dumps(
                    {
                        "batch": [
                            {"id": "1", "first_name": "John", "last_name": "Doe", "company_domain": "example.com"},
                            {"id": "2", "first_name": "Jane", "last_name": "Smith", "company_domain": "example.org"},
                        ]
                    }
                )
            }
        ]
    }

    # Call the Lambda handler
    lambda_handler(mock_event, None)

    # Verify data in DynamoDB
    table = dynamodb_setup["table"]
    response = table.scan()
    items = response["Items"]

    assert len(items) == 2
    assert any(item["professional_email"] == "john.doe@example.com" for item in items)
    assert any(item["professional_email"] == "jane.smith@example.org" for item in items)

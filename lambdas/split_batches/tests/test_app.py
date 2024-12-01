import json
import pytest
from moto import mock_aws
import boto3
from lambdas.split_batches import app


@pytest.fixture
def aws_setup(monkeypatch):
    """
    Mock AWS setup for testing.
    - Creates a mock SQS queue and DynamoDB table.
    - Sets the environment variables for the Lambda function.
    """
    with mock_aws():
        # Mock SQS setup
        sqs = boto3.client("sqs", region_name="us-east-1")
        queue = sqs.create_queue(QueueName="test-queue")
        queue_url = queue["QueueUrl"]

        # Mock DynamoDB setup
        dynamodb = boto3.client("dynamodb", region_name="us-east-1")
        table_name = "ControlTable"
        dynamodb.create_table(
            TableName=table_name,
            KeySchema=[{"AttributeName": "request_id", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "request_id", "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST",
        )

        # Set environment variables
        monkeypatch.setenv("SQS_QUEUE_URL", queue_url)
        monkeypatch.setenv("DYNAMO_TABLE_NAME", table_name)

        yield {
            "queue_url": queue_url,
            "sqs_client": sqs,
            "dynamodb_client": dynamodb,
            "table_name": table_name,
        }


def test_lambda_handler(aws_setup):
    """
    Test the Lambda handler function.
    """
    # Mock event payload
    mock_event = {
        "body": json.dumps(
            {
                "contacts": [
                    {"first_name": "John", "last_name": "Doe", "company_domain": "mycompany.com"},
                    {"first_name": "Jane", "last_name": "Smith", "company_domain": "notmycompany.com"},
                ]
            }
        )
    }

    # Call the Lambda handler
    response = app.lambda_handler(mock_event, None)

    # Assert the response
    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert body["message"] == "Contacts successfully split into batches and queued."
    assert "request_id" in body
    assert body["total_batches"] == 1

    # Check if the SQS queue received the messages
    messages = aws_setup["sqs_client"].receive_message(
        QueueUrl=aws_setup["queue_url"],
        MaxNumberOfMessages=10,
    )
    assert "Messages" in messages
    assert len(messages["Messages"]) == 1
    message_body = json.loads(messages["Messages"][0]["Body"])
    assert "request_id" in message_body
    assert "batch" in message_body
    assert len(message_body["batch"]) == 2

    # Check DynamoDB initialization
    dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
    table = dynamodb.Table(aws_setup["table_name"])
    response = table.get_item(Key={"request_id": body["request_id"]})

    assert "Item" in response
    item = response["Item"]
    assert item["request_id"] == body["request_id"]
    assert item["expected_batches"] == 1
    assert item["processed_batches"] == 0

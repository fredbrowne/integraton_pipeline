import json
import pytest
from moto import mock_aws
import boto3
from lambdas.check_completion.app import lambda_handler


@pytest.fixture
def dynamodb_setup(monkeypatch):
    """
    Sets up a mock DynamoDB table for the control table.
    """
    with mock_aws():
        # Create DynamoDB resource
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        control_table_name = "ControlTable"

        # Create the control table
        table = dynamodb.create_table(
            TableName=control_table_name,
            KeySchema=[{"AttributeName": "request_id", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "request_id", "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST",
        )

        # Wait for table creation
        table.meta.client.get_waiter("table_exists").wait(TableName=control_table_name)

        # Seed the table
        table.put_item(
            Item={
                "request_id": "uuid-12345",
                "expected_batches": 10,
                "processed_batches": 10,
            }
        )
        table.put_item(
            Item={
                "request_id": "uuid-67890",
                "expected_batches": 10,
                "processed_batches": 5,
            }
        )

        # Set environment variable
        monkeypatch.setenv("CONTROL_TABLE_NAME", control_table_name)

        yield table

def test_lambda_handler_completed(dynamodb_setup):
    """
    Test when all batches are completed.
    """
    event = {"request_id": "uuid-12345"}
    response = lambda_handler(event, None)

    # Assert completed status
    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert body["status"] == "completed"

def test_lambda_handler_incomplete(dynamodb_setup):
    """
    Test when batches are incomplete.
    """
    event = {"request_id": "uuid-67890"}
    response = lambda_handler(event, None)

    # Assert incomplete status
    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert body["status"] == "incomplete"

def test_lambda_handler_missing_request_id():
    """
    Test when request_id is missing in the event payload.
    """
    event = {}
    response = lambda_handler(event, None)

    # Assert bad request
    assert response["statusCode"] == 400
    body = json.loads(response["body"])
    assert "error" in body
    assert "Missing 'request_id'" in body["error"]

def test_lambda_handler_not_found(dynamodb_setup):
    """
    Test when request_id is not found in the control table.
    """
    event = {"request_id": "non-existent-id"}
    response = lambda_handler(event, None)

    # Assert not found
    assert response["statusCode"] == 404
    body = json.loads(response["body"])
    assert "error" in body
    assert "not found" in body["error"]

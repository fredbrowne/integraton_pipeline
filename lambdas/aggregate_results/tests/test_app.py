import json
import pytest
import boto3
from moto import mock_aws
from lambdas.aggregate_results.app import lambda_handler


@pytest.fixture
def aws_setup(monkeypatch):
    """
    Sets up mock DynamoDB and S3 services for testing.
    """
    with mock_aws():
        # Mock DynamoDB
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        table_name = "EnrichedData"
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[{"AttributeName": "request_id", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "request_id", "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST",
        )

        # Wait for the table to be active
        table.meta.client.get_waiter("table_exists").wait(TableName=table_name)

        # Seed the table
        table.put_item(
            Item={
                "request_id": "uuid-12345",
                "id": "batch-1",
                "data": {"name": "John Doe", "email": "john.doe@example.com"},
            }
        )
        table.put_item(
            Item={
                "request_id": "uuid-12345",
                "id": "batch-2",
                "data": {"name": "Jane Smith", "email": "jane.smith@example.com"},
            }
        )

        # Mock S3
        s3 = boto3.client("s3", region_name="us-east-1")
        bucket_name = "data-enrichment-aggregated-output"
        s3.create_bucket(Bucket=bucket_name)

        # Set environment variables
        monkeypatch.setenv("DYNAMO_TABLE_NAME", table_name)
        monkeypatch.setenv("S3_BUCKET_NAME", bucket_name)

        yield {"table_name": table_name, "bucket_name": bucket_name}


def test_lambda_handler_success(aws_setup):
    """
    Test aggregation and file upload when all data is present.
    """
    event = {"request_id": "uuid-12345"}
    response = lambda_handler(event, None)

    # Assert the response
    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert "url" in body
    assert body["message"] == "Aggregation successful"

def test_lambda_handler_no_data(aws_setup):
    """
    Test the case where no data is available for the given request_id.
    """
    event = {"request_id": "uuid-nonexistent"}
    response = lambda_handler(event, None)

    # Assert the response
    assert response["statusCode"] == 404
    body = json.loads(response["body"])
    assert "error" in body
    assert "No data found for request_id" in body["error"]

def test_lambda_handler_missing_request_id(aws_setup):
    """
    Test the case where the request_id is missing from the event payload.
    """
    event = {}
    response = lambda_handler(event, None)

    # Assert the response
    assert response["statusCode"] == 400
    body = json.loads(response["body"])
    assert "error" in body
    assert "Missing 'request_id'" in body["error"]


def test_lambda_handler_dynamodb_error(monkeypatch, aws_setup):
    """
    Test handling of a DynamoDB client error.
    """
    def mock_query(*args, **kwargs):
        print("Mocked query triggered")
        raise boto3.exceptions.Boto3Error("DynamoDB query failed.")

    table_mock = boto3.resource("dynamodb").Table(aws_setup["table_name"])
    monkeypatch.setattr("lambdas.aggregate_results.app.dynamodb.Table", lambda table_name: table_mock)
    monkeypatch.setattr(table_mock, "query", mock_query)

    event = {"request_id": "uuid-12345"}
    response = lambda_handler(event, None)

    # Assert the response
    assert response["statusCode"] == 500
    body = json.loads(response["body"])
    assert "error" in body
    assert "DynamoDB query failed." in body["error"]



def test_lambda_handler_s3_error(monkeypatch, aws_setup):
    """
    Test handling of an S3 upload error.
    """
    def mock_put_object(*args, **kwargs):
        print("Mocked S3 put_object triggered")
        raise boto3.exceptions.Boto3Error("S3 upload failed.")

    # Mock the S3 client globally in the Lambda
    monkeypatch.setattr("lambdas.aggregate_results.app.s3_client.put_object", mock_put_object)

    event = {"request_id": "uuid-12345"}
    response = lambda_handler(event, None)

    # Assert the response
    assert response["statusCode"] == 500
    body = json.loads(response["body"])
    assert "error" in body
    assert "S3 upload failed" in body["error"]


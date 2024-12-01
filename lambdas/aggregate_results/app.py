import os
import boto3
import json
from botocore.exceptions import ClientError

# Initialize AWS resources
dynamodb = boto3.resource("dynamodb")
s3_client = boto3.client("s3")

# Environment variables
table_name = os.environ.get("DYNAMO_TABLE_NAME", "EnrichedData")
bucket_name = os.environ.get("S3_BUCKET_NAME", "data-enrichment-aggregated-output")


def fetch_data_from_dynamodb(request_id):
    """
    Fetch all processed items for a given request_id from DynamoDB.
    """
    table = dynamodb.Table(table_name)
    try:
        # Query DynamoDB for items with the specified request_id
        response = table.query(
            KeyConditionExpression=boto3.dynamodb.conditions.Key("request_id").eq(request_id)
        )
        return response.get("Items", [])
    except ClientError as e:
        print(f"Error fetching data from DynamoDB: {e}")
        raise


def upload_to_s3(file_content, file_name):
    """
    Upload the aggregated file to S3.
    """
    try:
        s3_client.put_object(
            Bucket=bucket_name,
            Key=file_name,
            Body=file_content,
            ContentType="application/json",
        )
        # Generate pre-signed URL for the uploaded file
        return s3_client.generate_presigned_url(
            "get_object", Params={"Bucket": bucket_name, "Key": file_name}, ExpiresIn=3600
        )
    except ClientError as e:
        print(f"Error uploading to S3: {e}")
        raise


def lambda_handler(event, context):
    """
    Aggregate data and upload to S3.
    """
    try:
        # Extract request_id from event
        request_id = event.get("request_id")
        if not request_id:
            raise KeyError("Missing 'request_id' in event payload.")

        # Fetch data from DynamoDB
        print(f"Fetching data for request_id: {request_id}")
        data = fetch_data_from_dynamodb(request_id)
        if not data:
            return {
                "statusCode": 404,
                "body": json.dumps({"error": f"No data found for request_id '{request_id}'"}),
            }

        # Aggregate data into a single file (JSON format for simplicity)
        aggregated_content = json.dumps(data, indent=4)
        file_name = f"{request_id}_aggregated.json"

        # Upload aggregated file to S3
        print(f"Uploading aggregated file to S3 bucket: {bucket_name}")
        presigned_url = upload_to_s3(aggregated_content, file_name)

        # Return the pre-signed URL
        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Aggregation successful", "url": presigned_url}),
        }

    except KeyError as e:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": str(e)}),
        }
    except Exception as e:
        print(f"Error in aggregation: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)}),  # Include the actual error message
        }

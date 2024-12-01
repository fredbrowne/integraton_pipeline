import boto3

class DynamoDBControlTable:
    """
    A class to handle DynamoDB interactions for the control table.
    """

    def __init__(self, table_name):
        """
        Initialize the DynamoDB client and table.
        Args:
            table_name (str): The name of the DynamoDB table.
        """
        self.table_name = table_name
        self.dynamodb = boto3.resource("dynamodb")
        self.table = self.dynamodb.Table(table_name)

    def initialize_request(self, request_id, total_batches):
        """
        Initialize a record in the control table.
        Args:
            request_id (str): The unique ID for the request.
            total_batches (int): The total number of batches for the request.
        """
        self.table.put_item(
            Item={
                "request_id": request_id,
                "expected_batches": total_batches,
                "processed_batches": 0
            }
        )

import boto3

class DynamoDBClient:
    """
    Handles interactions with the DynamoDB table.
    """

    def __init__(self, table_name):
        self.table_name = table_name
        self.dynamodb = boto3.resource("dynamodb")
        self.table = self.dynamodb.Table(table_name)

    def save_records(self, records):
        """
        Save a list of records to DynamoDB.
        """
        for record in records:
            self.table.put_item(Item=record)

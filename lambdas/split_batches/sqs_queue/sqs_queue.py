import json
import boto3

class SQSQueue:
    """
    A class to interact with an SQS queue.
    """
    def __init__(self, queue_url):
        """
        Initializes the SQSQueue instance.
        Args:
            queue_url (str): The URL of the SQS queue.
        """
        self.queue_url = queue_url
        self.sqs_client = boto3.client("sqs")

    def send_message(self, batch, request_id, batch_id):
        """
        Sends a batch of contacts to the SQS queue.
        Args:
            batch (list): List of contacts in the batch.
            request_id (str): Unique identifier for the request.
            batch_id (int): Identifier for the current batch.
        """
        message = {
            "request_id": request_id,
            "batch_id": batch_id,
            "batch": batch,
        }
        self.sqs_client.send_message(
            QueueUrl=self.queue_url,
            MessageBody=json.dumps(message),
        )
import uuid

class RequestProcessor:
    """
    Processes the incoming request to split and enqueue contacts.
    """

    def __init__(self, sqs_queue, batch_splitter, dynamodb_table):
        """
        Initializes the RequestProcessor instance.
        Args:
            sqs_queue (SQSQueue): Instance of SQSQueue.
            batch_splitter (BatchSplitter): Instance of BatchSplitter.
            dynamodb_table (DynamoDBControlTable): Instance of DynamoDBControlTable.
        """
        self.sqs_queue = sqs_queue
        self.batch_splitter = batch_splitter
        self.dynamodb_table = dynamodb_table

    def process(self, payload):
        """
        Processes the incoming request.
        Splits the contacts into batches, sends them to SQS, and initializes the DynamoDB control table.
        Args:
            payload (dict): The incoming payload containing contacts.
        Returns:
            dict: Metadata about the processed request.
        """
        # Generate a unique request ID
        request_id = str(uuid.uuid4())

        # Split contacts into batches
        contacts = payload["contacts"]
        batches = list(self.batch_splitter.split(contacts))
        total_batches = len(batches)

        # Initialize DynamoDB record for the request
        self.dynamodb_table.initialize_request(request_id, total_batches)

        # Send each batch to the SQS queue
        for batch_id, batch in enumerate(batches, start=1):
            self.sqs_queue.send_message(batch, request_id, batch_id)

        return {
            "request_id": request_id,
            "total_batches": total_batches,
        }

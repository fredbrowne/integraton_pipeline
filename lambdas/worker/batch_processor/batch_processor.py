class BatchProcessor:
    """
    Processes a batch of records, enriches them, and stores them in DynamoDB.
    """

    def __init__(self, dynamo_client, provider_factory):
        self.dynamo_client = dynamo_client
        self.provider_factory = provider_factory

    def process_batch(self, batch):
        """
        Enrich and store a batch of records.
        """
        enriched_records = []
        for record in batch:
            # Fetch the provider (currently one, but scalable)
            provider = self.provider_factory.get_provider("default")
            enriched_record = provider.enrich_record(record)
            enriched_records.append(enriched_record)

        # Store enriched records in DynamoDB
        self.dynamo_client.save_records(enriched_records)

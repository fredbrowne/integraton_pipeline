class DataProvider:
    """
    Fetches enriched data for records.
    """

    def enrich_record(self, record):
        """
        Simulate data enrichment for a record.
        """
        # Simulate enriching the record
        enriched_record = record.copy()
        enriched_record["professional_email"] = f"{record['first_name'].lower()}.{record['last_name'].lower()}@{record['company_domain']}"
        return enriched_record

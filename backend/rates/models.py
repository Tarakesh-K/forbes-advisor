import uuid
from django.db import models


class Rate(models.Model):
    """
    Stores financial rate data as an immutable ledger.
    Uniqueness is tied to the Transaction (raw_response_id), not the Data.
    """

    # --- Core Data ---
    rate_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    provider = models.CharField(max_length=255)
    rate_type = models.CharField(max_length=255, db_index=True)
    rate_value = models.DecimalField(max_digits=10, decimal_places=6)
    currency = models.CharField(max_length=10, default="USD")

    # --- Temporal Data ---
    effective_date = models.DateField(db_index=True)
    ingestion_ts = models.DateTimeField(db_index=True)  # Source Time
    sys_ingested_ts = models.DateTimeField(db_index=True)  # System Time

    # --- The Only Unique Constraint ---
    # We remove the default=uuid.uuid4 so we are forced to use the
    # ID provided in the Parquet file.
    raw_response_id = models.UUIDField(unique=True, db_index=True, editable=False)

    # --- Traceability ---
    source_url = models.URLField(max_length=500, blank=True, null=True)
    raw_data_snapshot = models.JSONField(null=True)

    class Meta:
        db_table = "rates"
        ordering = ["-effective_date", "-sys_ingested_ts"]

        indexes = [
            # Efficient lookup for the "Latest" version of a rate
            models.Index(
                fields=["provider", "rate_type", "-effective_date", "-sys_ingested_ts"],
                name="provider_rate_lookup_idx",
            ),
        ]

    def __str__(self):
        return f"{self.provider} ({self.rate_type}): {self.rate_value}"

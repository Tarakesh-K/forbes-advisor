import os
import math
from utils.json_converter import to_json_safe
import pyarrow.parquet as pq
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from rates.models import Rate
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Streams Parquet data into the database.
    Allows different values for the same day (History) but blocks
    identical records (Idempotency).
    """

    help = "Ingests interest rate data with full audit history."

    def handle(self, *args, **options):
        cache_key = os.getenv("RATE_CACHE_KEY", "rates_data_latest_master")

        try:
            file_path = os.path.join(settings.BASE_DIR, "seeds", "rates_seed.parquet")
            BATCH_SIZE = int(os.getenv("SEED_BATCH_SIZE", 5000))

            if not os.path.exists(file_path):
                self.stdout.write(self.style.ERROR(f"File not found: {file_path}"))
                return

            # Our System 'Sync' Timestamp (The Batch ID)
            sys_now = timezone.now()

            parquet_file = pq.ParquetFile(file_path)
            total_rows = parquet_file.metadata.num_rows

            self.stdout.write(
                self.style.SUCCESS(f"Starting ingestion of {total_rows:,} rows...")
            )
            self.stdout.write(f"System Timestamp: {sys_now}")

            processed_count = 0

            for batch in parquet_file.iter_batches(batch_size=BATCH_SIZE):
                data_list = batch.to_pydict()
                rows_to_create = []
                batch_len = len(batch)

                for i in range(batch_len):
                    # Extract raw row
                    raw_row = {k: v[i] for k, v in data_list.items()}

                    # 1. Capture the USER provided timestamp from the file
                    # If the file's 'ingestion_ts' is missing, we fallback to our sys_now
                    user_ts = raw_row.get("ingestion_ts") or sys_now

                    # Ensure user_ts is timezone-aware (fixes naive datetime warning)
                    if user_ts and hasattr(user_ts, "tzinfo"):
                        if user_ts.tzinfo is None:
                            user_ts = timezone.make_aware(user_ts)

                    # 2. Extract and sanitize values
                    rate_val = raw_row.get("rate_value")
                    safe_rate = (
                        0
                        if (
                            rate_val is None
                            or (isinstance(rate_val, float) and math.isnan(rate_val))
                        )
                        else rate_val
                    )

                    provider_raw = raw_row.get("provider")
                    type_raw = raw_row.get("rate_type")

                    provider = str(provider_raw).strip().lower() if provider_raw else ""
                    r_type = str(type_raw).strip().lower() if type_raw else ""
                    eff_date = raw_row.get("effective_date")

                    if (
                        not provider
                        or not r_type
                        or not eff_date
                        or not raw_row.get("raw_response_id")
                    ):
                        continue

                    # 3. Build the Model Instance
                    rows_to_create.append(
                        Rate(
                            provider=provider,
                            rate_type=r_type,
                            rate_value=safe_rate,
                            effective_date=eff_date,
                            ingestion_ts=user_ts,  # User's "Source" TS
                            sys_ingested_ts=sys_now,  # Our "System" TS
                            currency=raw_row.get("currency", "USD"),
                            source_url=raw_row.get("source_url"),
                            raw_response_id=raw_row.get("raw_response_id"),
                            raw_data_snapshot=to_json_safe(raw_row),
                        )
                    )

                # --- THE SENIOR IDEMPOTENT UPSERT ---
                with transaction.atomic():
                    Rate.objects.bulk_create(
                        rows_to_create,
                        # 1. These fields must match your models.UniqueConstrainjt exactly
                        update_conflicts=True,
                        unique_fields=["raw_response_id"],
                        # 2. These fields get updated if the record already exists
                        # (e.g. updating our system sync time or the audit snapshot)
                        update_fields=[
                            "provider",
                            "rate_type",
                            "rate_value",
                            "effective_date",
                            "ingestion_ts",
                            "sys_ingested_ts",
                            "raw_data_snapshot",
                            "source_url",
                            "currency",
                        ],
                    )

                processed_count += batch_len
                self.stdout.write(f"Processed {processed_count:,} / {total_rows:,}...")

            self.stdout.write(
                self.style.SUCCESS("\nIngestion complete with History tracking.")
            )

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"\nIngestion failed: {e}"))
            raise e

        finally:
            # THIS RUNS NO MATTER WHAT (Success or Error)
            try:
                deleted = cache.delete(cache_key)
                # Also consider cache.clear() if you have multiple dependent keys
                logger.info(
                    f"Final cache invalidation",
                    extra={"cache_key": cache_key, "deleted": deleted},
                )
                self.stdout.write(f"Final Cache Clean: {deleted} (key: {cache_key})")
            except Exception as cache_err:
                logger.error(f"Final cache delete failed: {cache_err}")

import pytest
from unittest.mock import patch, MagicMock
from django.core.management import call_command
from rates.models import Rate
import io


def make_mock_parquet(rows: dict, num_rows: int = None):
    """Helper: builds a mock ParquetFile from a row dict"""
    mock_batch = MagicMock()
    mock_batch.to_pydict.return_value = rows
    mock_batch.__len__.return_value = num_rows or len(next(iter(rows.values())))

    mock_instance = MagicMock()
    mock_instance.metadata.num_rows = mock_batch.__len__.return_value
    mock_instance.iter_batches.return_value = [mock_batch]
    return mock_instance


VALID_ROW = {
    "provider": ["Chase"],
    "rate_type": ["savings"],
    "rate_value": [0.05],
    "effective_date": ["2026-04-01"],
    "raw_response_id": ["550e8400-e29b-41d4-a716-446655440000"],
    "ingestion_ts": ["2026-04-01T10:00:00Z"],
    "currency": ["USD"],
    "source_url": ["https://chase.com/rates"],
}


@pytest.mark.django_db
class TestSeedDataCommand:

    @patch("rates.management.commands.seed_data.pq.ParquetFile")
    @patch("rates.management.commands.seed_data.os.path.exists")
    def test_seed_data_ingestion(self, mock_exists, mock_parquet_class):
        """1. Happy Path: Valid row is created with correct field normalisation"""
        mock_exists.return_value = True
        mock_parquet_class.return_value = make_mock_parquet(VALID_ROW)

        call_command("seed_data")

        assert Rate.objects.count() == 1
        rate = Rate.objects.get(raw_response_id="550e8400-e29b-41d4-a716-446655440000")
        assert rate.provider == "chase"
        assert rate.rate_type == "savings"
        assert float(rate.rate_value) == 0.05

    @patch("pyarrow.parquet.ParquetFile")
    @patch("os.path.exists")
    def test_nan_rate_value_defaults_to_zero(self, mock_exists, mock_parquet_class):
        """2. Sanitisation: NaN rate_value is stored as 0"""
        mock_exists.return_value = True
        rows = {**VALID_ROW, "rate_value": [float("nan")]}
        mock_parquet_class.return_value = make_mock_parquet(rows)

        call_command("seed_data")

        rate = Rate.objects.get(raw_response_id="550e8400-e29b-41d4-a716-446655440000")
        assert float(rate.rate_value) == 0.0

    @patch("pyarrow.parquet.ParquetFile")
    @patch("os.path.exists")
    def test_none_rate_value_defaults_to_zero(self, mock_exists, mock_parquet_class):
        """3. Sanitisation: None rate_value is stored as 0"""
        mock_exists.return_value = True
        rows = {**VALID_ROW, "rate_value": [None]}
        mock_parquet_class.return_value = make_mock_parquet(rows)

        call_command("seed_data")

        rate = Rate.objects.get(raw_response_id="550e8400-e29b-41d4-a716-446655440000")
        assert float(rate.rate_value) == 0.0

    @patch("pyarrow.parquet.ParquetFile")
    @patch("os.path.exists")
    def test_missing_provider_skips_row(self, mock_exists, mock_parquet_class):
        """4. Guard: Row missing provider is silently skipped"""
        mock_exists.return_value = True
        rows = {**VALID_ROW, "provider": [None]}
        mock_parquet_class.return_value = make_mock_parquet(rows)

        call_command("seed_data")

        assert Rate.objects.count() == 0

    @patch("pyarrow.parquet.ParquetFile")
    @patch("os.path.exists")
    def test_missing_raw_response_id_skips_row(self, mock_exists, mock_parquet_class):
        """5. Guard: Row missing raw_response_id is silently skipped"""
        mock_exists.return_value = True
        rows = {**VALID_ROW, "raw_response_id": [None]}
        mock_parquet_class.return_value = make_mock_parquet(rows)

        call_command("seed_data")

        assert Rate.objects.count() == 0

    @patch("pyarrow.parquet.ParquetFile")
    @patch("os.path.exists")
    def test_missing_effective_date_skips_row(self, mock_exists, mock_parquet_class):
        """6. Guard: Row missing effective_date is silently skipped"""
        mock_exists.return_value = True
        rows = {**VALID_ROW, "effective_date": [None]}
        mock_parquet_class.return_value = make_mock_parquet(rows)

        call_command("seed_data")

        assert Rate.objects.count() == 0

    @patch("pyarrow.parquet.ParquetFile")
    @patch("os.path.exists")
    def test_duplicate_raw_response_id_upserts(self, mock_exists, mock_parquet_class):
        """7. Idempotency: Duplicate raw_response_id updates existing row"""
        shared_uuid = "550e8400-e29b-41d4-a716-446655440000"

        # Pre-existing record
        Rate.objects.create(
            provider="chase",
            rate_type="savings",
            rate_value=0.05,
            effective_date="2026-04-01",
            raw_response_id=shared_uuid,
            ingestion_ts="2026-04-01T10:00:00Z",
            sys_ingested_ts="2026-04-01T10:00:00Z",
        )

        mock_exists.return_value = True
        rows = {**VALID_ROW, "rate_value": [9.99]}  # Changed value
        mock_parquet_class.return_value = make_mock_parquet(rows)

        call_command("seed_data")

        assert Rate.objects.count() == 1  # no duplicate
        assert (
            float(Rate.objects.get(raw_response_id=shared_uuid).rate_value) == 9.99
        )  # updated

    @patch("pyarrow.parquet.ParquetFile")
    @patch("os.path.exists")
    def test_file_not_found_exits_early(self, mock_exists, mock_parquet_class):
        """8. Safety: Missing file exits early without touching the DB"""
        mock_exists.return_value = False

        call_command("seed_data")

        mock_parquet_class.assert_not_called()
        assert Rate.objects.count() == 0

    @patch("pyarrow.parquet.ParquetFile")
    @patch("os.path.exists")
    def test_multiple_batches_all_ingested(self, mock_exists, mock_parquet_class):
        """9. Batching: All rows across multiple batches are persisted"""
        mock_exists.return_value = True

        def make_batch(uuid, provider):
            batch = MagicMock()
            batch.to_pydict.return_value = {
                **VALID_ROW,
                "provider": [provider],
                "raw_response_id": [uuid],
            }
            batch.__len__.return_value = 1
            return batch

        mock_instance = MagicMock()
        mock_instance.metadata.num_rows = 2
        mock_instance.iter_batches.return_value = [
            make_batch("550e8400-e29b-41d4-a716-446655440001", "BankA"),
            make_batch("550e8400-e29b-41d4-a716-446655440002", "BankB"),
        ]
        mock_parquet_class.return_value = mock_instance

        call_command("seed_data")

        assert Rate.objects.count() == 2
        assert Rate.objects.filter(provider="banka").exists()  # .lower() applied
        assert Rate.objects.filter(provider="bankb").exists()

    @patch("pyarrow.parquet.ParquetFile")
    @patch("os.path.exists")
    def test_missing_ingestion_ts_falls_back_to_sys_now(
        self, mock_exists, mock_parquet_class
    ):
        """10. Fallback: Missing ingestion_ts uses sys_now instead of crashing"""
        mock_exists.return_value = True
        rows = {**VALID_ROW, "ingestion_ts": [None]}
        mock_parquet_class.return_value = make_mock_parquet(rows)

        call_command("seed_data")

        # Row still created — no crash, sys_now used as fallback
        assert Rate.objects.count() == 1

import pytest
import json
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework_simplejwt.tokens import AccessToken
from rates.models import Rate
from decimal import Decimal


@pytest.mark.django_db
class TestLatestRatesAPI:
    """Test cases for the GET /rates/latest/ endpoint"""

    def test_get_latest_rates_success(self, client):
        """1. Happy Path: Public access returns 200 OK"""
        url = reverse("rates-latest")
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_get_latest_rates_filtering(self, client):
        """2. Logic: Ensure we can filter by provider or rate_type if implemented"""
        # Create dummy data first
        Rate.objects.create(
            provider="chase",
            rate_type="savings",
            rate_value=1.5,
            effective_date="2026-04-02",
            raw_response_id="111e8400-e29b-41d4-a716-446655440001",
            ingestion_ts="2026-04-02T10:00:00Z",
            sys_ingested_ts="2026-04-02T10:00:00Z",
        )
        url = reverse("rates-latest") + "?provider=chase"
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_get_latest_rates_empty(self, client):
        """3. Edge Case: Returns 200 even if no rates exist in DB"""
        Rate.objects.all().delete()
        url = reverse("rates-latest")
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0

    def test_get_latest_rates_method_not_allowed(self, client):
        """4. Security: POST is not allowed on this endpoint"""
        url = reverse("rates-latest")
        response = client.post(url, {})
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


@pytest.mark.django_db
class TestRateHistoryAPI:
    """Test cases for the GET /rates/history/ endpoint"""

    def setup_method(self):
        """Create a few historical records for testing"""
        self.url = reverse("rates-history")
        # Record 1: Older
        Rate.objects.create(
            provider="chase",
            rate_type="mortgage",
            rate_value=3.5,
            ingestion_ts="2026-01-01T10:00:00Z",
            sys_ingested_ts="2026-01-01T10:00:00Z",
            effective_date="2026-01-01",
            raw_response_id="c8b8a3f1-5c6d-4c7f-9c4d-2a1f0e9b7a12",
        )
        # Record 2: Newer
        Rate.objects.create(
            provider="chase",
            rate_type="mortgage",
            rate_value=3.8,
            ingestion_ts="2026-02-01T10:00:00Z",
            sys_ingested_ts="2026-02-01T10:00:00Z",
            effective_date="2026-02-01",
            raw_response_id="c8b8a3f1-5c6d-4c7f-9c4d-2a1f0e9b7a13",
        )
        # Record 3: Different Provider
        Rate.objects.create(
            provider="barclays",
            rate_type="mortgage",
            rate_value=4.0,
            ingestion_ts="2026-02-01T10:00:00Z",
            sys_ingested_ts="2026-02-01T10:00:00Z",
            effective_date="2026-02-01",
            raw_response_id="c8b8a3f1-5c6d-4c7f-9c4d-2a1f0e9b7a14",
        )

    def test_get_history_success(self, client):
        """1. Happy Path: Public access returns 200 OK with data"""
        url = self.url  # trailing slash belongs HERE on the path

        params = {
            "provider": "hsbc",
            "type": "15yr_fixed_mortgage",
            "from": "2025-01-01",
            "range": "10:100",  # no trailing slash here
        }

        response = client.get(url, params)
        assert response.status_code == 200

    def test_get_history_filter_by_provider(self, client):
        """2. Logic: Ensure filtering by provider and type works"""
        params = {"provider": "barclays", "type": "mortgage"}
        response = client.get(self.url, params)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["provider"] == "barclays"

    def test_get_history_ordering(self, client):
        """3. Logic: Ensure history is returned in chronological order"""
        params = {"provider": "chase", "type": "mortgage"}
        response = client.get(self.url, params)

        # Newest (Feb) should be index 0, Oldest (Jan) index 1
        assert response.data[0]["effective_date"] == "2026-02-01"
        assert response.data[1]["effective_date"] == "2026-01-01"

    def test_get_history_invalid_filter(self, client):
        """4. Edge Case: Returns empty list for non-existent provider"""
        params = {"provider": "nonexistent_bank", "type": "mortgage"}
        response = client.get(self.url, params)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0

    def test_get_history_returns_total_count_header(self, client):
        """5. Additional: total count should be available in a header"""
        params = {"provider": "chase", "type": "mortgage"}
        response = client.get(self.url, params)

        assert response.status_code == status.HTTP_200_OK
        assert response.headers.get("X-Total-Count") == "2"


@pytest.mark.django_db
class TestIngestRateAPI:
    """Test cases for the POST /rates/ingest/ endpoint"""

    # Reusable valid payload matching ALL serializer required fields
    valid_payload = {
        "provider": "chase",
        "rate_type": "savings_easy_access",
        "currency": "USD",
        "rate_value": 4.25,
        "effective_date": "2026-04-02",
        "ingestion_ts": "2026-04-02T10:00:00Z",
        "source_url": "https://chase.com/rates",
        "raw_response_id": "550e8400-e29b-41d4-a716-446655440000",
    }

    def test_post_ingest_success(self, client):
        """1. Happy Path: Valid JWT + Valid Data creates a record"""
        user = User.objects.create_user(username="admin", password="password")
        token = AccessToken.for_user(user)
        url = reverse("rates-ingest")

        auth_headers = {"HTTP_AUTHORIZATION": f"Bearer {str(token)}"}
        response = client.post(
            url,
            data=json.dumps(self.valid_payload),
            content_type="application/json",
            **auth_headers,
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert Rate.objects.filter(
            raw_response_id="550e8400-e29b-41d4-a716-446655440000"
        ).exists()

    def test_post_ingest_no_auth(self, client):
        """2. Security: Fails with 401 if token is missing"""
        url = reverse("rates-ingest")
        response = client.post(
            url, data=json.dumps(self.valid_payload), content_type="application/json"
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_post_ingest_invalid_data(self, client):
        """3. Validation: Fails with 400 if required fields are missing"""
        user = User.objects.create_user(username="tester", password="password")
        token = AccessToken.for_user(user)
        url = reverse("rates-ingest")

        payload = {
            "provider": "only-provider-given"
        }  # Missing currency, rate_value, etc.
        auth_headers = {"HTTP_AUTHORIZATION": f"Bearer {str(token)}"}

        response = client.post(
            url,
            data=json.dumps(payload),
            content_type="application/json",
            **auth_headers,
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_post_ingest_duplicate_id(self, client):
        """4. Data Integrity: Upsert updates existing record, does NOT return 400"""
        user = User.objects.create_user(username="guard", password="password")
        token = AccessToken.for_user(user)
        shared_uuid = "000e8400-e29b-41d4-a716-446655440000"
        url = reverse("rates-ingest")
        auth_headers = {"HTTP_AUTHORIZATION": f"Bearer {str(token)}"}

        # First insert
        payload = {
            **self.valid_payload,
            "raw_response_id": shared_uuid,
            "rate_value": 1.0,
        }
        client.post(
            url,
            data=json.dumps(payload),
            content_type="application/json",
            **auth_headers,
        )

        # Second insert with same UUID but different rate_value — should upsert
        updated_payload = {
            **self.valid_payload,
            "raw_response_id": shared_uuid,
            "rate_value": 9.99,
        }
        response = client.post(
            url,
            data=json.dumps(updated_payload),
            content_type="application/json",
            **auth_headers,
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert (
            Rate.objects.filter(raw_response_id=shared_uuid).count() == 1
        )  # no duplicate row
        assert Rate.objects.get(raw_response_id=shared_uuid).rate_value == Decimal(
            "9.99"
        )  # value updated

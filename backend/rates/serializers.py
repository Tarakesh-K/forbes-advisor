from rest_framework import serializers
from .models import Rate


class RateSerializer(serializers.ModelSerializer):
    """
    Serializer for the Rate model.
    Includes strict validation to ensure data integrity during ingestion.
    """

    class Meta:
        model = Rate
        fields = [
            "provider",
            "rate_type",
            "effective_date",
            "rate_value",
            "ingestion_ts",
        ]

    def validate(self, data):
        """
        Check for duplicates within the same batch or system.
        This provides a cleaner error message than a generic IntegrityError.
        """
        if Rate.objects.filter(
            provider=data["provider"],
            rate_type=data["rate_type"],
            effective_date=data["effective_date"],
            rate_value=data["rate_value"],
            ingestion_ts=data["ingestion_ts"],
        ).exists():
            raise serializers.ValidationError(
                {"error": "This specific rate record has already been ingested."}
            )

        return data


class RateIngestionSerializer(serializers.ModelSerializer):
    # Explicitly overriding to ensure "not empty" validation
    provider = serializers.CharField(required=True, allow_blank=False)
    rate_type = serializers.CharField(required=True, allow_blank=False)
    currency = serializers.CharField(required=True, allow_blank=False, min_length=3)
    rate_value = serializers.DecimalField(
        required=True, max_digits=10, decimal_places=6
    )
    effective_date = serializers.DateField(required=True)
    ingestion_ts = serializers.DateTimeField(required=True)
    source_url = serializers.URLField(required=True, allow_blank=False)
    raw_response_id = serializers.UUIDField(required=True)

    class Meta:
        model = Rate
        fields = [
            "provider",
            "rate_type",
            "currency",
            "rate_value",
            "effective_date",
            "ingestion_ts",
            "source_url",
            "raw_response_id",
        ]

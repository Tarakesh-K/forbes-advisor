import os
from django.core.cache import cache
from utils.json_converter import to_json_safe
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
import logging
from .models import Rate
from django.utils.dateparse import parse_date
from .serializers import RateSerializer, RateIngestionSerializer
from django.utils import timezone
from datetime import timedelta
from django.db import transaction
from django.db.models import Q

logger = logging.getLogger(__name__)


class RatesLatestView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        try:
            cache_key = os.getenv("RATE_CACHE_KEY", "rates_data_latest_master")

            # 1. Try to get the pre-computed "Latest" list
            latest_snapshot = cache.get(cache_key)
            logger.info(
                "Cache lookup",
                extra={
                    "cache_key": cache_key,
                    "cache_hit": latest_snapshot is not None,
                },
            )

            if not latest_snapshot:
                try:
                    # 2. The Senior Query: Get the absolute top record for every provider
                    # Logic: Order by Provider, then Date Descending, then Time Descending.
                    # Distinct('provider') picks the ver y first row for each bank group.
                    queryset = Rate.objects.order_by(
                        "provider",
                        "-effective_date",
                        "-ingestion_ts",
                        "-sys_ingested_ts",
                    ).distinct("provider")

                    # Serialize the "Latest Truth" only
                    serializer = RateSerializer(queryset, many=True)
                    latest_snapshot = serializer.data

                    # 3. Cache it (Longer timeout is fine since we invalidate on POST)
                    cache.set(cache_key, latest_snapshot, timeout=3600)
                    logger.info(
                        "Cache set",
                        extra={"cache_key": cache_key, "count": len(latest_snapshot)},
                    )

                except Exception as e:
                    logger.error(f"Failed to fetch latest rates: {e}")
                    return Response({"error": "Database error"}, status=500)

            # Assuming 'latest_snapshot' is the list of 10 objects from your cache
            rate_type = request.query_params.get("type", "").strip('"/ ')
            # 4. In-Memory Filter for Type
            if rate_type:
                # We filter the list of objects in Python
                filtered_data = [
                    obj for obj in latest_snapshot if obj.get("rate_type") == rate_type
                ]

                # If the user asked for 'savings_1yr_fixed',
                # filtered_data will contain only the Bank of America object.
                return Response(filtered_data)

            return Response(latest_snapshot)
        except Exception as e:
            logger.error(f"Unexpected error in RatesLatestView: {e}")
            return Response({"error": "Internal server error"}, status=500)


class RateHistoryPagination(PageNumberPagination):
    page_size = 100
    max_page_size = 1000


class RatesHistoryView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        try:
            # 1. Initialize empty Filter Object
            filters = Q()

            # 2. Dynamic Filtering (Optional params)
            provider = request.query_params.get("provider")
            if provider:
                filters &= Q(provider__iexact=provider.strip('"/ '))

            rate_type = request.query_params.get("type")
            if rate_type:
                filters &= Q(rate_type__iexact=rate_type.strip('"/ '))

            # 3. Date Range Handling
            d_from_str = request.query_params.get("from")
            d_to_str = request.query_params.get("to")

            d_from = parse_date(d_from_str) if d_from_str else None
            d_to = parse_date(d_to_str) if d_to_str else timezone.now().date()

            if d_from:
                if d_to < d_from:
                    return Response(
                        {
                            "error": "Invalid date range: 'to' cannot be earlier than 'from'."
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                filters &= Q(effective_date__range=(d_from, d_to))
            else:
                # Default to last 365 days only if no 'from' is provided
                default_start = d_to - timedelta(days=365)
                filters &= Q(effective_date__range=(default_start, d_to))

            # 4. Slicing Logic (range=a:b)
            raw_range = (
                request.query_params.get("range", "1:1000").strip("/ ").split(":")
            )
            try:
                # Convert 1-based "1:1000" to 0-based Python [0:1000]
                start_idx = max(0, int(raw_range[0]) - 1)
                end_idx = int(raw_range[1])

                if end_idx <= start_idx:
                    return Response(
                        {"error": "Range 'to' must be greater than 'from'"}, status=400
                    )

                # Safety Cap
                if (end_idx - start_idx) > 1000:
                    end_idx = start_idx + 10000
            except (ValueError, IndexError):
                return Response(
                    {"error": "Invalid range format. Use range=start:end"}, status=400
                )

            # 5. Execute Query with combined filters and slice
            total_count = Rate.objects.filter(
                filters
            ).count()  # overall filtered set count

            queryset = Rate.objects.filter(filters).order_by(
                "-effective_date", "-ingestion_ts"
            )[start_idx:end_idx]

            serializer = RateSerializer(queryset, many=True)
            return Response(serializer.data, headers={"Total-Count": str(total_count)})

        except Exception as e:
            # Log the error here in a real app
            return Response({"error": f"An internal error occurred. {e}"}, status=500)


class RatesIngestView(APIView):
    def post(self, request):
        try:
            # 1. Determine if it's a list or a single object
            data = request.data
            is_many = isinstance(data, list)

            # 2. Validate using the Serializer
            serializer = RateIngestionSerializer(data=data, many=is_many)

            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            # 3. Process the validated data
            validated_data = serializer.validated_data
            if not is_many:
                validated_data = [validated_data]  # Normalize to list

            sys_now = timezone.now()
            rows_to_sync = []

            for item in validated_data:
                rows_to_sync.append(
                    Rate(
                        **item,
                        sys_ingested_ts=sys_now,
                        raw_data_snapshot=to_json_safe(
                            item
                        ),  # Save the validated dict as the snapshot
                    )
                )

            # 4. The Final Upsert (Single or Bulk)
            with transaction.atomic():
                Rate.objects.bulk_create(
                    rows_to_sync,
                    update_conflicts=True,
                    unique_fields=["raw_response_id"],
                    update_fields=[
                        "rate_value",
                        "effective_date",
                        "ingestion_ts",
                        "sys_ingested_ts",
                        "raw_data_snapshot",
                    ],
                )

            cache_key = os.getenv("RATE_CACHE_KEY", "rates_data_latest_master")
            deleted = cache.delete(cache_key)
            logger.info(
                "Cache invalidated", extra={"cache_key": cache_key, "deleted": deleted}
            )

            return Response(
                {
                    "message": f"Successfully processed {len(rows_to_sync)} records",
                    "status": "success",
                },
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            logger.error(f"Database error during ingestion: {e}")
            return Response({"error": "Internal server error"}, status=500)

from django.urls import path
from .views import RatesLatestView, RatesHistoryView, RatesIngestView

urlpatterns = [
    path("latest/", RatesLatestView.as_view(), name="rates-latest"),
    path("history/", RatesHistoryView.as_view(), name="rates-history"),
    path("ingest/", RatesIngestView.as_view(), name="rates-ingest"),
]

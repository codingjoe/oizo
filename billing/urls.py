from django.urls import path

from .views import UsageRecordListView, WalletView

urlpatterns = [
    path("usage/", UsageRecordListView.as_view(), name="usage-list"),
    path("wallet/", WalletView.as_view(), name="wallet"),
]

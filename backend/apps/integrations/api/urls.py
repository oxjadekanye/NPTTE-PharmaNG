from django.urls import path

from apps.integrations.api.views import (
    AnalyticsSnapshotView,
    DeliveryLogsView,
    ExportDownloadView,
    ExportJobListView,
    ExternalConnectorListView,
    IntegrationApiKeyRevokeView,
    IntegrationApiKeyRotateView,
    IntegrationApiKeysView,
    IntegrationHealthView,
    PdfGenerateView,
    PushRegisterView,
    PushTestView,
    SmsSendView,
    WebhookDeliveryLogView,
    WebhookSubscriptionListView,
    WebhookTestView,
)

urlpatterns = [
    path("health/", IntegrationHealthView.as_view(), name="integration-health"),
    path("webhooks/", WebhookSubscriptionListView.as_view(), name="integration-webhooks"),
    path("webhooks/deliveries/", WebhookDeliveryLogView.as_view(), name="integration-webhook-deliveries"),
    path("webhooks/test/", WebhookTestView.as_view(), name="integration-webhook-test"),
    path("exports/", ExportJobListView.as_view(), name="integration-exports"),
    path("exports/<uuid:pk>/download/", ExportDownloadView.as_view(), name="integration-export-download"),
    path("pdf/generate/", PdfGenerateView.as_view(), name="integration-pdf-generate"),
    path("analytics/", AnalyticsSnapshotView.as_view(), name="integration-analytics"),
    path("connectors/", ExternalConnectorListView.as_view(), name="integration-connectors"),
    path("push/register/", PushRegisterView.as_view(), name="integration-push-register"),
    path("push/test/", PushTestView.as_view(), name="integration-push-test"),
    path("sms/send/", SmsSendView.as_view(), name="integration-sms-send"),
    path("delivery-logs/", DeliveryLogsView.as_view(), name="integration-delivery-logs"),
    path("keys/", IntegrationApiKeysView.as_view(), name="integration-api-keys"),
    path("keys/<uuid:pk>/revoke/", IntegrationApiKeyRevokeView.as_view(), name="integration-api-key-revoke"),
    path("keys/<uuid:pk>/rotate/", IntegrationApiKeyRotateView.as_view(), name="integration-api-key-rotate"),
]

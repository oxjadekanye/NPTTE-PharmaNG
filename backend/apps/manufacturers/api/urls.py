from django.urls import path

from apps.manufacturers.api.views import (
    BatchCreateView,
    BatchGenerateSerialsView,
    BatchListView,
    BatchSubmitForApprovalView,
    ManufacturerProfileView,
    ManufacturingSiteListView,
    ProductRegisterView,
    RecallNoticeCreateView,
)

urlpatterns = [
    path("profile/", ManufacturerProfileView.as_view(), name="manufacturer-profile"),
    path("products/register/", ProductRegisterView.as_view(), name="manufacturer-product-register"),
    path("sites/", ManufacturingSiteListView.as_view(), name="manufacturer-sites"),
    path("batches/", BatchListView.as_view(), name="manufacturer-batches"),
    path("batches/create/", BatchCreateView.as_view(), name="manufacturer-batch-create"),
    path("batches/<uuid:pk>/submit-for-approval/", BatchSubmitForApprovalView.as_view(), name="manufacturer-batch-submit"),
    path("batches/<uuid:pk>/generate-serials/", BatchGenerateSerialsView.as_view(), name="manufacturer-batch-generate-serials"),
    path("recalls/", RecallNoticeCreateView.as_view(), name="manufacturer-recalls"),
]

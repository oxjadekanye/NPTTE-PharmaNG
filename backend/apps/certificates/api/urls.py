from django.urls import path

from apps.certificates.api.views import CertificateIssueView, CertificateListView, CertificateVerifyView

urlpatterns = [
    path("", CertificateListView.as_view(), name="certificates-list"),
    path("issue/", CertificateIssueView.as_view(), name="certificates-issue"),
    path("verify/", CertificateVerifyView.as_view(), name="certificates-verify"),
]

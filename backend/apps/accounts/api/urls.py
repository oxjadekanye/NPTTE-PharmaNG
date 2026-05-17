from django.urls import path

from apps.accounts.api.views import (
    LoginView,
    LogoutView,
    PasswordChangeView,
    PermissionsView,
    ProfileView,
    RefreshTokenView,
    RegisterView,
    VerifyTokenView,
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="auth-register"),
    path("login/", LoginView.as_view(), name="auth-login"),
    path("refresh/", RefreshTokenView.as_view(), name="auth-refresh"),
    path("verify/", VerifyTokenView.as_view(), name="auth-verify"),
    path("logout/", LogoutView.as_view(), name="auth-logout"),
    path("profile/", ProfileView.as_view(), name="auth-profile"),
    path("password/change/", PasswordChangeView.as_view(), name="auth-password-change"),
    path("permissions/", PermissionsView.as_view(), name="auth-permissions"),
]

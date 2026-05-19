from django.urls import path

from .views import (
    RegisterAPIView,
    LoginAPIView,
    ChangePasswordAPIView,
    ForgotPasswordAPIView,
    ResetPasswordAPIView,
)

urlpatterns = [
    path("register/", RegisterAPIView.as_view(), name="register"),
    path("login/", LoginAPIView.as_view(), name="login"),
    # path("change-password/", ChangePasswordAPIView.as_view(), name="change-password"),
    path(
        "change-password/",
        ChangePasswordAPIView.as_view()
    ),
    path("forgot-password/", ForgotPasswordAPIView.as_view(), name="forgot-password"),
    path("reset-password/", ResetPasswordAPIView.as_view(), name="reset-password"),
]
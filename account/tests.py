from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from .models import User


class UserSetupMixin:
    """Shared helper to create a test user."""

    def create_user(self, email="test@example.com", username="testuser", password="StrongPass123"):
        return User.objects.create_user(email=email, username=username, password=password)


# ──────────────────────────────────────────────
# Registration
# ──────────────────────────────────────────────

class RegisterAPIViewTests(UserSetupMixin, TestCase):

    def setUp(self):
        self.client = APIClient()
        self.url = reverse("register")
        self.valid_payload = {
            "username": "newuser",
            "email": "new@example.com",
            "password": "StrongPass123",
            "confirm_password": "StrongPass123",
        }

    def test_register_success(self):
        response = self.client.post(self.url, self.valid_payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email="new@example.com").exists())

    def test_register_password_mismatch(self):
        payload = {**self.valid_payload, "confirm_password": "WrongPass"}
        response = self.client.post(self.url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_duplicate_email(self):
        self.create_user(email="new@example.com")
        response = self.client.post(self.url, self.valid_payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


# ──────────────────────────────────────────────
# Login
# ──────────────────────────────────────────────

class LoginAPIViewTests(UserSetupMixin, TestCase):

    def setUp(self):
        self.client = APIClient()
        self.url = reverse("login")
        self.user = self.create_user()

    def test_login_success(self):
        response = self.client.post(self.url, {"email": "test@example.com", "password": "StrongPass123"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_login_wrong_password(self):
        response = self.client.post(self.url, {"email": "test@example.com", "password": "wrongpassword"})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_nonexistent_user(self):
        response = self.client.post(self.url, {"email": "ghost@example.com", "password": "anything"})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


# ──────────────────────────────────────────────
# Change Password
# ──────────────────────────────────────────────

class ChangePasswordAPIViewTests(UserSetupMixin, TestCase):

    def setUp(self):
        self.client = APIClient()
        self.url = reverse("change-password")
        self.user = self.create_user()
        self.client.force_authenticate(user=self.user)  # Simulate authenticated session

    def test_change_password_success(self):
        response = self.client.post(self.url, {
            "old_password": "StrongPass123",
            "new_password": "NewPass456!",
            "confirm_password": "NewPass456!",
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("NewPass456!"))

    def test_change_password_wrong_old_password(self):
        response = self.client.post(self.url, {
            "old_password": "WrongOldPass",
            "new_password": "NewPass456!",
            "confirm_password": "NewPass456!",
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_change_password_mismatch(self):
        response = self.client.post(self.url, {
            "old_password": "StrongPass123",
            "new_password": "NewPass456!",
            "confirm_password": "DifferentPass!",
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_change_password_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.post(self.url, {
            "old_password": "StrongPass123",
            "new_password": "NewPass456!",
            "confirm_password": "NewPass456!",
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


# ──────────────────────────────────────────────
# Forgot / Reset Password
# ──────────────────────────────────────────────

class ForgotPasswordAPIViewTests(UserSetupMixin, TestCase):

    def setUp(self):
        self.client = APIClient()
        self.url = reverse("forgot-password")
        self.user = self.create_user()

    def test_forgot_password_existing_email(self):
        response = self.client.post(self.url, {"email": "test@example.com"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertIsNotNone(self.user.forgot_password_token)

    def test_forgot_password_nonexistent_email_returns_200(self):
        # Must return 200 to avoid leaking whether an email is registered
        response = self.client.post(self.url, {"email": "ghost@example.com"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class ResetPasswordAPIViewTests(UserSetupMixin, TestCase):

    def setUp(self):
        self.client = APIClient()
        self.url = reverse("reset-password")
        self.user = self.create_user()
        # Manually assign a reset token
        import uuid
        self.token = uuid.uuid4()
        self.user.forgot_password_token = self.token
        self.user.save()

    def test_reset_password_success(self):
        response = self.client.post(self.url, {
            "token": str(self.token),
            "password": "BrandNew789!",
            "confirm_password": "BrandNew789!",
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("BrandNew789!"))
        self.assertIsNone(self.user.forgot_password_token)  # Token invalidated

    def test_reset_password_invalid_token(self):
        import uuid
        response = self.client.post(self.url, {
            "token": str(uuid.uuid4()),  # Random token — won't match
            "password": "BrandNew789!",
            "confirm_password": "BrandNew789!",
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
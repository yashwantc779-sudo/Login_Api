from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import User


class CustomUserCreationForm(UserCreationForm):
    """Form used in the admin 'Add User' page."""

    class Meta:
        model = User
        fields = ("email", "username")  # password1 & password2 inherited from UserCreationForm


class CustomUserChangeForm(UserChangeForm):
    """Form used in the admin 'Edit User' page."""

    class Meta:
        model = User
        fields = ("email", "username", "is_active", "is_staff", "is_superuser", "groups", "user_permissions")


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    form = CustomUserChangeForm        # Used when editing
    add_form = CustomUserCreationForm  # Used when adding

    list_display = ["email", "username", "is_active", "is_staff"]
    list_filter = ["is_active", "is_staff"]
    search_fields = ["email", "username"]
    ordering = ["email"]

    # ✅ These two lines fix the admin login page to use email instead of username
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    # Fields shown when EDITING an existing user
    fieldsets = (
        ("Account",     {"fields": ("email", "username", "password")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
    )

    # Fields shown when ADDING a new user
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "username", "password1", "password2"),
        }),
    )
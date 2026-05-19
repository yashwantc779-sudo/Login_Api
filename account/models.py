import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class UserManager(BaseUserManager):

    def create_user(self, email, username, password=None):
        if not email:
            raise ValueError("Email is required")
        if not username:
            raise ValueError("Username is required")

        user = self.model(
            email=self.normalize_email(email),
            username=username,
        )
        user.set_password(password)  # Hashes the password automatically
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password):
        user = self.create_user(email, username, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model using email as the unique identifier for authentication.
    Extends AbstractBaseUser so Django handles password hashing, session tokens, etc.
    """

    username = models.CharField(max_length=100)
    email = models.EmailField(unique=True)

    # Override the ManyToMany fields from PermissionsMixin to avoid reverse accessor
    # clashes with the built-in auth.User model. Required whenever you define a
    # custom user model alongside Django's default auth app.
    groups = models.ManyToManyField(
        "auth.Group",
        blank=True,
        related_name="account_users",   # avoids clash with auth.User.groups
        verbose_name="groups",
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        blank=True,
        related_name="account_users",   # avoids clash with auth.User.user_permissions
        verbose_name="user permissions",
    )

    # AbstractBaseUser already provides a `password` field — do NOT redefine it.

    forgot_password_token = models.UUIDField(
        null=True,
        blank=True,
        default=None,
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)   # Required for admin access

    objects = UserManager()

    USERNAME_FIELD = "email"          # Login via email
    REQUIRED_FIELDS = ["username"]    # Asked when using createsuperuser

    def __str__(self):
        return self.username
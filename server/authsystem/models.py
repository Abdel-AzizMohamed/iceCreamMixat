from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = (
        ("admin", "Admin"),
        ("staff", "Staff"),
    )

    # Make email unique and required
    email = models.EmailField(unique=True)

    role = models.CharField(
        max_length=10, choices=ROLE_CHOICES, default="staff"
    )
    branch_id = models.IntegerField(
        null=True,
        blank=True,
        help_text="Branch assigned to staff member. Admins can leave this blank.",
    )

    # Set email as the main identifier for login
    USERNAME_FIELD = "email"

    # Username is no longer required for login, but still kept for Django internal compatibility
    REQUIRED_FIELDS = ["username"]

    def is_admin(self):
        return self.role == "admin" or self.is_superuser

    def is_staff_member(self):
        return self.role == "staff"

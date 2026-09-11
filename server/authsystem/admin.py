# accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ["email", "username", "role", "branch_id", "is_staff"]
    fieldsets = UserAdmin.fieldsets + (
        ("Shop Permissions & Role", {"fields": ("role", "branch_id")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Shop Permissions & Role", {"fields": ("role", "branch_id")}),
    )


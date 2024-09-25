from gettext import ngettext
from django.contrib import messages
from django.contrib import admin

from . import models
from .auth import models as auth_models


@admin.register(models.User)
class UserAdmin(admin.ModelAdmin):
    """User admin"""

    list_display = ("id", "username", "first_name", "last_name", "email", "created_in", "is_active", "is_staff")
    list_display_links = ("id", "username", "first_name", "last_name")
    fields = ("username", "first_name", "last_name", "email", "is_active", "is_staff","hashed_password")
    search_fields = ("username", "first_name", "last_name")
    list_filter = ("is_active", "is_staff")
    list_max_show_all = 250
    list_per_page = 150
    actions = ["activate_user", "deactivate_user", "grant_access_to_admin_site", "deny_access_to_admin_site"]

    @admin.action(description="Activate user(-s)")
    def activate_user(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, ngettext(
            '%d user was successfully activated.',
            '%d users were successfully activated.',
            updated,
        ) % updated, messages.SUCCESS)

    @admin.action(description="Deactivate user(-s)")
    def deactivate_user(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, ngettext(
            '%d user was successfully activated.',
            '%d users were successfully activated.',
            updated,
        ) % updated, messages.SUCCESS)

    @admin.action(description="Grant access to admin site")
    def grant_access_to_admin_site(self, request, queryset):
        updated = queryset.update(is_staff=True)
        self.message_user(request, ngettext(
            '%d user was successfully granted access to the admin site.',
            '%d users were successfully granted access to the admin site.',
            updated,
        ) % updated, messages.SUCCESS)

    @admin.action(description="Deny access to admin site")
    def deny_access_to_admin_site(self, request, queryset):
        updated = queryset.update(is_staff=False)
        self.message_user(request, ngettext(
            '%d user was successfully denied access to the admin site.',
            '%d users were successfully denied access to the admin site.',
            updated,
        ) % updated, messages.SUCCESS)


@admin.register(auth_models.SecretKey)
class SecretKeyAdmin(admin.ModelAdmin):
    """SecretKey admin"""

    list_display = ("id", "user", "created")
    list_display_links = ("id", "user", "created")
    fields = ("key", "user")
    list_max_show_all = 250
    list_per_page = 150


@admin.register(auth_models.JWTToken)
class JWTTokenAdmin(admin.ModelAdmin):
    """JWTToken admin"""

    list_display = ("id", "user", "created")
    list_display_links = ("id", "user", "created")
    fields = ("access_token", "refresh_token", "user")
    list_max_show_all = 250
    list_per_page = 150
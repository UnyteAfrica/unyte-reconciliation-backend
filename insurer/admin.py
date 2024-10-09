from django.contrib import admin
from .models import Insurer, InsurerProfile


@admin.register(Insurer)
class InsurerModelAdmin(admin.ModelAdmin):
    list_display = ("get_insurer_email", "admin_name", "business_registration_number", "get_insurer_created_at")

    def get_insurer_email(self, obj: Insurer) -> str:
        return obj.user.email

    def get_insurer_created_at(self, obj: Insurer) -> str:
        return obj.user.created_at

    get_insurer_email.short_description = "insurer_email"
    get_insurer_created_at.short_description = "created_at"


@admin.register(InsurerProfile)
class InsurerProfileModelAdmin(admin.ModelAdmin):
    list_display = ("get_insurer_email", "get_insurer_admin_name", "get_insurer_profile_picture")

    def get_insurer_email(self, obj: InsurerProfile) -> str:
        return obj.insurer.user.email

    def get_insurer_admin_name(self, obj: InsurerProfile) -> str:
        return obj.insurer.admin_name

    def get_insurer_profile_picture(self, obj: InsurerProfile) -> str:
        return obj.profile_image

    get_insurer_email.short_description = "email"
    get_insurer_admin_name.short_description = "admin_name"
    get_insurer_profile_picture.short_description = "profile_picture"

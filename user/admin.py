from django.contrib import admin

from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdminModel(admin.ModelAdmin):
    list_display = ('email', 'reference_id', 'get_user_type')

    def get_user_type(self, obj: CustomUser) -> str:
        if obj.is_agent:
            return 'AGENT'
        if obj.is_merchant:
            return 'MERCHANT'
        if obj.is_insurer:
            return 'INSURER'
        return None

    get_user_type.short_description = 'user_type'

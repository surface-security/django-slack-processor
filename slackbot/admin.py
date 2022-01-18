from django.contrib import admin
from django.utils.html import format_html

from . import get_user_model


@admin.register(get_user_model())
class UserAdmin(admin.ModelAdmin):
    list_display = ['ext_id', 'username', 'name', 'email', 'active', 'is_bot', 'is_admin', 'get_photo', 'last_seen']
    list_filter = ('active', 'is_bot', 'is_admin')
    search_fields = ['username', 'name', 'email', 'ext_id']
    readonly_fields = ['ext_id', 'username', 'name', 'email', 'active', 'is_bot', 'is_admin', 'get_photo', 'last_seen']
    exclude = ['photo', 'photo_thumb']

    def get_photo(self, obj):
        if obj.photo:
            return format_html(
                '<a href="{}" target="_blank"><img src="{}" style="width:50px;"></a>', obj.photo, obj.photo_thumb
            )
        return None

    get_photo.short_description = 'Photo'
    get_photo.allow_tags = True

    def has_add_permission(self, _):
        return False

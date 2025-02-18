from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from logbasecommand.base import LogBaseCommand
from . import get_user_model, get_message_model
import json


@admin.register(get_user_model())
class UserAdmin(admin.ModelAdmin):
    list_display = [
        "ext_id",
        "username",
        "name",
        "email",
        "active",
        "is_bot",
        "is_admin",
        "get_photo",
        "last_seen",
    ]
    list_filter = ("active", "is_bot", "is_admin")
    search_fields = ["username", "name", "email", "ext_id"]
    readonly_fields = [
        "ext_id",
        "username",
        "name",
        "email",
        "active",
        "is_bot",
        "is_admin",
        "get_photo",
        "last_seen",
    ]
    exclude = ["photo", "photo_thumb"]

    def get_photo(self, obj):
        if obj.photo:
            return format_html(
                '<a href="{}" target="_blank"><img src="{}" style="width:50px;"></a>',
                obj.photo,
                obj.photo_thumb,
            )
        return None

    get_photo.short_description = "Photo"
    get_photo.allow_tags = True

    def has_add_permission(self, _):
        return False


@admin.register(get_message_model())
class SlackMessageAdmin(admin.ModelAdmin, LogBaseCommand):
    list_display = (
        "channel",
        "message_from",
        "reply_count",
        "reply_users_list",
        "reply_users_count",
        "reactions_pretty",
        "type",
        "user_team",
    )

    readonly_fields = (
        "channel",
        "channel_id",
        "client_msg_id",
        "reactions_pretty",
        "reply_count",
        "reply_users_list",
        "reply_users_count",
        "team",
        "text",
        "thread_timestamp",
        "time_stamp",
        "type",
        "user",
        "message_from",
        "user_team",
        "thread_message_pretty",
    )
    exclude = ("reactions", "reply_users", "thread_message")
    list_filter = ("channel", "message_from")

    def reply_users_list(self, obj):
        return ", ".join(obj.reply_users)

    def thread_message_pretty(self, obj):
        if not obj.thread_message:
            return "-"
        formatted_json = json.dumps(obj.thread_message, indent=4, ensure_ascii=False)
        return mark_safe(f"<pre>{formatted_json}</pre>")

    def reactions_pretty(self, obj):
        if not obj.reactions:
            return "-"
        data = json.loads(obj.reactions) if isinstance(obj.reactions, str) else obj.reactions
        formatted_output = []
        for item in data:
            name = item.get("name", "N/A")
            count = item.get("count", 0)
            users = item.get("users", [])
            formatted_output.append(f"<b>{name}</b> (Count: {count})<br>Users: {users}")

        return format_html("<br><br>".join(formatted_output))

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

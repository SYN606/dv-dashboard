from django.contrib import admin
from .models import (
    GuildConfig,
    AFK,
    AdminRole,
    MediaOnlyChannel,
    StickyMessage,
    DisabledCommand,
    RestrictedCommand,
    TempbanConfig,
    TempbanRecord,
    ModerationLogConfig,
    ChannelPermissionSnapshot,
    VerificationConfig,
)


@admin.register(GuildConfig)
class GuildConfigAdmin(admin.ModelAdmin):
    list_display = ("guild_name", "guild_id", "prefix", "is_active", "updated_at")
    search_fields = ("guild_name", "guild_id")
    list_filter = ("is_active",)


@admin.register(TempbanRecord)
class TempbanRecordAdmin(admin.ModelAdmin):
    list_display = ("guild_id", "user_id", "moderator_id", "active", "expires_at")
    search_fields = ("guild_id", "user_id", "moderator_id")
    list_filter = ("active", "expires_at")


# Bulk registration for standard structural configuration modules
simple_models = [
    AFK,
    AdminRole,
    MediaOnlyChannel,
    StickyMessage,
    DisabledCommand,
    RestrictedCommand,
    TempbanConfig,
    ModerationLogConfig,
    ChannelPermissionSnapshot,
    VerificationConfig,
]

admin.site.register(simple_models)

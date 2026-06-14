from django.db import models


class RestrictionScope(models.TextChoices):
    ALLOW = "allow", "Allow"
    DENY = "deny", "Deny"
    BOTH = "both", "Both"


class TimestampMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class GuildConfig(TimestampMixin):
    guild_id = models.CharField(max_length=30, primary_key=True)
    guild_name = models.CharField(max_length=100)
    prefix = models.CharField(max_length=5, default="!")
    is_active = models.BooleanField(default=True)

    class Meta(TimestampMixin.Meta):
        db_table = "guild_config"

    def __str__(self) -> str:
        return f"{self.guild_name} ({self.guild_id})"


class AFK(models.Model):
    guild_id = models.CharField(max_length=30)
    user_id = models.CharField(max_length=30)
    afk_reason = models.CharField(max_length=256)
    since = models.IntegerField()

    class Meta:
        db_table = "afk"
        constraints = [
            models.UniqueConstraint(fields=["guild_id", "user_id"], name="pk_afk")
        ]
        indexes = [
            models.Index(fields=["guild_id"]),
            models.Index(fields=["user_id"]),
        ]

    def __str__(self) -> str:
        return f"<AFK guild={self.guild_id} user={self.user_id}>"


class AdminRole(models.Model):
    guild_id = models.CharField(max_length=30)
    role_id = models.CharField(max_length=30)

    class Meta:
        db_table = "admin_roles"
        constraints = [
            models.UniqueConstraint(
                fields=["guild_id", "role_id"], name="pk_admin_roles"
            )
        ]
        indexes = [
            models.Index(fields=["guild_id"]),
        ]

    def __str__(self) -> str:
        return f"<AdminRole guild={self.guild_id} role={self.role_id}>"


class MediaOnlyChannel(TimestampMixin):
    guild_id = models.CharField(max_length=30)
    channel_id = models.CharField(max_length=30)
    sticky_message_id = models.CharField(max_length=30, null=True, blank=True)
    whitelist_role_id = models.CharField(max_length=30, null=True, blank=True)
    image_only = models.BooleanField(default=False)
    auto_mute = models.BooleanField(default=False)
    nsfw_bypass = models.BooleanField(default=True)

    class Meta(TimestampMixin.Meta):
        db_table = "media_only_channels"
        constraints = [
            models.UniqueConstraint(
                fields=["guild_id", "channel_id"], name="pk_media_only_channels"
            )
        ]
        indexes = [
            models.Index(fields=["guild_id"]),
        ]


class StickyMessage(TimestampMixin):
    guild_id = models.CharField(max_length=30)
    channel_id = models.CharField(max_length=30)
    sticky_content = models.TextField()
    last_message_id = models.CharField(max_length=30, null=True, blank=True)
    counter = models.IntegerField(default=0)

    class Meta(TimestampMixin.Meta):
        db_table = "sticky_messages"
        constraints = [
            models.UniqueConstraint(
                fields=["guild_id", "channel_id"], name="pk_sticky_messages"
            ),
            models.CheckConstraint(
                condition=models.Q(counter__gte=0), name="chk_sticky_counter"
            ),
        ]
        indexes = [
            models.Index(fields=["guild_id"]),
        ]


class DisabledCommand(models.Model):
    guild_id = models.CharField(max_length=30)
    command_name = models.CharField(max_length=64)

    class Meta:
        db_table = "disabled_commands"
        constraints = [
            models.UniqueConstraint(
                fields=["guild_id", "command_name"], name="pk_disabled_commands"
            )
        ]
        indexes = [
            models.Index(fields=["guild_id"]),
        ]


class RestrictedCommand(models.Model):
    guild_id = models.CharField(max_length=30)
    channel_id = models.CharField(max_length=30)
    command_name = models.CharField(max_length=64)
    restriction_scope = models.CharField(
        max_length=10, choices=RestrictionScope.choices, default=RestrictionScope.BOTH
    )

    class Meta:
        db_table = "restricted_commands"
        constraints = [
            models.UniqueConstraint(
                fields=["guild_id", "channel_id", "command_name"],
                name="pk_restricted_commands",
            )
        ]
        indexes = [
            models.Index(fields=["guild_id"]),
        ]


class TempbanConfig(models.Model):
    guild_id = models.CharField(max_length=30, primary_key=True)
    role_id = models.CharField(max_length=30)

    class Meta:
        db_table = "tempban_config"

    def __str__(self) -> str:
        return f"<TempbanConfig guild={self.guild_id} role={self.role_id}>"


class TempbanRecord(TimestampMixin):
    guild_id = models.CharField(max_length=30)
    user_id = models.CharField(max_length=30)
    moderator_id = models.CharField(max_length=30)
    tempban_reason = models.CharField(max_length=512, null=True, blank=True)
    active = models.BooleanField(default=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta(TimestampMixin.Meta):
        db_table = "tempban_records"
        constraints = [
            models.UniqueConstraint(
                fields=["guild_id", "user_id"], name="pk_tempban_records"
            )
        ]
        indexes = [
            models.Index(
                fields=["guild_id", "active"], name="idx_tempban_active_lookup"
            ),
            models.Index(fields=["expires_at"], name="idx_tempban_expiry"),
        ]

    def __str__(self) -> str:
        return f"<TempbanRecord guild={self.guild_id} user={self.user_id} active={self.active}>"


class ModerationLogConfig(TimestampMixin):
    guild_id = models.CharField(max_length=30, primary_key=True)
    channel_id = models.CharField(max_length=30)
    enabled = models.BooleanField(default=True)

    class Meta(TimestampMixin.Meta):
        db_table = "moderation_log_config"

    def __str__(self) -> str:
        return f"<ModerationLogConfig guild={self.guild_id} channel={self.channel_id}>"


class ChannelPermissionSnapshot(TimestampMixin):
    guild_id = models.CharField(max_length=30)
    channel_id = models.CharField(max_length=30)
    target_id = models.CharField(max_length=30)
    permission_name = models.CharField(max_length=64)
    permission_value = models.BooleanField(null=True)

    class Meta(TimestampMixin.Meta):
        db_table = "channel_permission_snapshots"
        constraints = [
            models.UniqueConstraint(
                fields=["guild_id", "channel_id", "target_id", "permission_name"],
                name="pk_channel_perm_snapshots",
            )
        ]
        indexes = [
            models.Index(fields=["guild_id"]),
        ]


class VerificationConfig(TimestampMixin):
    guild_id = models.CharField(max_length=30, primary_key=True)
    verify_channel_id = models.CharField(max_length=30, null=True, blank=True)
    log_channel_id = models.CharField(max_length=30, null=True, blank=True)
    verified_role_id = models.CharField(max_length=30, null=True, blank=True)
    unverified_role_id = models.CharField(max_length=30, null=True, blank=True)

    class Meta(TimestampMixin.Meta):
        db_table = "verification_config"

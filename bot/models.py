from django.db import models
from django.core.validators import MinValueValidator


# Core Enum Choices Definitions
class RestrictionScope(models.TextChoices):
    ALLOW = "allow", "Allow"
    DENY = "deny", "Deny"
    BOTH = "both", "Both"


# Base Structural & Shared Mixins
class TimestampMixin(models.Model):
    """
    Abstract Mixin to inject auto-managed database
    timestamps across operational configurations.
    """

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


# Shared Dashboard Link Models
class GuildConfig(TimestampMixin):
    """
    Core Configuration anchor. The background bot writes to this table
    upon entering a server. The Dashboard views check against this table
    to see if the bot is present.
    """

    guild_id = models.CharField(max_length=30, primary_key=True)
    guild_name = models.CharField(max_length=100)
    prefix = models.CharField(max_length=5, default="!")
    is_active = models.BooleanField(default=True)

    class Meta(TimestampMixin.Meta):
        db_table = "guild_config"

    def __str__(self) -> str:
        return f"{self.guild_name} ({self.guild_id})"


# Feature System Modules Configurations
class AFK(models.Model):
    """
    Tracks active global or server-specific AFK status blocks for users.
    """

    guild_id = models.CharField(max_length=30, validators=[MinValueValidator(1)])
    user_id = models.CharField(max_length=30, validators=[MinValueValidator(1)])
    afk_reason = models.CharField(max_length=256)
    since = models.IntegerField()  # Epoch timestamp representation

    class Meta:
        db_table = "afk"
        constraints = [
            models.UniqueConstraint(fields=["guild_id", "user_id"], name="pk_afk"),
            models.CheckConstraint(
                condition=models.Q(guild_id__gt="0"), name="chk_afk_guild_id"
            ),
            models.CheckConstraint(
                condition=models.Q(user_id__gt="0"), name="chk_afk_user_id"
            ),
        ]

    def __str__(self) -> str:
        return f"<AFK guild={self.guild_id} user={self.user_id}>"


class AdminRole(models.Model):
    """
    Explicit bot configuration permissions bypass maps.
    """

    guild_id = models.CharField(max_length=30)
    role_id = models.CharField(max_length=30)

    class Meta:
        db_table = "admin_roles"
        constraints = [
            models.UniqueConstraint(
                fields=["guild_id", "role_id"], name="pk_admin_roles"
            ),
            models.CheckConstraint(
                condition=models.Q(guild_id__gt="0"), name="chk_admin_role_guild"
            ),
        ]

    def __str__(self) -> str:
        return f"<AdminRole guild={self.guild_id} role={self.role_id}>"


class MediaOnlyChannel(TimestampMixin):
    """
    Enforces media attachments restrictions inside designated text nodes.
    """

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
            ),
            models.CheckConstraint(
                condition=models.Q(guild_id__gt="0"), name="chk_media_guild_id"
            ),
        ]


class StickyMessage(TimestampMixin):
    """
    Configures structural automatic pinning overlays for critical alert contexts.
    """

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


# Command & Flow Restrictions Matrix
class DisabledCommand(models.Model):
    """
    Hard global overrides disabling execution flags on specific commands.
    """

    guild_id = models.CharField(max_length=30)
    command_name = models.CharField(max_length=64)

    class Meta:
        db_table = "disabled_commands"
        constraints = [
            models.UniqueConstraint(
                fields=["guild_id", "command_name"], name="pk_disabled_commands"
            )
        ]


class RestrictedCommand(models.Model):
    """
    Granular blacklists/whitelists routing commands into precise channels.
    """

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


# Moderation & Escalation Enforcements
class TempbanConfig(models.Model):
    """
    Mute/Ban role configurations mapping across individual shards.
    """

    guild_id = models.CharField(max_length=30, primary_key=True)
    role_id = models.CharField(max_length=30)

    class Meta:
        db_table = "tempban_config"

    def __str__(self) -> str:
        return f"<TempbanConfig guild={self.guild_id} role={self.role_id}>"


class TempbanRecord(TimestampMixin):
    """
    Active system execution queues for timed moderation items.
    """

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
    """
    Core Dispatch paths logging moderation telemetry pipelines.
    """

    guild_id = models.CharField(max_length=30, primary_key=True)
    channel_id = models.CharField(max_length=30)
    enabled = models.BooleanField(default=True)

    class Meta(TimestampMixin.Meta):
        db_table = "moderation_log_config"

    def __str__(self) -> str:
        return f"<ModerationLogConfig guild={self.guild_id} channel={self.channel_id}>"


class ChannelPermissionSnapshot(TimestampMixin):
    """
    State backups tracking dynamic channel locks/unlock configurations.
    """

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


# Gatekeeper & Verification Infrastructure
class VerificationConfig(TimestampMixin):
    """
    Security verification nodes keeping automated onboarding paths isolated.
    """

    guild_id = models.CharField(max_length=30, primary_key=True)
    verify_channel_id = models.CharField(max_length=30, null=True, blank=True)
    log_channel_id = models.CharField(max_length=30, null=True, blank=True)
    verified_role_id = models.CharField(max_length=30, null=True, blank=True)
    unverified_role_id = models.CharField(max_length=30, null=True, blank=True)

    class Meta(TimestampMixin.Meta):
        db_table = "verification_config"

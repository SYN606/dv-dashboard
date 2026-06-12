import requests
from django.shortcuts import render, redirect
from django.contrib import messages

from bot.models import GuildConfig

API_BASE_URL = "https://discord.com/api/v10"
ADMIN_PERMISSION_BIT = 0x8


def homepage(request):
    discord_user = request.session.get("discord_user")
    access_token = request.session.get("access_token")

    admin_servers = []
    active_bot_guild_ids = set()
    bot_online = True

    if discord_user and access_token:
        headers = {"Authorization": f"Bearer {access_token}"}
        try:
            response = requests.get(
                f"{API_BASE_URL}/users/@me/guilds", headers=headers, timeout=5
            )

            if response.status_code == 401:
                request.session.flush()
                discord_user = None
            else:
                user_guilds = response.json()
                for guild in user_guilds:
                    perms = int(guild.get("permissions", 0))

                    if (perms & ADMIN_PERMISSION_BIT) == ADMIN_PERMISSION_BIT:
                        guild_id_str = str(guild["id"])

                        guild_config, created = GuildConfig.objects.get_or_create(
                            guild_id=guild_id_str,
                            defaults={"is_active": True},
                        )

                        if not guild_config.is_active:
                            guild_config.is_active = True
                            guild_config.save()

                        icon_hash = guild.get("icon")
                        icon_url = (
                            f"https://cdn.discordapp.com/icons/{guild_id_str}/{icon_hash}.png"
                            if icon_hash
                            else None
                        )

                        admin_servers.append(
                            {
                                "id": guild_id_str,
                                "name": guild["name"],
                                "icon": icon_url,
                                "has_bot": True,
                            }
                        )

                        active_bot_guild_ids.add(guild_id_str)

        except requests.exceptions.RequestException:
            messages.error(request, "Failed to connect to the Discord API gateway.")
            bot_online = False

    context = {
        "title": "DV Dashboard Core",
        "user": discord_user,
        "servers": admin_servers,
        "stats": {
            "shared_guilds": len(active_bot_guild_ids),
            "bot_online": bot_online,
            "ping_ms": 24 if bot_online else 0,
        },
    }
    return render(request, "index.html", context)


def guild_dashboard_gate(request, guild_id):
    discord_user = request.session.get("discord_user")
    access_token = request.session.get("access_token")

    if not discord_user or not access_token:
        return redirect("core:discord_login")

    guild_id_str = str(guild_id)

    headers = {"Authorization": f"Bearer {access_token}"}
    try:
        response = requests.get(
            f"{API_BASE_URL}/users/@me/guilds", headers=headers, timeout=5
        )

        if response.status_code != 200:
            messages.error(request, "Unable to verify server permissions.")
            return redirect("core:homepage")

        user_guilds = response.json()
        has_admin_perms = False

        for guild in user_guilds:
            if str(guild.get("id")) == guild_id_str:
                perms = int(guild.get("permissions", 0))
                if (perms & ADMIN_PERMISSION_BIT) == ADMIN_PERMISSION_BIT:
                    has_admin_perms = True
                break

        if not has_admin_perms:
            messages.error(
                request,
                "Access denied. You do not possess administrator rights for this server.",
            )
            return redirect("core:homepage")

    except requests.exceptions.RequestException:
        messages.error(
            request, "Authorization check failed due to an external network error."
        )
        return redirect("core:homepage")

    guild_config, created = GuildConfig.objects.get_or_create(
        guild_id=guild_id_str, defaults={"is_active": True}
    )

    if not guild_config.is_active:
        guild_config.is_active = True
        guild_config.save()

    return render(request, "dashboard_guild.html", {"guild_id": guild_id_str})

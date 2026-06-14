import requests
from django.shortcuts import render
from django.contrib import messages
from bot.models import GuildConfig

API_BASE_URL = "https://discord.com/api/v10"
ADMIN_PERMISSION_BIT = 0x8

def homepage(request):
    discord_user = request.session.get("discord_user")
    access_token = request.session.get("access_token")

    if not discord_user or not access_token:
        return render(request, "static_index.html", {"title": "DV Dashboard"})

    admin_servers = []
    active_bot_guild_ids = set()
    bot_online = True

    headers = {"Authorization": f"Bearer {access_token}"}
    try:
        response = requests.get(
            f"{API_BASE_URL}/users/@me/guilds", headers=headers, timeout=5
        )

        if response.status_code == 401:
            request.session.flush()
            return render(request, "static_index.html", {"title": "DV Dashboard"})
        
        elif response.status_code == 200:
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
        "servers": admin_servers if admin_servers else None,
        "stats": {
            "shared_guilds": len(active_bot_guild_ids),
            "bot_online": bot_online,
            "ping_ms": 24 if bot_online else 0,
        },
    }
    return render(request, "index.html", context)
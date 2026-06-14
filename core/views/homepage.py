import requests
from django.shortcuts import render
from django.contrib import messages
from bot.models import GuildConfig

API_BASE_URL = "https://discord.com/api/v10"
ADMIN_PERMISSION_BIT = 0x8

def homepage(request):
    user_session = request.session.get("user")
    access_token = request.session.get("access_token")
    if not user_session or not access_token:
        return render(request, "index.html", {"title": "DV Dashboard"})
    admin_servers = []
    active_bot_guild_ids = set()
    bot_online = True

    headers = {"Authorization": f"Bearer {access_token}"}
    try:
        response = requests.get(f"{API_BASE_URL}/users/@me/guilds", headers=headers, timeout=5)

        if response.status_code == 401:
            request.session.flush()
            return render(request, "index.html", {"title": "DV Dashboard"})
        
        elif response.status_code == 200:
            user_guilds = response.json()
            joined_guild_ids = set(
                GuildConfig.objects.filter(is_active=True).values_list("guild_id", flat=True)
            )
            for guild in user_guilds:
                perms = int(guild.get("permissions", 0))
                if (perms & ADMIN_PERMISSION_BIT) == ADMIN_PERMISSION_BIT:
                    guild_id_str = str(guild["id"])
                    has_bot = guild_id_str in joined_guild_ids
                    if has_bot:
                        active_bot_guild_ids.add(guild_id_str)
                    icon_hash = guild.get("icon")
                    icon_url = (
                        f"https://cdn.discordapp.com/icons/{guild_id_str}/{icon_hash}.png"
                        if icon_hash else None
                    )
                    admin_servers.append({
                        "id": guild_id_str,
                        "name": guild["name"],
                        "icon": icon_url,
                        "has_bot": has_bot,
                    })
    except requests.exceptions.RequestException:
        messages.error(request, "Failed to connect to the Discord API gateway.")
        bot_online = False
    context = {
        "title": "DV Dashboard Core",
        "user": user_session,
        "servers": admin_servers if admin_servers else None,
        "stats": {
            "shared_guilds": len(active_bot_guild_ids),
            "bot_online": bot_online,
            "ping_ms": 24 if bot_online else 0,
        },
    }
    return render(request, "index.html", context)
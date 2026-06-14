import requests
from django.shortcuts import render, redirect
from django.contrib import messages
from bot.models import GuildConfig
from bot.decorators import discord_login_required

API_BASE_URL = "https://discord.com/api/v10"
ADMIN_PERMISSION_BIT = 0x8


@discord_login_required
def guild_dashboard(request, guild_id):
    discord_user = request.session.get("discord_user")
    access_token = request.session.get("access_token")
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
        current_guild = None

        for guild in user_guilds:
            if str(guild.get("id")) == guild_id_str:
                perms = int(guild.get("permissions", 0))
                if (perms & ADMIN_PERMISSION_BIT) == ADMIN_PERMISSION_BIT:
                    current_guild = guild
                break

        if not current_guild:
            messages.error(
                request,
                "Access denied. You do not possess administrator rights for this server."
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

    if request.method == "POST":
        guild_config.is_active = request.POST.get("is_active") == "on"
        guild_config.save()
        messages.success(
            request, f"Configuration for {current_guild['name']} saved successfully."
        )
        return redirect("bot:guild_dashboard", guild_id=guild_id_str)

    icon_hash = current_guild.get("icon")
    icon_url = (
        f"https://cdn.discordapp.com/icons/{guild_id_str}/{icon_hash}.png"
        if icon_hash
        else None
    )

    context = {
        "title": f"Manage | {current_guild['name']}",
        "user": discord_user,
        "guild": {
            "id": guild_id_str,
            "name": current_guild["name"],
            "icon": icon_url,
        },
        "config": guild_config,
    }
    return render(request, "bot/dashboard_guild.html", context)

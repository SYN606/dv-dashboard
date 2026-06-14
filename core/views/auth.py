import os
import secrets
import requests
from django.shortcuts import redirect
from django.contrib import messages
from urllib.parse import urlencode

API_BASE_URL = "https://discord.com/api/v10"


def discord_login(request):
    state_token = secrets.token_urlsafe(16)
    request.session["oauth2_state"] = state_token

    params = {
        "client_id": os.getenv("DISCORD_CLIENT_ID"),
        "redirect_uri": os.getenv("DISCORD_REDIRECT_URI"),
        "response_type": "code",
        "scope": "identify guilds",
        "prompt": "none",
        "state": state_token,
    }
    return redirect(f"{API_BASE_URL}/oauth2/authorize?{urlencode(params)}")


def discord_callback(request):
    code = request.GET.get("code")
    state = request.GET.get("state")
    saved_state = request.session.pop("oauth2_state", None)

    if not state or state != saved_state:
        messages.error(request, "Security verification failed: State token mismatch.")
        return redirect("core:homepage")

    if not code:
        messages.error(request, "Authorization denied or missing code.")
        return redirect("core:homepage")

    token_payload = {
        "client_id": os.getenv("DISCORD_CLIENT_ID"),
        "client_secret": os.getenv("DISCORD_CLIENT_SECRET"),
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": os.getenv("DISCORD_REDIRECT_URI"),
    }

    try:
        token_response = requests.post(
            f"{API_BASE_URL}/oauth2/token", data=token_payload, timeout=5
        )
        if token_response.status_code != 200:
            messages.error(request, "Failed to exchange tokens with Discord.")
            return redirect("core:homepage")

        access_token = token_response.json().get("access_token")
        if not access_token:
            messages.error(request, "Missing access token from authentication payload.")
            return redirect("core:homepage")

        user_response = requests.get(
            f"{API_BASE_URL}/users/@me",
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=5,
        )
        if user_response.status_code != 200:
            messages.error(request, "Failed to fetch user profile.")
            return redirect("core:homepage")

        user_data = user_response.json()
        user_id_str = str(user_data["id"])
        owner_id = os.getenv("DISCORD_OWNER_ID")
        is_owner = owner_id and user_id_str == str(owner_id)
        if owner_id and not is_owner:
            messages.error(request, "Access Denied: Not an authorized operator.")
            return redirect("core:homepage")
        avatar_hash = user_data.get("avatar")
        if avatar_hash:
            avatar_url = (
                f"https://cdn.discordapp.com/avatars/{user_id_str}/{avatar_hash}.png"
            )
        else:
            avatar_url = f"https://cdn.discordapp.com/embed/avatars/{(int(user_id_str) >> 22) % 6}.png"

        request.session["access_token"] = access_token
        request.session["user"] = {
            "id": user_id_str,
            "username": user_data["username"],
            "global_name": user_data.get("global_name"),
            "avatar": avatar_url,
            "is_staff": bool(is_owner),
        }

        messages.success(
            request,
            f"Welcome back, {user_data.get('global_name') or user_data['username']}.",
        )
        return redirect("core:homepage")

    except requests.exceptions.RequestException:
        messages.error(request, "Network handshake error with Discord API gateway.")
        return redirect("core:homepage")


def discord_logout(request):
    request.session.flush()
    messages.warning(request, "Session terminated.")
    return redirect("core:homepage")

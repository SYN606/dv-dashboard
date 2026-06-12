import os
import requests
from django.shortcuts import redirect
from django.http import HttpResponse
from django.contrib import messages
from urllib.parse import urlencode

API_BASE_URL = "https://discord.com/api/v10"


def discord_login(request):
    """
    Redirect user to Discord OAuth.
    """
    params = {
        "client_id": os.getenv("DISCORD_CLIENT_ID"),
        "redirect_uri": os.getenv("DISCORD_REDIRECT_URI"),
        "response_type": "code",
        "scope": "identify guilds",
        "prompt": "none",  # Seamless re-auth if already authorized
    }

    oauth_url = f"{API_BASE_URL}/oauth2/authorize?{urlencode(params)}"
    return redirect(oauth_url)


def discord_callback(request):
    """
    Handle Discord OAuth callback, validate state, exchange tokens,
    and persist clean session parameters.
    """
    code = request.GET.get("code")
    if not code:
        messages.error(request, "Authorization denied or missing code from gateway.")
        return redirect("core:homepage")

    token_payload = {
        "client_id": os.getenv("DISCORD_CLIENT_ID"),
        "client_secret": os.getenv("DISCORD_CLIENT_SECRET"),
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": os.getenv("DISCORD_REDIRECT_URI"),
    }

    token_headers = {"Content-Type": "application/x-www-form-urlencoded"}

    try:
        # Exchange Auth Code for Access Token
        token_response = requests.post(
            f"{API_BASE_URL}/oauth2/token",
            data=token_payload,
            headers=token_headers,
            timeout=5,
        )

        if token_response.status_code != 200:
            return HttpResponse(
                "Failed to obtain Discord access token from gateway.", status=400
            )

        token_data = token_response.json()
        access_token = token_data.get("access_token")

        if not access_token:
            return HttpResponse(
                "Gateway token processing error: Missing access token.", status=400
            )

        # Fetch current user's profile metadata
        user_response = requests.get(
            f"{API_BASE_URL}/users/@me",
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=5,
        )

        if user_response.status_code != 200:
            return HttpResponse(
                "Failed to fetch profiles from Discord identification node.", status=400
            )

        user = user_response.json()

        # Enforce application owner restriction if configured
        owner_id = os.getenv("DISCORD_OWNER_ID")
        if owner_id and str(user["id"]) != str(owner_id):
            return HttpResponse(
                "Access Denied: Unauthorized Dashboard Operator.", status=403
            )

        avatar_hash = user.get("avatar")

        # CRITICAL FIX: Save access_token to the session so homepage can fetch guilds!
        request.session["access_token"] = access_token

        request.session["discord_user"] = {
            "id": user["id"],
            "username": user["username"],
            "global_name": user.get("global_name"),
            "avatar": avatar_hash,  # Pure string hash value
        }

        messages.success(
            request, f"Identity validated. Welcome back, {user['username']}."
        )
        return redirect("core:homepage")

    except requests.exceptions.RequestException:
        return HttpResponse(
            "Network timeout during Discord token handshake.", status=504
        )


def discord_logout(request):
    """
    Logout Discord session and clear memory nodes.
    """
    request.session.flush()
    return redirect("core:homepage")

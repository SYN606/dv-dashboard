from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def discord_login_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        discord_user = request.session.get("user")
        access_token = request.session.get("access_token")
        if not discord_user or not access_token:
            messages.warning(
                request, "Authentication required. Please sign in with Discord."
            )
            return redirect("core:discord_login")
        return view_func(request, *args, **kwargs)
    return _wrapped_view

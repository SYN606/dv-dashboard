from django.urls import path
from .views import (
    homepage,
    discord_login,
    discord_callback,
    discord_logout,
    terms_n_conditions,
    privay_policy,
    guild_dashboard_gate,  
)

app_name = "core"

urlpatterns = [
    path("", homepage, name="homepage"),
    path("login/", discord_login, name="discord_login"), 
    path("auth/discord/callback/", discord_callback, name="discord_callback"),
    path("logout/", discord_logout, name="discord_logout"),
    path("terms/", terms_n_conditions, name="terms"),
    path("privacy/", privay_policy, name="privacy"),
    path("dashboard/guild/<str:guild_id>/", guild_dashboard_gate, name="guild_dashboard"),
]
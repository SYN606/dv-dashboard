from django.urls import path
from .views import guild_dashboard

app_name = "bot"

urlpatterns = [
    path("guild/<str:guild_id>/", guild_dashboard, name="guild_dashboard"),
]

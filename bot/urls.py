from django.urls import path
from .views import dashboard

app_name = "bot"

urlpatterns = [path("", dashboard, name="dashbaord")]

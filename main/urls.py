from django.urls import path

from main.views import IndexView, health_check

app_name = "main"

urlpatterns = [
    path("health/", health_check, name="health"),
    path("", IndexView.as_view(), name="index"),
]

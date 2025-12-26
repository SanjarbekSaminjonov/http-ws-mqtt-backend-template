from django.urls import path

from apps.main.views import IndexView, check_mqtt_user, health_check

app_name = "main"

urlpatterns = [
    path("health/", health_check, name="health"),
    path("check-mqtt-user/", check_mqtt_user, name="check_mqtt_user"),
    path("", IndexView.as_view(), name="index"),
]

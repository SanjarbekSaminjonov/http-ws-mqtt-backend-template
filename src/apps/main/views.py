from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView


@csrf_exempt
def health_check(request):
    """Simple health check endpoint for Docker"""
    return JsonResponse({"status": "healthy"}, status=200)


@csrf_exempt
def check_mqtt_user(request):
    """Endpoint to verify MQTT user credentials"""
    username = request.POST.get("username")
    password = request.POST.get("password")

    # Replace these with your actual MQTT credentials
    VALID_USERNAME = settings.MQTT_USERNAME
    VALID_PASSWORD = settings.MQTT_PASSWORD

    print(f"{username=}, {password=}, {VALID_USERNAME=}, {VALID_PASSWORD=}")

    if username == VALID_USERNAME and password == VALID_PASSWORD:
        return JsonResponse({"authenticated": True}, status=200)
    else:
        return JsonResponse({"authenticated": False}, status=401)


class IndexView(TemplateView):
    template_name = "main/index.html"

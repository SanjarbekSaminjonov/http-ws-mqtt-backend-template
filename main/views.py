from django.http import JsonResponse
from django.views.generic import TemplateView


def health_check(request):
    """Simple health check endpoint for Docker"""
    return JsonResponse({"status": "healthy"}, status=200)


class IndexView(TemplateView):
    template_name = "main/index.html"

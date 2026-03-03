"""
URL configuration for hospital_project project.
"""
from django.contrib import admin
from django.http import JsonResponse
from django.urls import path, include

def health_check(_request):
    return JsonResponse({"status": "ok", "message": "API is running"})

urlpatterns = [
    path('', health_check, name='health-check'),
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
]

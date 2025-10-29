
from django.urls import path
from .views import api_redirect, health_check

urlpatterns = [
    path('not_found', api_redirect, name = 'api_redirect'),
    path('', health_check),
    path('healthz', health_check),
    path('healthz/', health_check)
]

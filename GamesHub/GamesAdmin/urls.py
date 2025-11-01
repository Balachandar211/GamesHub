
from django.urls import path
from .views import gamesAdmin

urlpatterns = [
    path('manage', gamesAdmin),
]

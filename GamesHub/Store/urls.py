
from django.urls import path
from .views import Home, gamesAdmin

urlpatterns = [
    path('home/', Home),
    path('gamesAdmin/', gamesAdmin)
]

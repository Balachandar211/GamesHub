
from django.urls import path
from .views import Home, gamesAdmin, userCart

urlpatterns = [
    path('home/', Home),
    path('gamesAdmin/', gamesAdmin),
    path('cart/', userCart)
]

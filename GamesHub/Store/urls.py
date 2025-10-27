
from django.urls import path
from .views import Home, gamesAdmin, userCart, WishlistUser

urlpatterns = [
    path('home', Home),
    path('gamesAdmin', gamesAdmin),
    path('cart', userCart),
    path('wishlist', WishlistUser)
]

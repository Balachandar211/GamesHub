
from django.urls import path
from .views import Home, userCart, WishlistUser

urlpatterns = [
    path('home', Home),
    path('cart', userCart),
    path('wishlist', WishlistUser)
]

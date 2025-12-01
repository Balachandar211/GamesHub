
from django.urls import path
from .views import Home, userCart, WishlistUser, featuredPage, library, wallet

urlpatterns = [
    path('home', Home),
    path('cart', userCart),
    path('wishlist', WishlistUser),
    path('featured', featuredPage),
    path('library', library),
    path('wallet', wallet)
]


from django.urls import path
from .views import Home, userCart, WishlistUser, featuredPage, library

urlpatterns = [
    path('home', Home),
    path('cart', userCart),
    path('wishlist', WishlistUser),
    path('featured', featuredPage),
    path('library', library)
]

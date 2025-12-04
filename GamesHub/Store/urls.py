
from django.urls import path
from .views import Home, UserCart, UserWishlist, featuredPage, library, wallet

urlpatterns = [
    path('home', Home),
    path('cart', UserCart.as_view()),
    path('wishlist', UserWishlist.as_view()),
    path('featured', featuredPage),
    path('library', library),
    path('wallet', wallet)
]

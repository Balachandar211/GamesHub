
from django.urls import path
from .views import Home, UserCart, UserWishlist, featuredPage, library, wallet, wallet_transaction, sale_view, sale_detail_view

urlpatterns = [
    path('home', Home),
    path('cart', UserCart.as_view()),
    path('wishlist', UserWishlist.as_view()),
    path('featured', featuredPage),
    path('library', library),
    path('wallet', wallet),
    path('wallet/transactions',wallet_transaction),
    path('sales', sale_view),
    path('sales/<int:pk>', sale_detail_view)
]

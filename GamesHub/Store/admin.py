from django.contrib import admin

from .models import Game, Cart, Wishlist, GamesMedia, Wallet, WalletTransaction, Sale

admin.site.register(Game)
admin.site.register(Cart)
admin.site.register(Wishlist)
admin.site.register(GamesMedia)
admin.site.register(Wallet)
admin.site.register(WalletTransaction)
admin.site.register(Sale)
from django.contrib import admin

from .models import Game, Cart, Wishlist

admin.site.register(Game)
admin.site.register(Cart)
admin.site.register(Wishlist)
# Register your models here.

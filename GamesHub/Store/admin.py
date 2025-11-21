from django.contrib import admin

from .models import Game, Cart, Wishlist, GamesMedia

admin.site.register(Game)
admin.site.register(Cart)
admin.site.register(Wishlist)
admin.site.register(GamesMedia)
# Register your models here.

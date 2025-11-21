
from django.urls import path
from .views import gamesAdmin, manageGames, manageGamesMedia

urlpatterns = [
    path('manage', gamesAdmin),
    path('manage_game/<int:pk>', manageGames),
    path('manage_game_media/<int:pk>', manageGamesMedia)
]

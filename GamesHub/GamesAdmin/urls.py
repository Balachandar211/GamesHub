
from django.urls import path
from .views import games_admin, manage_games, manage_games_media, game_media_admin

urlpatterns = [
    path('manage', games_admin),
    path('manage_game/<int:pk>', manage_games),
    path('manage_game_media/<int:pk>', manage_games_media),
    path('update_game_media', game_media_admin)
]

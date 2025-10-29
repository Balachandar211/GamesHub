
from django.urls import path
from .views import purchase, games_detail, buy

urlpatterns = [
    path('purchase', purchase),
    path('buy', buy, name="buy"),
    path('<int:pk>', games_detail)
]

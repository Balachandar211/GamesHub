
from django.urls import path
from .views import purchase, games_detail, buy, comment

urlpatterns = [
    path('purchase', purchase),
    path('buy', buy, name="buy"),
    path('detail/<int:pk>', games_detail),
    path('detail/<int:pk>/comment', comment)
]

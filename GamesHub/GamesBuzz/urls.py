
from django.urls import path
from .views import purchase

urlpatterns = [
    path('purchase/', purchase),
    path('buy/', purchase, name="buy"),
]


from django.urls import path
from .views import monitor_1, monitor_2

urlpatterns = [
    path('monitor_one', monitor_1),
    path('monitor_two', monitor_2)
]

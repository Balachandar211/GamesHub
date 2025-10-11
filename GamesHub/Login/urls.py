
from django.urls import path
from .views import SignUp, Login

urlpatterns = [
    path('signup/', SignUp),
    path('login/', Login),
]

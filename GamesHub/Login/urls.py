
from django.urls import path
from .views import SignUp, Login, Forgot_Password

urlpatterns = [
    path('signup/', SignUp),
    path('login/', Login),
    path('forgot_password/', Forgot_Password)
]

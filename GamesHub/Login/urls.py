
from django.urls import path
from .views import SignUp, Login, Forgot_Password, extendSession, logout

urlpatterns = [
    path('signup/', SignUp),
    path('login/', Login),
    path('forgot_password/', Forgot_Password),
    path('extend_session/', extendSession),
    path('logout/', logout)
]

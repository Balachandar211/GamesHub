
from django.urls import path
from .views import SignUp, Login, Forgot_Password, extendSession, logout, delete_user, update_user

urlpatterns = [
    path('signup/', SignUp),
    path('login/', Login),
    path('forgot_password/', Forgot_Password),
    path('extend_session/', extendSession),
    path('logout/', logout),
    path('delete_user/', delete_user),
    path('update_user/', update_user)
]

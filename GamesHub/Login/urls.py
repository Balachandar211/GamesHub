
from django.urls import path
from .views import SignUp, Login, Forgot_Password, extendSession, logout, delete_user, update_user, recover_user

urlpatterns = [
    path('signup', SignUp),
    path('session/login', Login),
    path('forgot_password', Forgot_Password),
    path('session/refresh', extendSession),
    path('session/logout', logout),
    path('delete_user', delete_user),
    path('update_user', update_user),
    path('recover_user', recover_user)
]

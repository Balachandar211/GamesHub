
from django.urls import path
from .views import SignUp, Login, Forgot_Password, extendSession, logout, delete_user, update_user, api_redirect, recover_user, health_check

urlpatterns = [
    path('signup', SignUp),
    path('login', Login),
    path('forgot_password', Forgot_Password),
    path('extend_session', extendSession),
    path('logout', logout),
    path('delete_user', delete_user),
    path('update_user', update_user),
    path('', api_redirect, name = 'api_redirect'),
    path('recover_user', recover_user)
]


from django.urls import path
from .views import SignUp, Login, Forgot_Password, extendSession, logout, delete_user, update_user, recover_user, profile, validate_email, validate_email_token, admin_user_creation
from django.urls import re_path

urlpatterns = [
    path('signup', SignUp),
    path('session/login', Login),
    path('forgot_password', Forgot_Password),
    path('session/refresh', extendSession),
    path('session/logout', logout),
    path('delete_user', delete_user),
    path('update_user', update_user),
    path('recover_user', recover_user),
    path('profile', profile),
    path('validate_email', validate_email),
    re_path(r"^validate/(?P<token>.+)$", validate_email_token),
    path('store_admin', admin_user_creation)
]

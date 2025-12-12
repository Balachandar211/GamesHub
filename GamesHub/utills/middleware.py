from django.http import HttpResponseRedirect
from django.urls import resolve, reverse, Resolver404
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.models import AnonymousUser
from .models import BlacklistedAccessToken
from GamesHub.settings import REDIS_CLIENT
from rest_framework_simplejwt.authentication import JWTAuthentication
import re

class EndpointRedirectMiddleware(MiddlewareMixin):
    def process_request(self, request):
        path = request.path_info
        
        try:
            resolve(path)
            return None
        except Resolver404:
            return HttpResponseRedirect(reverse('api_redirect'))


class AccessRestrictionMiddleware(MiddlewareMixin):
    def process_request(self, request):
        try:
            if 'HTTP_AUTHORIZATION' in request.META:
                if BlacklistedAccessToken.objects.filter(access_token = request.META['HTTP_AUTHORIZATION'].split(' ')[1]).exists():
                    del request.META['HTTP_AUTHORIZATION']
                    request.user = AnonymousUser()
                    return None
        except Exception as e:
            pass

class UserTrackingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        try:
            jwt_auth = JWTAuthentication()

            user_auth_tuple = jwt_auth.authenticate(request)
            if user_auth_tuple is not None:
                user, auth = user_auth_tuple
                
            if user.is_authenticated and "/detail/" in request.path:
                match = re.search(r"(?<=detail/)\d+(?=/|$)", request.path)
                
                game_id = int(match.group())
                user    = user.get_username()
                
                REDIS_CLIENT.hincrby(user, game_id, 1)
                REDIS_CLIENT.expire(user, 60*60*24*30)

        except Exception as e:
            pass
        

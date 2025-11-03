from django.http import HttpResponseRedirect
from django.urls import resolve, reverse, Resolver404
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.models import AnonymousUser
from .models import BlacklistedAccessToken

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
        

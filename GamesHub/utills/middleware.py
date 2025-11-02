from django.http import HttpResponseRedirect
from django.urls import resolve, reverse, Resolver404
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.models import AnonymousUser

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
            cookie = request.COOKIES.get('Refresh_Token')
            if cookie == None:
                if 'HTTP_AUTHORIZATION' in request.META:
                    del request.META['HTTP_AUTHORIZATION']
                request.user = AnonymousUser()
                return None
        except:
            pass
        

from django.http import HttpResponseRedirect
from django.urls import resolve, reverse, Resolver404
from django.utils.deprecation import MiddlewareMixin

class EndpointRedirectMiddleware(MiddlewareMixin):
    def process_request(self, request):
        path = request.path_info
        
        if path == '/':
            return None   

        try:
            resolve(path)
            return None
        except Resolver404:
            return HttpResponseRedirect(reverse('api_redirect'))
        

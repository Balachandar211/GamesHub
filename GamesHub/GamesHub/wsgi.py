"""
WSGI config for GamesHub project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
import socket

# Monkey-patch DNS resolution to prefer IPv4
def force_ipv4_only():
    original_getaddrinfo = socket.getaddrinfo
    def getaddrinfo_ipv4(*args, **kwargs):
        return [info for info in original_getaddrinfo(*args, **kwargs) if info[0] == socket.AF_INET]
    socket.getaddrinfo = getaddrinfo_ipv4

force_ipv4_only()




from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GamesHub.settings')

application = get_wsgi_application()

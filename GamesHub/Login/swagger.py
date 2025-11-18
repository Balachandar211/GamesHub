from drf_spectacular.extensions import OpenApiAuthenticationExtension

class LenientJWTAuthScheme(OpenApiAuthenticationExtension):
    target_class = 'Login.auth.LenientJWTAuthentication'
    name = 'BearerAuth'

    def get_security_definition(self, auto_schema):
        return {
            'type': 'http',
            'scheme': 'bearer',
            'bearerFormat': 'JWT',
        }

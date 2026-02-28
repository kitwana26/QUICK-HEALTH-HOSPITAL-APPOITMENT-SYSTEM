from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .models import User


class TokenAuthentication(BaseAuthentication):
    """Custom token authentication matching Flask implementation"""
    
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization', '')
        
        if not auth_header:
            return None
            
        if not auth_header.startswith('Token '):
            return None
            
        token = auth_header.split(' ', 1)[1]
        
        try:
            user = User.objects.get(token=token)
            return (user, token)
        except User.DoesNotExist:
            raise AuthenticationFailed('Invalid token')
    
    def authenticate_header(self, request):
        return 'Token'

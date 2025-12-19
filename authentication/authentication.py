"""
Custom JWT Authentication using HTTP-only cookies.
"""
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken


class CookieJWTAuthentication(JWTAuthentication):
    """
    Custom JWT authentication class that reads token from cookies.
    """

    def authenticate(self, request):
        """
        Authenticate using JWT token from cookie.
        """
        cookie_name = 'access_token'
        raw_token = request.COOKIES.get(cookie_name)

        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token)

        try:
            return self.get_user(validated_token), validated_token
        except InvalidToken:
            return None

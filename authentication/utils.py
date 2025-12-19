"""
Utility functions for authentication app.
"""
from django.conf import settings


def set_access_cookie(response, access_token):
    """Set access token cookie on response."""
    response.set_cookie(
        key='access_token',
        value=str(access_token),
        httponly=settings.JWT_COOKIE_HTTP_ONLY,
        secure=settings.JWT_COOKIE_SECURE,
        samesite=settings.JWT_COOKIE_SAMESITE,
        max_age=settings.JWT_COOKIE_MAX_AGE
    )


def set_refresh_cookie(response, refresh_token):
    """Set refresh token cookie on response."""
    response.set_cookie(
        key='refresh_token',
        value=str(refresh_token),
        httponly=settings.JWT_COOKIE_HTTP_ONLY,
        secure=settings.JWT_COOKIE_SECURE,
        samesite=settings.JWT_COOKIE_SAMESITE,
        max_age=settings.JWT_COOKIE_MAX_AGE
    )


def delete_auth_cookies(response):
    """Delete authentication cookies from response."""
    response.delete_cookie('access_token')
    response.delete_cookie('refresh_token')


def create_success_response(detail, status_code):
    """Create success response with detail message."""
    from rest_framework.response import Response
    return Response({'detail': detail}, status=status_code)


def create_error_response(detail, status_code):
    """Create error response with detail message."""
    from rest_framework.response import Response
    return Response({'detail': detail}, status=status_code)

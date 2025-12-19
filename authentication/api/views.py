"""
Views for authentication app.
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.contrib.auth import authenticate

from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    UserSerializer
)
from ..utils import (
    set_access_cookie,
    set_refresh_cookie,
    delete_auth_cookies,
    create_success_response,
    create_error_response
)


@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    """Register a new user."""
    serializer = RegisterSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    serializer.save()
    return create_success_response(
        'User created successfully!',
        status.HTTP_201_CREATED
    )


def authenticate_user(username, password):
    """Authenticate user with credentials."""
    return authenticate(username=username, password=password)


def create_login_response(user):
    """Create login response with tokens."""
    refresh = RefreshToken.for_user(user)
    response = Response(
        {'detail': 'Login successfully!', 'user': UserSerializer(user).data},
        status=status.HTTP_200_OK
    )
    set_access_cookie(response, refresh.access_token)
    set_refresh_cookie(response, refresh)
    return response


def validate_and_authenticate(serializer):
    """Validate serializer and authenticate user."""
    if not serializer.is_valid():
        return None, Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
    user = authenticate_user(
        serializer.validated_data['username'],
        serializer.validated_data['password']
    )
    return user, None


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """Login user and set auth cookies."""
    serializer = LoginSerializer(data=request.data)
    user, error_response = validate_and_authenticate(serializer)

    if error_response:
        return error_response
    if not user:
        return create_error_response(
            'Invalid credentials',
            status.HTTP_401_UNAUTHORIZED
        )
    return create_login_response(user)


def blacklist_refresh_token(refresh_token):
    """Blacklist the refresh token."""
    if refresh_token:
        token = RefreshToken(refresh_token)
        token.blacklist()


def create_logout_response():
    """Create logout success response."""
    response = create_success_response(
        'Log-Out successfully! All Tokens will be deleted. '
        'Refresh token is now invalid.',
        status.HTTP_200_OK
    )
    delete_auth_cookies(response)
    return response


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """Logout user and blacklist tokens."""
    try:
        blacklist_refresh_token(request.COOKIES.get('refresh_token'))
        return create_logout_response()
    except TokenError:
        return create_error_response(
            'Invalid or expired token',
            status.HTTP_400_BAD_REQUEST
        )


def create_refresh_response(access_token):
    """Create refresh token response."""
    response = Response(
        {'detail': 'Token refreshed', 'access': str(access_token)},
        status=status.HTTP_200_OK
    )
    set_access_cookie(response, access_token)
    return response


def process_token_refresh(refresh_token):
    """Process token refresh and return response or error."""
    try:
        token = RefreshToken(refresh_token)
        return create_refresh_response(token.access_token), None
    except TokenError:
        error = create_error_response(
            'Invalid or expired refresh token',
            status.HTTP_401_UNAUTHORIZED
        )
        return None, error


@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_token_view(request):
    """Refresh access token using refresh token from cookie."""
    refresh_token = request.COOKIES.get('refresh_token')
    if not refresh_token:
        return create_error_response(
            'Refresh token not found',
            status.HTTP_401_UNAUTHORIZED
        )

    response, error = process_token_refresh(refresh_token)
    return response if response else error

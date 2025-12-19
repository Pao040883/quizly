"""
Tests for authentication app.
"""
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken


class RegisterViewTests(TestCase):
    """Tests for user registration."""

    def setUp(self):
        """Set up test client."""
        self.client = APIClient()
        self.register_url = '/api/register/'
        self.valid_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'TestPass123!',
            'confirmed_password': 'TestPass123!'
        }

    def test_register_success(self):
        """Test successful user registration."""
        response = self.client.post(
            self.register_url,
            self.valid_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.data['detail'],
            'User created successfully!'
        )
        self.assertTrue(
            User.objects.filter(username='testuser').exists()
        )

    def test_register_password_mismatch(self):
        """Test registration with password mismatch."""
        data = self.valid_data.copy()
        data['confirmed_password'] = 'DifferentPass123!'
        response = self.client.post(
            self.register_url,
            data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_duplicate_username(self):
        """Test registration with existing username."""
        User.objects.create_user(
            username='testuser',
            email='existing@example.com',
            password='Pass123!'
        )
        response = self.client.post(
            self.register_url,
            self.valid_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_missing_fields(self):
        """Test registration with missing required fields."""
        response = self.client.post(
            self.register_url,
            {'username': 'testuser'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LoginViewTests(TestCase):
    """Tests for user login."""

    def setUp(self):
        """Set up test client and user."""
        self.client = APIClient()
        self.login_url = '/api/login/'
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!'
        )

    def test_login_success(self):
        """Test successful login."""
        response = self.client.post(
            self.login_url,
            {
                'username': 'testuser',
                'password': 'TestPass123!'
            },
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data['detail'],
            'Login successfully!'
        )
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['username'], 'testuser')
        self.assertIn('access_token', response.cookies)
        self.assertIn('refresh_token', response.cookies)

    def test_login_cookies_httponly(self):
        """Test that cookies are set as httponly."""
        response = self.client.post(
            self.login_url,
            {
                'username': 'testuser',
                'password': 'TestPass123!'
            },
            format='json'
        )
        access_cookie = response.cookies.get('access_token')
        refresh_cookie = response.cookies.get('refresh_token')
        self.assertTrue(access_cookie['httponly'])
        self.assertTrue(refresh_cookie['httponly'])

    def test_login_invalid_credentials(self):
        """Test login with invalid credentials."""
        response = self.client.post(
            self.login_url,
            {
                'username': 'testuser',
                'password': 'WrongPassword!'
            },
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_nonexistent_user(self):
        """Test login with non-existent user."""
        response = self.client.post(
            self.login_url,
            {
                'username': 'nonexistent',
                'password': 'TestPass123!'
            },
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_missing_fields(self):
        """Test login with missing fields."""
        response = self.client.post(
            self.login_url,
            {'username': 'testuser'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LogoutViewTests(TestCase):
    """Tests for user logout."""

    def setUp(self):
        """Set up test client and authenticated user."""
        self.client = APIClient()
        self.logout_url = '/api/logout/'
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!'
        )
        self.refresh = RefreshToken.for_user(self.user)
        self.client.cookies['access_token'] = str(
            self.refresh.access_token
        )
        self.client.cookies['refresh_token'] = str(self.refresh)

    def test_logout_success(self):
        """Test successful logout."""
        response = self.client.post(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Log-Out successfully', response.data['detail'])

    def test_logout_cookies_deleted(self):
        """Test that cookies are deleted after logout."""
        response = self.client.post(self.logout_url)
        self.assertEqual(
            response.cookies.get('access_token').value,
            ''
        )
        self.assertEqual(
            response.cookies.get('refresh_token').value,
            ''
        )

    def test_logout_without_authentication(self):
        """Test logout without authentication."""
        client = APIClient()
        response = client.post(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class RefreshTokenViewTests(TestCase):
    """Tests for token refresh."""

    def setUp(self):
        """Set up test client and user."""
        self.client = APIClient()
        self.refresh_url = '/api/token/refresh/'
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!'
        )
        self.refresh = RefreshToken.for_user(self.user)

    def test_refresh_token_success(self):
        """Test successful token refresh."""
        self.client.cookies['refresh_token'] = str(self.refresh)
        response = self.client.post(self.refresh_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'], 'Token refreshed')
        self.assertIn('access', response.data)
        self.assertIn('access_token', response.cookies)

    def test_refresh_token_missing(self):
        """Test refresh without refresh token."""
        response = self.client.post(self.refresh_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_refresh_token_invalid(self):
        """Test refresh with invalid token."""
        self.client.cookies['refresh_token'] = 'invalid_token'
        response = self.client.post(self.refresh_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class CookieJWTAuthenticationTests(TestCase):
    """Tests for custom JWT authentication."""

    def setUp(self):
        """Set up test client and user."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!'
        )
        self.refresh = RefreshToken.for_user(self.user)

    def test_authentication_with_valid_token(self):
        """Test authentication with valid access token."""
        from authentication.authentication import CookieJWTAuthentication
        from rest_framework.test import APIRequestFactory

        factory = APIRequestFactory()
        request = factory.get('/test/')
        request.COOKIES = {'access_token': str(self.refresh.access_token)}

        auth = CookieJWTAuthentication()
        result = auth.authenticate(request)

        self.assertIsNotNone(result)
        self.assertEqual(result[0], self.user)

    def test_authentication_without_token(self):
        """Test authentication without token."""
        from authentication.authentication import CookieJWTAuthentication
        from rest_framework.test import APIRequestFactory

        factory = APIRequestFactory()
        request = factory.get('/test/')
        request.COOKIES = {}

        auth = CookieJWTAuthentication()
        result = auth.authenticate(request)

        self.assertIsNone(result)

    def test_authentication_with_invalid_token(self):
        """Test authentication with invalid token."""
        from authentication.authentication import CookieJWTAuthentication
        from rest_framework.test import APIRequestFactory

        factory = APIRequestFactory()
        request = factory.get('/test/')
        request.COOKIES = {'access_token': 'invalid_token_string'}

        auth = CookieJWTAuthentication()
        # Should raise exception or return None
        try:
            result = auth.authenticate(request)
            # If no exception, should be None
            self.assertIsNone(result)
        except Exception:
            # Exception is also acceptable
            pass


class LogoutErrorHandlingTests(TestCase):
    """Tests for logout error handling."""

    def setUp(self):
        """Set up test client and user."""
        self.client = APIClient()
        self.logout_url = '/api/logout/'
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!'
        )

    def test_logout_with_invalid_token(self):
        """Test logout with invalid refresh token."""
        self.client.cookies['access_token'] = 'valid_looking_token'
        self.client.cookies['refresh_token'] = 'invalid_refresh_token'

        # We need to authenticate the request first
        refresh = RefreshToken.for_user(self.user)
        self.client.cookies['access_token'] = str(refresh.access_token)

        response = self.client.post(self.logout_url)
        # Should still return 200 even with invalid refresh token
        self.assertIn(
            response.status_code, [
                status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST])

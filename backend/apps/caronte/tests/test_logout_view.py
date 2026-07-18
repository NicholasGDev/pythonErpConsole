# backend/apps/caronte/tests/test_logout_view.py
from django.urls import reverse
from unittest.mock import patch
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.exceptions import AuthenticationFailed

from apps.caronte.models import User


class LogoutViewTests(APITestCase):
    """POST /api/auth/logout/  (requires authentication)"""

    url = reverse('auth-logout')

    def setUp(self):
        self.user = User.objects.create_user(
            email='user@test.com', name='Test User', password='Senha@123'
        )
        self.client.force_authenticate(user=self.user)

    @patch('apps.caronte.services.auth_service.AuthService.logout')
    def test_returns_200_on_successful_logout(self, mock_logout):
        response = self.client.post(self.url, {'refresh': 'valid_token'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_logout.assert_called_once_with('valid_token')

    def test_returns_400_when_refresh_token_absent(self):
        response = self.client.post(self.url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_returns_401_when_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.post(self.url, {'refresh': 'token'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @patch('apps.caronte.services.auth_service.AuthService.logout')
    def test_returns_401_on_invalid_refresh_token(self, mock_logout):
        mock_logout.side_effect = AuthenticationFailed('Token inválido.')
        response = self.client.post(self.url, {'refresh': 'bad'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

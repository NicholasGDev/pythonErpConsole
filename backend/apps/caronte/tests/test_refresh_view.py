# backend/apps/caronte/tests/test_refresh_view.py
from django.urls import reverse
from unittest.mock import patch
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.exceptions import AuthenticationFailed


class RefreshViewTests(APITestCase):
    """POST /api/auth/refresh/"""

    url = reverse('auth-refresh')

    @patch('apps.caronte.services.auth_service.AuthService.refresh')
    def test_returns_200_and_new_tokens_on_valid_refresh(self, mock_refresh):
        mock_refresh.return_value = {'access': 'new_acc', 'refresh': 'new_ref'}
        response = self.client.post(self.url, {'refresh': 'valid_token'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_returns_400_when_refresh_token_absent(self):
        response = self.client.post(self.url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('apps.caronte.services.auth_service.AuthService.refresh')
    def test_returns_401_on_invalid_token(self, mock_refresh):
        mock_refresh.side_effect = AuthenticationFailed('Token inválido.')
        response = self.client.post(self.url, {'refresh': 'bad'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @patch('apps.caronte.services.auth_service.AuthService.refresh')
    def test_returns_401_on_revoked_token(self, mock_refresh):
        mock_refresh.side_effect = AuthenticationFailed('Token revogado.')
        response = self.client.post(self.url, {'refresh': 'old_token'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

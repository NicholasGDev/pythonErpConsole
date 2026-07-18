# backend/apps/caronte/tests/test_login_view.py
from django.urls import reverse
from unittest.mock import patch
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.exceptions import AuthenticationFailed, PermissionDenied


class LoginViewTests(APITestCase):
    """POST /api/auth/login/"""

    url = reverse('auth-login')
    valid_payload = {'email': 'user@test.com', 'password': 'Senha@123'}

    @patch('apps.caronte.services.auth_service.AuthService.login')
    def test_returns_200_and_tokens_on_valid_credentials(self, mock_login):
        mock_login.return_value = {'access': 'acc', 'refresh': 'ref'}
        response = self.client.post(self.url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_returns_400_on_missing_fields(self):
        response = self.client.post(self.url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_returns_400_on_invalid_email_format(self):
        response = self.client.post(self.url, {'email': 'not-an-email', 'password': 'x'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('apps.caronte.services.auth_service.AuthService.login')
    def test_returns_401_on_wrong_credentials(self, mock_login):
        mock_login.side_effect = AuthenticationFailed('Credenciais inválidas.')
        response = self.client.post(self.url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @patch('apps.caronte.services.auth_service.AuthService.login')
    def test_returns_403_on_locked_account(self, mock_login):
        mock_login.side_effect = PermissionDenied('Conta bloqueada.')
        response = self.client.post(self.url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

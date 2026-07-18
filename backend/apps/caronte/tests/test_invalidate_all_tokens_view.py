# backend/apps/caronte/tests/test_invalidate_all_tokens_view.py
from django.urls import reverse
from unittest.mock import patch
from rest_framework import status
from rest_framework.test import APITestCase

from apps.caronte.models import User


class InvalidateAllTokensViewTests(APITestCase):
    """POST /api/auth/invalidate-tokens/  (requires authentication)"""

    url = reverse('auth-invalidate')

    def setUp(self):
        self.user = User.objects.create_user(
            email='user@test.com', name='Test User', password='Senha@123'
        )
        self.client.force_authenticate(user=self.user)

    @patch('apps.caronte.services.auth_service.AuthService.invalidate_all_tokens')
    def test_returns_200_and_revokes_all_tokens(self, mock_invalidate):
        response = self.client.post(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_invalidate.assert_called_once_with(self.user.id)

    def test_returns_401_when_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.post(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

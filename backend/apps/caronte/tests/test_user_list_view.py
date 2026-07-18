# backend/apps/caronte/tests/test_user_list_view.py
from django.urls import reverse
from unittest.mock import patch
from rest_framework import status
from rest_framework.test import APITestCase

from apps.caronte.models import User


def _create_user(email='user@test.com', name='Test User', password='Senha@123', is_staff=False):
    return User.objects.create_user(email=email, name=name, password=password, is_staff=is_staff)


class UserListViewGetTests(APITestCase):
    """GET /api/users/  (admin only)"""

    url = reverse('user-list')

    def setUp(self):
        self.admin = _create_user(email='admin@test.com', name='Admin', is_staff=True)
        self.normal = _create_user()

    @patch('apps.caronte.services.user_service.UserService.list_users')
    def test_returns_200_for_admin(self, mock_list):
        mock_list.return_value = []
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_list.assert_called_once()

    def test_returns_403_for_non_admin(self):
        self.client.force_authenticate(user=self.normal)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_returns_401_when_unauthenticated(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class UserListViewPostTests(APITestCase):
    """POST /api/users/  (admin only)"""

    url = reverse('user-list')

    def setUp(self):
        self.admin = _create_user(email='admin@test.com', name='Admin', is_staff=True)
        self.normal = _create_user()

    @patch('apps.caronte.services.user_service.UserService.create_user')
    def test_returns_201_when_admin_creates_valid_user(self, mock_create):
        mock_create.return_value = self.admin
        self.client.force_authenticate(user=self.admin)
        payload = {'name': 'New User', 'email': 'new@test.com', 'password': 'NewPass@1'}
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_returns_400_on_missing_payload(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(self.url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_returns_400_on_short_password(self):
        self.client.force_authenticate(user=self.admin)
        payload = {'name': 'X', 'email': 'x@test.com', 'password': '123'}
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_returns_403_for_non_admin(self):
        self.client.force_authenticate(user=self.normal)
        payload = {'name': 'X', 'email': 'x@test.com', 'password': 'NewPass@1'}
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

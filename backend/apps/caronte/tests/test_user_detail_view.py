# backend/apps/caronte/tests/test_user_detail_view.py
from django.urls import reverse
from unittest.mock import patch
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.test import APITestCase

from apps.caronte.models import User


def _create_user(email='user@test.com', name='Test User', password='Senha@123'):
    return User.objects.create_user(email=email, name=name, password=password)


class UserDetailViewGetTests(APITestCase):
    """GET /api/users/<id>/"""

    def setUp(self):
        self.user = _create_user()
        self.client.force_authenticate(user=self.user)

    @patch('apps.caronte.services.user_service.UserService.get_user_by_id')
    def test_returns_200_when_user_found(self, mock_get):
        mock_get.return_value = self.user
        response = self.client.get(reverse('user-detail', kwargs={'user_id': self.user.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_get.assert_called_once_with(self.user.id)

    @patch('apps.caronte.services.user_service.UserService.get_user_by_id')
    def test_returns_404_when_user_not_found(self, mock_get):
        mock_get.side_effect = ObjectDoesNotExist()
        response = self.client.get(reverse('user-detail', kwargs={'user_id': 9999}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_returns_401_when_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(reverse('user-detail', kwargs={'user_id': self.user.id}))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class UserDetailViewPatchTests(APITestCase):
    """PATCH /api/users/<id>/"""

    def setUp(self):
        self.user = _create_user()
        self.client.force_authenticate(user=self.user)

    @patch('apps.caronte.services.user_service.UserService.update_user')
    def test_returns_200_on_successful_update(self, mock_update):
        mock_update.return_value = self.user
        response = self.client.patch(
            reverse('user-detail', kwargs={'user_id': self.user.id}),
            {'name': 'Updated Name'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_update.assert_called_once()

    @patch('apps.caronte.services.user_service.UserService.update_user')
    def test_returns_404_when_user_not_found(self, mock_update):
        mock_update.side_effect = ObjectDoesNotExist()
        response = self.client.patch(
            reverse('user-detail', kwargs={'user_id': 9999}),
            {'name': 'X'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_returns_401_when_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.patch(
            reverse('user-detail', kwargs={'user_id': self.user.id}),
            {'name': 'X'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class UserDetailViewDeleteTests(APITestCase):
    """DELETE /api/users/<id>/"""

    def setUp(self):
        self.user = _create_user()
        self.client.force_authenticate(user=self.user)

    @patch('apps.caronte.services.user_service.UserService.delete_user')
    def test_returns_204_on_successful_delete(self, mock_delete):
        response = self.client.delete(reverse('user-detail', kwargs={'user_id': self.user.id}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        mock_delete.assert_called_once_with(self.user.id)

    @patch('apps.caronte.services.user_service.UserService.delete_user')
    def test_returns_404_when_user_not_found(self, mock_delete):
        mock_delete.side_effect = ObjectDoesNotExist()
        response = self.client.delete(reverse('user-detail', kwargs={'user_id': 9999}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_returns_401_when_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.delete(reverse('user-detail', kwargs={'user_id': self.user.id}))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

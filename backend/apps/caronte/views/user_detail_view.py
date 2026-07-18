# backend/apps/caronte/views/user_detail_view.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ObjectDoesNotExist

from apps.caronte.services.user_service import UserService
from apps.caronte.serializers import UserSerializer


class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id: int):
        try:
            user = UserService.get_user_by_id(user_id)
        except ObjectDoesNotExist as e:
            return Response({'detail': str(e)}, status=status.HTTP_404_NOT_FOUND)

        return Response(UserSerializer(user).data, status=status.HTTP_200_OK)

    def patch(self, request, user_id: int):
        try:
            user = UserService.update_user(user_id, request.data)
        except ObjectDoesNotExist as e:
            return Response({'detail': str(e)}, status=status.HTTP_404_NOT_FOUND)

        return Response(UserSerializer(user).data, status=status.HTTP_200_OK)

    def delete(self, request, user_id: int):
        try:
            UserService.delete_user(user_id)
        except ObjectDoesNotExist as e:
            return Response({'detail': str(e)}, status=status.HTTP_404_NOT_FOUND)

        return Response(status=status.HTTP_204_NO_CONTENT)

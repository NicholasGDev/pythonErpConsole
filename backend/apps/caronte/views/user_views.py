# backend/apps/caronte/views/user_views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.core.exceptions import ObjectDoesNotExist

from apps.caronte.services.user_service import UserService
from apps.caronte.serializers import UserSerializer, CreateUserSerializer


class UserListView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        users = UserService.list_users()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = CreateUserSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = UserService.create_user(serializer.validated_data)
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


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
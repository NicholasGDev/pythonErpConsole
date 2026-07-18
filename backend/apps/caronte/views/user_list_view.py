# backend/apps/caronte/views/user_list_view.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser

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

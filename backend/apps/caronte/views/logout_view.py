# backend/apps/caronte/views/logout_view.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from apps.caronte.services.auth_service import AuthService


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({'detail': 'refresh token obrigatório.'}, status=status.HTTP_400_BAD_REQUEST)

        AuthService.logout(refresh_token)
        return Response({'detail': 'Logout realizado com sucesso.'}, status=status.HTTP_200_OK)

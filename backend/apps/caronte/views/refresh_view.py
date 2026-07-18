# backend/apps/caronte/views/refresh_view.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from apps.caronte.services.auth_service import AuthService


class RefreshView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({'detail': 'refresh token obrigatório.'}, status=status.HTTP_400_BAD_REQUEST)

        tokens = AuthService.refresh(refresh_token)
        return Response(tokens, status=status.HTTP_200_OK)

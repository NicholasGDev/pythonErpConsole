# backend/apps/caronte/views/auth_views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated

from apps.caronte.services.auth_service import AuthService
from apps.caronte.serializers import LoginSerializer


def _get_client_ip(request) -> str:
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '')


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        tokens = AuthService.login(
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password'],
            ip_address=_get_client_ip(request),
        )
        return Response(tokens, status=status.HTTP_200_OK)


class RefreshView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({'detail': 'refresh token obrigatório.'}, status=status.HTTP_400_BAD_REQUEST)

        tokens = AuthService.refresh(refresh_token)
        return Response(tokens, status=status.HTTP_200_OK)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({'detail': 'refresh token obrigatório.'}, status=status.HTTP_400_BAD_REQUEST)

        AuthService.logout(refresh_token)
        return Response({'detail': 'Logout realizado com sucesso.'}, status=status.HTTP_200_OK)


class InvalidateAllTokensView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Revoga todos os tokens do usuário autenticado (logout em todos os dispositivos)."""
        AuthService.invalidate_all_tokens(request.user.id)
        return Response({'detail': 'Todos os tokens foram revogados.'}, status=status.HTTP_200_OK)
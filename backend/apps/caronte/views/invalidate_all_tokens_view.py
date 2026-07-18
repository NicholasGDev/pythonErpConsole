# backend/apps/caronte/views/invalidate_all_tokens_view.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from apps.caronte.services.auth_service import AuthService


class InvalidateAllTokensView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Revoga todos os tokens do usuário autenticado (logout em todos os dispositivos)."""
        AuthService.invalidate_all_tokens(request.user.id)
        return Response({'detail': 'Todos os tokens foram revogados.'}, status=status.HTTP_200_OK)

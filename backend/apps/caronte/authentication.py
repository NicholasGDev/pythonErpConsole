# backend/apps/caronte/authentication.py
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken


class CaronteJWTAuthentication(JWTAuthentication):
    """
    Estende o JWTAuthentication padrão adicionando verificação
    do jwt_token_version armazenado no User.

    Se o campo for rotacionado no banco (invalidate_all_tokens),
    todos os tokens emitidos anteriormente se tornam inválidos
    imediatamente, sem precisar esperar a expiração natural.
    """

    def get_user(self, validated_token):
        user = super().get_user(validated_token)

        token_version = validated_token.get('jwt_token_version')
        if token_version is None:
            raise InvalidToken('Token não contém jwt_token_version.')

        if str(user.jwt_token_version) != token_version:
            raise InvalidToken('Token revogado. Faça login novamente.')

        return user
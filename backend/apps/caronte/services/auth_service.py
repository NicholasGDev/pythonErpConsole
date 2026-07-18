# backend/apps/caronte/services/auth_service.py
import uuid
from django.conf import settings
from django.utils import timezone
from django.contrib.auth import authenticate

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken

from rest_framework.exceptions import AuthenticationFailed, PermissionDenied

from apps.caronte.models import User, AccessControl


MAX_ATTEMPTS    = getattr(settings, 'AUTH_MAX_FAILED_ATTEMPTS', 5)
LOCKOUT_MINUTES = getattr(settings, 'AUTH_LOCKOUT_MINUTES', 30)


class AuthService:

    # ─────────────────────────────────────────────────────────────
    # LOGIN
    # ─────────────────────────────────────────────────────────────

    @staticmethod
    def login(email: str, password: str, ip_address: str = None) -> dict:
        """
        Autentica o usuário, aplica lógica de bloqueio e retorna
        access + refresh tokens com jwt_token_version nos claims.
        """
        # 1. Busca o usuário pelo email (não vaza se existe ou não na msg de erro)
        try:
            user = User.objects.select_related('security_control').get(email=email)
        except User.DoesNotExist:
            raise AuthenticationFailed('Credenciais inválidas.')

        if not user.is_active:
            raise AuthenticationFailed('Conta desativada.')

        # 2. Verifica bloqueio por tentativas
        ac = AuthService._get_or_create_access_control(user)
        AuthService._check_lockout(ac)

        # 3. Valida a senha
        authenticated_user = authenticate(username=email, password=password)
        if authenticated_user is None:
            AuthService._register_failed_attempt(ac)
            raise AuthenticationFailed('Credenciais inválidas.')

        # 4. Login bem-sucedido — atualiza AccessControl
        ac.failed_login_attempts = 0
        ac.lockout_until          = None
        ac.last_login_ip          = ip_address
        ac.last_login_at          = timezone.now()
        ac.save()

        # 5. Gera tokens com claims customizados
        return AuthService._generate_tokens(user)

    # ─────────────────────────────────────────────────────────────
    # REFRESH
    # ─────────────────────────────────────────────────────────────

    @staticmethod
    def refresh(refresh_token_str: str) -> dict:
        """
        Valida o refresh token e retorna um novo par de tokens.
        O token antigo é blacklistado automaticamente (ROTATE_REFRESH_TOKENS=True).
        """
        try:
            refresh = RefreshToken(refresh_token_str)
        except TokenError as e:
            raise AuthenticationFailed(str(e))

        # Verifica jwt_token_version no refresh token
        try:
            user = User.objects.get(pk=refresh['user_id'])
        except User.DoesNotExist:
            raise AuthenticationFailed('Usuário não encontrado.')

        if str(user.jwt_token_version) != refresh.get('jwt_token_version'):
            raise AuthenticationFailed('Token revogado. Faça login novamente.')

        try:
            refresh.blacklist()
        except AttributeError:
            pass  # token_blacklist não instalado (não deve acontecer)

        return AuthService._generate_tokens(user)

    # ─────────────────────────────────────────────────────────────
    # LOGOUT
    # ─────────────────────────────────────────────────────────────

    @staticmethod
    def logout(refresh_token_str: str) -> None:
        """Blacklista o refresh token, invalidando a sessão atual."""
        try:
            token = RefreshToken(refresh_token_str)
            token.blacklist()
        except TokenError as e:
            raise AuthenticationFailed(str(e))

    # ─────────────────────────────────────────────────────────────
    # REVOGAR TODOS OS TOKENS (logout global)
    # ─────────────────────────────────────────────────────────────

    @staticmethod
    def invalidate_all_tokens(user_id: int) -> None:
        """
        Rotaciona o jwt_token_version do usuário.
        Todos os access/refresh tokens emitidos anteriormente
        são rejeitados pelo CaronteJWTAuthentication imediatamente.
        """
        updated = User.objects.filter(pk=user_id).update(
            jwt_token_version=str(uuid.uuid4())
        )
        if not updated:
            raise AuthenticationFailed(f'Usuário {user_id} não encontrado.')

        # Blacklista todos os outstanding tokens no banco também
        tokens = OutstandingToken.objects.filter(user_id=user_id)
        for token in tokens:
            BlacklistedToken.objects.get_or_create(token=token)

    # ─────────────────────────────────────────────────────────────
    # HELPERS PRIVADOS
    # ─────────────────────────────────────────────────────────────

    @staticmethod
    def _get_or_create_access_control(user: User) -> AccessControl:
        ac, _ = AccessControl.objects.get_or_create(user=user)
        return ac

    @staticmethod
    def _check_lockout(ac: AccessControl) -> None:
        if ac.lockout_until and ac.lockout_until > timezone.now():
            remaining = int((ac.lockout_until - timezone.now()).total_seconds() / 60) + 1
            raise PermissionDenied(
                f'Conta bloqueada. Tente novamente em {remaining} minuto(s).'
            )

    @staticmethod
    def _register_failed_attempt(ac: AccessControl) -> None:
        ac.failed_login_attempts += 1
        if ac.failed_login_attempts >= MAX_ATTEMPTS:
            ac.lockout_until = timezone.now() + timezone.timedelta(minutes=LOCKOUT_MINUTES)
        ac.save()

    @staticmethod
    def _generate_tokens(user: User) -> dict:
        """Gera o par de tokens incluindo jwt_token_version nos claims."""
        refresh = RefreshToken.for_user(user)
        version = str(user.jwt_token_version)

        # Adiciona no refresh E no access token
        refresh['jwt_token_version'] = version
        refresh['name']              = user.name
        refresh['email']             = user.email

        access = refresh.access_token
        access['jwt_token_version'] = version
        access['name']              = user.name
        access['email']             = user.email

        return {
            'access':  str(access),
            'refresh': str(refresh),
        }
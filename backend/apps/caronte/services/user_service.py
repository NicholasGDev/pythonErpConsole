# backend/apps/caronte/services/user_service.py
import secrets
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist, ValidationError

from apps.caronte.models import User, UserData, AccessControl, PasswordReset


class UserService:

    # ─────────────────────────────────────────────
    # READ
    # ─────────────────────────────────────────────

    @staticmethod
    def get_user_by_id(user_id: int) -> User:
        try:
            return (
                User.objects
                .select_related('user_data', 'security_control')
                .prefetch_related('password_resets')
                .get(pk=user_id)
            )
        except User.DoesNotExist:
            raise ObjectDoesNotExist(f"User with id {user_id} does not exist.")

    @staticmethod
    def list_users(include_inactive: bool = False):
        qs = User.objects.select_related('user_data', 'security_control')
        if not include_inactive:
            qs = qs.filter(is_active=True)
        return qs.all()

    # ─────────────────────────────────────────────
    # CREATE
    # ─────────────────────────────────────────────

    @staticmethod
    @transaction.atomic
    def create_user(data: dict) -> User:
        """
        data esperado:
        {
            "email": "...", "name": "...", "password": "...",
            "user_data": { "city": "...", "country": "...", ... }  # opcional
        }
        """
        user_data_payload = data.pop('user_data', {})

        user = User.objects.create_user(
            email=data['email'],
            name=data['name'],
            password=data['password'],
        )

        UserData.objects.create(user_id=user, **user_data_payload)
        AccessControl.objects.create(user=user)

        return user

    # ─────────────────────────────────────────────
    # UPDATE
    # ─────────────────────────────────────────────

    @staticmethod
    @transaction.atomic
    def update_user(user_id: int, data: dict) -> User:
        """
        Atualiza campos de User e, opcionalmente, de UserData.
        data esperado:
        {
            "name": "...",                              # campos de User
            "user_data": { "city": "...", ... }        # campos de UserData (opcional)
        }
        """
        user = UserService.get_user_by_id(user_id)

        user_data_payload = data.pop('user_data', None)

        user_fields = ('name', 'is_active', 'is_staff',
                       'force_password_change', 'generic_password_in_use')
        for field in user_fields:
            if field in data:
                setattr(user, field, data[field])
        user.save()

        if user_data_payload:
            UserData.objects.filter(user_id=user).update(**user_data_payload)

        user.refresh_from_db()
        return user

    @staticmethod
    def change_password(user_id: int, new_password: str) -> None:
        user = UserService.get_user_by_id(user_id)
        user.set_password(new_password)
        user.force_password_change = False
        user.generic_password_in_use = False
        user.save()

    # ─────────────────────────────────────────────
    # DELETE
    # ─────────────────────────────────────────────

    @staticmethod
    def deactivate_user(user_id: int) -> None:
        """Soft-delete: mantém o registro, apenas desativa."""
        user = UserService.get_user_by_id(user_id)
        user.is_active = False
        user.save()

    @staticmethod
    @transaction.atomic
    def delete_user(user_id: int) -> None:
        """Hard-delete: remove permanentemente o usuário e todos os dados relacionados."""
        user = UserService.get_user_by_id(user_id)
        user.delete()  # CASCADE apaga UserData, AccessControl e PasswordResets

    # ─────────────────────────────────────────────
    # ACCESS CONTROL
    # ─────────────────────────────────────────────

    @staticmethod
    def get_access_control(user_id: int) -> AccessControl:
        try:
            return AccessControl.objects.get(user_id=user_id)
        except AccessControl.DoesNotExist:
            raise ObjectDoesNotExist(f"AccessControl for user {user_id} not found.")

    @staticmethod
    def update_access_control(user_id: int, data: dict) -> AccessControl:
        """Atualiza campos de segurança: last_login_ip, lockout_until, etc."""
        ac = UserService.get_access_control(user_id)
        ac_fields = ('failed_login_attempts', 'lockout_until',
                     'last_login_ip', 'last_login_at')
        for field in ac_fields:
            if field in data:
                setattr(ac, field, data[field])
        ac.save()
        return ac

    @staticmethod
    def reset_failed_attempts(user_id: int) -> None:
        AccessControl.objects.filter(user_id=user_id).update(
            failed_login_attempts=0,
            lockout_until=None,
        )

    # ─────────────────────────────────────────────
    # PASSWORD RESET
    # ─────────────────────────────────────────────

    @staticmethod
    def create_password_reset_token(user_id: int, expires_in_minutes: int = 30) -> PasswordReset:
        user = UserService.get_user_by_id(user_id)
        token = secrets.token_urlsafe(64)
        expires_at = timezone.now() + timezone.timedelta(minutes=expires_in_minutes)
        return PasswordReset.objects.create(
            user_id=user,
            reset_token=token,
            expires_at=expires_at,
        )

    @staticmethod
    def consume_password_reset_token(token: str, new_password: str) -> User:
        """Valida o token, aplica a nova senha e marca o token como usado."""
        try:
            reset = PasswordReset.objects.select_related('user_id').get(
                reset_token=token,
                is_used=False,
            )
        except PasswordReset.DoesNotExist:
            raise ValidationError("Token inválido ou já utilizado.")

        if reset.expires_at < timezone.now():
            raise ValidationError("Token expirado.")

        user = reset.user_id
        user.set_password(new_password)
        user.force_password_change = False
        user.save()

        reset.is_used = True
        reset.save()

        return user

    @staticmethod
    def list_password_resets(user_id: int):
        return PasswordReset.objects.filter(user_id=user_id).order_by('-created_at')

    @staticmethod
    def invalidate_all_tokens(user_id: int) -> None:
        """Invalida todos os tokens ativos de um usuário."""
        PasswordReset.objects.filter(user_id=user_id, is_used=False).update(is_used=True)
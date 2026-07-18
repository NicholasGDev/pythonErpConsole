from django.db import models
from .user import User

class PasswordReset(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_resets')
    reset_token = models.CharField(max_length=128, unique=True)
    is_used = models.BooleanField(default=False)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'caronte'
        db_table = 'password_resets'
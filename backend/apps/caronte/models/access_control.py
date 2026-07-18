from django.db import models
from .user import User

class AccessControl(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='security_control')
    failed_login_attempts = models.SmallIntegerField(default=0)
    lockout_until = models.DateTimeField(blank=True, null=True)
    last_login_ip = models.CharField(max_length=45, blank=True, null=True)
    last_login_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'caronte'
        db_table = 'access_control'
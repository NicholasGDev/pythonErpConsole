from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()

class Command(BaseCommand):
    help = 'Seed the admin user'

    @transaction.atomic
    def handle(self, *args, **kwargs):
        if not User.objects.filter(is_superuser=True).exists():
            User.objects.create_superuser(
                name='nicAdmin',
                email='nicholas.goulart1@gmail.com',
                password='C@r0nte#333999'
            )
            self.stdout.write(self.style.SUCCESS('Admin user created successfully.'))
        else:
            self.stdout.write(self.style.WARNING('Admin user already exists.'))
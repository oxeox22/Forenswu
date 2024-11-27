from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from Server.models import Profile

class Command(BaseCommand):
    help = "Create missing profiles for all users"

    def handle(self, *args, **kwargs):
        for user in User.objects.all():
            if not hasattr(user, 'profile'):
                Profile.objects.create(user=user)
                self.stdout.write(self.style.SUCCESS(f'Created profile for user: {user.username}'))

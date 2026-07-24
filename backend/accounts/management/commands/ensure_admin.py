import os

from django.core.management.base import BaseCommand, CommandError

from accounts.models import User


class Command(BaseCommand):
    help = "Railway env o'zgaruvchilaridan production adminini yaratadi yoki yangilaydi."

    def handle(self, *args, **options):
        username = os.environ.get('ADMIN_USERNAME', '').strip()
        password = os.environ.get('ADMIN_PASSWORD', '')
        email = os.environ.get('ADMIN_EMAIL', '').strip()

        if not username or not password:
            self.stdout.write(self.style.WARNING(
                "ADMIN_USERNAME yoki ADMIN_PASSWORD berilmagan. Admin avtomatik yaratilmadi."
            ))
            return

        user, created = User.objects.get_or_create(username=username)
        user.role = User.ROLE_ADMIN
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.faol = True
        if email:
            user.email = email

        reset_password = os.environ.get('RESET_ADMIN_PASSWORD', '').strip().lower() in {
            '1', 'true', 'yes', 'on'
        }
        if created or reset_password or not user.has_usable_password():
            user.set_password(password)
        user.save()

        action = 'yaratildi' if created else 'tekshirildi'
        self.stdout.write(self.style.SUCCESS(f"Production admin {action}: {username}"))

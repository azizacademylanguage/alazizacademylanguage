import os

from django.core.management.base import BaseCommand

from accounts.models import User


class Command(BaseCommand):
    help = "Railway uchun production adminini ishonchli yaratadi yoki parolini yangilaydi."

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help="Admin parolini environment qiymatiga (yoki standart parolga) majburan tenglaydi.",
        )

    def handle(self, *args, **options):
        # Environment variable kiritilmagan taqdirda ham loyiha birinchi deploydayoq
        # kirishga tayyor bo'lishi uchun xavfsiz bo'lmagan, ammo aniq standart login.
        # Productionda ADMIN_PASSWORD ni Railway Variables ichida almashtirish tavsiya etiladi.
        username = os.environ.get('ADMIN_USERNAME', 'admin').strip() or 'admin'
        password = os.environ.get('ADMIN_PASSWORD', 'admin12345') or 'admin12345'
        email = os.environ.get('ADMIN_EMAIL', 'admin@alazizacademy.uz').strip()

        # RESET_ADMIN_PASSWORD berilmasa Railway deploylarida parol avtomatik
        # sinxronlanadi. False berilsa, mavjud parol saqlanadi.
        reset_raw = os.environ.get('RESET_ADMIN_PASSWORD', 'true').strip().lower()
        reset_password = reset_raw in {'1', 'true', 'yes', 'on'}
        force = bool(options.get('force'))

        user = User.objects.filter(username=username).first()
        created = user is None
        if created:
            user = User(username=username)

        user.role = User.ROLE_ADMIN
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.faol = True
        if email:
            user.email = email

        password_changed = created or force or reset_password or not user.has_usable_password()
        if password_changed:
            user.set_password(password)

        user.save()

        # Deploy logida aniq diagnostika ko'rinadi, lekin parolning o'zi chiqarilmaydi.
        self.stdout.write(self.style.SUCCESS(
            "ADMIN_READY "
            f"username={user.username} "
            f"created={created} "
            f"password_synced={password_changed} "
            f"password_check={user.check_password(password)} "
            f"active={user.is_active and user.faol} "
            f"role={user.role}"
        ))

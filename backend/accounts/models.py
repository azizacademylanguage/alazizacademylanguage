from django.db import models
from django.contrib.auth.models import AbstractUser


class Filial(models.Model):
    nomi = models.CharField(max_length=150, unique=True)
    manzil = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'filiallar'
        verbose_name = 'Filial'
        verbose_name_plural = 'Filiallar'

    def __str__(self):
        return self.nomi


class User(AbstractUser):
    ROLE_ADMIN = 'admin'
    ROLE_NAZORATCHI = 'nazoratchi'
    ROLE_OQUVCHI = 'oquvchi'
    ROLE_CHOICES = (
        (ROLE_ADMIN, 'Admin'),
        (ROLE_NAZORATCHI, 'Nazoratchi'),
        (ROLE_OQUVCHI, "O'quvchi"),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_ADMIN)
    filial = models.ForeignKey(Filial, on_delete=models.SET_NULL, null=True, blank=True, related_name='users')
    yaratgan = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='yaratganlari')
    ism = models.CharField(max_length=100, blank=True)
    familya = models.CharField(max_length=100, blank=True)
    faol = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    token_version = models.PositiveIntegerField(default=1)

    class Meta:
        db_table = 'users'
        verbose_name = 'Foydalanuvchi'
        verbose_name_plural = 'Foydalanuvchilar'

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    @property
    def full_name(self):
        return f"{self.ism} {self.familya}".strip() or self.username

    def save(self, *args, **kwargs):
        # createsuperuser orqali yaratilgan har qanday foydalanuvchi
        # avtomatik ravishda 'admin' roliga ega bo'ladi — shunday qilib u
        # ham Django Admin panelga (/admin/), ham React saytga (Admin
        # dashboard) bir xil login/parol bilan kira oladi.
        if self.is_superuser:
            self.role = self.ROLE_ADMIN
        super().save(*args, **kwargs)


class KirishTarixi(models.Model):
    """Login urinishlari va qurilma xavfsizlik tarixi."""
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='kirish_tarixi')
    username = models.CharField(max_length=150, blank=True)
    muvaffaqiyatli = models.BooleanField(default=False)
    ip_manzil = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'kirish_tarixi'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at'], name='kirish_created_idx'),
            models.Index(fields=['username', '-created_at'], name='kirish_user_created_idx'),
        ]
        verbose_name = 'Kirish tarixi'
        verbose_name_plural = 'Kirish tarixi'

    def __str__(self):
        holat = 'Muvaffaqiyatli' if self.muvaffaqiyatli else 'Xato'
        return f"{self.username} - {holat}"

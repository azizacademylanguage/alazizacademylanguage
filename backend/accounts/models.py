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
    # Legacy Railway bazalarida bu ustun allaqachon NOT NULL ko‘rinishda bor.
    # Modelda ham default bilan saqlansa yangi foydalanuvchi yaratishda NULL
    # yuborilmaydi va eski tokenlarni bekor qilish uchun foydalanish mumkin.
    token_version = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

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

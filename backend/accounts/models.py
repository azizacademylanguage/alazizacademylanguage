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

    TARIF_YAGONA = 'Yagona'
    TOLOV_TOLANGAN = 'tolangan'
    TOLOV_TOLANMAGAN = 'tolanmagan'
    # Eski frontend yoki eski bazadagi qiymatlar bilan moslik uchun aliaslar.
    TOLOV_QARZDOR = TOLOV_TOLANMAGAN
    TOLOV_KUTILMOQDA = TOLOV_TOLANMAGAN
    TOLOV_CHOICES = (
        (TOLOV_TOLANGAN, "To'langan"),
        (TOLOV_TOLANMAGAN, "To'lanmagan"),
    )
    tarif = models.CharField(max_length=80, default=TARIF_YAGONA, blank=True)
    boshlanish_sana = models.DateField(null=True, blank=True)
    tugash_sana = models.DateField(null=True, blank=True)
    tolov_holati = models.CharField(max_length=20, choices=TOLOV_CHOICES, default=TOLOV_TOLANGAN)
    muddat_bloklash = models.BooleanField(default=True)
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

    @property
    def muddat_tugagan(self):
        from django.utils import timezone
        return bool(self.role == self.ROLE_OQUVCHI and self.muddat_bloklash and self.tugash_sana and self.tugash_sana < timezone.localdate())

    @property
    def qolgan_kun(self):
        from django.utils import timezone
        if not self.tugash_sana:
            return None
        return (self.tugash_sana - timezone.localdate()).days

    @property
    def obuna_holati(self):
        if self.tolov_holati != self.TOLOV_TOLANGAN:
            return self.tolov_holati
        if self.muddat_tugagan:
            return 'tugagan'
        if self.qolgan_kun is not None and self.qolgan_kun <= 5:
            return 'tugamoqda'
        return 'faol'

    def save(self, *args, **kwargs):
        # createsuperuser orqali yaratilgan har qanday foydalanuvchi
        # avtomatik ravishda 'admin' roliga ega bo'ladi — shunday qilib u
        # ham Django Admin panelga (/admin/), ham React saytga (Admin
        # dashboard) bir xil login/parol bilan kira oladi.
        if self.is_superuser:
            self.role = self.ROLE_ADMIN
        # Platformada endi bitta tarif va ikkita to'lov holati mavjud.
        self.tarif = self.TARIF_YAGONA
        if self.tolov_holati in {'qarzdor', 'kutilmoqda', self.TOLOV_TOLANMAGAN}:
            self.tolov_holati = self.TOLOV_TOLANMAGAN
        else:
            self.tolov_holati = self.TOLOV_TOLANGAN
        super().save(*args, **kwargs)

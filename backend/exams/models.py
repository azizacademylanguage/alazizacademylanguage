import uuid

from django.db import models
from accounts.models import User
from courses.models import Dars


class Mashq(models.Model):
    """Har bir darsga tegishli test to'plami (odatda 40 ta savol)"""
    dars = models.OneToOneField(Dars, on_delete=models.CASCADE, related_name='mashq')
    sarlavha = models.CharField(max_length=200, default="Mashq")
    vaqt_chegarasi_daq = models.PositiveIntegerField(null=True, blank=True)
    otish_bali_foiz = models.PositiveIntegerField(default=80)  # nechi foiz bilan "o'tdi" hisoblanadi

    class Meta:
        db_table = 'mashqlar'
        verbose_name = 'Mashq'
        verbose_name_plural = 'Mashqlar'

    def __str__(self):
        return f"{self.sarlavha} ({self.dars.sarlavha})"

    @property
    def savollar_soni(self):
        return self.savollar.count()


class Savol(models.Model):
    TUR_SINGLE = 'single'
    TUR_MULTIPLE = 'multiple'
    TUR_TEXT = 'text'
    TUR_CHOICES = (
        (TUR_SINGLE, "Bitta to'g'ri javob"),
        (TUR_MULTIPLE, "Ko'p to'g'ri javob"),
        (TUR_TEXT, "Matn kiritish"),
    )
    mashq = models.ForeignKey(Mashq, on_delete=models.CASCADE, related_name='savollar')
    matn = models.TextField()
    rasm = models.ImageField(upload_to='savollar/rasm/', blank=True, null=True)
    tur = models.CharField(max_length=20, choices=TUR_CHOICES, default=TUR_SINGLE)
    togri_matn_javob = models.CharField(max_length=255, blank=True)  # 'text' turi uchun
    tartib = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'savollar'
        ordering = ['tartib']
        verbose_name = 'Savol'
        verbose_name_plural = 'Savollar'

    def __str__(self):
        return self.matn[:60]


class Javob(models.Model):
    savol = models.ForeignKey(Savol, on_delete=models.CASCADE, related_name='javoblar')
    matn = models.CharField(max_length=500)
    togri = models.BooleanField(default=False)
    tartib = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'javoblar'
        ordering = ['tartib']
        verbose_name = 'Javob'
        verbose_name_plural = 'Javoblar'

    def __str__(self):
        return self.matn


class MashqNatija(models.Model):
    oquvchi = models.ForeignKey(User, on_delete=models.CASCADE, related_name='natijalar')
    mashq = models.ForeignKey(Mashq, on_delete=models.CASCADE, related_name='natijalar')
    togri_soni = models.PositiveIntegerField(default=0)
    jami_soni = models.PositiveIntegerField(default=0)
    foiz = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    urinish_raqami = models.PositiveIntegerField(default=1)
    boshlangan_vaqt = models.DateTimeField(auto_now_add=True)
    tugagan_vaqt = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'mashq_natijalari'
        ordering = ['-boshlangan_vaqt']
        verbose_name = 'Mashq natijasi'
        verbose_name_plural = 'Mashq natijalari'

    def __str__(self):
        return f"{self.oquvchi} - {self.mashq} - {self.foiz}%"


class OquvchiJavob(models.Model):
    """Har bir urinishda o'quvchi qaysi javobni bergani"""
    natija = models.ForeignKey(MashqNatija, on_delete=models.CASCADE, related_name='berilgan_javoblar')
    savol = models.ForeignKey(Savol, on_delete=models.CASCADE, related_name='+')
    tanlangan_javoblar = models.ManyToManyField(Javob, blank=True, related_name='+')
    matn_javob = models.TextField(blank=True)
    togri_berilgan = models.BooleanField(default=False)

    class Meta:
        db_table = 'oquvchi_javoblari'
        verbose_name = "O'quvchi javobi"
        verbose_name_plural = "O'quvchi javoblari"


# ==================== GATE TEST (daraja ochish testi) ====================

class GateTest(models.Model):
    """
    Har bir Daraja uchun bitta kirish testi. O'quvchi shu testdan
    ochish_uchun_foiz dan yuqori ball olsa, keyingi daraja avtomatik ochiladi.
    """
    daraja = models.OneToOneField(
        'courses.Daraja', on_delete=models.CASCADE, related_name='gate_test'
    )
    sarlavha = models.CharField(max_length=200, default='Daraja testi')
    vaqt_chegarasi_daq = models.PositiveIntegerField(default=25)

    class Meta:
        db_table = 'gate_testlar'
        verbose_name = 'Gate Test'
        verbose_name_plural = 'Gate Testlar'

    def __str__(self):
        return f"{self.sarlavha} ({self.daraja})"

    @property
    def savollar_soni(self):
        return self.savollar.count()


class GateTestSavol(models.Model):
    gate_test = models.ForeignKey(GateTest, on_delete=models.CASCADE, related_name='savollar')
    matn = models.TextField()
    tartib = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'gate_test_savollari'
        ordering = ['tartib']
        verbose_name = 'Gate Test savoli'
        verbose_name_plural = 'Gate Test savollari'

    def __str__(self):
        return self.matn[:60]


class GateTestJavob(models.Model):
    savol = models.ForeignKey(GateTestSavol, on_delete=models.CASCADE, related_name='javoblar')
    matn = models.CharField(max_length=500)
    togri = models.BooleanField(default=False)
    tartib = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'gate_test_javoblari'
        ordering = ['tartib']
        verbose_name = 'Gate Test javobi'
        verbose_name_plural = 'Gate Test javoblari'


class GateTestNatija(models.Model):
    oquvchi = models.ForeignKey(User, on_delete=models.CASCADE, related_name='gate_test_natijalari')
    gate_test = models.ForeignKey(GateTest, on_delete=models.CASCADE, related_name='natijalar')
    togri_soni = models.PositiveIntegerField(default=0)
    jami_soni = models.PositiveIntegerField(default=0)
    foiz = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    otdi = models.BooleanField(default=False)
    urinish_raqami = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'gate_test_natijalari'
        ordering = ['-created_at']
        verbose_name = 'Gate Test natijasi'
        verbose_name_plural = 'Gate Test natijalari'


# ==================== FINAL TEST + SERTIFIKAT ====================

class FinalTest(models.Model):
    """Daraja to'liq tugatilgandan keyingi yakuniy test."""
    daraja = models.OneToOneField(
        'courses.Daraja', on_delete=models.CASCADE, related_name='final_test'
    )
    sarlavha = models.CharField(max_length=200, default='Yakuniy test')
    vaqt_chegarasi_daq = models.PositiveIntegerField(default=30)
    otish_bali_foiz = models.PositiveIntegerField(default=70)

    class Meta:
        db_table = 'final_testlar'
        verbose_name = 'Final Test'
        verbose_name_plural = 'Final Testlar'

    def __str__(self):
        return f"{self.sarlavha} ({self.daraja})"

    @property
    def savollar_soni(self):
        return self.savollar.count()


class FinalTestSavol(models.Model):
    final_test = models.ForeignKey(FinalTest, on_delete=models.CASCADE, related_name='savollar')
    matn = models.TextField()
    tartib = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'final_test_savollari'
        ordering = ['tartib']
        verbose_name = 'Final Test savoli'
        verbose_name_plural = 'Final Test savollari'


class FinalTestJavob(models.Model):
    savol = models.ForeignKey(FinalTestSavol, on_delete=models.CASCADE, related_name='javoblar')
    matn = models.CharField(max_length=500)
    togri = models.BooleanField(default=False)
    tartib = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'final_test_javoblari'
        ordering = ['tartib']
        verbose_name = 'Final Test javobi'
        verbose_name_plural = 'Final Test javoblari'


class Sertifikat(models.Model):
    """Final Test'dan muvaffaqiyatli o'tgan o'quvchiga beriladigan sertifikat."""
    oquvchi = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sertifikatlar')
    daraja = models.ForeignKey('courses.Daraja', on_delete=models.CASCADE, related_name='sertifikatlar')
    kod = models.CharField(max_length=20, unique=True, db_index=True)  # tekshirish kodi
    foiz = models.DecimalField(max_digits=5, decimal_places=2)
    berilgan_sana = models.DateTimeField(auto_now_add=True)
    faol = models.BooleanField(default=True)
    bekor_qilingan_sana = models.DateTimeField(null=True, blank=True)
    bekor_sabab = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = 'sertifikatlar'
        ordering = ['-berilgan_sana']
        verbose_name = 'Sertifikat'
        verbose_name_plural = 'Sertifikatlar'

    def __str__(self):
        return f"{self.oquvchi} - {self.daraja} ({self.kod})"


class FinalTestNatija(models.Model):
    oquvchi = models.ForeignKey(User, on_delete=models.CASCADE, related_name='final_test_natijalari')
    final_test = models.ForeignKey(FinalTest, on_delete=models.CASCADE, related_name='natijalar')
    togri_soni = models.PositiveIntegerField(default=0)
    jami_soni = models.PositiveIntegerField(default=0)
    foiz = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    otdi = models.BooleanField(default=False)
    sertifikat = models.ForeignKey(Sertifikat, on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    urinish_raqami = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'final_test_natijalari'
        ordering = ['-created_at']
        verbose_name = 'Final Test natijasi'
        verbose_name_plural = 'Final Test natijalari'


# ==================== WRITING (yozma mashq, AI baholaydi) ====================

class WritingTopshiriq(models.Model):
    """Darsga tegishli yozma topshiriq (masalan: 'Write about your family')."""
    dars = models.ForeignKey('courses.Dars', on_delete=models.CASCADE, related_name='writing_topshiriqlar')
    matn = models.TextField(help_text="Topshiriq matni, masalan: 'Write 5 sentences about your daily routine.'")
    minimal_soz_soni = models.PositiveIntegerField(default=30)
    tartib = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'writing_topshiriqlar'
        ordering = ['tartib']
        verbose_name = 'Writing topshiriq'
        verbose_name_plural = 'Writing topshiriqlar'

    def __str__(self):
        return self.matn[:60]


class WritingNatija(models.Model):
    oquvchi = models.ForeignKey(User, on_delete=models.CASCADE, related_name='writing_natijalari')
    topshiriq = models.ForeignKey(WritingTopshiriq, on_delete=models.CASCADE, related_name='natijalar')
    matn_javob = models.TextField()
    # AI (Claude) tomonidan qaytarilgan baholash:
    ai_foiz = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    ai_izoh = models.TextField(blank=True, help_text="AI tomonidan berilgan qisqa fikr-mulohaza")
    ai_xatolar = models.JSONField(default=list, blank=True, help_text="Aniqlangan grammatik xatolar ro'yxati")
    baholanmoqda = models.BooleanField(default=True)  # AI hali javob bermagan bo'lsa True
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'writing_natijalari'
        ordering = ['-created_at']
        verbose_name = 'Writing natijasi'
        verbose_name_plural = 'Writing natijalari'


# ==================== SPEAKING (talaffuz mashqi, AI baholaydi) ====================

class SpeakingTopshiriq(models.Model):
    """Darsga tegishli talaffuz mashqi — o'quvchi matnni ovoz orqali o'qiydi."""
    dars = models.ForeignKey('courses.Dars', on_delete=models.CASCADE, related_name='speaking_topshiriqlar')
    matn = models.TextField(help_text="O'quvchi talaffuz qilishi kerak bo'lgan matn/gap")
    tartib = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'speaking_topshiriqlar'
        ordering = ['tartib']
        verbose_name = 'Speaking topshiriq'
        verbose_name_plural = 'Speaking topshiriqlar'

    def __str__(self):
        return self.matn[:60]


class SpeakingNatija(models.Model):
    oquvchi = models.ForeignKey(User, on_delete=models.CASCADE, related_name='speaking_natijalari')
    topshiriq = models.ForeignKey(SpeakingTopshiriq, on_delete=models.CASCADE, related_name='natijalar')
    audio_yozuv = models.FileField(upload_to='speaking/', blank=True, null=True)
    # AI baholash natijasi (talaffuz aniqligi, aytilgan matn transkripsiyasi va h.k.)
    ai_foiz = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    ai_izoh = models.TextField(blank=True)
    baholanmoqda = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'speaking_natijalari'
        ordering = ['-created_at']
        verbose_name = 'Speaking natijasi'
        verbose_name_plural = 'Speaking natijalari'


# ==================== COIN / SHOP (motivatsiya tizimi) ====================

class OquvchiCoin(models.Model):
    """Har bir o'quvchining coin balansi."""
    oquvchi = models.OneToOneField(User, on_delete=models.CASCADE, related_name='coin_balans')
    balans = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'oquvchi_coinlari'
        verbose_name = "O'quvchi coini"
        verbose_name_plural = "O'quvchi coinlari"

    def __str__(self):
        return f"{self.oquvchi} - {self.balans} coin"


class CoinTarix(models.Model):
    """Coin qo'shilishi/sarflanishi tarixi (audit uchun)."""
    SABAB_CHOICES = (
        ('mashq', 'Mashq yakunlandi'),
        ('gate_test', 'Gate Test topshirildi'),
        ('final_test', 'Final Test topshirildi'),
        ('shop', "Do'kondan xarid"),
        ('tezkor_oyin', "Tezkor tarjima o'yini"),
        ('yutuq', 'Yutuq mukofoti'),
        ('kunlik', 'Kunlik faollik'),
        ('admin', 'Admin tomonidan qo\'lda berilgan'),
    )
    oquvchi = models.ForeignKey(User, on_delete=models.CASCADE, related_name='coin_tarixi')
    miqdor = models.IntegerField(help_text="Musbat — qo'shilgan, manfiy — sarflangan")
    sabab = models.CharField(max_length=20, choices=SABAB_CHOICES)
    izoh = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'coin_tarixi'
        ordering = ['-created_at']
        verbose_name = 'Coin tarixi'
        verbose_name_plural = 'Coin tarixi'


class ShopMahsulot(models.Model):
    """Do'konda sotiladigan (ramziy) mahsulotlar — masalan avatar, unvon va h.k."""
    nomi = models.CharField(max_length=150)
    tavsif = models.CharField(max_length=255, blank=True)
    narx_coin = models.PositiveIntegerField()
    rasm = models.ImageField(upload_to='shop/', blank=True, null=True)
    faol = models.BooleanField(default=True)

    class Meta:
        db_table = 'shop_mahsulotlari'
        verbose_name = 'Shop mahsuloti'
        verbose_name_plural = 'Shop mahsulotlari'

    def __str__(self):
        return f"{self.nomi} ({self.narx_coin} coin)"


class ShopBuyurtma(models.Model):
    STATUS_YANGI = 'yangi'
    STATUS_TAYYOR = 'tayyor'
    STATUS_BERILDI = 'berildi'
    STATUS_CHOICES = (
        (STATUS_YANGI, 'Yangi'),
        (STATUS_TAYYOR, 'Tayyorlanmoqda'),
        (STATUS_BERILDI, 'Berildi'),
    )

    oquvchi = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shop_buyurtmalari')
    mahsulot = models.ForeignKey(ShopMahsulot, on_delete=models.CASCADE, related_name='buyurtmalar')
    narx_coin = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_YANGI)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'shop_buyurtmalari'
        ordering = ['-created_at']
        verbose_name = 'Shop buyurtmasi'
        verbose_name_plural = 'Shop buyurtmalari'

    def __str__(self):
        return f"{self.oquvchi.full_name} - {self.mahsulot.nomi}"


# ==================== O‘YIN UCHUN SO‘Z JUFTLIKLARI ====================

class SozJuftligi(models.Model):
    """Biriktirilgan fan bo'yicha chet tili va o'zbekcha tarjima jufti."""
    fan = models.ForeignKey('courses.Fan', on_delete=models.CASCADE, related_name='soz_juftliklari')
    chet_soz = models.CharField(max_length=180)
    uzbek_soz = models.CharField(max_length=180)
    tartib = models.PositiveIntegerField(default=0)
    faol = models.BooleanField(default=True)

    class Meta:
        db_table = 'soz_juftliklari'
        ordering = ['tartib', 'id']
        unique_together = ('fan', 'chet_soz', 'uzbek_soz')
        verbose_name = "So'z juftligi"
        verbose_name_plural = "So'z juftliklari"

    def __str__(self):
        return f"{self.chet_soz} — {self.uzbek_soz}"


# ==================== ADMIN AUDIT LOG ====================

class AdminAmalLog(models.Model):
    """Admin/Nazoratchi tomonidan qilingan har bir muhim amalni yozib boradi."""
    foydalanuvchi = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='amal_loglari')
    amal = models.CharField(max_length=255, help_text="masalan: 'oquvchi_yaratildi', 'daraja_ochildi'")
    tavsif = models.TextField(blank=True)
    nishon_user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='+',
        help_text="Amal kimga nisbatan bajarilgan (masalan qaysi o'quvchi)"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'admin_amal_loglari'
        ordering = ['-created_at']
        verbose_name = 'Admin amal logi'
        verbose_name_plural = 'Admin amal loglari'

    def __str__(self):
        return f"{self.foydalanuvchi} - {self.amal} - {self.created_at:%Y-%m-%d %H:%M}"

# ==================== AI YORDAMCHI ====================

class AIYordamchiXabar(models.Model):
    ROLE_USER = 'user'
    ROLE_ASSISTANT = 'assistant'
    ROLE_CHOICES = ((ROLE_USER, "O'quvchi"), (ROLE_ASSISTANT, 'AI yordamchi'))

    oquvchi = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_yordamchi_xabarlari')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    matn = models.TextField()
    meta = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ai_yordamchi_xabarlari'
        ordering = ['created_at']
        indexes = [models.Index(fields=['oquvchi', '-created_at'], name='ai_oquvchi_created_idx')]
        verbose_name = 'AI yordamchi xabari'
        verbose_name_plural = 'AI yordamchi xabarlari'


# ==================== MUROJAATLAR ====================

class Murojaat(models.Model):
    KATEGORIYA_CHOICES = (
        ('texnik', 'Texnik muammo'),
        ('dars', "Dars bo'yicha savol"),
        ('test', "Test yoki natija"),
        ('sertifikat', 'Sertifikat'),
        ('hisob', 'Hisob va xavfsizlik'),
        ('taklif', 'Taklif'),
        ('boshqa', 'Boshqa'),
    )
    STATUS_CHOICES = (
        ('yangi', 'Yangi'),
        ('korilmoqda', "Ko'rib chiqilmoqda"),
        ('javob_berildi', 'Javob berildi'),
        ('yopildi', 'Yopildi'),
    )
    USTUVORLIK_CHOICES = (
        ('past', 'Past'),
        ('oddiy', 'Oddiy'),
        ('yuqori', 'Yuqori'),
        ('shoshilinch', 'Shoshilinch'),
    )

    kod = models.CharField(max_length=16, unique=True, db_index=True, editable=False)
    foydalanuvchi = models.ForeignKey(User, on_delete=models.CASCADE, related_name='murojaatlar')
    kategoriya = models.CharField(max_length=30, choices=KATEGORIYA_CHOICES, default='boshqa')
    sarlavha = models.CharField(max_length=200)
    matn = models.TextField()
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='yangi')
    ustuvorlik = models.CharField(max_length=20, choices=USTUVORLIK_CHOICES, default='oddiy')
    oxirgi_javob_adminniki = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    closed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'murojaatlar'
        ordering = ['-updated_at']
        indexes = [models.Index(fields=['status', '-updated_at'], name='murojaat_status_idx')]
        verbose_name = 'Murojaat'
        verbose_name_plural = 'Murojaatlar'

    def save(self, *args, **kwargs):
        if not self.kod:
            self.kod = f"MR-{uuid.uuid4().hex[:10].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.kod} - {self.sarlavha}"


class MurojaatJavob(models.Model):
    murojaat = models.ForeignKey(Murojaat, on_delete=models.CASCADE, related_name='javoblar')
    muallif = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='murojaat_javoblari')
    matn = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'murojaat_javoblari'
        ordering = ['created_at']
        verbose_name = 'Murojaat javobi'
        verbose_name_plural = 'Murojaat javoblari'


# ==================== PLATFORMA SOZLAMALARI ====================

class PlatformSozlama(models.Model):
    platform_nomi = models.CharField(max_length=150, default='Al-Aziz Academy')
    platform_qisqa_nomi = models.CharField(max_length=40, default='AL-AZIZ')
    logo_url = models.URLField(blank=True)
    ai_yordamchi_faol = models.BooleanField(default=True)
    ai_kunlik_limit = models.PositiveIntegerField(default=30)
    murojaatlar_faol = models.BooleanField(default=True)
    texnik_rejim = models.BooleanField(default=False)
    texnik_xabar = models.CharField(max_length=255, blank=True, default="Platformada texnik ishlar olib borilmoqda.")
    max_fayl_mb = models.PositiveIntegerField(default=10)
    standart_test_foizi = models.PositiveIntegerField(default=80)
    mashq_coin = models.PositiveIntegerField(default=5)
    final_test_coin = models.PositiveIntegerField(default=50)
    tezkor_oyin_har_javob_coin = models.PositiveIntegerField(default=1)
    tezkor_oyin_mukammal_bonus = models.PositiveIntegerField(default=5)
    birinchi_urinish_bonus = models.PositiveIntegerField(default=3)
    mukammal_test_bonus = models.PositiveIntegerField(default=10)
    bildirishnomalar_faol = models.BooleanField(default=True)
    tolov_nazorati_faol = models.BooleanField(default=False)
    tolov_ogohlantirish_kun = models.PositiveIntegerField(default=3)
    xavfsizlik_eslatmasi = models.CharField(
        max_length=255,
        default="Parolingizni hech kimga bermang va umumiy qurilmalarda hisobdan chiqishni unutmang.",
    )
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'platform_sozlamalari'
        verbose_name = 'Platforma sozlamasi'
        verbose_name_plural = 'Platforma sozlamalari'

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


# ==================== BILDIRISHNOMALAR ====================

class Bildirishnoma(models.Model):
    TARGET_ALL = 'all'
    TARGET_USER = 'user'
    TARGET_FAN = 'fan'
    TARGET_DARAJA = 'daraja'
    TARGET_CHOICES = (
        (TARGET_ALL, 'Barcha o‘quvchilar'),
        (TARGET_USER, 'Bitta o‘quvchi'),
        (TARGET_FAN, 'Fan bo‘yicha'),
        (TARGET_DARAJA, 'Daraja bo‘yicha'),
    )
    TUR_CHOICES = (
        ('info', 'Ma’lumot'),
        ('success', 'Muvaffaqiyat'),
        ('warning', 'Ogohlantirish'),
        ('danger', 'Muhim'),
    )

    sarlavha = models.CharField(max_length=180)
    matn = models.TextField()
    tur = models.CharField(max_length=20, choices=TUR_CHOICES, default='info')
    target_turi = models.CharField(max_length=20, choices=TARGET_CHOICES, default=TARGET_ALL)
    target_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='shaxsiy_bildirishnomalar')
    target_fan = models.ForeignKey('courses.Fan', on_delete=models.CASCADE, null=True, blank=True, related_name='bildirishnomalar')
    target_daraja = models.ForeignKey('courses.Daraja', on_delete=models.CASCADE, null=True, blank=True, related_name='bildirishnomalar')
    havola = models.CharField(max_length=300, blank=True)
    faol = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='yaratgan_bildirishnomalar')
    created_at = models.DateTimeField(auto_now_add=True)
    tugash_sana = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'bildirishnomalar'
        ordering = ['-created_at']
        indexes = [models.Index(fields=['faol', '-created_at'], name='bildirishnoma_faol_idx')]

    def __str__(self):
        return self.sarlavha


class BildirishnomaOqildi(models.Model):
    bildirishnoma = models.ForeignKey(Bildirishnoma, on_delete=models.CASCADE, related_name='oqilganlar')
    oquvchi = models.ForeignKey(User, on_delete=models.CASCADE, related_name='oqilgan_bildirishnomalar')
    oqilgan_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'bildirishnoma_oqildi'
        unique_together = ('bildirishnoma', 'oquvchi')


# ==================== PLACEMENT TEST NATIJASI ====================

class PlacementNatija(models.Model):
    oquvchi = models.ForeignKey(User, on_delete=models.CASCADE, related_name='placement_natijalari')
    fan = models.ForeignKey('courses.Fan', on_delete=models.CASCADE, related_name='placement_natijalari')
    togri_soni = models.PositiveIntegerField(default=0)
    jami_soni = models.PositiveIntegerField(default=0)
    foiz = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    tavsiya_daraja = models.ForeignKey('courses.Daraja', on_delete=models.SET_NULL, null=True, blank=True, related_name='placement_tavsiyalari')
    javoblar = models.JSONField(default=list, blank=True)
    xavfsizlik = models.JSONField(default=dict, blank=True)
    tasdiqlangan = models.BooleanField(default=False)
    tasdiqlagan = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='tasdiqlagan_placement_natijalari')
    tasdiqlangan_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'placement_natijalari'
        ordering = ['-created_at']


# ==================== TEST XAVFSIZLIGI ====================

class TestXavfsizlikLog(models.Model):
    TEST_CHOICES = (
        ('mashq', 'Mashq'),
        ('gate', 'Gate Test'),
        ('final', 'Final Test'),
        ('placement', 'Placement Test'),
    )
    oquvchi = models.ForeignKey(User, on_delete=models.CASCADE, related_name='test_xavfsizlik_loglari')
    test_turi = models.CharField(max_length=20, choices=TEST_CHOICES)
    obyekt_id = models.PositiveIntegerField(default=0)
    davomiylik_soniya = models.PositiveIntegerField(default=0)
    sahifadan_chiqish_soni = models.PositiveIntegerField(default=0)
    shubhali = models.BooleanField(default=False)
    sabablar = models.JSONField(default=list, blank=True)
    user_agent = models.CharField(max_length=500, blank=True)
    ip_manzil = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'test_xavfsizlik_loglari'
        ordering = ['-created_at']
        indexes = [models.Index(fields=['shubhali', '-created_at'], name='test_xavfsiz_shubha_idx')]


# ==================== FOYDALANUVCHI FAOLIYATI ====================

class FaoliyatLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='faoliyat_loglari')
    amal = models.CharField(max_length=60)
    tavsif = models.CharField(max_length=300, blank=True)
    obyekt_turi = models.CharField(max_length=60, blank=True)
    obyekt_id = models.PositiveIntegerField(null=True, blank=True)
    meta = models.JSONField(default=dict, blank=True)
    ip_manzil = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'foydalanuvchi_faoliyati'
        ordering = ['-created_at']
        indexes = [models.Index(fields=['user', '-created_at'], name='faoliyat_user_created_idx')]


class OquvchiKunlikFaollik(models.Model):
    oquvchi = models.ForeignKey(User, on_delete=models.CASCADE, related_name='kunlik_faollik')
    sana = models.DateField()

    class Meta:
        db_table = 'oquvchi_kunlik_faollik'
        unique_together = ('oquvchi', 'sana')
        ordering = ['-sana']


# ==================== YUTUQLAR ====================

class Yutuq(models.Model):
    kod = models.CharField(max_length=50, unique=True)
    nomi = models.CharField(max_length=150)
    tavsif = models.CharField(max_length=300)
    icon = models.CharField(max_length=40, default='🏆')
    coin_mukofot = models.PositiveIntegerField(default=0)
    faol = models.BooleanField(default=True)
    tartib = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'yutuqlar'
        ordering = ['tartib', 'id']

    def __str__(self):
        return self.nomi


class OquvchiYutuq(models.Model):
    oquvchi = models.ForeignKey(User, on_delete=models.CASCADE, related_name='yutuqlari')
    yutuq = models.ForeignKey(Yutuq, on_delete=models.CASCADE, related_name='olganlar')
    meta = models.JSONField(default=dict, blank=True)
    olingan_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'oquvchi_yutuqlari'
        unique_together = ('oquvchi', 'yutuq')
        ordering = ['-olingan_at']


# ==================== TO‘LOV VA FOYDALANISH MUDDATI ====================

class Tolov(models.Model):
    STATUS_CHOICES = (
        ('tolangan', 'To‘langan'),
        ('qisman', 'Qisman to‘langan'),
        ('qarzdor', 'Qarzdor'),
        ('imtiyozli', 'Imtiyozli'),
        ('bekor', 'Bekor qilingan'),
    )
    oquvchi = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tolovlar')
    summa = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tolangan_summa = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    chegirma_foiz = models.PositiveIntegerField(default=0)
    boshlanish_sana = models.DateField()
    tugash_sana = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='qarzdor')
    izoh = models.CharField(max_length=300, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='kiritgan_tolovlar')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'tolovlar'
        ordering = ['-tugash_sana', '-created_at']
        indexes = [models.Index(fields=['oquvchi', '-tugash_sana'], name='tolov_user_end_idx')]

    @property
    def qolgan_summa(self):
        return max(self.summa - self.tolangan_summa, 0)


# ==================== TEZKOR TARJIMA O‘YINI ====================

class TezkorOyiniSessiya(models.Model):
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True)
    oquvchi = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tezkor_oyin_sessiyalari')
    fan = models.ForeignKey('courses.Fan', on_delete=models.CASCADE, related_name='tezkor_oyin_sessiyalari')
    savollar = models.JSONField(default=list)
    togri_soni = models.PositiveIntegerField(default=0)
    jami_soni = models.PositiveIntegerField(default=10)
    berilgan_coin = models.PositiveIntegerField(default=0)
    tugallangan = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'tezkor_oyin_sessiyalari'
        ordering = ['-created_at']

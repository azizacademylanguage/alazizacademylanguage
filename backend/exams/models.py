import uuid

from django.db import models
from django.utils import timezone
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
    otish_bali_foiz = models.PositiveIntegerField(default=80)

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
    baholash_tafsiloti = models.JSONField(default=dict, blank=True)
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
    transkripsiya = models.TextField(blank=True)
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
        ('soz_oyini', "So'z o'yini"),
        ('streak', 'Kunlik faollik bonusi'),
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


# ==================== SO'Z XOTIRA O'YINI ====================

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


class SozOyiniSessiya(models.Model):
    """20 ta yopiq karta (10 juft) uchun bir martalik, tekshiriladigan o'yin sessiyasi."""
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True)
    oquvchi = models.ForeignKey(User, on_delete=models.CASCADE, related_name='soz_oyini_sessiyalari')
    fan = models.ForeignKey('courses.Fan', on_delete=models.CASCADE, related_name='soz_oyini_sessiyalari')
    cardlar = models.JSONField(default=list)
    tugallangan = models.BooleanField(default=False)
    topilgan_soni = models.PositiveIntegerField(default=0)
    berilgan_coin = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'soz_oyini_sessiyalari'
        ordering = ['-created_at']
        verbose_name = "So'z o'yini sessiyasi"
        verbose_name_plural = "So'z o'yini sessiyalari"

    def __str__(self):
        return f"{self.oquvchi.full_name} - {self.fan.nomi} - {self.topilgan_soni}/10"


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
    obyekt_turi = models.CharField(max_length=80, blank=True)
    obyekt_id = models.CharField(max_length=80, blank=True)
    ip_manzil = models.GenericIPAddressField(null=True, blank=True)
    oldingi_holat = models.JSONField(default=dict, blank=True)
    yangi_holat = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'admin_amal_loglari'
        ordering = ['-created_at']
        verbose_name = 'Admin amal logi'
        verbose_name_plural = 'Admin amal loglari'

    def __str__(self):
        return f"{self.foydalanuvchi} - {self.amal} - {self.created_at:%Y-%m-%d %H:%M}"

# ==================== LISTENING / FAOLLIK / BILDIRISHNOMALAR ====================

class ListeningSavol(models.Model):
    """Brauzer ovoz chiqarib o'qiydigan listening savoli."""
    dars = models.ForeignKey('courses.Dars', on_delete=models.CASCADE, related_name='listening_savollari')
    audio_matn = models.CharField(max_length=500)
    savol = models.CharField(max_length=500, default="Eshitgan so'zingizning tarjimasini tanlang")
    variantlar = models.JSONField(default=list)
    togri_javob = models.CharField(max_length=255)
    til_kodi = models.CharField(max_length=20, default='en-US')
    tartib = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'listening_savollari'
        ordering = ['tartib', 'id']
        verbose_name = 'Listening savoli'
        verbose_name_plural = 'Listening savollari'

    def __str__(self):
        return f"{self.dars} - {self.audio_matn}"


class ListeningNatija(models.Model):
    oquvchi = models.ForeignKey(User, on_delete=models.CASCADE, related_name='listening_natijalari')
    dars = models.ForeignKey('courses.Dars', on_delete=models.CASCADE, related_name='listening_natijalari')
    togri_soni = models.PositiveIntegerField(default=0)
    jami_soni = models.PositiveIntegerField(default=0)
    foiz = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    javoblar = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'listening_natijalari'
        ordering = ['-created_at']
        verbose_name = 'Listening natijasi'
        verbose_name_plural = 'Listening natijalari'

    def __str__(self):
        return f"{self.oquvchi} - {self.dars} - {self.foiz}%"


class KunlikFaollik(models.Model):
    """O'quvchining kunlik kirishi va o'quv amallari streak uchun."""
    oquvchi = models.ForeignKey(User, on_delete=models.CASCADE, related_name='kunlik_faolliklar')
    sana = models.DateField(default=timezone.localdate)
    faollik_soni = models.PositiveIntegerField(default=0)
    turlar = models.JSONField(default=list, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'kunlik_faolliklar'
        unique_together = ('oquvchi', 'sana')
        ordering = ['-sana']
        verbose_name = 'Kunlik faollik'
        verbose_name_plural = 'Kunlik faolliklar'

    def __str__(self):
        return f"{self.oquvchi} - {self.sana} ({self.faollik_soni})"


class Bildirishnoma(models.Model):
    TUR_INFO = 'info'
    TUR_SUCCESS = 'success'
    TUR_WARNING = 'warning'
    TUR_SHOP = 'shop'
    TUR_CERTIFICATE = 'certificate'
    TUR_CHOICES = (
        (TUR_INFO, 'Ma\'lumot'),
        (TUR_SUCCESS, 'Muvaffaqiyat'),
        (TUR_WARNING, 'Ogohlantirish'),
        (TUR_SHOP, "Do'kon"),
        (TUR_CERTIFICATE, 'Sertifikat'),
    )

    oquvchi = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bildirishnomalar')
    sarlavha = models.CharField(max_length=180)
    matn = models.TextField(blank=True)
    tur = models.CharField(max_length=20, choices=TUR_CHOICES, default=TUR_INFO)
    havola = models.CharField(max_length=300, blank=True)
    oqilgan = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'bildirishnomalar'
        ordering = ['-created_at']
        verbose_name = 'Bildirishnoma'
        verbose_name_plural = 'Bildirishnomalar'
        indexes = [models.Index(fields=['oquvchi', 'oqilgan', '-created_at'], name='bildirish_oquvchi_0b824d_idx')]

    def __str__(self):
        return f"{self.oquvchi} - {self.sarlavha}"


# ==================== REYTING VA MUSOBAQA ====================

class Musobaqa(models.Model):
    STATUS_REJA = 'reja'
    STATUS_FAOL = 'faol'
    STATUS_YAKUN = 'yakun'
    STATUS_CHOICES = ((STATUS_REJA, 'Rejada'), (STATUS_FAOL, 'Faol'), (STATUS_YAKUN, 'Yakunlangan'))

    nomi = models.CharField(max_length=180)
    tavsif = models.TextField(blank=True)
    boshlanish_sana = models.DateField()
    tugash_sana = models.DateField()
    fan = models.ForeignKey('courses.Fan', on_delete=models.SET_NULL, null=True, blank=True, related_name='musobaqalar')
    filial = models.ForeignKey('accounts.Filial', on_delete=models.SET_NULL, null=True, blank=True, related_name='musobaqalar')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_REJA)
    davomiyligi_daq = models.PositiveIntegerField(default=15)
    savollar_soni = models.PositiveIntegerField(default=20)
    boshlangan_vaqt = models.DateTimeField(null=True, blank=True)
    yakunlangan_vaqt = models.DateTimeField(null=True, blank=True)
    birinchi_coin = models.PositiveIntegerField(default=100)
    ikkinchi_coin = models.PositiveIntegerField(default=60)
    uchinchi_coin = models.PositiveIntegerField(default=30)
    goliblar = models.JSONField(default=list, blank=True)
    yaratgan = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='yaratgan_musobaqalar')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'musobaqalar'
        ordering = ['-boshlanish_sana', '-id']

    def __str__(self):
        return self.nomi


class MusobaqaUrinish(models.Model):
    STATUS_BOSHLANDI = 'boshlandi'
    STATUS_YAKUN = 'yakun'
    STATUS_CHOICES = (
        (STATUS_BOSHLANDI, 'Boshlangan'),
        (STATUS_YAKUN, 'Yakunlangan'),
    )

    musobaqa = models.ForeignKey(Musobaqa, on_delete=models.CASCADE, related_name='urinishlar')
    oquvchi = models.ForeignKey(User, on_delete=models.CASCADE, related_name='musobaqa_urinishlari')
    savol_idlari = models.JSONField(default=list, blank=True)
    javoblar = models.JSONField(default=list, blank=True)
    togri_soni = models.PositiveIntegerField(default=0)
    jami_soni = models.PositiveIntegerField(default=0)
    foiz = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    sarflangan_soniya = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_BOSHLANDI)
    boshlangan_vaqt = models.DateTimeField(auto_now_add=True)
    tugagan_vaqt = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'musobaqa_urinishlari'
        unique_together = ('musobaqa', 'oquvchi')
        ordering = ['-foiz', 'sarflangan_soniya', 'boshlangan_vaqt']
        indexes = [
            models.Index(fields=['musobaqa', 'status'], name='mus_urinish_status_idx'),
            models.Index(fields=['oquvchi', '-boshlangan_vaqt'], name='mus_urinish_user_idx'),
        ]

    def __str__(self):
        return f"{self.musobaqa} - {self.oquvchi} - {self.foiz}%"

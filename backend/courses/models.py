from django.db import models
from accounts.models import User


class Fan(models.Model):
    """Masalan: English, Matematika"""
    nomi = models.CharField(max_length=100, unique=True)
    tavsif = models.TextField(blank=True)
    icon = models.CharField(max_length=255, blank=True)
    tartib = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'fanlar'
        ordering = ['tartib', 'nomi']
        verbose_name = 'Fan'
        verbose_name_plural = 'Fanlar'

    def __str__(self):
        return self.nomi


class Daraja(models.Model):
    """Masalan: Beginner, Intermediate, Advanced"""
    fan = models.ForeignKey(Fan, on_delete=models.CASCADE, related_name='darajalar')
    nomi = models.CharField(max_length=100)
    tartib = models.PositiveIntegerField(default=0)
    # Qulflash sozlamalari: birinchi daraja (tartib=0/1) odatda har doim ochiq.
    # Keyingi darajalar oldingi darajaning Gate Test'idan o'tilgandagina ochiladi,
    # yoki admin/nazoratchi tomonidan qo'lda ochib qo'yilishi mumkin (OquvchiFan.qolda_ochilgan).
    ochish_uchun_foiz = models.PositiveIntegerField(
        default=60, help_text="Gate Test'dan o'tish uchun kerakli minimal foiz"
    )

    class Meta:
        db_table = 'darajalar'
        unique_together = ('fan', 'nomi')
        ordering = ['tartib']
        verbose_name = 'Daraja'
        verbose_name_plural = 'Darajalar'

    def __str__(self):
        return f"{self.fan.nomi} - {self.nomi}"

    @property
    def oldingi_daraja(self):
        return Daraja.objects.filter(fan=self.fan, tartib__lt=self.tartib).order_by('-tartib').first()


class Mavzu(models.Model):
    daraja = models.ForeignKey(Daraja, on_delete=models.CASCADE, related_name='mavzular')
    nomi = models.CharField(max_length=200)
    tartib = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'mavzular'
        ordering = ['tartib']
        verbose_name = 'Mavzu'
        verbose_name_plural = 'Mavzular'

    def __str__(self):
        return self.nomi


class Dars(models.Model):
    mavzu = models.ForeignKey(Mavzu, on_delete=models.CASCADE, related_name='darslar')
    sarlavha = models.CharField(max_length=200)
    tushuntirish_matn = models.TextField(blank=True)
    video = models.FileField(upload_to='darslar/video/', blank=True, null=True)
    audio = models.FileField(upload_to='darslar/audio/', blank=True, null=True)
    misollar = models.TextField(blank=True)
    tartib = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'darslar'
        ordering = ['tartib']
        verbose_name = 'Dars'
        verbose_name_plural = 'Darslar'

    def __str__(self):
        return self.sarlavha


class OquvchiFan(models.Model):
    """O'quvchiga qaysi fan+daraja biriktirilgan"""
    oquvchi = models.ForeignKey(User, on_delete=models.CASCADE, related_name='biriktirilgan_fanlar')
    daraja = models.ForeignKey(Daraja, on_delete=models.CASCADE, related_name='biriktirilgan_oquvchilar')
    biriktirgan = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='biriktirishlar')
    # True bo'lsa — bu daraja admin/nazoratchi tomonidan qo'lda ochilgan (Gate Test talab qilinmaydi).
    qolda_ochilgan = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'oquvchi_fanlari'
        unique_together = ('oquvchi', 'daraja')
        verbose_name = "O'quvchi fani"
        verbose_name_plural = "O'quvchi fanlari"

    def __str__(self):
        return f"{self.oquvchi} - {self.daraja}"


class DarsProgress(models.Model):
    """O'quvchining har bir darsdagi progressi"""
    oquvchi = models.ForeignKey(User, on_delete=models.CASCADE, related_name='dars_progresslari')
    dars = models.ForeignKey(Dars, on_delete=models.CASCADE, related_name='progresslar')
    video_tugatilgan = models.BooleanField(default=False)
    video_pozitsiya_soniya = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'dars_progress'
        unique_together = ('oquvchi', 'dars')
        verbose_name = 'Dars progressi'
        verbose_name_plural = 'Dars progresslari'

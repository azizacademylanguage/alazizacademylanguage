"""
Gate Test, Final Test, Sertifikat, Writing, Speaking, Coin/Shop uchun serializerlar.
Asosiy exams/serializers.py faylini ortiqcha kattalashtirmaslik uchun alohida fayl.
"""
import random

from rest_framework import serializers
from .models import (
    GateTest, GateTestSavol, GateTestJavob, GateTestNatija,
    FinalTest, FinalTestSavol, FinalTestJavob, FinalTestNatija, Sertifikat,
    WritingTopshiriq, WritingNatija, SpeakingTopshiriq, SpeakingNatija,
    OquvchiCoin, CoinTarix, ShopMahsulot, ShopBuyurtma, SozJuftligi, SozOyiniSessiya, AdminAmalLog,
    ListeningSavol, ListeningNatija, KunlikFaollik, Bildirishnoma,
)
from courses.utils import toza_daraja_nomi


# ==================== GATE TEST ====================

class GateTestJavobSerializer(serializers.ModelSerializer):
    class Meta:
        model = GateTestJavob
        fields = ['id', 'savol', 'matn', 'togri']


class GateTestJavobOquvchigaSerializer(serializers.ModelSerializer):
    class Meta:
        model = GateTestJavob
        fields = ['id', 'matn']


class GateTestSavolSerializer(serializers.ModelSerializer):
    javoblar = GateTestJavobSerializer(many=True, read_only=True)

    class Meta:
        model = GateTestSavol
        fields = ['id', 'gate_test', 'matn', 'tartib', 'javoblar']


class GateTestSavolOquvchigaSerializer(serializers.ModelSerializer):
    javoblar = GateTestJavobOquvchigaSerializer(many=True, read_only=True)

    class Meta:
        model = GateTestSavol
        fields = ['id', 'matn', 'tartib', 'javoblar']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        random.shuffle(data['javoblar'])
        return data


class GateTestSerializer(serializers.ModelSerializer):
    savollar = GateTestSavolSerializer(many=True, read_only=True)
    daraja_nomi = serializers.CharField(source='daraja.nomi', read_only=True)

    class Meta:
        model = GateTest
        fields = ['id', 'daraja', 'daraja_nomi', 'sarlavha', 'savollar']


class GateTestOquvchigaSerializer(serializers.ModelSerializer):
    savollar = GateTestSavolOquvchigaSerializer(many=True, read_only=True)

    class Meta:
        model = GateTest
        fields = ['id', 'sarlavha', 'savollar']


class GateTestNatijaSerializer(serializers.ModelSerializer):
    class Meta:
        model = GateTestNatija
        fields = ['id', 'gate_test', 'togri_soni', 'jami_soni', 'foiz', 'otdi', 'urinish_raqami', 'created_at']


# ==================== FINAL TEST ====================

class FinalTestJavobSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinalTestJavob
        fields = ['id', 'savol', 'matn', 'togri']


class FinalTestJavobOquvchigaSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinalTestJavob
        fields = ['id', 'matn']


class FinalTestSavolSerializer(serializers.ModelSerializer):
    javoblar = FinalTestJavobSerializer(many=True, read_only=True)

    class Meta:
        model = FinalTestSavol
        fields = ['id', 'final_test', 'matn', 'tartib', 'javoblar']


class FinalTestSavolOquvchigaSerializer(serializers.ModelSerializer):
    javoblar = FinalTestJavobOquvchigaSerializer(many=True, read_only=True)

    class Meta:
        model = FinalTestSavol
        fields = ['id', 'matn', 'tartib', 'javoblar']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        random.shuffle(data['javoblar'])
        return data


class FinalTestSerializer(serializers.ModelSerializer):
    savollar = FinalTestSavolSerializer(many=True, read_only=True)
    daraja_nomi = serializers.CharField(source='daraja.nomi', read_only=True)

    class Meta:
        model = FinalTest
        fields = ['id', 'daraja', 'daraja_nomi', 'sarlavha', 'otish_bali_foiz', 'savollar']


class FinalTestOquvchigaSerializer(serializers.ModelSerializer):
    savollar = FinalTestSavolOquvchigaSerializer(many=True, read_only=True)
    daraja_nomi = serializers.SerializerMethodField()
    fan_nomi = serializers.CharField(source='daraja.fan.nomi', read_only=True)

    class Meta:
        model = FinalTest
        fields = ['id', 'sarlavha', 'otish_bali_foiz', 'fan_nomi', 'daraja_nomi', 'savollar']

    def get_daraja_nomi(self, obj):
        return toza_daraja_nomi(obj.daraja.nomi)


class SertifikatSerializer(serializers.ModelSerializer):
    oquvchi_ism = serializers.CharField(source='oquvchi.full_name', read_only=True)
    oquvchi_username = serializers.CharField(source='oquvchi.username', read_only=True)
    daraja_nomi = serializers.SerializerMethodField()
    fan_nomi = serializers.CharField(source='daraja.fan.nomi', read_only=True)
    pdf_url = serializers.SerializerMethodField()
    qr_url = serializers.SerializerMethodField()
    tekshirish_url = serializers.SerializerMethodField()

    class Meta:
        model = Sertifikat
        fields = [
            'id', 'oquvchi', 'oquvchi_ism', 'oquvchi_username', 'daraja',
            'daraja_nomi', 'fan_nomi', 'kod', 'foiz', 'berilgan_sana',
            'pdf_url', 'qr_url', 'tekshirish_url',
        ]

    def get_daraja_nomi(self, obj):
        return toza_daraja_nomi(obj.daraja.nomi)

    def get_pdf_url(self, obj):
        return f'/api/sertifikat/{obj.kod}/pdf/'

    def get_qr_url(self, obj):
        return f'/api/sertifikat/{obj.kod}/qr/'

    def get_tekshirish_url(self, obj):
        from .certificate_pdf import certificate_public_url
        return certificate_public_url(obj)


class FinalTestNatijaSerializer(serializers.ModelSerializer):
    sertifikat = SertifikatSerializer(read_only=True)

    class Meta:
        model = FinalTestNatija
        fields = ['id', 'final_test', 'togri_soni', 'jami_soni', 'foiz', 'otdi', 'sertifikat', 'urinish_raqami', 'created_at']


# ==================== WRITING ====================

class WritingTopshiriqSerializer(serializers.ModelSerializer):
    class Meta:
        model = WritingTopshiriq
        fields = ['id', 'dars', 'matn', 'minimal_soz_soni', 'tartib']


class WritingNatijaSerializer(serializers.ModelSerializer):
    topshiriq_matni = serializers.CharField(source='topshiriq.matn', read_only=True)

    class Meta:
        model = WritingNatija
        fields = ['id', 'topshiriq', 'topshiriq_matni', 'matn_javob', 'ai_foiz', 'ai_izoh',
                   'ai_xatolar', 'baholash_tafsiloti', 'baholanmoqda', 'created_at']
        read_only_fields = ['ai_foiz', 'ai_izoh', 'ai_xatolar', 'baholash_tafsiloti', 'baholanmoqda']


# ==================== SPEAKING ====================

class SpeakingTopshiriqSerializer(serializers.ModelSerializer):
    til_kodi = serializers.SerializerMethodField()

    class Meta:
        model = SpeakingTopshiriq
        fields = ['id', 'dars', 'matn', 'tartib', 'til_kodi']

    def get_til_kodi(self, obj):
        nom = obj.dars.mavzu.daraja.fan.nomi.lower()
        if 'rus' in nom:
            return 'ru-RU'
        if 'kore' in nom:
            return 'ko-KR'
        return 'en-US'


class SpeakingNatijaSerializer(serializers.ModelSerializer):
    topshiriq_matni = serializers.CharField(source='topshiriq.matn', read_only=True)

    class Meta:
        model = SpeakingNatija
        fields = ['id', 'topshiriq', 'topshiriq_matni', 'audio_yozuv', 'transkripsiya', 'ai_foiz', 'ai_izoh',
                   'baholanmoqda', 'created_at']
        read_only_fields = ['ai_foiz', 'ai_izoh', 'baholanmoqda']


# ==================== COIN / SHOP ====================

class OquvchiCoinSerializer(serializers.ModelSerializer):
    class Meta:
        model = OquvchiCoin
        fields = ['balans', 'updated_at']


class CoinTarixSerializer(serializers.ModelSerializer):
    sabab_display = serializers.CharField(source='get_sabab_display', read_only=True)

    class Meta:
        model = CoinTarix
        fields = ['id', 'miqdor', 'sabab', 'sabab_display', 'izoh', 'created_at']


class ShopMahsulotSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShopMahsulot
        fields = ['id', 'nomi', 'tavsif', 'narx_coin', 'rasm', 'faol']


class ShopBuyurtmaSerializer(serializers.ModelSerializer):
    mahsulot_nomi = serializers.CharField(source='mahsulot.nomi', read_only=True)
    mahsulot_tavsif = serializers.CharField(source='mahsulot.tavsif', read_only=True)
    oquvchi_ism = serializers.CharField(source='oquvchi.full_name', read_only=True)
    oquvchi_username = serializers.CharField(source='oquvchi.username', read_only=True)
    filial_nomi = serializers.CharField(source='oquvchi.filial.nomi', read_only=True, allow_null=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = ShopBuyurtma
        fields = [
            'id', 'oquvchi', 'oquvchi_ism', 'oquvchi_username', 'filial_nomi',
            'mahsulot', 'mahsulot_nomi', 'mahsulot_tavsif', 'narx_coin',
            'status', 'status_display', 'created_at',
        ]
        read_only_fields = ['oquvchi', 'mahsulot', 'narx_coin', 'created_at']


class SozJuftligiSerializer(serializers.ModelSerializer):
    fan_nomi = serializers.CharField(source='fan.nomi', read_only=True)

    class Meta:
        model = SozJuftligi
        fields = ['id', 'fan', 'fan_nomi', 'chet_soz', 'uzbek_soz', 'tartib', 'faol']


# ==================== ADMIN AUDIT LOG ====================

class AdminAmalLogSerializer(serializers.ModelSerializer):
    foydalanuvchi_ism = serializers.CharField(source='foydalanuvchi.full_name', read_only=True)
    nishon_ism = serializers.CharField(source='nishon_user.full_name', read_only=True)

    class Meta:
        model = AdminAmalLog
        fields = ['id', 'foydalanuvchi', 'foydalanuvchi_ism', 'amal', 'tavsif', 'nishon_user', 'nishon_ism',
                  'obyekt_turi', 'obyekt_id', 'ip_manzil', 'oldingi_holat', 'yangi_holat', 'created_at']


# ==================== LISTENING / FAOLLIK / BILDIRISHNOMALAR ====================

class ListeningSavolOquvchigaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListeningSavol
        fields = ['id', 'audio_matn', 'savol', 'variantlar', 'til_kodi', 'tartib']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        variants = list(data.get('variantlar') or [])
        random.shuffle(variants)
        data['variantlar'] = variants
        return data


class ListeningNatijaSerializer(serializers.ModelSerializer):
    dars_nomi = serializers.CharField(source='dars.sarlavha', read_only=True)

    class Meta:
        model = ListeningNatija
        fields = ['id', 'dars', 'dars_nomi', 'togri_soni', 'jami_soni', 'foiz', 'created_at']


class BildirishnomaSerializer(serializers.ModelSerializer):
    tur_display = serializers.CharField(source='get_tur_display', read_only=True)

    class Meta:
        model = Bildirishnoma
        fields = ['id', 'sarlavha', 'matn', 'tur', 'tur_display', 'havola', 'oqilgan', 'created_at']

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
                   'ai_xatolar', 'baholanmoqda', 'created_at']
        read_only_fields = ['ai_foiz', 'ai_izoh', 'ai_xatolar', 'baholanmoqda']


# ==================== SPEAKING ====================

class SpeakingTopshiriqSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpeakingTopshiriq
        fields = ['id', 'dars', 'matn', 'tartib']


class SpeakingNatijaSerializer(serializers.ModelSerializer):
    topshiriq_matni = serializers.CharField(source='topshiriq.matn', read_only=True)

    class Meta:
        model = SpeakingNatija
        fields = ['id', 'topshiriq', 'topshiriq_matni', 'audio_yozuv', 'ai_foiz', 'ai_izoh',
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
        fields = ['id', 'foydalanuvchi', 'foydalanuvchi_ism', 'amal', 'tavsif', 'nishon_user', 'nishon_ism', 'created_at']

# ==================== AI YORDAMCHI / MUROJAAT / SOZLAMA ====================

from .models import AIYordamchiXabar, Murojaat, MurojaatJavob, PlatformSozlama


class AIYordamchiXabarSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIYordamchiXabar
        fields = ['id', 'role', 'matn', 'meta', 'created_at']


class MurojaatJavobSerializer(serializers.ModelSerializer):
    muallif_ism = serializers.SerializerMethodField()
    muallif_role = serializers.CharField(source='muallif.role', read_only=True, allow_null=True)

    class Meta:
        model = MurojaatJavob
        fields = ['id', 'muallif', 'muallif_ism', 'muallif_role', 'matn', 'created_at']
        read_only_fields = ['muallif']

    def get_muallif_ism(self, obj):
        return obj.muallif.full_name if obj.muallif else 'Tizim'


class MurojaatSerializer(serializers.ModelSerializer):
    foydalanuvchi_ism = serializers.CharField(source='foydalanuvchi.full_name', read_only=True)
    username = serializers.CharField(source='foydalanuvchi.username', read_only=True)
    filial_nomi = serializers.CharField(source='foydalanuvchi.filial.nomi', read_only=True, allow_null=True)
    kategoriya_display = serializers.CharField(source='get_kategoriya_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    ustuvorlik_display = serializers.CharField(source='get_ustuvorlik_display', read_only=True)
    javoblar = MurojaatJavobSerializer(many=True, read_only=True)
    javoblar_soni = serializers.SerializerMethodField()

    class Meta:
        model = Murojaat
        fields = [
            'id', 'kod', 'foydalanuvchi', 'foydalanuvchi_ism', 'username', 'filial_nomi',
            'kategoriya', 'kategoriya_display', 'sarlavha', 'matn', 'status', 'status_display',
            'ustuvorlik', 'ustuvorlik_display', 'oxirgi_javob_adminniki', 'javoblar_soni',
            'javoblar', 'created_at', 'updated_at', 'closed_at',
        ]
        read_only_fields = ['kod', 'foydalanuvchi', 'status', 'ustuvorlik', 'oxirgi_javob_adminniki', 'closed_at']

    def get_javoblar_soni(self, obj):
        return obj.javoblar.count()


class PlatformSozlamaSerializer(serializers.ModelSerializer):
    updated_by_ism = serializers.CharField(source='updated_by.full_name', read_only=True, allow_null=True)

    class Meta:
        model = PlatformSozlama
        fields = [
            'id', 'platform_nomi', 'platform_qisqa_nomi', 'logo_url', 'ai_yordamchi_faol',
            'ai_kunlik_limit', 'murojaatlar_faol', 'texnik_rejim', 'texnik_xabar',
            'max_fayl_mb', 'standart_test_foizi', 'mashq_coin', 'final_test_coin',
            'xavfsizlik_eslatmasi', 'updated_by', 'updated_by_ism', 'updated_at',
        ]
        read_only_fields = ['updated_by', 'updated_at']

    def validate_ai_kunlik_limit(self, value):
        if value > 500:
            raise serializers.ValidationError('Kunlik limit 500 tadan oshmasin.')
        return value

    def validate_standart_test_foizi(self, value):
        if value < 1 or value > 100:
            raise serializers.ValidationError("Foiz 1 dan 100 gacha bo'lishi kerak.")
        return value

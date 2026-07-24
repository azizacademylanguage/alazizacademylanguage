import random

from rest_framework import serializers
from .models import Mashq, Savol, Javob, MashqNatija, OquvchiJavob


class JavobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Javob
        fields = ['id', 'savol', 'matn', 'togri']


class JavobOquvchigaSerializer(serializers.ModelSerializer):
    """O'quvchiga ko'rsatiladigan variant — 'togri' maydoni yashiriladi"""
    class Meta:
        model = Javob
        fields = ['id', 'matn']


class SavolSerializer(serializers.ModelSerializer):
    javoblar = JavobSerializer(many=True, read_only=True)

    class Meta:
        model = Savol
        fields = ['id', 'mashq', 'matn', 'rasm', 'tur', 'togri_matn_javob', 'tartib', 'javoblar']


class SavolOquvchigaSerializer(serializers.ModelSerializer):
    """Mashqni boshlaganda o'quvchiga ko'rsatiladigan savol — to'g'ri javob yashirilgan"""
    javoblar = JavobOquvchigaSerializer(many=True, read_only=True)

    class Meta:
        model = Savol
        fields = ['id', 'matn', 'rasm', 'tur', 'tartib', 'javoblar']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        random.shuffle(data['javoblar'])
        return data


class MashqSerializer(serializers.ModelSerializer):
    savollar = SavolSerializer(many=True, read_only=True)
    savollar_soni = serializers.ReadOnlyField()

    class Meta:
        model = Mashq
        fields = ['id', 'dars', 'sarlavha', 'vaqt_chegarasi_daq', 'otish_bali_foiz', 'savollar', 'savollar_soni']


class MashqOquvchigaSerializer(serializers.ModelSerializer):
    """O'quvchi mashqni boshlaganda ko'radigan versiya (javoblar yashirin)"""
    savollar = SavolOquvchigaSerializer(many=True, read_only=True)
    savollar_soni = serializers.ReadOnlyField()

    class Meta:
        model = Mashq
        fields = ['id', 'sarlavha', 'vaqt_chegarasi_daq', 'otish_bali_foiz', 'savollar', 'savollar_soni']


class MashqNatijaSerializer(serializers.ModelSerializer):
    mashq_sarlavha = serializers.CharField(source='mashq.sarlavha', read_only=True)
    oquvchi_ism = serializers.CharField(source='oquvchi.full_name', read_only=True)

    class Meta:
        model = MashqNatija
        fields = ['id', 'oquvchi', 'oquvchi_ism', 'mashq', 'mashq_sarlavha', 'togri_soni',
                   'jami_soni', 'foiz', 'urinish_raqami', 'boshlangan_vaqt', 'tugagan_vaqt']


class OquvchiJavobBatafsilSerializer(serializers.ModelSerializer):
    """Xatolar ustida ishlash uchun — savol, berilgan javob, to'g'ri javob"""
    savol_matni = serializers.CharField(source='savol.matn', read_only=True)
    tanlangan_javoblar_matni = serializers.SerializerMethodField()
    togri_javoblar_matni = serializers.SerializerMethodField()

    class Meta:
        model = OquvchiJavob
        fields = ['id', 'savol', 'savol_matni', 'tanlangan_javoblar_matni',
                   'togri_javoblar_matni', 'matn_javob', 'togri_berilgan']

    def get_tanlangan_javoblar_matni(self, obj):
        return [j.matn for j in obj.tanlangan_javoblar.all()]

    def get_togri_javoblar_matni(self, obj):
        return [j.matn for j in obj.savol.javoblar.filter(togri=True)]

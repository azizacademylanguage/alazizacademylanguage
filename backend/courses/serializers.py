from rest_framework import serializers
from .models import Fan, Daraja, Mavzu, Dars, OquvchiFan, DarsProgress
from .utils import toza_daraja_nomi


class DarsSerializer(serializers.ModelSerializer):
    mashq_id = serializers.SerializerMethodField()

    class Meta:
        model = Dars
        fields = ['id', 'mavzu', 'sarlavha', 'tushuntirish_matn', 'video', 'audio', 'misollar', 'tartib', 'mashq_id']

    def get_mashq_id(self, obj):
        return obj.mashq.id if hasattr(obj, 'mashq') else None


class DarsQisqaSerializer(serializers.ModelSerializer):
    """Mavzu ichida darslar ro'yxati uchun (progress bilan)"""
    tugatilgan = serializers.SerializerMethodField()
    mashq_bor = serializers.SerializerMethodField()
    testdan_otilgan = serializers.SerializerMethodField()
    eng_yaxshi_foiz = serializers.SerializerMethodField()

    class Meta:
        model = Dars
        fields = ['id', 'sarlavha', 'tartib', 'tugatilgan', 'mashq_bor', 'testdan_otilgan', 'eng_yaxshi_foiz']

    def get_tugatilgan(self, obj):
        oquvchi = self.context.get('oquvchi')
        if not oquvchi:
            return False
        progress = obj.progresslar.filter(oquvchi=oquvchi).first()
        return bool(progress and progress.video_tugatilgan)

    def get_mashq_bor(self, obj):
        return hasattr(obj, 'mashq')

    def get_testdan_otilgan(self, obj):
        oquvchi = self.context.get('oquvchi')
        if not oquvchi or not hasattr(obj, 'mashq'):
            return False
        return obj.mashq.natijalar.filter(oquvchi=oquvchi, foiz__gte=80).exists()

    def get_eng_yaxshi_foiz(self, obj):
        oquvchi = self.context.get('oquvchi')
        if not oquvchi or not hasattr(obj, 'mashq'):
            return 0
        best = obj.mashq.natijalar.filter(oquvchi=oquvchi).order_by('-foiz').values_list('foiz', flat=True).first()
        return float(best or 0)


class MavzuSerializer(serializers.ModelSerializer):
    darslar = DarsSerializer(many=True, read_only=True)

    class Meta:
        model = Mavzu
        fields = ['id', 'daraja', 'nomi', 'tartib', 'darslar']


class MavzuQisqaSerializer(serializers.ModelSerializer):
    darslar = DarsQisqaSerializer(many=True, read_only=True)
    darslar_soni = serializers.SerializerMethodField()
    ochiq = serializers.SerializerMethodField()
    otilgan = serializers.SerializerMethodField()
    eng_yaxshi_foiz = serializers.SerializerMethodField()
    otish_foizi = serializers.SerializerMethodField()
    qulf_sababi = serializers.SerializerMethodField()

    class Meta:
        model = Mavzu
        fields = ['id', 'nomi', 'tartib', 'darslar', 'darslar_soni', 'ochiq', 'otilgan',
                  'eng_yaxshi_foiz', 'otish_foizi', 'qulf_sababi']

    def get_darslar_soni(self, obj):
        return obj.darslar.count()

    def _holat(self, obj):
        cache = self.context.setdefault('_mavzu_holat_cache', {})
        if obj.id not in cache:
            from .access import mavzu_holati
            cache[obj.id] = mavzu_holati(self.context.get('oquvchi'), obj)
        return cache[obj.id]

    def get_ochiq(self, obj):
        return self._holat(obj)['ochiq']

    def get_otilgan(self, obj):
        return self._holat(obj)['otilgan']

    def get_eng_yaxshi_foiz(self, obj):
        return self._holat(obj)['eng_yaxshi_foiz']

    def get_otish_foizi(self, obj):
        return self._holat(obj)['otish_foizi']

    def get_qulf_sababi(self, obj):
        return self._holat(obj)['qulf_sababi']


class DarajaSerializer(serializers.ModelSerializer):
    mavzular = MavzuSerializer(many=True, read_only=True)
    fan_nomi = serializers.CharField(source='fan.nomi', read_only=True)
    nomi = serializers.SerializerMethodField()

    class Meta:
        model = Daraja
        fields = ['id', 'fan', 'fan_nomi', 'nomi', 'tartib', 'mavzular']

    def get_nomi(self, obj):
        return toza_daraja_nomi(obj.nomi)


class FanSerializer(serializers.ModelSerializer):
    darajalar = DarajaSerializer(many=True, read_only=True)

    class Meta:
        model = Fan
        fields = ['id', 'nomi', 'tavsif', 'icon', 'tartib', 'darajalar']


class FanQisqaSerializer(serializers.ModelSerializer):
    """Ro'yxatlarda ishlatish uchun (nested bo'lmagan)"""
    class Meta:
        model = Fan
        fields = ['id', 'nomi', 'tavsif', 'icon', 'tartib']


class DarajaEngQisqaSerializer(serializers.ModelSerializer):
    nomi = serializers.SerializerMethodField()

    class Meta:
        model = Daraja
        fields = ['id', 'nomi', 'tartib']

    def get_nomi(self, obj):
        return toza_daraja_nomi(obj.nomi)


class FanRoyxatSerializer(serializers.ModelSerializer):
    """Fan ro'yxati + darajalar (mavzu/darslarsiz) — nazoratchi fan biriktirish uchun"""
    darajalar = DarajaEngQisqaSerializer(many=True, read_only=True)

    class Meta:
        model = Fan
        fields = ['id', 'nomi', 'tavsif', 'icon', 'tartib', 'darajalar']


class DarajaQisqaSerializer(serializers.ModelSerializer):
    fan_nomi = serializers.CharField(source='fan.nomi', read_only=True)
    nomi = serializers.SerializerMethodField()

    class Meta:
        model = Daraja
        fields = ['id', 'fan', 'fan_nomi', 'nomi', 'tartib']

    def get_nomi(self, obj):
        return toza_daraja_nomi(obj.nomi)


class OquvchiFanSerializer(serializers.ModelSerializer):
    daraja_nomi = serializers.SerializerMethodField()
    fan_nomi = serializers.CharField(source='daraja.fan.nomi', read_only=True)
    fan_id = serializers.IntegerField(source='daraja.fan.id', read_only=True)
    ochiq = serializers.SerializerMethodField()
    gate_test_bor = serializers.SerializerMethodField()
    final_test_bor = serializers.SerializerMethodField()
    darajalar = serializers.SerializerMethodField()

    class Meta:
        model = OquvchiFan
        fields = ['id', 'oquvchi', 'daraja', 'daraja_nomi', 'fan_nomi', 'fan_id',
                  'ochiq', 'gate_test_bor', 'final_test_bor', 'darajalar', 'created_at']
        read_only_fields = ['oquvchi', 'biriktirgan']

    def get_daraja_nomi(self, obj):
        return toza_daraja_nomi(obj.daraja.nomi)

    def get_ochiq(self, obj):
        from .access import daraja_ochiqmi
        return daraja_ochiqmi(obj.oquvchi, obj.daraja)

    def get_gate_test_bor(self, obj):
        return hasattr(obj.daraja, 'gate_test')

    def get_final_test_bor(self, obj):
        return hasattr(obj.daraja, 'final_test')

    def get_darajalar(self, obj):
        """Faqat tanlangan fan darajalari, avtomatik ochilish holati bilan."""
        from .access import daraja_ochiqmi, daraja_qulf_sababi
        from exams.models import FinalTestNatija

        data = []
        for daraja in obj.daraja.fan.darajalar.all().order_by('tartib', 'id'):
            ochiq = daraja_ochiqmi(obj.oquvchi, daraja)
            eng_yaxshi = FinalTestNatija.objects.filter(
                oquvchi=obj.oquvchi,
                final_test__daraja=daraja,
            ).order_by('-foiz').values_list('foiz', flat=True).first()
            otilgan = FinalTestNatija.objects.filter(
                oquvchi=obj.oquvchi,
                final_test__daraja=daraja,
                otdi=True,
                foiz__gte=80,
            ).exists()
            data.append({
                'id': daraja.id,
                'nomi': toza_daraja_nomi(daraja.nomi),
                'tartib': daraja.tartib,
                'tanlangan': daraja.id == obj.daraja_id,
                'ochiq': ochiq,
                'otilgan': otilgan,
                'eng_yaxshi_foiz': float(eng_yaxshi or 0),
                'qulf_sababi': '' if ochiq else daraja_qulf_sababi(obj.oquvchi, daraja),
            })
        return data


class DarsProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = DarsProgress
        fields = ['id', 'dars', 'video_tugatilgan', 'video_pozitsiya_soniya', 'updated_at']
        read_only_fields = ['oquvchi']

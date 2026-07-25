from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from courses.models import Daraja, OquvchiFan
from courses.utils import toza_daraja_nomi
from .models import Filial, KirishTarixi

User = get_user_model()


class FilialSerializer(serializers.ModelSerializer):
    oquvchilar_soni = serializers.SerializerMethodField()
    nazoratchilar_soni = serializers.SerializerMethodField()

    class Meta:
        model = Filial
        fields = ['id', 'nomi', 'manzil', 'created_at', 'oquvchilar_soni', 'nazoratchilar_soni']

    def get_oquvchilar_soni(self, obj):
        return obj.users.filter(role=User.ROLE_OQUVCHI).count()

    def get_nazoratchilar_soni(self, obj):
        return obj.users.filter(role=User.ROLE_NAZORATCHI).count()


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Login qilganda token bilan birga user ma'lumotlarini ham qaytaradi."""

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = user.role
        token['username'] = user.username
        token['token_version'] = user.token_version
        return token

    def validate(self, attrs):
        request = self.context.get('request')
        username = attrs.get(self.username_field, '')
        ip_manzil = None
        user_agent = ''
        if request:
            forwarded = request.META.get('HTTP_X_FORWARDED_FOR', '')
            ip_manzil = (forwarded.split(',')[0].strip() if forwarded else request.META.get('REMOTE_ADDR')) or None
            user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]
        try:
            data = super().validate(attrs)
        except Exception:
            KirishTarixi.objects.create(
                user=User.objects.filter(username=username).first(),
                username=username,
                muvaffaqiyatli=False,
                ip_manzil=ip_manzil,
                user_agent=user_agent,
            )
            raise

        user = self.user
        KirishTarixi.objects.create(
            user=user,
            username=user.username,
            muvaffaqiyatli=True,
            ip_manzil=ip_manzil,
            user_agent=user_agent,
        )
        try:
            from exams.features import log_faoliyat, check_achievements
            if request:
                log_faoliyat(request, 'kirish', 'Platformaga muvaffaqiyatli kirildi')
                if user.role == User.ROLE_OQUVCHI:
                    check_achievements(user)
        except Exception:
            # Yangi migratsiyalar hali bajarilmagan birinchi deployda loginni to'xtatmaydi.
            pass
        data['user'] = {
            'id': user.id,
            'username': user.username,
            'role': user.role,
            'ism': user.ism,
            'familya': user.familya,
            'full_name': user.full_name,
            'filial': FilialSerializer(user.filial).data if user.filial else None,
        }
        return data


class UserMeSerializer(serializers.ModelSerializer):
    filial = FilialSerializer(read_only=True)
    full_name = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = ['id', 'username', 'role', 'ism', 'familya', 'full_name', 'filial', 'faol', 'created_at']


class NazoratchiSerializer(serializers.ModelSerializer):
    """Admin nazoratchi yaratish/ko'rish uchun."""
    password = serializers.CharField(write_only=True, required=False)
    filial_nomi = serializers.CharField(source='filial.nomi', read_only=True)
    oquvchilar_soni = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'ism', 'familya', 'filial', 'filial_nomi',
                  'faol', 'created_at', 'oquvchilar_soni']

    def get_oquvchilar_soni(self, obj):
        return obj.yaratganlari.filter(role=User.ROLE_OQUVCHI).count()

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data, role=User.ROLE_NAZORATCHI)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class OquvchiAssignmentMixin:
    """O'quvchining tanlangan fan/daraja ma'lumotlarini serializerga qo'shadi."""

    def _assignment(self, obj):
        prefetched = getattr(obj, '_prefetched_objects_cache', {}).get('biriktirilgan_fanlar')
        if prefetched is not None:
            return sorted(prefetched, key=lambda x: (x.daraja.fan.tartib, x.daraja.tartib))[0] if prefetched else None
        return obj.biriktirilgan_fanlar.select_related('daraja__fan').order_by(
            'daraja__fan__tartib', 'daraja__tartib'
        ).first()

    def get_daraja(self, obj):
        assignment = self._assignment(obj)
        return assignment.daraja_id if assignment else None

    def get_daraja_nomi(self, obj):
        assignment = self._assignment(obj)
        return toza_daraja_nomi(assignment.daraja.nomi) if assignment else ''

    def get_fan_id(self, obj):
        assignment = self._assignment(obj)
        return assignment.daraja.fan_id if assignment else None

    def get_fan_nomi(self, obj):
        assignment = self._assignment(obj)
        return assignment.daraja.fan.nomi if assignment else ''


class OquvchiSerializer(OquvchiAssignmentMixin, serializers.ModelSerializer):
    """Nazoratchi o'quvchi yaratish/ko'rish uchun."""
    password = serializers.CharField(write_only=True, required=False)
    filial_nomi = serializers.CharField(source='filial.nomi', read_only=True)
    daraja = serializers.PrimaryKeyRelatedField(queryset=Daraja.objects.all(), write_only=True, required=False)
    tanlangan_daraja = serializers.SerializerMethodField(method_name='get_daraja')
    daraja_nomi = serializers.SerializerMethodField()
    fan_id = serializers.SerializerMethodField()
    fan_nomi = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'ism', 'familya', 'filial', 'filial_nomi',
                  'faol', 'created_at', 'daraja', 'tanlangan_daraja', 'daraja_nomi', 'fan_id', 'fan_nomi']
        read_only_fields = ['filial']

    @transaction.atomic
    def create(self, validated_data):
        password = validated_data.pop('password')
        daraja = validated_data.pop('daraja', None)
        request = self.context['request']
        nazoratchi = request.user
        user = User(
            **validated_data,
            role=User.ROLE_OQUVCHI,
            filial=nazoratchi.filial,
            yaratgan=nazoratchi,
        )
        user.set_password(password)
        user.save()
        if daraja:
            OquvchiFan.objects.create(
                oquvchi=user,
                daraja=daraja,
                biriktirgan=nazoratchi,
                qolda_ochilgan=True,
            )
        return user

    @transaction.atomic
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        daraja = validated_data.pop('daraja', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        if daraja:
            # O'quvchiga faqat bitta tanlangan fan va boshlang'ich daraja saqlanadi.
            OquvchiFan.objects.filter(oquvchi=instance).delete()
            OquvchiFan.objects.create(
                oquvchi=instance,
                daraja=daraja,
                biriktirgan=self.context['request'].user,
                qolda_ochilgan=True,
            )
        return instance


class AdminOquvchiSerializer(OquvchiAssignmentMixin, serializers.ModelSerializer):
    """Admin login, parol, fan va darajani bir oynada tanlab o'quvchi yaratadi."""
    password = serializers.CharField(write_only=True, required=False, min_length=4)
    daraja = serializers.PrimaryKeyRelatedField(queryset=Daraja.objects.select_related('fan').all(), write_only=True)
    tanlangan_daraja = serializers.SerializerMethodField(method_name='get_daraja')
    daraja_nomi = serializers.SerializerMethodField()
    fan_id = serializers.SerializerMethodField()
    fan_nomi = serializers.SerializerMethodField()
    filial_nomi = serializers.CharField(source='filial.nomi', read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'password', 'ism', 'familya', 'filial', 'filial_nomi',
            'faol', 'created_at', 'daraja', 'tanlangan_daraja', 'daraja_nomi', 'fan_id', 'fan_nomi',
        ]
        read_only_fields = ['created_at']

    def validate(self, attrs):
        if self.instance is None and not attrs.get('password'):
            raise serializers.ValidationError({'password': 'Parol majburiy.'})
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        daraja = validated_data.pop('daraja')
        password = validated_data.pop('password')
        admin = self.context['request'].user
        user = User(**validated_data, role=User.ROLE_OQUVCHI, yaratgan=admin)
        user.set_password(password)
        user.save()
        OquvchiFan.objects.create(
            oquvchi=user,
            daraja=daraja,
            biriktirgan=admin,
            qolda_ochilgan=True,
        )
        return user

    @transaction.atomic
    def update(self, instance, validated_data):
        daraja = validated_data.pop('daraja', None)
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()

        if daraja:
            # Admin fan yoki darajani almashtirsa, eski fan biriktirishlari olib tashlanadi.
            OquvchiFan.objects.filter(oquvchi=instance).delete()
            OquvchiFan.objects.create(
                oquvchi=instance,
                daraja=daraja,
                biriktirgan=self.context['request'].user,
                qolda_ochilgan=True,
            )
        return instance

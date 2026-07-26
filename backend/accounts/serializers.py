from django.contrib.auth import get_user_model
from django.db import IntegrityError, DatabaseError, transaction
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from courses.models import Daraja, OquvchiFan
from .db_utils import is_primary_key_collision, reset_model_sequences
from courses.utils import toza_daraja_nomi
from .models import Filial

User = get_user_model()


class FilialSerializer(serializers.ModelSerializer):
    oquvchilar_soni = serializers.SerializerMethodField()
    nazoratchilar_soni = serializers.SerializerMethodField()

    class Meta:
        model = Filial
        fields = ['id', 'nomi', 'manzil', 'created_at', 'oquvchilar_soni', 'nazoratchilar_soni']

    def get_oquvchilar_soni(self, obj):
        try:
            return obj.users.filter(role=User.ROLE_OQUVCHI).count()
        except DatabaseError:
            return 0

    def get_nazoratchilar_soni(self, obj):
        try:
            return obj.users.filter(role=User.ROLE_NAZORATCHI).count()
        except DatabaseError:
            return 0


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Login qilganda token bilan birga user ma'lumotlarini ham qaytaradi."""

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = user.role
        token['username'] = user.username
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user
        if user.role == User.ROLE_OQUVCHI:
            try:
                from exams.engagement import faollik_qayd_et
                faollik_qayd_et(user, 'kirish')
            except Exception:
                # Login migratsiya yoki vaqtinchalik DB muammosi sabab to'xtab qolmasin.
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
    password = serializers.CharField(write_only=True, required=True, min_length=4)
    filial_nomi = serializers.SerializerMethodField()
    oquvchilar_soni = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'ism', 'familya', 'filial', 'filial_nomi',
                  'faol', 'created_at', 'oquvchilar_soni']

    def get_filial_nomi(self, obj):
        try:
            return obj.filial.nomi if obj.filial_id and obj.filial else ''
        except (Filial.DoesNotExist, AttributeError):
            return ''

    def get_oquvchilar_soni(self, obj):
        annotated = getattr(obj, '_oquvchilar_soni', None)
        if annotated is not None:
            return int(annotated)
        try:
            return obj.yaratganlari.filter(role=User.ROLE_OQUVCHI).count()
        except DatabaseError:
            # Legacy Railway bazasida yaratgan_id ustuni migratsiya tugaguncha
            # mavjud bo'lmasligi mumkin. Ro'yxat butunlay 500 bermasin.
            return 0

    def validate_username(self, value):
        value = (value or '').strip()
        if not value:
            raise serializers.ValidationError('Login majburiy.')
        queryset = User.objects.filter(username__iexact=value)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise serializers.ValidationError('Bu login avval ishlatilgan.')
        return value

    @transaction.atomic
    def create(self, validated_data):
        password = validated_data.pop('password')
        return User.objects.create_user(
            password=password,
            role=User.ROLE_NAZORATCHI,
            is_active=True,
            **validated_data,
        )

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

    def validate_username(self, value):
        value = (value or '').strip()
        if not value:
            raise serializers.ValidationError('Login majburiy.')
        queryset = User.objects.filter(username__iexact=value)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise serializers.ValidationError('Bu login avval ishlatilgan. Boshqa login kiriting.')
        return value

    def validate(self, attrs):
        if self.instance is None and not attrs.get('password'):
            raise serializers.ValidationError({'password': 'Parol majburiy.'})
        return attrs

    def _default_filial(self, admin, requested_filial=None):
        """Student must belong to a branch for manager/shop visibility.

        The current form does not require a branch selector, so use the chosen
        branch, then the admin's branch, then the first branch. If the database
        is empty, create the standard main branch automatically.
        """
        if requested_filial:
            return requested_filial
        if admin.filial_id:
            return admin.filial
        existing = Filial.objects.order_by('id').first()
        if existing:
            return existing
        filial, _ = Filial.objects.get_or_create(
            nomi='Asosiy filial',
            defaults={'manzil': 'Toshkent'},
        )
        return filial

    def _create_once(self, validated_data):
        data = dict(validated_data)
        daraja = data.pop('daraja')
        password = data.pop('password')
        admin = self.context['request'].user
        data['filial'] = self._default_filial(admin, data.get('filial'))

        user = User.objects.create_user(
            password=password,
            role=User.ROLE_OQUVCHI,
            yaratgan=admin,
            is_active=True,
            token_version=0,
            **data,
        )
        OquvchiFan.objects.create(
            oquvchi=user,
            daraja=daraja,
            biriktirgan=admin,
            qolda_ochilgan=True,
        )
        return user

    def create(self, validated_data):
        # A restored/imported PostgreSQL database can have stale sequences.
        # Retry once after synchronising the relevant sequences.
        for attempt in range(2):
            try:
                with transaction.atomic():
                    return self._create_once(validated_data)
            except IntegrityError as exc:
                if attempt == 0 and is_primary_key_collision(exc):
                    reset_model_sequences([User, Filial, OquvchiFan])
                    continue
                message = str(exc).lower()
                if 'username' in message or 'users_username' in message:
                    raise serializers.ValidationError({'username': 'Bu login avval ishlatilgan.'}) from exc
                raise serializers.ValidationError({
                    'detail': "O'quvchini saqlashda baza cheklovi xatosi. Railway migratsiyasini qayta deploy qiling."
                }) from exc
            except DatabaseError as exc:
                raise serializers.ValidationError({
                    'detail': f"O'quvchini saqlashda ma'lumotlar bazasi xatosi: {exc.__class__.__name__}."
                }) from exc

        raise serializers.ValidationError({'detail': "O'quvchini yaratib bo'lmadi."})

    @transaction.atomic
    def update(self, instance, validated_data):
        daraja = validated_data.pop('daraja', None)
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        if not instance.filial_id:
            instance.filial = self._default_filial(self.context['request'].user)
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


from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Filial, KirishTarixi


@admin.register(Filial)
class FilialAdmin(admin.ModelAdmin):
    list_display = ['id', 'nomi', 'manzil', 'created_at']
    search_fields = ['nomi']


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'ism', 'familya', 'role', 'filial', 'faol', 'created_at']
    list_filter = ['role', 'filial', 'faol']
    search_fields = ['username', 'ism', 'familya']
    fieldsets = UserAdmin.fieldsets + (
        ('Qo\'shimcha', {'fields': ('role', 'filial', 'yaratgan', 'ism', 'familya', 'faol', 'token_version')}),
    )


@admin.register(KirishTarixi)
class KirishTarixiAdmin(admin.ModelAdmin):
    list_display = ['username', 'muvaffaqiyatli', 'ip_manzil', 'created_at']
    list_filter = ['muvaffaqiyatli']
    search_fields = ['username', 'ip_manzil', 'user_agent']
    readonly_fields = ['user', 'username', 'muvaffaqiyatli', 'ip_manzil', 'user_agent', 'created_at']

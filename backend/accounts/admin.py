from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Filial


@admin.register(Filial)
class FilialAdmin(admin.ModelAdmin):
    list_display = ['id', 'nomi', 'manzil', 'created_at']
    search_fields = ['nomi']


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'ism', 'familya', 'role', 'filial', 'tarif', 'tolov_holati', 'tugash_sana', 'faol', 'created_at']
    list_filter = ['role', 'filial', 'faol', 'tolov_holati', 'tarif']
    search_fields = ['username', 'ism', 'familya']
    readonly_fields = ['tarif']
    fieldsets = UserAdmin.fieldsets + (
        ('Qo\'shimcha', {'fields': ('role', 'filial', 'yaratgan', 'ism', 'familya', 'faol', 'tarif', 'boshlanish_sana', 'tugash_sana', 'tolov_holati', 'muddat_bloklash')}),
    )

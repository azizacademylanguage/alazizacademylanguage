from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Filial


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
        ('Qo\'shimcha', {'fields': ('role', 'filial', 'yaratgan', 'ism', 'familya', 'faol')}),
    )

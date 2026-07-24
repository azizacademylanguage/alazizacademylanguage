from django.contrib import admin
from .models import Fan, Daraja, Mavzu, Dars, OquvchiFan, DarsProgress


@admin.register(Fan)
class FanAdmin(admin.ModelAdmin):
    list_display = ['id', 'nomi', 'tartib']
    search_fields = ['nomi']


@admin.register(Daraja)
class DarajaAdmin(admin.ModelAdmin):
    list_display = ['id', 'fan', 'nomi', 'tartib']
    list_filter = ['fan']


@admin.register(Mavzu)
class MavzuAdmin(admin.ModelAdmin):
    list_display = ['id', 'daraja', 'nomi', 'tartib']
    list_filter = ['daraja__fan', 'daraja']


@admin.register(Dars)
class DarsAdmin(admin.ModelAdmin):
    list_display = ['id', 'mavzu', 'sarlavha', 'tartib']
    list_filter = ['mavzu__daraja__fan']


@admin.register(OquvchiFan)
class OquvchiFanAdmin(admin.ModelAdmin):
    list_display = ['id', 'oquvchi', 'daraja', 'biriktirgan', 'created_at']
    list_filter = ['daraja__fan']


@admin.register(DarsProgress)
class DarsProgressAdmin(admin.ModelAdmin):
    list_display = ['id', 'oquvchi', 'dars', 'video_tugatilgan', 'updated_at']

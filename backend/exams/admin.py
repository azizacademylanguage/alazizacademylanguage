from django.contrib import admin
from .models import (
    Mashq, Savol, Javob, MashqNatija, OquvchiJavob,
    GateTest, GateTestSavol, GateTestJavob, GateTestNatija,
    FinalTest, FinalTestSavol, FinalTestJavob, FinalTestNatija, Sertifikat,
    WritingTopshiriq, WritingNatija, SpeakingTopshiriq, SpeakingNatija,
    OquvchiCoin, CoinTarix, ShopMahsulot, ShopBuyurtma, SozJuftligi, SozOyiniSessiya, AdminAmalLog,
    ListeningSavol, ListeningNatija, KunlikFaollik, Bildirishnoma, Musobaqa,
)


class JavobInline(admin.TabularInline):
    model = Javob
    extra = 2


@admin.register(Savol)
class SavolAdmin(admin.ModelAdmin):
    list_display = ['id', 'matn', 'mashq', 'tur', 'tartib']
    list_filter = ['mashq', 'tur']
    inlines = [JavobInline]


@admin.register(Mashq)
class MashqAdmin(admin.ModelAdmin):
    list_display = ['id', 'sarlavha', 'dars', 'savollar_soni']


@admin.register(MashqNatija)
class MashqNatijaAdmin(admin.ModelAdmin):
    list_display = ['id', 'oquvchi', 'mashq', 'togri_soni', 'jami_soni', 'foiz', 'boshlangan_vaqt']
    list_filter = ['mashq']


admin.site.register(Javob)
admin.site.register(OquvchiJavob)


# ==================== GATE TEST ====================

class GateTestJavobInline(admin.TabularInline):
    model = GateTestJavob
    extra = 2


@admin.register(GateTestSavol)
class GateTestSavolAdmin(admin.ModelAdmin):
    list_display = ['id', 'matn', 'gate_test', 'tartib']
    inlines = [GateTestJavobInline]


@admin.register(GateTest)
class GateTestAdmin(admin.ModelAdmin):
    list_display = ['id', 'sarlavha', 'daraja', 'savollar_soni']


@admin.register(GateTestNatija)
class GateTestNatijaAdmin(admin.ModelAdmin):
    list_display = ['id', 'oquvchi', 'gate_test', 'foiz', 'otdi', 'created_at']
    list_filter = ['otdi']


# ==================== FINAL TEST ====================

class FinalTestJavobInline(admin.TabularInline):
    model = FinalTestJavob
    extra = 2


@admin.register(FinalTestSavol)
class FinalTestSavolAdmin(admin.ModelAdmin):
    list_display = ['id', 'matn', 'final_test', 'tartib']
    inlines = [FinalTestJavobInline]


@admin.register(FinalTest)
class FinalTestAdmin(admin.ModelAdmin):
    list_display = ['id', 'sarlavha', 'daraja', 'otish_bali_foiz', 'savollar_soni']


@admin.register(FinalTestNatija)
class FinalTestNatijaAdmin(admin.ModelAdmin):
    list_display = ['id', 'oquvchi', 'final_test', 'foiz', 'otdi', 'created_at']
    list_filter = ['otdi']


@admin.register(Sertifikat)
class SertifikatAdmin(admin.ModelAdmin):
    list_display = ['id', 'oquvchi', 'daraja', 'kod', 'foiz', 'berilgan_sana']
    search_fields = ['kod']


# ==================== WRITING / SPEAKING ====================

@admin.register(WritingTopshiriq)
class WritingTopshiriqAdmin(admin.ModelAdmin):
    list_display = ['id', 'matn', 'dars', 'minimal_soz_soni']


@admin.register(WritingNatija)
class WritingNatijaAdmin(admin.ModelAdmin):
    list_display = ['id', 'oquvchi', 'topshiriq', 'ai_foiz', 'baholanmoqda', 'created_at']


@admin.register(SpeakingTopshiriq)
class SpeakingTopshiriqAdmin(admin.ModelAdmin):
    list_display = ['id', 'matn', 'dars']


@admin.register(SpeakingNatija)
class SpeakingNatijaAdmin(admin.ModelAdmin):
    list_display = ['id', 'oquvchi', 'topshiriq', 'ai_foiz', 'baholanmoqda', 'created_at']


# ==================== COIN / SHOP ====================

@admin.register(OquvchiCoin)
class OquvchiCoinAdmin(admin.ModelAdmin):
    list_display = ['id', 'oquvchi', 'balans', 'updated_at']


@admin.register(CoinTarix)
class CoinTarixAdmin(admin.ModelAdmin):
    list_display = ['id', 'oquvchi', 'miqdor', 'sabab', 'created_at']
    list_filter = ['sabab']


@admin.register(ShopMahsulot)
class ShopMahsulotAdmin(admin.ModelAdmin):
    list_display = ['id', 'nomi', 'narx_coin', 'faol']


@admin.register(ShopBuyurtma)
class ShopBuyurtmaAdmin(admin.ModelAdmin):
    list_display = ['id', 'oquvchi', 'mahsulot', 'narx_coin', 'status', 'created_at']
    list_filter = ['status', 'oquvchi__filial']


@admin.register(SozJuftligi)
class SozJuftligiAdmin(admin.ModelAdmin):
    list_display = ['id', 'fan', 'chet_soz', 'uzbek_soz', 'tartib', 'faol']
    list_filter = ['fan', 'faol']
    search_fields = ['chet_soz', 'uzbek_soz']


@admin.register(SozOyiniSessiya)
class SozOyiniSessiyaAdmin(admin.ModelAdmin):
    list_display = ['id', 'oquvchi', 'fan', 'topilgan_soni', 'berilgan_coin', 'tugallangan', 'created_at']
    list_filter = ['fan', 'tugallangan']


# ==================== AUDIT LOG ====================

@admin.register(AdminAmalLog)
class AdminAmalLogAdmin(admin.ModelAdmin):
    list_display = ['id', 'foydalanuvchi', 'amal', 'nishon_user', 'created_at']
    list_filter = ['amal']
    readonly_fields = ['created_at']


# ==================== LISTENING / FAOLLIK / BILDIRISHNOMALAR ====================

@admin.register(ListeningSavol)
class ListeningSavolAdmin(admin.ModelAdmin):
    list_display = ['id', 'dars', 'audio_matn', 'til_kodi', 'tartib']
    list_filter = ['til_kodi', 'dars__mavzu__daraja__fan']


@admin.register(ListeningNatija)
class ListeningNatijaAdmin(admin.ModelAdmin):
    list_display = ['id', 'oquvchi', 'dars', 'foiz', 'created_at']
    list_filter = ['dars__mavzu__daraja__fan']


@admin.register(KunlikFaollik)
class KunlikFaollikAdmin(admin.ModelAdmin):
    list_display = ['id', 'oquvchi', 'sana', 'faollik_soni', 'updated_at']
    list_filter = ['sana']


@admin.register(Bildirishnoma)
class BildirishnomaAdmin(admin.ModelAdmin):
    list_display = ['id', 'oquvchi', 'sarlavha', 'tur', 'oqilgan', 'created_at']
    list_filter = ['tur', 'oqilgan']
    search_fields = ['oquvchi__username', 'sarlavha', 'matn']


@admin.register(Musobaqa)
class MusobaqaAdmin(admin.ModelAdmin):
    list_display = ['id', 'nomi', 'boshlanish_sana', 'tugash_sana', 'fan', 'filial', 'status']
    list_filter = ['status', 'fan', 'filial']
    search_fields = ['nomi', 'tavsif']

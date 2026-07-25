from django.contrib import admin
from .models import (
    Mashq, Savol, Javob, MashqNatija, OquvchiJavob,
    GateTest, GateTestSavol, GateTestJavob, GateTestNatija,
    FinalTest, FinalTestSavol, FinalTestJavob, FinalTestNatija, Sertifikat,
    WritingTopshiriq, WritingNatija, SpeakingTopshiriq, SpeakingNatija,
    OquvchiCoin, CoinTarix, ShopMahsulot, ShopBuyurtma, SozJuftligi, AdminAmalLog,
    AIYordamchiXabar, Murojaat, MurojaatJavob, PlatformSozlama,
    Bildirishnoma, BildirishnomaOqildi, PlacementNatija, TestXavfsizlikLog,
    FaoliyatLog, OquvchiKunlikFaollik, Yutuq, OquvchiYutuq, Tolov, TezkorOyiniSessiya,
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


# ==================== AUDIT LOG ====================

@admin.register(AdminAmalLog)
class AdminAmalLogAdmin(admin.ModelAdmin):
    list_display = ['id', 'foydalanuvchi', 'amal', 'nishon_user', 'created_at']
    list_filter = ['amal']
    readonly_fields = ['created_at']


# ==================== AI / MUROJAAT / SOZLAMALAR ====================

@admin.register(AIYordamchiXabar)
class AIYordamchiXabarAdmin(admin.ModelAdmin):
    list_display = ['id', 'oquvchi', 'role', 'created_at']
    list_filter = ['role']
    search_fields = ['oquvchi__username', 'matn']


class MurojaatJavobInline(admin.TabularInline):
    model = MurojaatJavob
    extra = 0
    readonly_fields = ['created_at']


@admin.register(Murojaat)
class MurojaatAdmin(admin.ModelAdmin):
    list_display = ['kod', 'foydalanuvchi', 'kategoriya', 'status', 'ustuvorlik', 'updated_at']
    list_filter = ['status', 'kategoriya', 'ustuvorlik']
    search_fields = ['kod', 'sarlavha', 'foydalanuvchi__username']
    inlines = [MurojaatJavobInline]


@admin.register(PlatformSozlama)
class PlatformSozlamaAdmin(admin.ModelAdmin):
    list_display = ['platform_nomi', 'ai_yordamchi_faol', 'murojaatlar_faol', 'texnik_rejim', 'updated_at']


# ==================== QO‘SHIMCHA PLATFORM FUNKSIYALARI ====================

@admin.register(Bildirishnoma)
class BildirishnomaAdmin(admin.ModelAdmin):
    list_display = ['id', 'sarlavha', 'target_turi', 'tur', 'faol', 'created_at']
    list_filter = ['target_turi', 'tur', 'faol']
    search_fields = ['sarlavha', 'matn']

admin.site.register(BildirishnomaOqildi)

@admin.register(PlacementNatija)
class PlacementNatijaAdmin(admin.ModelAdmin):
    list_display = ['id', 'oquvchi', 'fan', 'foiz', 'tavsiya_daraja', 'tasdiqlangan', 'created_at']
    list_filter = ['fan', 'tavsiya_daraja']

@admin.register(TestXavfsizlikLog)
class TestXavfsizlikLogAdmin(admin.ModelAdmin):
    list_display = ['id', 'oquvchi', 'test_turi', 'davomiylik_soniya', 'sahifadan_chiqish_soni', 'shubhali', 'created_at']
    list_filter = ['test_turi', 'shubhali']

@admin.register(FaoliyatLog)
class FaoliyatLogAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'amal', 'obyekt_turi', 'created_at']
    list_filter = ['amal', 'user__role']
    search_fields = ['user__username', 'tavsif']

admin.site.register(OquvchiKunlikFaollik)
admin.site.register(Yutuq)
admin.site.register(OquvchiYutuq)

@admin.register(Tolov)
class TolovAdmin(admin.ModelAdmin):
    list_display = ['id', 'oquvchi', 'summa', 'tolangan_summa', 'status', 'boshlanish_sana', 'tugash_sana']
    list_filter = ['status', 'tugash_sana']
    search_fields = ['oquvchi__username', 'oquvchi__ism', 'oquvchi__familya']

@admin.register(TezkorOyiniSessiya)
class TezkorOyiniSessiyaAdmin(admin.ModelAdmin):
    list_display = ['id', 'oquvchi', 'fan', 'togri_soni', 'berilgan_coin', 'tugallangan', 'created_at']
    list_filter = ['fan', 'tugallangan']

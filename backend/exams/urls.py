from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views
from . import views_extra
from .admin_progress import AdminOquvchiProgressView
from . import features_views

router = DefaultRouter()
router.register('admin/mashqlar', views.MashqViewSet, basename='mashq')
router.register('admin/savollar', views.SavolViewSet, basename='savol')
router.register('admin/javoblar', views.JavobViewSet, basename='javob')

router.register('admin/gate-testlar', views_extra.GateTestViewSet, basename='gate-test')
router.register('admin/gate-test-savollari', views_extra.GateTestSavolViewSet, basename='gate-test-savol')
router.register('admin/gate-test-javoblari', views_extra.GateTestJavobViewSet, basename='gate-test-javob')

router.register('admin/final-testlar', views_extra.FinalTestViewSet, basename='final-test')
router.register('admin/final-test-savollari', views_extra.FinalTestSavolViewSet, basename='final-test-savol')
router.register('admin/final-test-javoblari', views_extra.FinalTestJavobViewSet, basename='final-test-javob')

router.register('admin/shop-mahsulotlari', views_extra.AdminShopMahsulotViewSet, basename='shop-mahsulot')
router.register('admin/writing-topshiriqlari', views_extra.WritingTopshiriqViewSet, basename='writing-topshiriq')
router.register('admin/speaking-topshiriqlari', views_extra.SpeakingTopshiriqViewSet, basename='speaking-topshiriq')

urlpatterns = [
    # ---- Mashq (dars darajasidagi test) ----
    path('oquvchi/mashq/<int:mashq_id>/', views.MashqOlishView.as_view(), name='mashq-olish'),
    path('oquvchi/mashq/<int:mashq_id>/topshirish/', views.MashqTopshirishView.as_view(), name='mashq-topshirish'),
    path('oquvchi/natijalarim/', views.NatijalarimView.as_view(), name='natijalarim'),
    path('oquvchi/xatolarim/<int:mashq_id>/', views.XatolarimView.as_view(), name='xatolarim'),
    path('nazoratchi/oquvchilar/<int:oquvchi_id>/statistika/', views.OquvchiStatistikaView.as_view(), name='oquvchi-statistika'),

    # ---- Gate Test (daraja ochish testi) ----
    path('oquvchi/gate-test/<int:daraja_id>/', views_extra.GateTestOlishView.as_view(), name='gate-test-olish'),
    path('oquvchi/gate-test/<int:daraja_id>/topshirish/', views_extra.GateTestTopshirishView.as_view(), name='gate-test-topshirish'),

    # ---- Final Test + Sertifikat ----
    path('oquvchi/final-test/<int:daraja_id>/', views_extra.FinalTestOlishView.as_view(), name='final-test-olish'),
    path('oquvchi/final-test/<int:daraja_id>/topshirish/', views_extra.FinalTestTopshirishView.as_view(), name='final-test-topshirish'),
    path('oquvchi/sertifikatlarim/', views_extra.MeningSertifikatlarimView.as_view(), name='sertifikatlarim'),
    path('admin/sertifikatlar/', views_extra.AdminSertifikatlarView.as_view(), name='admin-sertifikatlar'),
    path('sertifikat-tekshirish/<str:kod>/', views_extra.SertifikatTekshirishView.as_view(), name='sertifikat-tekshirish'),
    path('sertifikat/<str:kod>/pdf/', views_extra.SertifikatPDFView.as_view(), name='sertifikat-pdf'),
    path('sertifikat/<str:kod>/qr/', views_extra.SertifikatQRView.as_view(), name='sertifikat-qr'),

    # ---- Writing ----
    path('oquvchi/writing/<int:dars_id>/', views_extra.WritingTopshiriqlarView.as_view(), name='writing-topshiriqlar'),
    path('oquvchi/writing-topshirish/<int:topshiriq_id>/', views_extra.WritingTopshirishView.as_view(), name='writing-topshirish'),

    # ---- Speaking ----
    path('oquvchi/speaking/<int:dars_id>/', views_extra.SpeakingTopshiriqlarView.as_view(), name='speaking-topshiriqlar'),
    path('oquvchi/speaking-topshirish/<int:topshiriq_id>/', views_extra.SpeakingTopshirishView.as_view(), name='speaking-topshirish'),

    # ---- So'z o'yini / Coin / Shop ----
    path('oquvchi/coinlarim/', views_extra.MeningCoinlarimView.as_view(), name='coinlarim'),
    path('oquvchi/shop/', views_extra.ShopMahsulotlarView.as_view(), name='shop-royxati'),
    path('oquvchi/shop-buyurtmalarim/', views_extra.MeningShopBuyurtmalarimView.as_view(), name='shop-buyurtmalarim'),
    path('oquvchi/shop/<int:mahsulot_id>/xarid/', views_extra.ShopXaridView.as_view(), name='shop-xarid'),
    path('boshqaruv/shop-buyurtmalar/', views_extra.ShopBuyurtmalarBoshqaruvView.as_view(), name='shop-buyurtmalar-boshqaruv'),
    path('boshqaruv/shop-buyurtmalar/<int:buyurtma_id>/status/', views_extra.ShopBuyurtmaStatusView.as_view(), name='shop-buyurtma-status'),
    path('admin/oquvchilar/<int:oquvchi_id>/coin-berish/', views_extra.AdminCoinBerishView.as_view(), name='admin-coin-berish'),


    # ---- Bildirishnomalar ----
    path('oquvchi/bildirishnomalar/', features_views.MeningBildirishnomalarimView.as_view(), name='mening-bildirishnomalarim'),
    path('oquvchi/bildirishnomalar/barchasini-oqish/', features_views.BarchaBildirishnomalarniOqishView.as_view(), name='bildirishnoma-barchasini-oqish'),
    path('oquvchi/bildirishnomalar/<int:bildirishnoma_id>/oqish/', features_views.BildirishnomaOqishView.as_view(), name='bildirishnoma-oqish'),
    path('admin/bildirishnomalar/', features_views.AdminBildirishnomalarView.as_view(), name='admin-bildirishnomalar'),
    path('admin/bildirishnomalar/<int:bildirishnoma_id>/', features_views.AdminBildirishnomaDetailView.as_view(), name='admin-bildirishnoma-detail'),

    # ---- Placement test ----
    path('oquvchi/placement-test/', features_views.PlacementTestView.as_view(), name='placement-test'),
    path('admin/placement-natijalari/', features_views.AdminPlacementNatijalarView.as_view(), name='admin-placement-natijalari'),
    path('admin/placement-natijalari/<int:natija_id>/tasdiqlash/', features_views.AdminPlacementTasdiqlashView.as_view(), name='admin-placement-tasdiqlash'),

    # ---- Faoliyat, test xavfsizligi va yutuqlar ----
    path('oquvchi/faoliyatim/', features_views.MeningFaoliyatimView.as_view(), name='mening-faoliyatim'),
    path('admin/faoliyat/', features_views.AdminFaoliyatView.as_view(), name='admin-faoliyat'),
    path('admin/test-xavfsizligi/', features_views.AdminTestXavfsizligiView.as_view(), name='admin-test-xavfsizligi'),
    path('oquvchi/yutuqlarim/', features_views.MeningYutuqlarimView.as_view(), name='mening-yutuqlarim'),

    # ---- To'lov va foydalanish muddati ----
    path('oquvchi/tolovim/', features_views.MeningTolovimView.as_view(), name='mening-tolovim'),
    path('admin/tolovlar/', features_views.AdminTolovlarView.as_view(), name='admin-tolovlar'),
    path('admin/tolovlar/<int:tolov_id>/', features_views.AdminTolovDetailView.as_view(), name='admin-tolov-detail'),

    # ---- Yangi tezkor tarjima o'yini ----
    path('oquvchi/tezkor-oyin/', features_views.TezkorOyiniBoshlashView.as_view(), name='tezkor-oyin-boshlash'),
    path('oquvchi/tezkor-oyin/<uuid:token>/yakunlash/', features_views.TezkorOyiniYakunlashView.as_view(), name='tezkor-oyin-yakunlash'),

    # ---- Sertifikat holati ----
    path('admin/sertifikatlar/<int:sertifikat_id>/status/', features_views.AdminSertifikatStatusView.as_view(), name='admin-sertifikat-status'),

    # ---- Backup va tiklash ----
    path('admin/backup/yuklash/', features_views.AdminBackupDownloadView.as_view(), name='admin-backup-yuklash'),
    path('admin/backup/tiklash/', features_views.AdminBackupRestoreView.as_view(), name='admin-backup-tiklash'),

    # ---- AI yordamchi ----
    path('oquvchi/ai-yordamchi/', views_extra.AIYordamchiView.as_view(), name='ai-yordamchi'),

    # ---- Murojaatlar ----
    path('oquvchi/murojaatlar/', views_extra.MeningMurojaatlarimView.as_view(), name='mening-murojaatlarim'),
    path('oquvchi/murojaatlar/<int:murojaat_id>/', views_extra.MeningMurojaatimDetailView.as_view(), name='mening-murojaatim-detail'),
    path('admin/murojaatlar/', views_extra.AdminMurojaatlarView.as_view(), name='admin-murojaatlar'),
    path('admin/murojaatlar/<int:murojaat_id>/', views_extra.AdminMurojaatDetailView.as_view(), name='admin-murojaat-detail'),

    # ---- Kuchli analitika ----
    path('admin/kuchli-analitika/', views_extra.KuchliAnalitikaView.as_view(), name='kuchli-analitika'),
    path('admin/oquvchilar/<int:oquvchi_id>/progress/', AdminOquvchiProgressView.as_view(), name='admin-oquvchi-progress'),

    # ---- Platforma sozlamalari ----
    path('platform-holati/', views_extra.PlatformHolatiView.as_view(), name='platform-holati'),
    path('admin/platform-sozlamalari/', views_extra.PlatformSozlamaView.as_view(), name='platform-sozlamalari'),

    # ---- Admin audit log ----
    path('admin/amal-loglari/', views_extra.AdminAmalLoglariView.as_view(), name='admin-amal-loglari'),
] + router.urls

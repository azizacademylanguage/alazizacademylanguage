from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views
from . import views_extra
from . import engagement_views

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

    # ---- Listening / Shaxsiy reja / Streak / Bildirishnomalar ----
    path('oquvchi/listening/<int:dars_id>/', engagement_views.ListeningSavollarView.as_view(), name='listening-savollar'),
    path('oquvchi/listening/<int:dars_id>/topshirish/', engagement_views.ListeningTopshirishView.as_view(), name='listening-topshirish'),
    path('oquvchi/oqish-rejasi/', engagement_views.OqishRejasiView.as_view(), name='oqish-rejasi'),
    path('oquvchi/streak/', engagement_views.StreakView.as_view(), name='streak'),
    path('oquvchi/bildirishnomalar/', engagement_views.BildirishnomalarView.as_view(), name='bildirishnomalar'),
    path('oquvchi/bildirishnomalar/<int:notification_id>/oqildi/', engagement_views.BildirishnomaOqildiView.as_view(), name='bildirishnoma-oqildi'),
    path('oquvchi/bildirishnomalar/barchasi-oqildi/', engagement_views.BarchaBildirishnomalarOqildiView.as_view(), name='bildirishnomalar-barchasi-oqildi'),

    # ---- So'z o'yini / Coin / Shop ----
    path('oquvchi/soz-oyini/', views_extra.SozOyiniBoshlashView.as_view(), name='soz-oyini-boshlash'),
    path('oquvchi/soz-oyini/<uuid:token>/tekshirish/', views_extra.SozOyiniJuftTekshirishView.as_view(), name='soz-oyini-tekshirish'),
    path('oquvchi/soz-oyini/<uuid:token>/yakunlash/', views_extra.SozOyiniYakunlashView.as_view(), name='soz-oyini-yakunlash'),
    path('oquvchi/coinlarim/', views_extra.MeningCoinlarimView.as_view(), name='coinlarim'),
    path('oquvchi/shop/', views_extra.ShopMahsulotlarView.as_view(), name='shop-royxati'),
    path('oquvchi/shop-buyurtmalarim/', views_extra.MeningShopBuyurtmalarimView.as_view(), name='shop-buyurtmalarim'),
    path('oquvchi/shop/<int:mahsulot_id>/xarid/', views_extra.ShopXaridView.as_view(), name='shop-xarid'),
    path('boshqaruv/shop-buyurtmalar/', views_extra.ShopBuyurtmalarBoshqaruvView.as_view(), name='shop-buyurtmalar-boshqaruv'),
    path('boshqaruv/shop-buyurtmalar/<int:buyurtma_id>/status/', views_extra.ShopBuyurtmaStatusView.as_view(), name='shop-buyurtma-status'),
    path('admin/oquvchilar/<int:oquvchi_id>/coin-berish/', views_extra.AdminCoinBerishView.as_view(), name='admin-coin-berish'),

    # ---- Admin audit log ----
    path('admin/amal-loglari/', views_extra.AdminAmalLoglariView.as_view(), name='admin-amal-loglari'),
] + router.urls

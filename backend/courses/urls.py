from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('admin/fanlar', views.FanViewSet, basename='fan')
router.register('admin/darajalar', views.DarajaViewSet, basename='daraja')
router.register('admin/mavzular', views.MavzuViewSet, basename='mavzu')
router.register('admin/darslar', views.DarsViewSet, basename='dars')

urlpatterns = [
    path('nazoratchi/oquvchilar/<int:oquvchi_id>/fan-biriktirish/',
         views.FanBiriktirishView.as_view(), name='fan-biriktirish'),

    path('oquvchi/fanlarim/', views.FanlarimView.as_view(), name='fanlarim'),
    path('oquvchi/mavzular/<int:daraja_id>/', views.MavzularView.as_view(), name='mavzular'),
    path('oquvchi/dars/<int:dars_id>/', views.DarsBatafsilView.as_view(), name='dars-batafsil'),
    path('oquvchi/dars/<int:dars_id>/progress/', views.DarsProgressSaqlashView.as_view(), name='dars-progress'),
] + router.urls

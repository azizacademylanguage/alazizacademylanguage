from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from . import views
from . import csv_views
from . import content_tools

router = DefaultRouter()
router.register('admin/filiallar', views.FilialViewSet, basename='filial')
router.register('admin/nazoratchilar', views.NazoratchiViewSet, basename='nazoratchi')
router.register('admin/oquvchilar', views.AdminOquvchiViewSet, basename='admin-oquvchi')
router.register('nazoratchi/oquvchilar', views.OquvchiViewSet, basename='oquvchi')

urlpatterns = [
    path('auth/login/', views.LoginView.as_view(), name='login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/me/', views.MeView.as_view(), name='me'),
    path('admin/statistika/', views.AdminStatistikaView.as_view(), name='admin-statistika'),
    path('admin/kengaytirilgan-statistika/', views.KengaytirilganStatistikaView.as_view(), name='kengaytirilgan-statistika'),
    path('reyting/', views.ReytingView.as_view(), name='reyting'),
    path('nazoratchi/statistika/', views.NazoratchiStatistikaView.as_view(), name='nazoratchi-statistika'),

    # CSV export/import
    path('admin/export/users.csv', csv_views.FoydalanuvchilarCSVExportView.as_view(), name='export-users-csv'),
    path('admin/export/natijalar.csv', csv_views.NatijalarCSVExportView.as_view(), name='export-natijalar-csv'),
    path('admin/import/users-csv/', csv_views.OquvchilarCSVImportView.as_view(), name='import-users-csv'),
    path('admin/kontent-shablon.xlsx', content_tools.KontentExcelShablonView.as_view()),
    path('admin/kontent-import/', content_tools.KontentExcelImportView.as_view()),
    path('admin/backup.json', content_tools.BackupJsonView.as_view()),
] + router.urls

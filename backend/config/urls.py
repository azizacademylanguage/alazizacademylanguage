from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from django.views.static import serve as media_serve
from django.contrib.auth import get_user_model
from django.db import connection


def api_home(request):
    return JsonResponse({
        'status': 'ok',
        'service': 'alaziz-api',
        'message': "Backend ishlayapti. Frontend Netlify domenida ochiladi.",
        'health': '/health/',
        'admin': '/admin/',
        'login_api': '/api/auth/login/',
    })


def health_check(request):
    database_ok = True
    admin_ready = False
    database_engine = connection.vendor
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
            cursor.fetchone()
        User = get_user_model()
        admin_ready = User.objects.filter(
            username='admin',
            is_active=True,
            faol=True,
            role=User.ROLE_ADMIN,
        ).exists()
    except Exception:
        database_ok = False

    status_code = 200 if database_ok else 503
    return JsonResponse({
        'status': 'ok' if database_ok else 'error',
        'service': 'alaziz-api',
        'database': database_engine,
        'database_ok': database_ok,
        'admin_ready': admin_ready,
    }, status=status_code)


urlpatterns = [
    path('', api_home, name='api-home'),
    path('health/', health_check, name='health-check'),
    path('admin/', admin.site.urls),
    path('api/', include('accounts.urls')),
    path('api/', include('courses.urls')),
    path('api/', include('exams.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
elif settings.SERVE_MEDIA:
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', media_serve, {'document_root': settings.MEDIA_ROOT}),
    ]

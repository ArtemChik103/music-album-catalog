import mimetypes
from pathlib import Path
from django.conf import settings
from django.contrib import admin
from django.http import FileResponse, Http404, HttpResponse
from django.urls import include, path, re_path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)


def serve_spa(request):
    """Отдает собранный SPA Vue 3 или информационное сообщение при API-only режиме."""
    index_file = settings.BASE_DIR / 'frontend_dist' / 'index.html'
    if index_file.exists():
        return HttpResponse(
            index_file.read_text(encoding='utf-8'),
            content_type='text/html; charset=utf-8'
        )
    return HttpResponse(
        "Music Album Catalog API. Use /api/docs/ for Swagger UI.",
        content_type='text/plain; charset=utf-8'
    )


def serve_frontend_assets(request, path):
    """Раздает статические ассеты фронтенда (JS, CSS) с корректными MIME-типами."""
    file_path = settings.BASE_DIR / 'frontend_dist' / 'assets' / path
    if file_path.exists() and file_path.is_file():
        content_type, _ = mimetypes.guess_type(str(file_path))
        if path.endswith('.js'):
            content_type = 'application/javascript'
        elif path.endswith('.css'):
            content_type = 'text/css'
        return FileResponse(open(file_path, 'rb'), content_type=content_type)
    raise Http404("Asset not found")


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('catalog.urls')),
    # OpenAPI Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    # SPA Static Assets & Route Fallback
    path('assets/<path:path>', serve_frontend_assets, name='frontend-assets'),
    re_path(r'^(?!api|admin|static|media).*$', serve_spa, name='spa-fallback'),
]

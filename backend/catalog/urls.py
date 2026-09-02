from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import AlbumViewSet, ArtistViewSet, CatalogStatsView, SongViewSet

router = DefaultRouter()
router.register('artists', ArtistViewSet, basename='artist')
router.register('albums', AlbumViewSet, basename='album')
router.register('songs', SongViewSet, basename='song')

urlpatterns = [
    path('stats/', CatalogStatsView.as_view(), name='catalog-stats'),
    path('', include(router.urls)),
]

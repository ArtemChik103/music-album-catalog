from django.db.models import Count
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from .filters import AlbumFilter, ArtistFilter, SongFilter
from .models import Album, AlbumSong, Artist, Song
from .serializers import (
    AlbumCreateUpdateSerializer,
    AlbumDetailSerializer,
    AlbumListSerializer,
    AlbumSongSerializer,
    ArtistSerializer,
    SongSerializer,
    TrackInputItemSerializer,
)


class ArtistViewSet(viewsets.ModelViewSet):
    """
    CRUD операции для исполнителей.
    """
    queryset = Artist.objects.annotate(albums_count=Count('albums', distinct=True)).order_by('name')
    serializer_class = ArtistSerializer
    filterset_class = ArtistFilter
    search_fields = ['name']
    ordering_fields = ['name', 'albums_count', 'created_at']


class AlbumViewSet(viewsets.ModelViewSet):
    """
    CRUD операции для музыкальных альбомов.
    Поддерживает вложенное создание треклиста и фильтрацию.
    """
    filterset_class = AlbumFilter
    search_fields = ['title', 'artist__name']
    ordering_fields = ['title', 'release_year', 'created_at']

    def get_queryset(self):
        return (
            Album.objects.select_related('artist')
            .prefetch_related('tracks__song')
            .annotate(tracks_count=Count('tracks', distinct=True))
            .order_by('-release_year', 'title')
        )

    def get_serializer_class(self):
        if self.action == 'list':
            return AlbumListSerializer
        if self.action in ['create', 'update', 'partial_update']:
            return AlbumCreateUpdateSerializer
        return AlbumDetailSerializer

    @extend_schema(
        request=TrackInputItemSerializer,
        responses={201: AlbumSongSerializer, 400: OpenApiResponse(description='Ошибка валидации')}
    )
    @action(detail=True, methods=['post'], url_path='tracks')
    def add_track(self, request, pk=None):
        """Добавление трека в существующий альбом."""
        album = self.get_object()
        serializer = TrackInputItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        track_number = data['track_number']

        # Проверяем занятость номера трека
        if AlbumSong.objects.filter(album=album, track_number=track_number).exists():
            return Response(
                {'detail': f'Порядковый номер {track_number} уже занят в этом альбоме.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Получаем или создаем песню
        song = None
        if data.get('song_id'):
            song = get_object_or_404(Song, id=data['song_id'])
        else:
            title = data['song_title'].strip()
            song, _ = Song.objects.get_or_create(title=title)

        # Проверяем наличие песни в альбоме
        if AlbumSong.objects.filter(album=album, song=song).exists():
            return Response(
                {'detail': f'Песня «{song.title}» уже добавлена в этот альбом.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        track = AlbumSong.objects.create(
            album=album,
            song=song,
            track_number=track_number
        )
        return Response(AlbumSongSerializer(track).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['delete'], url_path=r'tracks/(?P<track_id>\d+)')
    def remove_track(self, request, pk=None, track_id=None):
        """Удаление трека из альбома."""
        album = self.get_object()
        track = get_object_or_404(AlbumSong, album=album, id=track_id)
        track.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SongViewSet(viewsets.ModelViewSet):
    """
    CRUD операции для песен с отображением всех альбомов, куда входит песня.
    """
    queryset = (
        Song.objects.prefetch_related('album_tracks__album__artist')
        .order_by('title')
    )
    serializer_class = SongSerializer
    filterset_class = SongFilter
    search_fields = ['title']
    ordering_fields = ['title', 'created_at']


class CatalogStatsView(APIView):
    """Статистика каталога для информационной панели."""

    def get(self, request):
        return Response({
            'total_artists': Artist.objects.count(),
            'total_albums': Album.objects.count(),
            'total_songs': Song.objects.count(),
            'total_tracks': AlbumSong.objects.count(),
        })

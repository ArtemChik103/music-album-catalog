from django_filters import rest_framework as filters
from .models import Album, Artist, Song


class AlbumFilter(filters.FilterSet):
    artist = filters.NumberFilter(field_name='artist_id')
    release_year = filters.NumberFilter(field_name='release_year')
    year_min = filters.NumberFilter(field_name='release_year', lookup_expr='gte')
    year_max = filters.NumberFilter(field_name='release_year', lookup_expr='lte')

    class Meta:
        model = Album
        fields = ['artist', 'release_year', 'year_min', 'year_max']


class ArtistFilter(filters.FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        model = Artist
        fields = ['name']


class SongFilter(filters.FilterSet):
    title = filters.CharFilter(field_name='title', lookup_expr='icontains')

    class Meta:
        model = Song
        fields = ['title']

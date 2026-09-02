from django.contrib import admin
from .models import Album, AlbumSong, Artist, Song


class AlbumSongInline(admin.TabularInline):
    model = AlbumSong
    extra = 1
    autocomplete_fields = ['song']
    fields = ['track_number', 'song']
    ordering = ['track_number']


@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_display = ['name', 'albums_count', 'created_at']
    search_fields = ['name']

    def albums_count(self, obj):
        return obj.albums.count()
    albums_count.short_description = 'Количество альбомов'


@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ['title', 'artist', 'release_year', 'tracks_count', 'created_at']
    list_filter = ['release_year', 'artist']
    search_fields = ['title', 'artist__name']
    autocomplete_fields = ['artist']
    inlines = [AlbumSongInline]

    def tracks_count(self, obj):
        return obj.tracks.count()
    tracks_count.short_description = 'Треков'


@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    list_display = ['title', 'albums_count', 'created_at']
    search_fields = ['title']

    def albums_count(self, obj):
        return obj.album_tracks.count()
    albums_count.short_description = 'Входит в альбомы'


@admin.register(AlbumSong)
class AlbumSongAdmin(admin.ModelAdmin):
    list_display = ['album', 'track_number', 'song']
    list_filter = ['album']
    search_fields = ['album__title', 'song__title']

from django.db import transaction
from rest_framework import serializers

from .models import Album, AlbumSong, Artist, Song


class ArtistSerializer(serializers.ModelSerializer):
    """Сериализатор исполнителя."""
    albums_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Artist
        fields = ['id', 'name', 'albums_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class SongAppearanceSerializer(serializers.ModelSerializer):
    """Отображение вхождения песни в альбом."""
    album_id = serializers.IntegerField(source='album.id', read_only=True)
    album_title = serializers.CharField(source='album.title', read_only=True)
    artist_name = serializers.CharField(source='album.artist.name', read_only=True)
    release_year = serializers.IntegerField(source='album.release_year', read_only=True)
    track_number = serializers.IntegerField(read_only=True)

    class Meta:
        model = AlbumSong
        fields = [
            'album_id',
            'album_title',
            'artist_name',
            'release_year',
            'track_number',
        ]


class SongSerializer(serializers.ModelSerializer):
    """Сериализатор песни с историей вхождений в альбомы."""
    albums = SongAppearanceSerializer(source='album_tracks', many=True, read_only=True)
    albums_count = serializers.SerializerMethodField()

    class Meta:
        model = Song
        fields = ['id', 'title', 'albums', 'albums_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_albums_count(self, obj):
        return obj.album_tracks.count()


class AlbumSongSerializer(serializers.ModelSerializer):
    """Сериализатор трека внутри альбома."""
    song_id = serializers.PrimaryKeyRelatedField(
        queryset=Song.objects.all(),
        source='song'
    )
    song_title = serializers.CharField(source='song.title', read_only=True)

    class Meta:
        model = AlbumSong
        fields = ['id', 'song_id', 'song_title', 'track_number']
        read_only_fields = ['id', 'song_title']


class TrackInputItemSerializer(serializers.Serializer):
    """Входные данные для одного трека в альбоме."""
    song_id = serializers.IntegerField(required=False, allow_null=True)
    song_title = serializers.CharField(required=False, allow_blank=False, max_length=255)
    track_number = serializers.IntegerField(min_value=1)

    def validate(self, attrs):
        if not attrs.get('song_id') and not attrs.get('song_title'):
            raise serializers.ValidationError(
                'Необходимо указать либо song_id, либо song_title.'
            )
        return attrs


class AlbumListSerializer(serializers.ModelSerializer):
    """Компактный сериализатор для каталога альбомов."""
    artist = ArtistSerializer(read_only=True)
    artist_id = serializers.PrimaryKeyRelatedField(
        queryset=Artist.objects.all(),
        source='artist',
        write_only=True
    )
    tracks_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Album
        fields = [
            'id',
            'title',
            'artist',
            'artist_id',
            'release_year',
            'tracks_count',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class AlbumDetailSerializer(serializers.ModelSerializer):
    """Детальный сериализатор альбома с упорядоченным списком треков."""
    artist = ArtistSerializer(read_only=True)
    tracks = AlbumSongSerializer(many=True, read_only=True)
    tracks_count = serializers.SerializerMethodField()

    class Meta:
        model = Album
        fields = [
            'id',
            'title',
            'artist',
            'release_year',
            'tracks',
            'tracks_count',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_tracks_count(self, obj):
        return obj.tracks.count()


class AlbumCreateUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор создания и обновления альбома с треклистом."""
    artist_id = serializers.PrimaryKeyRelatedField(
        queryset=Artist.objects.all(),
        source='artist'
    )
    tracks = TrackInputItemSerializer(many=True, required=False)

    class Meta:
        model = Album
        fields = ['id', 'title', 'artist_id', 'release_year', 'tracks']
        read_only_fields = ['id']

    def validate_tracks(self, tracks):
        if not tracks:
            return tracks

        track_numbers = set()
        seen_songs = set()

        for item in tracks:
            t_num = item['track_number']
            if t_num in track_numbers:
                raise serializers.ValidationError(
                    f'Порядковый номер {t_num} повторяется в треклисте.'
                )
            track_numbers.add(t_num)

            # Проверка уникальности песен по song_id или song_title
            song_identifier = item.get('song_id') or item.get('song_title', '').strip().lower()
            if song_identifier in seen_songs:
                raise serializers.ValidationError(
                    'Песня не может входить в один и тот же альбом дважды.'
                )
            seen_songs.add(song_identifier)

        return tracks

    @transaction.atomic
    def create(self, validated_data):
        tracks_data = validated_data.pop('tracks', [])
        album = Album.objects.create(**validated_data)
        self._sync_tracks(album, tracks_data)
        return album

    @transaction.atomic
    def update(self, instance, validated_data):
        tracks_data = validated_data.pop('tracks', None)
        instance.title = validated_data.get('title', instance.title)
        instance.artist = validated_data.get('artist', instance.artist)
        instance.release_year = validated_data.get('release_year', instance.release_year)
        instance.save()

        if tracks_data is not None:
            instance.tracks.all().delete()
            self._sync_tracks(instance, tracks_data)

        return instance

    def _sync_tracks(self, album, tracks_data):
        for item in tracks_data:
            song = None
            if item.get('song_id'):
                song = Song.objects.get(id=item['song_id'])
            elif item.get('song_title'):
                title = item['song_title'].strip()
                song, _ = Song.objects.get_or_create(title=title)

            AlbumSong.objects.create(
                album=album,
                song=song,
                track_number=item['track_number']
            )

    def to_representation(self, instance):
        return AlbumDetailSerializer(instance, context=self.context).data

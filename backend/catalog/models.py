from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Artist(models.Model):
    """Исполнитель (музыкальная группа или соло-артист)."""
    name = models.CharField(
        max_length=255,
        unique=True,
        verbose_name='Имя исполнителя'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        ordering = ['name']
        verbose_name = 'Исполнитель'
        verbose_name_plural = 'Исполнители'

    def __str__(self):
        return self.name


class Album(models.Model):
    """Музыкальный альбом."""
    title = models.CharField(
        max_length=255,
        verbose_name='Название альбома'
    )
    artist = models.ForeignKey(
        Artist,
        on_delete=models.CASCADE,
        related_name='albums',
        verbose_name='Исполнитель'
    )
    release_year = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1900, message='Год выпуска не может быть меньше 1900'),
            MaxValueValidator(2100, message='Год выпуска не может превышать 2100')
        ],
        verbose_name='Год выпуска'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        ordering = ['-release_year', 'title']
        verbose_name = 'Альбом'
        verbose_name_plural = 'Альбомы'

    def __str__(self):
        return f"{self.artist.name} - {self.title} ({self.release_year})"


class Song(models.Model):
    """Музыкальная композиция (песня)."""
    title = models.CharField(
        max_length=255,
        verbose_name='Название песни'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        ordering = ['title']
        verbose_name = 'Песня'
        verbose_name_plural = 'Песни'

    def __str__(self):
        return self.title


class AlbumSong(models.Model):
    """
    Связь песни и альбома с порядковым номером в альбоме.
    Позволяет одной песне входить в разные альбомы с разными порядковыми номерами.
    """
    album = models.ForeignKey(
        Album,
        on_delete=models.CASCADE,
        related_name='tracks',
        verbose_name='Альбом'
    )
    song = models.ForeignKey(
        Song,
        on_delete=models.CASCADE,
        related_name='album_tracks',
        verbose_name='Песня'
    )
    track_number = models.PositiveIntegerField(
        validators=[MinValueValidator(1, message='Номер трека должен быть 1 или больше')],
        verbose_name='Порядковый номер'
    )

    class Meta:
        ordering = ['track_number']
        verbose_name = 'Трек альбома'
        verbose_name_plural = 'Треки альбомов'
        constraints = [
            models.UniqueConstraint(
                fields=['album', 'track_number'],
                name='unique_album_track_number'
            ),
            models.UniqueConstraint(
                fields=['album', 'song'],
                name='unique_album_song'
            ),
        ]

    def __str__(self):
        return f"{self.track_number}. {self.song.title} ({self.album.title})"

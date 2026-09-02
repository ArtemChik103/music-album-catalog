from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase

from catalog.models import Album, AlbumSong, Artist, Song


class ModelConstraintsTestCase(TestCase):
    def setUp(self):
        self.artist = Artist.objects.create(name='Led Zeppelin')
        self.album1 = Album.objects.create(
            title='Led Zeppelin IV',
            artist=self.artist,
            release_year=1971
        )
        self.album2 = Album.objects.create(
            title='Mothership',
            artist=self.artist,
            release_year=2007
        )
        self.song1 = Song.objects.create(title='Stairway to Heaven')
        self.song2 = Song.objects.create(title='Black Dog')

    def test_artist_unique_name(self):
        """Имя исполнителя должно быть уникальным."""
        with self.assertRaises(IntegrityError):
            Artist.objects.create(name='Led Zeppelin')

    def test_same_song_in_different_albums_with_different_track_numbers(self):
        """
        Ключевое бизнес-требование:
        Одна и та же песня может входить в разные альбомы с разными порядковыми номерами.
        """
        # В первом альбоме трек №4
        track1 = AlbumSong.objects.create(
            album=self.album1,
            song=self.song1,
            track_number=4
        )
        # Во втором альбоме та же песня под треком №1
        track2 = AlbumSong.objects.create(
            album=self.album2,
            song=self.song1,
            track_number=1
        )

        self.assertEqual(track1.song, track2.song)
        self.assertNotEqual(track1.album, track2.album)
        self.assertEqual(track1.track_number, 4)
        self.assertEqual(track2.track_number, 1)
        self.assertEqual(self.song1.album_tracks.count(), 2)

    def test_unique_track_number_per_album(self):
        """В одном альбоме не может быть двух треков с одинаковым порядковым номером."""
        AlbumSong.objects.create(
            album=self.album1,
            song=self.song1,
            track_number=1
        )
        with self.assertRaises(IntegrityError):
            AlbumSong.objects.create(
                album=self.album1,
                song=self.song2,
                track_number=1
            )

    def test_unique_song_per_album(self):
        """Одна и та же песня не может быть добавлена дважды в один альбом."""
        AlbumSong.objects.create(
            album=self.album1,
            song=self.song1,
            track_number=1
        )
        with self.assertRaises(IntegrityError):
            AlbumSong.objects.create(
                album=self.album1,
                song=self.song1,
                track_number=2
            )

    def test_cascade_delete_album(self):
        """При удалении альбома удаляются связующие треки, но песня сохраняется."""
        AlbumSong.objects.create(
            album=self.album1,
            song=self.song1,
            track_number=4
        )
        song_id = self.song1.id
        self.album1.delete()

        self.assertEqual(AlbumSong.objects.filter(song_id=song_id).count(), 0)
        self.assertTrue(Song.objects.filter(id=song_id).exists())

    def test_cascade_delete_song(self):
        """При удалении песни удаляются связующие треки, но альбом сохраняется."""
        AlbumSong.objects.create(
            album=self.album1,
            song=self.song1,
            track_number=4
        )
        album_id = self.album1.id
        self.song1.delete()

        self.assertEqual(AlbumSong.objects.filter(album_id=album_id).count(), 0)
        self.assertTrue(Album.objects.filter(id=album_id).exists())

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from catalog.models import Album, AlbumSong, Artist, Song


class CatalogAPITestCase(APITestCase):
    def setUp(self):
        self.artist = Artist.objects.create(name='Pink Floyd')
        self.album = Album.objects.create(
            title='The Dark Side of the Moon',
            artist=self.artist,
            release_year=1973
        )
        self.song1 = Song.objects.create(title='Time')
        self.song2 = Song.objects.create(title='Money')

        self.track1 = AlbumSong.objects.create(
            album=self.album,
            song=self.song1,
            track_number=4
        )
        self.track2 = AlbumSong.objects.create(
            album=self.album,
            song=self.song2,
            track_number=6
        )

    def test_list_artists(self):
        url = reverse('artist-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['name'], 'Pink Floyd')
        self.assertEqual(data[0]['albums_count'], 1)

    def test_create_artist(self):
        url = reverse('artist-list')
        response = self.client.post(url, {'name': 'The Beatles'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Artist.objects.filter(name='The Beatles').exists())

    def test_list_albums(self):
        url = reverse('album-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['title'], 'The Dark Side of the Moon')
        self.assertEqual(data[0]['tracks_count'], 2)
        self.assertEqual(data[0]['artist']['name'], 'Pink Floyd')

    def test_retrieve_album_detail(self):
        url = reverse('album-detail', kwargs={'pk': self.album.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['title'], 'The Dark Side of the Moon')
        self.assertEqual(len(data['tracks']), 2)
        # Проверяем сортировку по track_number (4 идет раньше 6)
        self.assertEqual(data['tracks'][0]['track_number'], 4)
        self.assertEqual(data['tracks'][0]['song_title'], 'Time')
        self.assertEqual(data['tracks'][1]['track_number'], 6)
        self.assertEqual(data['tracks'][1]['song_title'], 'Money')

    def test_create_album_with_nested_tracks(self):
        url = reverse('album-list')
        payload = {
            'title': 'Wish You Were Here',
            'artist_id': self.artist.id,
            'release_year': 1975,
            'tracks': [
                {'song_title': 'Shine On You Crazy Diamond (Pts. 1-5)', 'track_number': 1},
                {'song_title': 'Welcome to the Machine', 'track_number': 2},
                {'song_id': self.song1.id, 'track_number': 3}  # Повторное использование существующей песни
            ]
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.json()
        self.assertEqual(data['title'], 'Wish You Were Here')
        self.assertEqual(len(data['tracks']), 3)

        # Проверяем, что песня Time теперь в двух альбомах
        song_url = reverse('song-detail', kwargs={'pk': self.song1.id})
        song_res = self.client.get(song_url)
        song_data = song_res.json()
        self.assertEqual(len(song_data['albums']), 2)

    def test_create_album_validation_duplicate_track_number(self):
        url = reverse('album-list')
        payload = {
            'title': 'Invalid Album',
            'artist_id': self.artist.id,
            'release_year': 2020,
            'tracks': [
                {'song_title': 'Song A', 'track_number': 1},
                {'song_title': 'Song B', 'track_number': 1}  # Дубликат номера
            ]
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_album_validation_duplicate_song(self):
        url = reverse('album-list')
        payload = {
            'title': 'Invalid Album 2',
            'artist_id': self.artist.id,
            'release_year': 2020,
            'tracks': [
                {'song_id': self.song1.id, 'track_number': 1},
                {'song_id': self.song1.id, 'track_number': 2}  # Та же песня дважды
            ]
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_track_to_album_endpoint(self):
        url = reverse('album-add-track', kwargs={'pk': self.album.id})
        payload = {'song_title': 'Us and Them', 'track_number': 7}
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(AlbumSong.objects.filter(album=self.album).count(), 3)

    def test_remove_track_from_album_endpoint(self):
        url = reverse('album-remove-track', kwargs={'pk': self.album.id, 'track_id': self.track1.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(AlbumSong.objects.filter(id=self.track1.id).exists())
        # Сама песня не должна удалиться!
        self.assertTrue(Song.objects.filter(id=self.song1.id).exists())

    def test_song_shows_all_album_appearances(self):
        # Добавим song1 во второй альбом
        album2 = Album.objects.create(
            title='Echoes: The Best of Pink Floyd',
            artist=self.artist,
            release_year=2001
        )
        AlbumSong.objects.create(album=album2, song=self.song1, track_number=2)

        url = reverse('song-detail', kwargs={'pk': self.song1.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['title'], 'Time')
        self.assertEqual(len(data['albums']), 2)
        # Проверяем номера в разных альбомах
        numbers = {item['album_title']: item['track_number'] for item in data['albums']}
        self.assertEqual(numbers['The Dark Side of the Moon'], 4)
        self.assertEqual(numbers['Echoes: The Best of Pink Floyd'], 2)

    def test_catalog_stats_endpoint(self):
        url = reverse('catalog-stats')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['total_artists'], 1)
        self.assertEqual(data['total_albums'], 1)
        self.assertEqual(data['total_songs'], 2)
        self.assertEqual(data['total_tracks'], 2)

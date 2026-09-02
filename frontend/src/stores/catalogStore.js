import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { albumsApi, artistsApi, songsApi, statsApi } from '../api/client'

export const useCatalogStore = defineStore('catalog', () => {
  // State
  const albums = ref([])
  const artists = ref([])
  const songs = ref([])
  const stats = ref({
    total_artists: 0,
    total_albums: 0,
    total_songs: 0,
    total_tracks: 0
  })

  const currentAlbum = ref(null)
  const isLoading = ref(false)
  const isActionLoading = ref(false)
  const error = ref(null)
  const toast = ref(null)

  // Filters
  const albumSearch = ref('')
  const selectedArtist = ref('')
  const selectedYear = ref('')

  // Toast notification helper
  const showToast = (message, type = 'success') => {
    toast.value = { message, type }
    setTimeout(() => {
      if (toast.value?.message === message) {
        toast.value = null
      }
    }, 4000)
  }

  // Fetch actions
  const fetchStats = async () => {
    try {
      const res = await statsApi.get()
      stats.value = res.data
    } catch (err) {
      console.error('Failed to load stats:', err)
    }
  }

  const fetchArtists = async () => {
    try {
      const res = await artistsApi.list()
      artists.value = res.data
    } catch (err) {
      console.error('Failed to load artists:', err)
      showToast('Ошибка загрузки исполнителей', 'error')
    }
  }

  const fetchSongs = async (search = '') => {
    try {
      const params = search ? { search } : {}
      const res = await songsApi.list(params)
      songs.value = res.data
    } catch (err) {
      console.error('Failed to load songs:', err)
      showToast('Ошибка загрузки песен', 'error')
    }
  }

  const fetchAlbums = async () => {
    isLoading.value = true
    error.value = null
    try {
      const params = {}
      if (albumSearch.value) params.search = albumSearch.value
      if (selectedArtist.value) params.artist = selectedArtist.value
      if (selectedYear.value) params.release_year = selectedYear.value

      const res = await albumsApi.list(params)
      albums.value = res.data
    } catch (err) {
      error.value = 'Не удалось загрузить список альбомов'
      showToast('Ошибка загрузки альбомов', 'error')
    } finally {
      isLoading.value = false
    }
  }

  const fetchAlbumDetail = async (id) => {
    isLoading.value = true
    error.value = null
    try {
      const res = await albumsApi.get(id)
      currentAlbum.value = res.data
      return res.data
    } catch (err) {
      error.value = 'Альбом не найден'
      showToast('Ошибка загрузки альбома', 'error')
      throw err
    } finally {
      isLoading.value = false
    }
  }

  // Mutation actions
  const createAlbum = async (albumData) => {
    isActionLoading.value = true
    try {
      const res = await albumsApi.create(albumData)
      showToast(`Альбом «${res.data.title}» создан`)
      await Promise.all([fetchAlbums(), fetchStats(), fetchSongs()])
      return res.data
    } catch (err) {
      const msg = err.response?.data?.detail || err.response?.data?.tracks?.[0] || 'Ошибка при создании альбома'
      showToast(typeof msg === 'string' ? msg : JSON.stringify(msg), 'error')
      throw err
    } finally {
      isActionLoading.value = false
    }
  }

  const updateAlbum = async (id, albumData) => {
    isActionLoading.value = true
    try {
      const res = await albumsApi.update(id, albumData)
      currentAlbum.value = res.data
      showToast('Альбом успешно обновлен')
      await fetchAlbums()
      return res.data
    } catch (err) {
      const msg = err.response?.data?.detail || 'Ошибка при сохранении альбома'
      showToast(typeof msg === 'string' ? msg : JSON.stringify(msg), 'error')
      throw err
    } finally {
      isActionLoading.value = false
    }
  }

  const deleteAlbum = async (id) => {
    isActionLoading.value = true
    try {
      await albumsApi.delete(id)
      showToast('Альбом удален')
      await Promise.all([fetchAlbums(), fetchStats(), fetchSongs()])
    } catch (err) {
      showToast('Ошибка при удалении альбома', 'error')
      throw err
    } finally {
      isActionLoading.value = false
    }
  }

  const addTrackToAlbum = async (albumId, trackData) => {
    isActionLoading.value = true
    try {
      await albumsApi.addTrack(albumId, trackData)
      showToast('Трек добавлен в альбом')
      await Promise.all([fetchAlbumDetail(albumId), fetchStats(), fetchSongs()])
    } catch (err) {
      const msg = err.response?.data?.detail || 'Ошибка при добавлении трека'
      showToast(typeof msg === 'string' ? msg : JSON.stringify(msg), 'error')
      throw err
    } finally {
      isActionLoading.value = false
    }
  }

  const removeTrackFromAlbum = async (albumId, trackId) => {
    isActionLoading.value = true
    try {
      await albumsApi.removeTrack(albumId, trackId)
      showToast('Трек удален из альбома')
      await Promise.all([fetchAlbumDetail(albumId), fetchStats(), fetchSongs()])
    } catch (err) {
      showToast('Ошибка при удалении трека', 'error')
      throw err
    } finally {
      isActionLoading.value = false
    }
  }

  // Artist mutations
  const createArtist = async (name) => {
    isActionLoading.value = true
    try {
      const res = await artistsApi.create({ name })
      showToast(`Исполнитель «${res.data.name}» добавлен`)
      await Promise.all([fetchArtists(), fetchStats()])
      return res.data
    } catch (err) {
      const msg = err.response?.data?.name?.[0] || 'Ошибка при создании исполнителя'
      showToast(msg, 'error')
      throw err
    } finally {
      isActionLoading.value = false
    }
  }

  const updateArtist = async (id, name) => {
    isActionLoading.value = true
    try {
      const res = await artistsApi.update(id, { name })
      showToast('Исполнитель переименован')
      await Promise.all([fetchArtists(), fetchAlbums()])
      return res.data
    } catch (err) {
      const msg = err.response?.data?.name?.[0] || 'Ошибка при переименовании исполнителя'
      showToast(msg, 'error')
      throw err
    } finally {
      isActionLoading.value = false
    }
  }

  const deleteArtist = async (id) => {
    isActionLoading.value = true
    try {
      await artistsApi.delete(id)
      showToast('Исполнитель удален')
      await Promise.all([fetchArtists(), fetchAlbums(), fetchStats()])
    } catch (err) {
      showToast('Ошибка при удалении исполнителя', 'error')
      throw err
    } finally {
      isActionLoading.value = false
    }
  }

  // Song mutations
  const createSong = async (title) => {
    isActionLoading.value = true
    try {
      const res = await songsApi.create({ title })
      showToast(`Песня «${res.data.title}» добавлена`)
      await Promise.all([fetchSongs(), fetchStats()])
      return res.data
    } catch (err) {
      const msg = err.response?.data?.title?.[0] || 'Ошибка при создании песни'
      showToast(msg, 'error')
      throw err
    } finally {
      isActionLoading.value = false
    }
  }

  const updateSong = async (id, title) => {
    isActionLoading.value = true
    try {
      const res = await songsApi.update(id, { title })
      showToast('Название песни изменено')
      await Promise.all([fetchSongs(), fetchAlbums()])
      if (currentAlbum.value) await fetchAlbumDetail(currentAlbum.value.id)
      return res.data
    } catch (err) {
      const msg = err.response?.data?.title?.[0] || 'Ошибка при обновлении песни'
      showToast(msg, 'error')
      throw err
    } finally {
      isActionLoading.value = false
    }
  }

  const deleteSong = async (id) => {
    isActionLoading.value = true
    try {
      await songsApi.delete(id)
      showToast('Песня удалена')
      await Promise.all([fetchSongs(), fetchAlbums(), fetchStats()])
      if (currentAlbum.value) await fetchAlbumDetail(currentAlbum.value.id)
    } catch (err) {
      showToast('Ошибка при удалении песни', 'error')
      throw err
    } finally {
      isActionLoading.value = false
    }
  }

  return {
    albums,
    artists,
    songs,
    stats,
    currentAlbum,
    isLoading,
    isActionLoading,
    error,
    toast,
    albumSearch,
    selectedArtist,
    selectedYear,
    showToast,
    fetchStats,
    fetchArtists,
    fetchSongs,
    fetchAlbums,
    fetchAlbumDetail,
    createAlbum,
    updateAlbum,
    deleteAlbum,
    addTrackToAlbum,
    removeTrackFromAlbum,
    createArtist,
    updateArtist,
    deleteArtist,
    createSong,
    updateSong,
    deleteSong
  }
})

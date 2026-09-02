<script setup>
import { ref, onMounted, computed } from 'vue'
import { useCatalogStore } from '../stores/catalogStore'
import AlbumCard from '../components/AlbumCard.vue'
import SkeletonCard from '../components/SkeletonCard.vue'
import EmptyState from '../components/EmptyState.vue'
import AlbumModal from '../components/AlbumModal.vue'
import ConfirmModal from '../components/ConfirmModal.vue'
import {
  PhMagnifyingGlass,
  PhPlus,
  PhFunnel,
  PhX,
  PhDisc
} from '@phosphor-icons/vue'

const catalogStore = useCatalogStore()

const isAlbumModalOpen = ref(false)
const selectedAlbumForEdit = ref(null)

const isDeleteModalOpen = ref(false)
const albumToDelete = ref(null)

onMounted(async () => {
  await Promise.all([
    catalogStore.fetchAlbums(),
    catalogStore.fetchArtists(),
    catalogStore.fetchStats(),
    catalogStore.fetchSongs()
  ])
})

const uniqueYears = computed(() => {
  const years = new Set(catalogStore.albums.map((a) => a.release_year))
  return Array.from(years).sort((a, b) => b - a)
})

let searchTimeout = null
const handleSearchInput = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    catalogStore.fetchAlbums()
  }, 250)
}

const handleFilterChange = () => {
  catalogStore.fetchAlbums()
}

const clearFilters = () => {
  catalogStore.albumSearch = ''
  catalogStore.selectedArtist = ''
  catalogStore.selectedYear = ''
  catalogStore.fetchAlbums()
}

const hasActiveFilters = computed(() => {
  return (
    Boolean(catalogStore.albumSearch) ||
    Boolean(catalogStore.selectedArtist) ||
    Boolean(catalogStore.selectedYear)
  )
})

const openCreateModal = () => {
  selectedAlbumForEdit.value = null
  isAlbumModalOpen.value = true
}

const openEditModal = (album) => {
  selectedAlbumForEdit.value = album
  isAlbumModalOpen.value = true
}

const handleSaveAlbum = async (albumData) => {
  try {
    let artistId = albumData.artist_id

    // If user typed a new artist on the fly
    if (albumData.new_artist_name) {
      const createdArtist = await catalogStore.createArtist(albumData.new_artist_name)
      artistId = createdArtist.id
    }

    const payload = {
      title: albumData.title,
      artist_id: artistId,
      release_year: albumData.release_year,
      tracks: albumData.tracks
    }

    if (albumData.id) {
      await catalogStore.updateAlbum(albumData.id, payload)
    } else {
      await catalogStore.createAlbum(payload)
    }
    isAlbumModalOpen.value = false
  } catch (err) {
    // Error is handled in store toast
  }
}

const openDeleteModal = (album) => {
  albumToDelete.value = album
  isDeleteModalOpen.value = true
}

const handleConfirmDelete = async () => {
  if (!albumToDelete.value) return
  try {
    await catalogStore.deleteAlbum(albumToDelete.value.id)
    isDeleteModalOpen.value = false
    albumToDelete.value = null
  } catch (err) {
    // Error handled in store
  }
}
</script>

<template>
  <div class="space-y-6">
    <!-- Top Action & Search Bar -->
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-2 border-b border-zinc-800/80">
      <div>
        <h1 class="text-2xl font-bold tracking-tight text-zinc-100 flex items-center gap-2.5">
          <PhDisc :size="28" weight="duotone" class="text-amber-500" />
          <span>Каталог альбомов</span>
        </h1>
        <p class="text-xs text-zinc-400 mt-1">
          Всего в коллекции: {{ catalogStore.stats.total_albums }} изданий · {{ catalogStore.stats.total_tracks }} композиций
        </p>
      </div>

      <button
        @click="openCreateModal"
        class="inline-flex items-center justify-center gap-2 px-4 py-2 rounded-lg bg-amber-500 hover:bg-amber-400 text-zinc-950 text-sm font-semibold transition-all active:scale-[0.98] shadow-md shadow-amber-500/10 cursor-pointer"
      >
        <PhPlus :size="18" weight="bold" />
        <span>Добавить альбом</span>
      </button>
    </div>

    <!-- Filters Row -->
    <div class="flex flex-col sm:flex-row items-stretch sm:items-center gap-3">
      <!-- Search Input -->
      <div class="relative flex-1">
        <PhMagnifyingGlass :size="16" class="absolute left-3 top-1/2 -translate-y-1/2 text-zinc-500 pointer-events-none" />
        <input
          v-model="catalogStore.albumSearch"
          @input="handleSearchInput"
          type="text"
          placeholder="Поиск по названию альбома или исполнителю..."
          class="w-full pl-9 pr-8 py-2 rounded-lg bg-zinc-900 border border-zinc-800 text-sm text-zinc-100 placeholder-zinc-500 focus:outline-none focus:ring-1 focus:ring-amber-500 focus:border-amber-500 transition-colors"
        />
        <button
          v-if="catalogStore.albumSearch"
          @click="catalogStore.albumSearch = ''; handleSearchInput()"
          class="absolute right-2.5 top-1/2 -translate-y-1/2 text-zinc-500 hover:text-zinc-300 p-0.5"
        >
          <PhX :size="14" />
        </button>
      </div>

      <!-- Filter by Artist -->
      <div class="w-full sm:w-56">
        <select
          v-model="catalogStore.selectedArtist"
          @change="handleFilterChange"
          class="w-full px-3 py-2 rounded-lg bg-zinc-900 border border-zinc-800 text-sm text-zinc-100 focus:outline-none focus:ring-1 focus:ring-amber-500 focus:border-amber-500 transition-colors"
        >
          <option value="">Все исполнители</option>
          <option v-for="a in catalogStore.artists" :key="a.id" :value="a.id">
            {{ a.name }} ({{ a.albums_count || 0 }})
          </option>
        </select>
      </div>

      <!-- Filter by Year -->
      <div class="w-full sm:w-40">
        <select
          v-model="catalogStore.selectedYear"
          @change="handleFilterChange"
          class="w-full px-3 py-2 rounded-lg bg-zinc-900 border border-zinc-800 text-sm text-zinc-100 focus:outline-none focus:ring-1 focus:ring-amber-500 focus:border-amber-500 transition-colors"
        >
          <option value="">Любой год</option>
          <option v-for="y in uniqueYears" :key="y" :value="y">
            {{ y }} год
          </option>
        </select>
      </div>

      <!-- Reset Filter Button -->
      <button
        v-if="hasActiveFilters"
        @click="clearFilters"
        class="px-3 py-2 rounded-lg text-xs font-medium text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900 border border-zinc-800 transition-colors flex items-center justify-center gap-1.5 cursor-pointer"
        title="Сбросить все фильтры"
      >
        <PhFunnel :size="14" />
        <span>Сбросить</span>
      </button>
    </div>

    <!-- Albums Grid -->
    <div v-if="catalogStore.isLoading" class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
      <SkeletonCard v-for="n in 8" :key="n" />
    </div>

    <div v-else-if="catalogStore.albums.length > 0" class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
      <AlbumCard
        v-for="album in catalogStore.albums"
        :key="album.id"
        :album="album"
        @edit="openEditModal"
        @delete="openDeleteModal"
      />
    </div>

    <!-- Empty State -->
    <EmptyState
      v-else
      :title="hasActiveFilters ? 'Альбомы по заданным критериям не найдены' : 'Каталог альбомов пуст'"
      :description="hasActiveFilters ? 'Попробуйте изменить поисковый запрос или сбросить фильтры.' : 'Начните коллекцию, добавив свой первый альбом.'"
      :action-text="hasActiveFilters ? 'Сбросить фильтры' : 'Добавить альбом'"
      @action="hasActiveFilters ? clearFilters() : openCreateModal()"
    />

    <!-- Modals -->
    <AlbumModal
      :is-open="isAlbumModalOpen"
      :album="selectedAlbumForEdit"
      :artists="catalogStore.artists"
      :songs="catalogStore.songs"
      :is-loading="catalogStore.isActionLoading"
      @save="handleSaveAlbum"
      @close="isAlbumModalOpen = false"
    />

    <ConfirmModal
      :is-open="isDeleteModalOpen"
      title="Удаление альбома"
      :message="`Вы действительно хотите удалить альбом «${albumToDelete?.title}»? Композиции останутся в общем каталоге песен.`"
      :is-loading="catalogStore.isActionLoading"
      @confirm="handleConfirmDelete"
      @close="isDeleteModalOpen = false"
    />
  </div>
</template>

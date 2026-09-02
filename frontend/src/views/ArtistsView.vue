<script setup>
import { ref, onMounted, computed } from 'vue'
import { RouterLink } from 'vue-router'
import { useCatalogStore } from '../stores/catalogStore'
import ArtistModal from '../components/ArtistModal.vue'
import ConfirmModal from '../components/ConfirmModal.vue'
import EmptyState from '../components/EmptyState.vue'
import {
  PhUsers,
  PhPlus,
  PhMagnifyingGlass,
  PhPencilSimple,
  PhTrash,
  PhDisc,
  PhX
} from '@phosphor-icons/vue'

const catalogStore = useCatalogStore()

const searchQuery = ref('')
const isModalOpen = ref(false)
const selectedArtist = ref(null)

const isDeleteModalOpen = ref(false)
const artistToDelete = ref(null)

onMounted(async () => {
  await Promise.all([
    catalogStore.fetchArtists(),
    catalogStore.fetchAlbums(),
    catalogStore.fetchStats()
  ])
})

const filteredArtists = computed(() => {
  const q = searchQuery.value.trim().toLowerCase()
  if (!q) return catalogStore.artists
  return catalogStore.artists.filter((a) => a.name.toLowerCase().includes(q))
})

const openCreateModal = () => {
  selectedArtist.value = null
  isModalOpen.value = true
}

const openEditModal = (artist) => {
  selectedArtist.value = artist
  isModalOpen.value = true
}

const handleSaveArtist = async (data) => {
  try {
    if (data.id) {
      await catalogStore.updateArtist(data.id, data.name)
    } else {
      await catalogStore.createArtist(data.name)
    }
    isModalOpen.value = false
  } catch (err) {
    // Handled in store
  }
}

const confirmDeleteArtist = (artist) => {
  artistToDelete.value = artist
  isDeleteModalOpen.value = true
}

const handleDeleteArtist = async () => {
  if (!artistToDelete.value) return
  try {
    await catalogStore.deleteArtist(artistToDelete.value.id)
    isDeleteModalOpen.value = false
    artistToDelete.value = null
  } catch (err) {
    // Handled in store
  }
}

// Get albums belonging to an artist
const getArtistAlbums = (artistId) => {
  return catalogStore.albums.filter((a) => a.artist?.id === artistId)
}
</script>

<template>
  <div class="space-y-6">
    <!-- Top Action Bar -->
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-2 border-b border-zinc-800/80">
      <div>
        <h1 class="text-2xl font-bold tracking-tight text-zinc-100 flex items-center gap-2.5">
          <PhUsers :size="28" weight="duotone" class="text-amber-500" />
          <span>Исполнители и группы</span>
        </h1>
        <p class="text-xs text-zinc-400 mt-1">
          Всего в каталоге: {{ catalogStore.stats.total_artists }} артистов
        </p>
      </div>

      <button
        @click="openCreateModal"
        class="inline-flex items-center justify-center gap-2 px-4 py-2 rounded-lg bg-amber-500 hover:bg-amber-400 text-zinc-950 text-sm font-semibold transition-all active:scale-[0.98] shadow-md shadow-amber-500/10 cursor-pointer"
      >
        <PhPlus :size="18" weight="bold" />
        <span>Добавить артиста</span>
      </button>
    </div>

    <!-- Search input -->
    <div class="relative max-w-md">
      <PhMagnifyingGlass :size="16" class="absolute left-3 top-1/2 -translate-y-1/2 text-zinc-500 pointer-events-none" />
      <input
        v-model="searchQuery"
        type="text"
        placeholder="Поиск исполнителя по имени..."
        class="w-full pl-9 pr-8 py-2 rounded-lg bg-zinc-900 border border-zinc-800 text-sm text-zinc-100 placeholder-zinc-500 focus:outline-none focus:ring-1 focus:ring-amber-500 focus:border-amber-500 transition-colors"
      />
      <button
        v-if="searchQuery"
        @click="searchQuery = ''"
        class="absolute right-2.5 top-1/2 -translate-y-1/2 text-zinc-500 hover:text-zinc-300 p-0.5"
      >
        <PhX :size="14" />
      </button>
    </div>

    <!-- Artists Grid -->
    <div v-if="filteredArtists.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div
        v-for="artist in filteredArtists"
        :key="artist.id"
        class="flex flex-col justify-between p-5 rounded-xl bg-zinc-900 border border-zinc-800/80 hover:border-zinc-700 transition-all hover:shadow-lg"
      >
        <div>
          <div class="flex items-start justify-between gap-3 mb-2">
            <h3 class="text-base font-semibold text-zinc-100 hover:text-amber-400 transition-colors">
              {{ artist.name }}
            </h3>

            <div class="flex items-center gap-1">
              <button
                @click="openEditModal(artist)"
                class="p-1.5 rounded-lg text-zinc-400 hover:text-zinc-100 hover:bg-zinc-800 transition-colors cursor-pointer"
                title="Редактировать имя"
              >
                <PhPencilSimple :size="15" />
              </button>
              <button
                @click="confirmDeleteArtist(artist)"
                class="p-1.5 rounded-lg text-zinc-400 hover:text-rose-400 hover:bg-rose-500/10 transition-colors cursor-pointer"
                title="Удалить артиста"
              >
                <PhTrash :size="15" />
              </button>
            </div>
          </div>

          <!-- Albums of this artist -->
          <div class="mt-3">
            <div class="text-[11px] font-medium text-zinc-400 mb-1.5 flex items-center gap-1.5">
              <PhDisc :size="13" class="text-amber-500" />
              <span>Издания ({{ getArtistAlbums(artist.id).length }}):</span>
            </div>

            <div v-if="getArtistAlbums(artist.id).length > 0" class="flex flex-wrap gap-1.5">
              <RouterLink
                v-for="alb in getArtistAlbums(artist.id)"
                :key="alb.id"
                :to="`/albums/${alb.id}`"
                class="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-zinc-950 border border-zinc-800 hover:border-amber-500/50 text-xs text-zinc-300 hover:text-amber-300 transition-colors"
              >
                <span>{{ alb.title }}</span>
                <span class="font-mono text-[10px] text-zinc-500">({{ alb.release_year }})</span>
              </RouterLink>
            </div>
            <p v-else class="text-xs text-zinc-500 italic">
              Альбомы пока не добавлены
            </p>
          </div>
        </div>

        <div class="mt-4 pt-3 border-t border-zinc-800/60 flex items-center justify-between text-xs text-zinc-500">
          <span>ID: {{ artist.id }}</span>
          <span>В каталоге</span>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <EmptyState
      v-else
      :title="searchQuery ? 'Исполнитель не найден' : 'Список артистов пуст'"
      :description="searchQuery ? 'Попробуйте изменить поисковый запрос.' : 'Добавьте первого исполнителя или музыкальную группу.'"
      :action-text="searchQuery ? 'Очистить поиск' : 'Добавить артиста'"
      @action="searchQuery ? (searchQuery = '') : openCreateModal()"
    />

    <!-- Modals -->
    <ArtistModal
      :is-open="isModalOpen"
      :artist="selectedArtist"
      :is-loading="catalogStore.isActionLoading"
      @save="handleSaveArtist"
      @close="isModalOpen = false"
    />

    <ConfirmModal
      :is-open="isDeleteModalOpen"
      title="Удаление исполнителя"
      :message="`Вы уверены, что хотите удалить исполнителя «${artistToDelete?.name}»? Внимание: все связанные альбомы этого исполнителя также будут удалены.`"
      :is-loading="catalogStore.isActionLoading"
      @confirm="handleDeleteArtist"
      @close="isDeleteModalOpen = false"
    />
  </div>
</template>

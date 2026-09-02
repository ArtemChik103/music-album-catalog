<script setup>
import { ref, onMounted, computed } from 'vue'
import { RouterLink } from 'vue-router'
import { useCatalogStore } from '../stores/catalogStore'
import SongModal from '../components/SongModal.vue'
import ConfirmModal from '../components/ConfirmModal.vue'
import EmptyState from '../components/EmptyState.vue'
import {
  PhMusicNotes,
  PhPlus,
  PhMagnifyingGlass,
  PhPencilSimple,
  PhTrash,
  PhDisc,
  PhHash,
  PhX,
  PhInfo
} from '@phosphor-icons/vue'

const catalogStore = useCatalogStore()

const searchQuery = ref('')
const isModalOpen = ref(false)
const selectedSong = ref(null)

const isDeleteModalOpen = ref(false)
const songToDelete = ref(null)

onMounted(async () => {
  await Promise.all([
    catalogStore.fetchSongs(),
    catalogStore.fetchStats()
  ])
})

const filteredSongs = computed(() => {
  const q = searchQuery.value.trim().toLowerCase()
  if (!q) return catalogStore.songs
  return catalogStore.songs.filter((s) => s.title.toLowerCase().includes(q))
})

const openCreateModal = () => {
  selectedSong.value = null
  isModalOpen.value = true
}

const openEditModal = (song) => {
  selectedSong.value = song
  isModalOpen.value = true
}

const handleSaveSong = async (data) => {
  try {
    if (data.id) {
      await catalogStore.updateSong(data.id, data.title)
    } else {
      await catalogStore.createSong(data.title)
    }
    isModalOpen.value = false
  } catch (err) {
    // Handled in store
  }
}

const confirmDeleteSong = (song) => {
  songToDelete.value = song
  isDeleteModalOpen.value = true
}

const handleDeleteSong = async () => {
  if (!songToDelete.value) return
  try {
    await catalogStore.deleteSong(songToDelete.value.id)
    isDeleteModalOpen.value = false
    songToDelete.value = null
  } catch (err) {
    // Handled in store
  }
}
</script>

<template>
  <div class="space-y-6">
    <!-- Top Action Bar -->
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-2 border-b border-zinc-800/80">
      <div>
        <h1 class="text-2xl font-bold tracking-tight text-zinc-100 flex items-center gap-2.5">
          <PhMusicNotes :size="28" weight="duotone" class="text-amber-500" />
          <span>Библиотека композиций</span>
        </h1>
        <p class="text-xs text-zinc-400 mt-1">
          Всего в фонотеке: {{ catalogStore.stats.total_songs }} песен · включений в треклисты: {{ catalogStore.stats.total_tracks }}
        </p>
      </div>

      <button
        @click="openCreateModal"
        class="inline-flex items-center justify-center gap-2 px-4 py-2 rounded-lg bg-amber-500 hover:bg-amber-400 text-zinc-950 text-sm font-semibold transition-all active:scale-[0.98] shadow-md shadow-amber-500/10 cursor-pointer"
      >
        <PhPlus :size="18" weight="bold" />
        <span>Добавить песню</span>
      </button>
    </div>

    <!-- Architectural Rule Banner -->
    <div class="p-3.5 rounded-xl bg-amber-500/5 border border-amber-500/20 flex items-start gap-3">
      <PhInfo :size="20" class="text-amber-400 shrink-0 mt-0.5" />
      <div class="text-xs text-zinc-300 leading-relaxed">
        <strong class="text-amber-400 font-semibold">Спецификация SDD:</strong>
        Одна и та же композиция может быть включена в несколько альбомов (студийные релизы, сборники лучших хитов, концертные записи) с разными порядковыми номерами треков.
      </div>
    </div>

    <!-- Search input -->
    <div class="relative max-w-md">
      <PhMagnifyingGlass :size="16" class="absolute left-3 top-1/2 -translate-y-1/2 text-zinc-500 pointer-events-none" />
      <input
        v-model="searchQuery"
        type="text"
        placeholder="Поиск по названию песни..."
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

    <!-- Songs Table / Card List -->
    <div v-if="filteredSongs.length > 0" class="space-y-3">
      <div
        v-for="song in filteredSongs"
        :key="song.id"
        class="p-4 rounded-xl bg-zinc-900 border border-zinc-800/80 hover:border-zinc-700 transition-all flex flex-col md:flex-row md:items-center justify-between gap-4"
      >
        <!-- Title & Basic Info -->
        <div class="flex-1">
          <div class="flex items-center gap-2">
            <h3 class="text-base font-semibold text-zinc-100">
              {{ song.title }}
            </h3>
            <span
              v-if="song.albums?.length > 1"
              class="px-2 py-0.5 text-[10px] font-mono rounded bg-amber-500/10 text-amber-400 border border-amber-500/20"
              title="Песня входит в несколько релизов с разными номерами треков"
            >
              В {{ song.albums.length }} альбомах
            </span>
          </div>

          <!-- Album Appearances -->
          <div class="mt-2.5 flex flex-wrap gap-2 items-center">
            <div
              v-for="app in song.albums"
              :key="app.album_id"
              class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-zinc-950 border border-zinc-800 text-xs text-zinc-300"
            >
              <PhDisc :size="14" class="text-amber-500" />
              <RouterLink
                :to="`/albums/${app.album_id}`"
                class="hover:text-amber-300 hover:underline transition-colors font-medium"
              >
                {{ app.album_title }}
              </RouterLink>
              <span class="text-zinc-500">({{ app.artist_name }}, {{ app.release_year }})</span>
              <span class="font-mono text-amber-400 bg-zinc-900 px-1.5 py-0.5 rounded border border-zinc-700 text-[11px] font-bold">
                Трек #{{ app.track_number }}
              </span>
            </div>

            <span v-if="!song.albums || song.albums.length === 0" class="text-xs text-zinc-500 italic">
              Не привязана ни к одному альбому
            </span>
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="flex items-center gap-1.5 shrink-0 self-end md:self-auto border-t md:border-t-0 pt-2 md:pt-0 border-zinc-800">
          <button
            @click="openEditModal(song)"
            class="p-2 rounded-lg text-zinc-400 hover:text-zinc-100 hover:bg-zinc-800 transition-colors cursor-pointer"
            title="Переименовать песню"
          >
            <PhPencilSimple :size="16" />
          </button>
          <button
            @click="confirmDeleteSong(song)"
            class="p-2 rounded-lg text-zinc-400 hover:text-rose-400 hover:bg-rose-500/10 transition-colors cursor-pointer"
            title="Удалить песню из каталога"
          >
            <PhTrash :size="16" />
          </button>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <EmptyState
      v-else
      :title="searchQuery ? 'Песня не найдена' : 'Библиотека песен пуста'"
      :description="searchQuery ? 'Попробуйте изменить поисковый запрос.' : 'Добавьте первую песню в фонотеку.'"
      :action-text="searchQuery ? 'Очистить поиск' : 'Добавить песню'"
      @action="searchQuery ? (searchQuery = '') : openCreateModal()"
    />

    <!-- Modals -->
    <SongModal
      :is-open="isModalOpen"
      :song="selectedSong"
      :is-loading="catalogStore.isActionLoading"
      @save="handleSaveSong"
      @close="isModalOpen = false"
    />

    <ConfirmModal
      :is-open="isDeleteModalOpen"
      title="Удаление песни"
      :message="`Вы действительно хотите удалить песню «${songToDelete?.title}»? Она будет исключена из всех связанных альбомов.`"
      :is-loading="catalogStore.isActionLoading"
      @confirm="handleDeleteSong"
      @close="isDeleteModalOpen = false"
    />
  </div>
</template>

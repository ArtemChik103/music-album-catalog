<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter, RouterLink } from 'vue-router'
import { useCatalogStore } from '../stores/catalogStore'
import AddTrackModal from '../components/AddTrackModal.vue'
import AlbumModal from '../components/AlbumModal.vue'
import ConfirmModal from '../components/ConfirmModal.vue'
import EmptyState from '../components/EmptyState.vue'
import {
  PhArrowLeft,
  PhDisc,
  PhPlus,
  PhPencilSimple,
  PhTrash,
  PhMusicNotes,
  PhCalendar,
  PhUser,
  PhPlayCircle,
  PhStack
} from '@phosphor-icons/vue'

const route = useRoute()
const router = useRouter()
const catalogStore = useCatalogStore()

const albumId = computed(() => route.params.id)
const album = computed(() => catalogStore.currentAlbum)

const isAddTrackOpen = ref(false)
const isEditAlbumOpen = ref(false)
const isDeleteAlbumOpen = ref(false)
const isDeleteTrackOpen = ref(false)
const trackToDelete = ref(null)

onMounted(async () => {
  try {
    await Promise.all([
      catalogStore.fetchAlbumDetail(albumId.value),
      catalogStore.fetchArtists(),
      catalogStore.fetchSongs()
    ])
  } catch (err) {
    router.push('/')
  }
})

const openAddTrackModal = () => {
  isAddTrackOpen.value = true
}

const handleAddTrack = async (data) => {
  try {
    await catalogStore.addTrackToAlbum(albumId.value, {
      song_id: data.song_id,
      song_title: data.song_title,
      track_number: data.track_number
    })
    isAddTrackOpen.value = false
  } catch (err) {
    // Error toast handled in store
  }
}

const confirmDeleteTrack = (track) => {
  trackToDelete.value = track
  isDeleteTrackOpen.value = true
}

const handleDeleteTrack = async () => {
  if (!trackToDelete.value) return
  try {
    await catalogStore.removeTrackFromAlbum(albumId.value, trackToDelete.value.id)
    isDeleteTrackOpen.value = false
    trackToDelete.value = null
  } catch (err) {
    // Handled in store
  }
}

const handleSaveAlbum = async (data) => {
  try {
    await catalogStore.updateAlbum(data.id, {
      title: data.title,
      artist_id: data.artist_id,
      release_year: data.release_year
    })
    isEditAlbumOpen.value = false
  } catch (err) {
    // Handled in store
  }
}

const handleDeleteAlbum = async () => {
  try {
    await catalogStore.deleteAlbum(albumId.value)
    isDeleteAlbumOpen.value = false
    router.push('/')
  } catch (err) {
    // Handled in store
  }
}

// Check other albums for a song
const getOtherAlbumsForSong = (songId) => {
  const found = catalogStore.songs.find((s) => s.id === songId)
  if (!found || !found.albums) return []
  return found.albums.filter((a) => a.album_id !== Number(albumId.value))
}
</script>

<template>
  <div class="space-y-6">
    <!-- Back to Catalog Link -->
    <div>
      <RouterLink
        to="/"
        class="inline-flex items-center gap-1.5 text-xs font-medium text-zinc-400 hover:text-amber-400 transition-colors"
      >
        <PhArrowLeft :size="14" />
        <span>Вернуться к каталогу альбомов</span>
      </RouterLink>
    </div>

    <!-- Album Hero Section -->
    <div
      v-if="album"
      class="relative overflow-hidden rounded-2xl bg-zinc-900 border border-zinc-800 p-6 md:p-8"
    >
      <div class="relative z-10 flex flex-col md:flex-row items-start md:items-center gap-6">
        <!-- Vinyl Record Graphic Icon -->
        <div class="relative w-28 h-28 sm:w-36 sm:h-36 rounded-2xl bg-gradient-to-br from-amber-950/40 via-zinc-900 to-zinc-950 border border-amber-500/20 flex items-center justify-center shadow-2xl shrink-0">
          <PhDisc :size="64" weight="duotone" class="text-amber-500 animate-spin-slow" />
          <div class="absolute inset-0 rounded-2xl border border-white/5 pointer-events-none"></div>
        </div>

        <!-- Meta Info -->
        <div class="flex-1 space-y-2">
          <div class="flex items-center gap-2">
            <span class="text-xs font-mono uppercase px-2 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/20">
              Музыкальный альбом
            </span>
            <span class="text-xs text-zinc-400 flex items-center gap-1">
              <PhCalendar :size="13" />
              {{ album.release_year }} год
            </span>
          </div>

          <h1 class="text-2xl sm:text-3xl font-bold tracking-tight text-zinc-100">
            {{ album.title }}
          </h1>

          <div class="flex items-center gap-3 text-sm text-zinc-300">
            <span class="flex items-center gap-1.5 font-medium text-amber-400">
              <PhUser :size="16" />
              {{ album.artist?.name }}
            </span>
            <span class="text-zinc-600">·</span>
            <span class="flex items-center gap-1.5 text-zinc-400">
              <PhMusicNotes :size="16" />
              {{ album.tracks?.length || 0 }} треков
            </span>
          </div>
        </div>

        <!-- Actions -->
        <div class="flex items-center gap-2 self-stretch md:self-auto justify-end pt-4 md:pt-0 border-t md:border-t-0 border-zinc-800">
          <button
            @click="openAddTrackModal"
            class="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-lg bg-amber-500 hover:bg-amber-400 text-zinc-950 text-sm font-semibold transition-all active:scale-[0.98] shadow-md shadow-amber-500/10 cursor-pointer"
          >
            <PhPlus :size="16" weight="bold" />
            <span>Добавить трек</span>
          </button>
          <button
            @click="isEditAlbumOpen = true"
            class="p-2 rounded-lg bg-zinc-800 hover:bg-zinc-700/80 border border-zinc-700 text-zinc-300 transition-colors active:scale-95 cursor-pointer"
            title="Редактировать альбом"
          >
            <PhPencilSimple :size="17" />
          </button>
          <button
            @click="isDeleteAlbumOpen = true"
            class="p-2 rounded-lg bg-zinc-800 hover:bg-rose-500/10 border border-zinc-700 hover:border-rose-500/30 text-zinc-400 hover:text-rose-400 transition-colors active:scale-95 cursor-pointer"
            title="Удалить альбом"
          >
            <PhTrash :size="17" />
          </button>
        </div>
      </div>
    </div>

    <!-- Tracklist Section -->
    <div class="rounded-2xl bg-zinc-900/60 border border-zinc-800/80 p-6">
      <div class="flex items-center justify-between pb-4 mb-2 border-b border-zinc-800">
        <div>
          <h2 class="text-lg font-semibold text-zinc-100 flex items-center gap-2">
            <PhMusicNotes :size="20" class="text-amber-500" />
            <span>Треклист издания</span>
          </h2>
          <p class="text-xs text-zinc-400 mt-0.5">
            Порядковые номера песен строго упорядочены согласно спецификации альбома
          </p>
        </div>

        <button
          @click="openAddTrackModal"
          class="inline-flex items-center gap-1 text-xs text-amber-400 hover:text-amber-300 font-medium cursor-pointer"
        >
          <PhPlus :size="14" weight="bold" />
          <span>Добавить композицию</span>
        </button>
      </div>

      <!-- Tracks Table -->
      <div v-if="album?.tracks?.length > 0" class="overflow-x-auto">
        <table class="w-full text-left text-sm">
          <thead>
            <tr class="text-xs text-zinc-400 border-b border-zinc-800/60">
              <th class="py-3 px-3 w-16 text-center font-mono">#</th>
              <th class="py-3 px-4 font-medium">Название композиции</th>
              <th class="py-3 px-4 font-medium">Другие издания этой песни</th>
              <th class="py-3 px-4 w-20 text-right font-medium">Действие</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-zinc-800/40">
            <tr
              v-for="track in album.tracks"
              :key="track.id"
              class="group hover:bg-zinc-800/40 transition-colors"
            >
              <!-- Track Number -->
              <td class="py-3.5 px-3 text-center font-mono font-bold text-amber-400 text-sm">
                {{ track.track_number }}
              </td>

              <!-- Song Title -->
              <td class="py-3.5 px-4 font-medium text-zinc-100">
                <span class="hover:text-amber-300 transition-colors">
                  {{ track.song_title }}
                </span>
              </td>

              <!-- Other Albums where this song appears -->
              <td class="py-3.5 px-4 text-xs text-zinc-400">
                <div v-if="getOtherAlbumsForSong(track.song_id).length > 0" class="flex flex-wrap gap-1.5 items-center">
                  <RouterLink
                    v-for="other in getOtherAlbumsForSong(track.song_id)"
                    :key="other.album_id"
                    :to="`/albums/${other.album_id}`"
                    class="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-zinc-800/80 hover:bg-zinc-700 text-zinc-300 hover:text-amber-300 border border-zinc-700 transition-colors"
                    :title="`Также входит в ${other.album_title} под треком #${other.track_number}`"
                  >
                    <PhStack :size="12" class="text-amber-500" />
                    <span>{{ other.album_title }}</span>
                    <span class="font-mono text-[10px] text-amber-400">#{{ other.track_number }}</span>
                  </RouterLink>
                </div>
                <span v-else class="text-zinc-500 italic text-[11px]">
                  Только в этом издании
                </span>
              </td>

              <!-- Remove Track Button -->
              <td class="py-3.5 px-4 text-right">
                <button
                  @click="confirmDeleteTrack(track)"
                  class="p-1.5 rounded-lg text-zinc-500 hover:text-rose-400 hover:bg-rose-500/10 transition-colors opacity-80 group-hover:opacity-100 cursor-pointer"
                  title="Исключить трек из альбома"
                >
                  <PhTrash :size="15" />
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Empty Tracklist -->
      <EmptyState
        v-else
        title="В этом альбоме пока нет треков"
        description="Добавьте первую композицию с указанием порядкового номера."
        action-text="Добавить первый трек"
        @action="openAddTrackModal"
      />
    </div>

    <!-- Modals -->
    <AddTrackModal
      :is-open="isAddTrackOpen"
      :album="album"
      :available-songs="catalogStore.songs"
      :is-loading="catalogStore.isActionLoading"
      @add="handleAddTrack"
      @close="isAddTrackOpen = false"
    />

    <AlbumModal
      :is-open="isEditAlbumOpen"
      :album="album"
      :artists="catalogStore.artists"
      :songs="catalogStore.songs"
      :is-loading="catalogStore.isActionLoading"
      @save="handleSaveAlbum"
      @close="isEditAlbumOpen = false"
    />

    <ConfirmModal
      :is-open="isDeleteAlbumOpen"
      title="Удаление альбома"
      :message="`Вы действительно хотите удалить альбом «${album?.title}»?`"
      :is-loading="catalogStore.isActionLoading"
      @confirm="handleDeleteAlbum"
      @close="isDeleteAlbumOpen = false"
    />

    <ConfirmModal
      :is-open="isDeleteTrackOpen"
      title="Исключение трека"
      :message="`Исключить трек #${trackToDelete?.track_number} «${trackToDelete?.song_title}» из этого альбома? Композиция сохранится в каталоге.`"
      :is-loading="catalogStore.isActionLoading"
      @confirm="handleDeleteTrack"
      @close="isDeleteTrackOpen = false"
    />
  </div>
</template>

<style scoped>
@keyframes spin-slow {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
.animate-spin-slow {
  animation: spin-slow 25s linear infinite;
}
</style>

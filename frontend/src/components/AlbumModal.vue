<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'
import { PhX, PhDisc, PhPlus, PhTrash, PhArrowsDownUp } from '@phosphor-icons/vue'

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  },
  album: {
    type: Object,
    default: null
  },
  artists: {
    type: Array,
    default: () => []
  },
  songs: {
    type: Array,
    default: () => []
  },
  isLoading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['save', 'createArtist', 'close'])

const title = ref('')
const artistId = ref('')
const isNewArtistMode = ref(false)
const newArtistName = ref('')
const releaseYear = ref(new Date().getFullYear())
const tracks = ref([])
const error = ref('')

watch(
  () => props.isOpen,
  (open) => {
    if (open) {
      error.value = ''
      isNewArtistMode.value = false
      newArtistName.value = ''

      if (props.album) {
        title.value = props.album.title || ''
        artistId.value = props.album.artist?.id || ''
        releaseYear.value = props.album.release_year || new Date().getFullYear()
        tracks.value = props.album.tracks?.map((t) => ({
          track_number: t.track_number,
          song_id: t.song_id,
          song_title: t.song_title
        })) || []
      } else {
        title.value = ''
        artistId.value = props.artists[0]?.id || ''
        releaseYear.value = new Date().getFullYear()
        tracks.value = [
          { track_number: 1, song_title: '', song_id: null },
          { track_number: 2, song_title: '', song_id: null }
        ]
      }
    }
  }
)

const addTrackRow = () => {
  const nextNum = tracks.value.length ? Math.max(...tracks.value.map((t) => Number(t.track_number) || 0)) + 1 : 1
  tracks.value.push({
    track_number: nextNum,
    song_title: '',
    song_id: null
  })
}

const removeTrackRow = (index) => {
  tracks.value.splice(index, 1)
}

const handleSubmit = () => {
  error.value = ''
  const trimmedTitle = title.value.trim()
  if (!trimmedTitle) {
    error.value = 'Название альбома обязательно для заполнения'
    return
  }

  const year = parseInt(releaseYear.value, 10)
  if (!year || year < 1900 || year > 2100) {
    error.value = 'Год выпуска должен быть в диапазоне от 1900 до 2100'
    return
  }

  let finalArtistId = artistId.value
  if (isNewArtistMode.value) {
    const trimmedArtist = newArtistName.value.trim()
    if (!trimmedArtist) {
      error.value = 'Укажите имя нового исполнителя'
      return
    }
  } else if (!finalArtistId) {
    error.value = 'Выберите исполнителя'
    return
  }

  // Validate tracks
  const seenNumbers = new Set()
  const seenSongs = new Set()
  const validTracks = []

  for (const t of tracks.value) {
    const tNum = parseInt(t.track_number, 10)
    const tTitle = t.song_title?.trim()

    if (!tTitle && !t.song_id) continue // skip empty rows

    if (!tNum || tNum < 1) {
      error.value = 'Номер каждого трека должен быть >= 1'
      return
    }

    if (seenNumbers.has(tNum)) {
      error.value = `Порядковый номер ${tNum} повторяется в треклисте`
      return
    }
    seenNumbers.add(tNum)

    const key = t.song_id ? `id:${t.song_id}` : `title:${tTitle.toLowerCase()}`
    if (seenSongs.has(key)) {
      error.value = 'Песня не может входить в один и тот же альбом дважды'
      return
    }
    seenSongs.add(key)

    validTracks.push({
      track_number: tNum,
      song_id: t.song_id || null,
      song_title: tTitle || undefined
    })
  }

  emit('save', {
    id: props.album?.id,
    title: trimmedTitle,
    artist_id: isNewArtistMode.value ? null : Number(finalArtistId),
    new_artist_name: isNewArtistMode.value ? newArtistName.value.trim() : null,
    release_year: year,
    tracks: validTracks
  })
}

const handleKeyDown = (e) => {
  if (e.key === 'Escape' && props.isOpen) {
    emit('close')
  }
}

onMounted(() => window.addEventListener('keydown', handleKeyDown))
onUnmounted(() => window.removeEventListener('keydown', handleKeyDown))
</script>

<template>
  <Teleport to="body">
    <div
      v-if="isOpen"
      class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm overflow-y-auto"
      @click.self="emit('close')"
    >
      <div class="w-full max-w-xl rounded-2xl bg-zinc-900 border border-zinc-800 p-6 shadow-2xl relative my-8">
        <button
          @click="emit('close')"
          class="absolute top-4 right-4 p-1 rounded-lg text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800 transition-colors"
        >
          <PhX :size="18" />
        </button>

        <div class="flex items-center gap-3 mb-5">
          <div class="w-9 h-9 rounded-xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400">
            <PhDisc :size="20" weight="duotone" />
          </div>
          <div>
            <h3 class="text-base font-semibold text-zinc-100">
              {{ album ? 'Редактировать альбом' : 'Добавить новый альбом' }}
            </h3>
            <p class="text-xs text-zinc-400">Каталогизация издания и состава треков</p>
          </div>
        </div>

        <form @submit.prevent="handleSubmit" class="space-y-4">
          <!-- Title -->
          <div>
            <label class="block text-xs font-medium text-zinc-300 mb-1.5">
              Название альбома <span class="text-amber-500">*</span>
            </label>
            <input
              v-model="title"
              type="text"
              required
              placeholder="Например, The Dark Side of the Moon"
              class="w-full px-3.5 py-2.5 rounded-lg bg-zinc-950 border border-zinc-700 text-sm text-zinc-100 placeholder-zinc-500 focus:outline-none focus:ring-1 focus:ring-amber-500 focus:border-amber-500"
            />
          </div>

          <!-- Artist & Year Grid -->
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div class="sm:col-span-2">
              <div class="flex items-center justify-between mb-1.5">
                <label class="block text-xs font-medium text-zinc-300">
                  Исполнитель <span class="text-amber-500">*</span>
                </label>
                <button
                  type="button"
                  @click="isNewArtistMode = !isNewArtistMode"
                  class="text-[11px] text-amber-400 hover:underline cursor-pointer"
                >
                  {{ isNewArtistMode ? 'Выбрать из списка' : '+ Новый артист' }}
                </button>
              </div>

              <input
                v-if="isNewArtistMode"
                v-model="newArtistName"
                type="text"
                placeholder="Имя нового исполнителя"
                class="w-full px-3.5 py-2.5 rounded-lg bg-zinc-950 border border-amber-500/50 text-sm text-zinc-100 placeholder-zinc-500 focus:outline-none focus:ring-1 focus:ring-amber-500"
              />
              <select
                v-else
                v-model="artistId"
                class="w-full px-3.5 py-2.5 rounded-lg bg-zinc-950 border border-zinc-700 text-sm text-zinc-100 focus:outline-none focus:ring-1 focus:ring-amber-500"
              >
                <option value="" disabled>Выберите артиста</option>
                <option v-for="a in artists" :key="a.id" :value="a.id">
                  {{ a.name }}
                </option>
              </select>
            </div>

            <div>
              <label class="block text-xs font-medium text-zinc-300 mb-1.5">
                Год выпуска <span class="text-amber-500">*</span>
              </label>
              <input
                v-model.number="releaseYear"
                type="number"
                min="1900"
                max="2100"
                required
                class="w-full px-3.5 py-2.5 rounded-lg bg-zinc-950 border border-zinc-700 text-sm text-zinc-100 focus:outline-none focus:ring-1 focus:ring-amber-500"
              />
            </div>
          </div>

          <!-- Tracklist Builder (optional on create/edit) -->
          <div class="pt-2 border-t border-zinc-800">
            <div class="flex items-center justify-between mb-2">
              <label class="text-xs font-medium text-zinc-300 flex items-center gap-1.5">
                <PhArrowsDownUp :size="14" />
                <span>Треклист альбома (номер и композиция)</span>
              </label>
              <button
                type="button"
                @click="addTrackRow"
                class="inline-flex items-center gap-1 text-xs text-amber-400 hover:text-amber-300 font-medium cursor-pointer"
              >
                <PhPlus :size="14" weight="bold" />
                <span>Добавить строку</span>
              </button>
            </div>

            <div class="space-y-2 max-h-56 overflow-y-auto pr-1">
              <div
                v-for="(t, idx) in tracks"
                :key="idx"
                class="flex items-center gap-2 p-1.5 rounded-lg bg-zinc-950 border border-zinc-800"
              >
                <input
                  v-model.number="t.track_number"
                  type="number"
                  min="1"
                  placeholder="#"
                  title="Порядковый номер в альбоме"
                  class="w-14 px-2 py-1.5 rounded bg-zinc-900 border border-zinc-700 text-xs text-center text-zinc-200 font-mono focus:outline-none focus:border-amber-500"
                />
                <input
                  v-model="t.song_title"
                  type="text"
                  placeholder="Название песни"
                  class="flex-1 px-2.5 py-1.5 rounded bg-zinc-900 border border-zinc-700 text-xs text-zinc-100 placeholder-zinc-500 focus:outline-none focus:border-amber-500"
                />
                <button
                  type="button"
                  @click="removeTrackRow(idx)"
                  class="p-1.5 rounded text-zinc-500 hover:text-rose-400 hover:bg-zinc-800 transition-colors"
                  title="Удалить строку"
                >
                  <PhTrash :size="14" />
                </button>
              </div>

              <div v-if="tracks.length === 0" class="text-xs text-zinc-500 py-3 text-center italic">
                Нет добавленных треков. Вы сможете добавить их позже на странице альбома.
              </div>
            </div>
          </div>

          <!-- Error notice -->
          <p v-if="error" class="text-xs text-rose-400 mt-1">{{ error }}</p>

          <div class="pt-3 border-t border-zinc-800 flex items-center justify-end gap-3">
            <button
              type="button"
              @click="emit('close')"
              class="px-4 py-2 rounded-lg border border-zinc-700 bg-zinc-800 hover:bg-zinc-700/80 text-zinc-200 text-sm font-medium transition-all active:scale-[0.98] cursor-pointer"
            >
              Отмена
            </button>
            <button
              type="submit"
              :disabled="isLoading"
              class="px-5 py-2 rounded-lg bg-amber-500 hover:bg-amber-400 text-zinc-950 text-sm font-semibold transition-all active:scale-[0.98] disabled:opacity-50 cursor-pointer shadow-md shadow-amber-500/10"
            >
              {{ isLoading ? 'Сохранение...' : (album ? 'Сохранить изменения' : 'Создать альбом') }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { PhX, PhPlus, PhHash } from '@phosphor-icons/vue'

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  },
  album: {
    type: Object,
    default: null
  },
  availableSongs: {
    type: Array,
    default: () => []
  },
  isLoading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['add', 'close'])

const trackNumber = ref(1)
const mode = ref('existing') // 'existing' | 'new'
const selectedSongId = ref('')
const newSongTitle = ref('')
const error = ref('')

const nextAvailableNumber = computed(() => {
  if (!props.album?.tracks?.length) return 1
  const numbers = props.album.tracks.map((t) => t.track_number)
  return Math.max(...numbers) + 1
})

watch(
  () => props.isOpen,
  (open) => {
    if (open) {
      trackNumber.value = nextAvailableNumber.value
      mode.value = props.availableSongs.length > 0 ? 'existing' : 'new'
      selectedSongId.value = props.availableSongs[0]?.id || ''
      newSongTitle.value = ''
      error.value = ''
    }
  }
)

const handleSubmit = () => {
  error.value = ''
  const tNum = parseInt(trackNumber.value, 10)
  if (!tNum || tNum < 1) {
    error.value = 'Номер трека должен быть 1 или больше'
    return
  }

  // Check duplicate track number in album
  if (props.album?.tracks?.some((t) => t.track_number === tNum)) {
    error.value = `Трек с номером ${tNum} уже существует в этом альбоме`
    return
  }

  if (mode.value === 'existing') {
    if (!selectedSongId.value) {
      error.value = 'Выберите песню из списка'
      return
    }
    // Check if song already in album
    if (props.album?.tracks?.some((t) => t.song_id === Number(selectedSongId.value))) {
      error.value = 'Эта песня уже присутствует в данном альбоме'
      return
    }
    emit('add', {
      albumId: props.album.id,
      song_id: Number(selectedSongId.value),
      track_number: tNum
    })
  } else {
    const trimmed = newSongTitle.value.trim()
    if (!trimmed) {
      error.value = 'Введите название песни'
      return
    }
    if (props.album?.tracks?.some((t) => t.song_title.toLowerCase() === trimmed.toLowerCase())) {
      error.value = 'Песня с таким названием уже есть в этом альбоме'
      return
    }
    emit('add', {
      albumId: props.album.id,
      song_title: trimmed,
      track_number: tNum
    })
  }
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
      class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm"
      @click.self="emit('close')"
    >
      <div class="w-full max-w-md rounded-2xl bg-zinc-900 border border-zinc-800 p-6 shadow-2xl relative">
        <button
          @click="emit('close')"
          class="absolute top-4 right-4 p-1 rounded-lg text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800 transition-colors"
        >
          <PhX :size="18" />
        </button>

        <div class="flex items-center gap-3 mb-5">
          <div class="w-9 h-9 rounded-xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400">
            <PhPlus :size="20" weight="bold" />
          </div>
          <div>
            <h3 class="text-base font-semibold text-zinc-100">Добавить трек в альбом</h3>
            <p class="text-xs text-zinc-400">{{ album?.title }}</p>
          </div>
        </div>

        <form @submit.prevent="handleSubmit" class="space-y-4">
          <!-- Track Number -->
          <div>
            <label class="block text-xs font-medium text-zinc-300 mb-1.5 flex items-center gap-1.5">
              <PhHash :size="14" />
              <span>Порядковый номер трека</span>
            </label>
            <input
              v-model.number="trackNumber"
              type="number"
              min="1"
              required
              class="w-full px-3.5 py-2.5 rounded-lg bg-zinc-950 border border-zinc-700 text-sm text-zinc-100 focus:outline-none focus:ring-1 focus:ring-amber-500 focus:border-amber-500"
            />
          </div>

          <!-- Mode switch tabs -->
          <div>
            <label class="block text-xs font-medium text-zinc-300 mb-1.5">Выбор композиции</label>
            <div class="grid grid-cols-2 p-1 rounded-lg bg-zinc-950 border border-zinc-800 gap-1 text-xs">
              <button
                type="button"
                @click="mode = 'existing'"
                class="py-1.5 rounded-md font-medium transition-all"
                :class="mode === 'existing' ? 'bg-zinc-800 text-amber-400 shadow-sm' : 'text-zinc-400 hover:text-zinc-200'"
              >
                Существующая песня
              </button>
              <button
                type="button"
                @click="mode = 'new'"
                class="py-1.5 rounded-md font-medium transition-all"
                :class="mode === 'new' ? 'bg-zinc-800 text-amber-400 shadow-sm' : 'text-zinc-400 hover:text-zinc-200'"
              >
                Создать новую песню
              </button>
            </div>
          </div>

          <!-- Existing song select -->
          <div v-if="mode === 'existing'">
            <label class="block text-xs font-medium text-zinc-300 mb-1.5">Песня из каталога</label>
            <select
              v-model="selectedSongId"
              class="w-full px-3.5 py-2.5 rounded-lg bg-zinc-950 border border-zinc-700 text-sm text-zinc-100 focus:outline-none focus:ring-1 focus:ring-amber-500 focus:border-amber-500"
            >
              <option value="" disabled>Выберите песню</option>
              <option
                v-for="s in availableSongs"
                :key="s.id"
                :value="s.id"
              >
                {{ s.title }} (в {{ s.albums_count || 0 }} альб.)
              </option>
            </select>
          </div>

          <!-- New song input -->
          <div v-else>
            <label class="block text-xs font-medium text-zinc-300 mb-1.5">Название новой песни</label>
            <input
              v-model="newSongTitle"
              type="text"
              placeholder="Например, Stairway to Heaven"
              class="w-full px-3.5 py-2.5 rounded-lg bg-zinc-950 border border-zinc-700 text-sm text-zinc-100 placeholder-zinc-500 focus:outline-none focus:ring-1 focus:ring-amber-500 focus:border-amber-500"
            />
          </div>

          <!-- Validation error -->
          <p v-if="error" class="text-xs text-rose-400 mt-1">{{ error }}</p>

          <div class="pt-2 flex items-center justify-end gap-3">
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
              class="px-4 py-2 rounded-lg bg-amber-500 hover:bg-amber-400 text-zinc-950 text-sm font-semibold transition-all active:scale-[0.98] disabled:opacity-50 cursor-pointer shadow-md shadow-amber-500/10"
            >
              {{ isLoading ? 'Добавление...' : 'Добавить трек' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </Teleport>
</template>

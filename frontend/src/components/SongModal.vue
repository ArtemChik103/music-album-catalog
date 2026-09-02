<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'
import { PhX, PhMusicNotes } from '@phosphor-icons/vue'

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  },
  song: {
    type: Object,
    default: null
  },
  isLoading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['save', 'close'])

const title = ref('')
const error = ref('')

watch(
  () => props.isOpen,
  (open) => {
    if (open) {
      title.value = props.song ? props.song.title : ''
      error.value = ''
    }
  }
)

const handleSubmit = () => {
  const trimmed = title.value.trim()
  if (!trimmed) {
    error.value = 'Название песни обязательно для заполнения'
    return
  }
  error.value = ''
  emit('save', { id: props.song?.id, title: trimmed })
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
            <PhMusicNotes :size="20" weight="duotone" />
          </div>
          <h3 class="text-base font-semibold text-zinc-100">
            {{ song ? 'Редактировать песню' : 'Новая песня' }}
          </h3>
        </div>

        <form @submit.prevent="handleSubmit" class="space-y-4">
          <div>
            <label class="block text-xs font-medium text-zinc-300 mb-1.5">
              Название песни
            </label>
            <input
              v-model="title"
              type="text"
              autofocus
              placeholder="Например, Bohemian Rhapsody"
              class="w-full px-3.5 py-2.5 rounded-lg bg-zinc-950 border text-sm text-zinc-100 placeholder-zinc-500 focus:outline-none focus:ring-1 focus:ring-amber-500 transition-colors"
              :class="error ? 'border-rose-500 ring-1 ring-rose-500' : 'border-zinc-700 focus:border-amber-500'"
            />
            <p v-if="error" class="text-xs text-rose-400 mt-1">{{ error }}</p>
          </div>

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
              {{ isLoading ? 'Сохранение...' : (song ? 'Сохранить' : 'Добавить') }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </Teleport>
</template>

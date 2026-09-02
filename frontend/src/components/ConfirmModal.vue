<script setup>
import { onMounted, onUnmounted } from 'vue'
import { PhWarning, PhX } from '@phosphor-icons/vue'

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  },
  title: {
    type: String,
    default: 'Подтверждение удаления'
  },
  message: {
    type: String,
    default: 'Вы уверены, что хотите удалить эту запись? Действие нельзя отменить.'
  },
  confirmText: {
    type: String,
    default: 'Удалить'
  },
  isLoading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['confirm', 'close'])

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

        <div class="flex items-start gap-4">
          <div class="w-10 h-10 rounded-xl bg-rose-500/10 border border-rose-500/20 flex items-center justify-center text-rose-400 shrink-0">
            <PhWarning :size="22" weight="fill" />
          </div>
          <div class="flex-1">
            <h3 class="text-base font-semibold text-zinc-100 mb-1.5">{{ title }}</h3>
            <p class="text-sm text-zinc-400 leading-relaxed">{{ message }}</p>
          </div>
        </div>

        <div class="mt-6 flex items-center justify-end gap-3">
          <button
            type="button"
            @click="emit('close')"
            :disabled="isLoading"
            class="px-4 py-2 rounded-lg border border-zinc-700 bg-zinc-800 hover:bg-zinc-700/80 text-zinc-200 text-sm font-medium transition-all active:scale-[0.98] cursor-pointer"
          >
            Отмена
          </button>
          <button
            type="button"
            @click="emit('confirm')"
            :disabled="isLoading"
            class="px-4 py-2 rounded-lg bg-rose-600 hover:bg-rose-500 text-white text-sm font-medium transition-all active:scale-[0.98] disabled:opacity-50 cursor-pointer"
          >
            {{ isLoading ? 'Удаление...' : confirmText }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

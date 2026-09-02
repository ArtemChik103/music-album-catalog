<script setup>
import { PhMusicNotesPlus } from '@phosphor-icons/vue'

defineProps({
  title: {
    type: String,
    default: 'Записей не найдено'
  },
  description: {
    type: String,
    default: 'Попробуйте изменить параметры поиска или добавьте новый элемент.'
  },
  actionText: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['action'])
</script>

<template>
  <div class="flex flex-col items-center justify-center p-12 text-center rounded-2xl border border-dashed border-zinc-800 bg-zinc-900/40 my-6">
    <div class="w-14 h-14 rounded-2xl bg-zinc-900 border border-zinc-800 flex items-center justify-center text-zinc-400 mb-4 shadow-inner">
      <slot name="icon">
        <PhMusicNotesPlus :size="28" />
      </slot>
    </div>
    <h3 class="text-base font-semibold text-zinc-200 mb-1.5">{{ title }}</h3>
    <p class="text-sm text-zinc-400 max-w-sm mb-5 leading-relaxed">{{ description }}</p>
    <button
      v-if="actionText"
      @click="emit('action')"
      class="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-amber-500 hover:bg-amber-400 text-zinc-950 text-sm font-semibold transition-all active:scale-[0.98] shadow-md shadow-amber-500/10 cursor-pointer"
    >
      {{ actionText }}
    </button>
  </div>
</template>

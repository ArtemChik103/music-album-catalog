<script setup>
import { computed } from 'vue'
import { RouterLink } from 'vue-router'
import { PhDisc, PhPencilSimple, PhTrash, PhMusicNotes } from '@phosphor-icons/vue'

const props = defineProps({
  album: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['edit', 'delete'])

// Palette tints based on string hash for unique album sleeves
const palettes = [
  { bg: 'from-amber-950/40 to-zinc-900', border: 'border-amber-500/30', accent: 'text-amber-400', groove: 'rgba(245, 158, 11, 0.15)' },
  { bg: 'from-blue-950/40 to-zinc-900', border: 'border-blue-500/30', accent: 'text-blue-400', groove: 'rgba(59, 130, 246, 0.15)' },
  { bg: 'from-emerald-950/40 to-zinc-900', border: 'border-emerald-500/30', accent: 'text-emerald-400', groove: 'rgba(16, 185, 129, 0.15)' },
  { bg: 'from-rose-950/40 to-zinc-900', border: 'border-rose-500/30', accent: 'text-rose-400', groove: 'rgba(244, 63, 94, 0.15)' },
  { bg: 'from-indigo-950/40 to-zinc-900', border: 'border-indigo-500/30', accent: 'text-indigo-400', groove: 'rgba(99, 102, 241, 0.15)' },
  { bg: 'from-teal-950/40 to-zinc-900', border: 'border-teal-500/30', accent: 'text-teal-400', groove: 'rgba(20, 184, 166, 0.15)' },
]

const palette = computed(() => {
  const hash = (props.album.title + props.album.artist?.name)
    .split('')
    .reduce((acc, char) => acc + char.charCodeAt(0), 0)
  return palettes[hash % palettes.length]
})
</script>

<template>
  <div class="group relative flex flex-col rounded-xl bg-zinc-900 border border-zinc-800/80 hover:border-zinc-700 transition-all duration-200 overflow-hidden hover:shadow-xl hover:shadow-black/40">
    <!-- Vinyl Sleeve Artwork Header -->
    <RouterLink
      :to="`/albums/${album.id}`"
      class="relative aspect-square w-full overflow-hidden bg-gradient-to-br flex items-center justify-center p-6 select-none"
      :class="palette.bg"
    >
      <!-- Concentric Vinyl Grooves Graphic -->
      <div class="absolute inset-0 flex items-center justify-center opacity-35 group-hover:opacity-50 transition-opacity duration-300 pointer-events-none">
        <svg viewBox="0 0 200 200" class="w-full h-full p-4 transform group-hover:rotate-12 transition-transform duration-700">
          <circle cx="100" cy="100" r="88" fill="none" stroke="currentColor" stroke-width="1.5" :stroke="palette.groove" />
          <circle cx="100" cy="100" r="76" fill="none" stroke="currentColor" stroke-width="1.5" :stroke="palette.groove" />
          <circle cx="100" cy="100" r="64" fill="none" stroke="currentColor" stroke-width="1.5" :stroke="palette.groove" />
          <circle cx="100" cy="100" r="52" fill="none" stroke="currentColor" stroke-width="1.5" :stroke="palette.groove" />
          <circle cx="100" cy="100" r="40" fill="none" stroke="currentColor" stroke-width="1.5" :stroke="palette.groove" />
          <!-- Vinyl Center Label -->
          <circle cx="100" cy="100" r="28" fill="#18181b" stroke="#3f3f46" stroke-width="1.5" />
          <circle cx="100" cy="100" r="8" fill="#27272a" />
        </svg>
      </div>

      <!-- Disc Icon in Center -->
      <div class="relative z-10 w-16 h-16 rounded-full bg-zinc-950/80 border border-zinc-700/60 backdrop-blur-sm flex items-center justify-center shadow-lg group-hover:scale-105 transition-transform duration-200" :class="palette.accent">
        <PhDisc :size="32" weight="duotone" />
      </div>

      <!-- Release Year Badge -->
      <div class="absolute top-3 right-3 z-10 px-2 py-0.5 rounded text-[11px] font-mono font-medium bg-zinc-950/80 text-zinc-300 border border-zinc-800 backdrop-blur-sm">
        {{ album.release_year }}
      </div>
    </RouterLink>

    <!-- Info & Actions Footer -->
    <div class="p-4 flex flex-col flex-1 justify-between gap-3">
      <div>
        <RouterLink :to="`/albums/${album.id}`" class="block">
          <h3 class="text-base font-semibold text-zinc-100 group-hover:text-amber-400 transition-colors line-clamp-1" :title="album.title">
            {{ album.title }}
          </h3>
        </RouterLink>
        <p class="text-sm text-zinc-400 font-medium line-clamp-1 mt-0.5">
          {{ album.artist?.name || 'Неизвестный исполнитель' }}
        </p>
      </div>

      <div class="pt-2 border-t border-zinc-800/80 flex items-center justify-between">
        <span class="inline-flex items-center gap-1.5 text-xs text-zinc-400">
          <PhMusicNotes :size="14" />
          <span>{{ album.tracks_count || 0 }} треков</span>
        </span>

        <div class="flex items-center gap-1">
          <button
            @click.stop="emit('edit', album)"
            class="p-1.5 rounded-lg text-zinc-400 hover:text-zinc-100 hover:bg-zinc-800 transition-colors active:scale-95"
            title="Редактировать альбом"
          >
            <PhPencilSimple :size="15" />
          </button>
          <button
            @click.stop="emit('delete', album)"
            class="p-1.5 rounded-lg text-zinc-400 hover:text-rose-400 hover:bg-rose-500/10 transition-colors active:scale-95"
            title="Удалить альбом"
          >
            <PhTrash :size="15" />
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

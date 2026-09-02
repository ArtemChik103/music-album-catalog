<script setup>
import { computed } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { useCatalogStore } from '../stores/catalogStore'
import {
  PhDisc,
  PhUsers,
  PhMusicNotes,
  PhBookOpen,
  PhRecord
} from '@phosphor-icons/vue'

const route = useRoute()
const catalogStore = useCatalogStore()

const stats = computed(() => catalogStore.stats)

const navLinks = [
  { to: '/', name: 'albums', label: 'Альбомы', icon: PhDisc, count: () => stats.value.total_albums },
  { to: '/artists', name: 'artists', label: 'Исполнители', icon: PhUsers, count: () => stats.value.total_artists },
  { to: '/songs', name: 'songs', label: 'Песни', icon: PhMusicNotes, count: () => stats.value.total_songs },
]
</script>

<template>
  <header class="sticky top-0 z-40 w-full border-b border-zinc-800/80 bg-zinc-950/80 backdrop-blur-md">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
      <!-- Logo & Brand -->
      <RouterLink to="/" class="flex items-center gap-2.5 group">
        <div class="w-9 h-9 rounded-full bg-zinc-900 border border-zinc-700 flex items-center justify-center text-amber-500 group-hover:border-amber-500/50 transition-colors">
          <PhRecord :size="22" weight="fill" class="animate-spin-slow" />
        </div>
        <div class="flex flex-col">
          <span class="text-base font-semibold tracking-tight text-zinc-100 flex items-center gap-1.5">
            VinylLog
            <span class="text-[10px] uppercase font-mono px-1.5 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/20">SDD</span>
          </span>
          <span class="text-[11px] text-zinc-400">Музыкальный каталог</span>
        </div>
      </RouterLink>

      <!-- Desktop Navigation -->
      <nav class="flex items-center gap-1 sm:gap-2">
        <RouterLink
          v-for="link in navLinks"
          :key="link.to"
          :to="link.to"
          class="flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-medium transition-all"
          :class="route.name === link.name || (link.name === 'albums' && route.name === 'album-detail')
            ? 'bg-zinc-800 text-zinc-100 shadow-sm border border-zinc-700'
            : 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900'"
        >
          <component :is="link.icon" :size="18" />
          <span>{{ link.label }}</span>
          <span
            v-if="link.count() > 0"
            class="text-xs px-1.5 py-0.2 rounded-full font-mono bg-zinc-900 text-zinc-400 border border-zinc-800"
          >
            {{ link.count() }}
          </span>
        </RouterLink>

        <!-- API Docs link -->
        <a
          href="/api/docs/"
          target="_blank"
          rel="noopener noreferrer"
          class="hidden md:flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm text-zinc-400 hover:text-amber-400 hover:bg-zinc-900 transition-colors"
          title="Интерактивная спецификация OpenAPI Swagger"
        >
          <PhBookOpen :size="18" />
          <span>OpenAPI</span>
        </a>
      </nav>
    </div>
  </header>
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
  animation: spin-slow 20s linear infinite;
}
</style>

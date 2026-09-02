<script setup>
import { useCatalogStore } from './stores/catalogStore'
import Navbar from './components/Navbar.vue'
import { PhCheckCircle, PhWarningCircle, PhX } from '@phosphor-icons/vue'

const catalogStore = useCatalogStore()
</script>

<template>
  <div class="min-h-screen flex flex-col bg-zinc-950 text-zinc-100 selection:bg-amber-500/20 selection:text-amber-400">
    <!-- Navbar -->
    <Navbar />

    <!-- Main Content Area -->
    <main class="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 py-8">
      <RouterView :key="$route.fullPath" />
    </main>

    <!-- Global Toast Notification -->
    <Teleport to="body">
      <Transition
        enter-active-class="transform ease-out duration-300 transition"
        enter-from-class="translate-y-2 opacity-0 sm:translate-y-0 sm:translate-x-2"
        enter-to-class="translate-y-0 opacity-100 sm:translate-x-0"
        leave-active-class="transition ease-in duration-200"
        leave-from-class="opacity-100"
        leave-to-class="opacity-0"
      >
        <div
          v-if="catalogStore.toast"
          class="fixed bottom-5 right-5 z-50 flex items-center gap-3 px-4 py-3 rounded-xl shadow-2xl border backdrop-blur-md text-sm font-medium"
          :class="catalogStore.toast.type === 'error'
            ? 'bg-rose-950/90 text-rose-200 border-rose-800/80 shadow-rose-950/50'
            : 'bg-zinc-900/95 text-zinc-100 border-zinc-700/80 shadow-black/60'"
        >
          <component
            :is="catalogStore.toast.type === 'error' ? PhWarningCircle : PhCheckCircle"
            :size="20"
            weight="fill"
            :class="catalogStore.toast.type === 'error' ? 'text-rose-400' : 'text-amber-400'"
          />
          <span>{{ catalogStore.toast.message }}</span>
          <button
            @click="catalogStore.toast = null"
            class="p-1 -mr-1 rounded-lg text-zinc-400 hover:text-zinc-200 transition-colors"
          >
            <PhX :size="14" />
          </button>
        </div>
      </Transition>
    </Teleport>

    <!-- Footer -->
    <footer class="border-t border-zinc-800/80 bg-zinc-950 py-6 text-xs text-zinc-500">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 flex flex-col sm:flex-row items-center justify-between gap-3 text-center sm:text-left">
        <div class="flex items-center gap-2">
          <span class="font-semibold text-zinc-400">VinylLog</span>
          <span>·</span>
          <span>Разработано по методологии SDD (Specification-Driven Development)</span>
        </div>
        <div class="flex items-center gap-4">
          <a href="/api/docs/" target="_blank" class="hover:text-amber-400 transition-colors">Swagger UI</a>
          <a href="/api/redoc/" target="_blank" class="hover:text-amber-400 transition-colors">ReDoc</a>
          <a href="/api/schema/" target="_blank" class="hover:text-amber-400 transition-colors">OpenAPI YAML</a>
        </div>
      </div>
    </footer>
  </div>
</template>

import { createRouter, createWebHistory } from 'vue-router'
import AlbumsView from '../views/AlbumsView.vue'
import AlbumDetailView from '../views/AlbumDetailView.vue'
import ArtistsView from '../views/ArtistsView.vue'
import SongsView from '../views/SongsView.vue'

const routes = [
  {
    path: '/',
    name: 'albums',
    component: AlbumsView,
    meta: { title: 'Альбомы' }
  },
  {
    path: '/albums/:id',
    name: 'album-detail',
    component: AlbumDetailView,
    meta: { title: 'Альбом' }
  },
  {
    path: '/artists',
    name: 'artists',
    component: ArtistsView,
    meta: { title: 'Исполнители' }
  },
  {
    path: '/songs',
    name: 'songs',
    component: SongsView,
    meta: { title: 'Песни' }
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.afterEach((to) => {
  document.title = `${to.meta.title || 'Каталог'} — VinylLog`
})

export default router

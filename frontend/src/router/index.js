import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/login',
    name: 'login',
    component: () => import('../views/LoginView.vue'),
    meta: { public: true },
  },
  {
    path: '/',
    redirect: '/products',
  },
  {
    path: '/products',
    name: 'products',
    component: () => import('../views/ProductManage.vue'),
  },
  {
    path: '/publish',
    name: 'publish',
    component: () => import('../views/PlaceholderView.vue'),
  },
  {
    path: '/accounts',
    name: 'accounts',
    component: () => import('../views/PlaceholderView.vue'),
  },
  {
    path: '/settings',
    name: 'settings',
    component: () => import('../views/PlaceholderView.vue'),
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 路由守卫：未登录跳转登录页
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  if (!to.meta.public && !token) {
    next('/login')
  } else if (to.path === '/login' && token) {
    next('/')
  } else {
    next()
  }
})

export default router

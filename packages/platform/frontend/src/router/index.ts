/**
 * Vue Router 配置
 */
import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'
import { useUserStore } from '@/stores'

const routes: RouteRecordRaw[] = [
  // 公共路由
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/LoginView.vue'),
    meta: { requiresAuth: false },
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/RegisterView.vue'),
    meta: { requiresAuth: false },
  },

  // 技能市场（无需登录即可浏览）
  {
    path: '/marketplace',
    name: 'Marketplace',
    component: () => import('@/layouts/MainLayout.vue'),
    meta: { requiresAuth: false },
    children: [
      {
        path: '',
        component: () => import('@/views/MarketplaceView.vue'),
      },
      {
        path: ':id',
        name: 'MarketplaceSkillDetail',
        component: () => import('@/views/MarketplaceSkillDetailView.vue'),
      },
    ],
  },

  // 主布局路由
  {
    path: '/',
    component: () => import('@/layouts/MainLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'Dashboard',
        component: () => import('@/views/DashboardView.vue'),
      },
      {
        path: 'skills',
        name: 'Skills',
        component: () => import('@/views/SkillsView.vue'),
      },
      {
        path: 'skills/:id',
        name: 'SkillDetail',
        component: () => import('@/views/SkillDetailView.vue'),
      },
      {
        path: 'skill-creator',
        name: 'SkillCreator',
        component: () => import('@/views/SkillCreatorView.vue'),
      },
      {
        path: 'agents',
        name: 'Agents',
        component: () => import('@/views/AgentsView.vue'),
      },
      {
        path: 'agents/:id',
        name: 'AgentDetail',
        component: () => import('@/views/AgentDetailView.vue'),
      },
      {
        path: 'monitoring',
        name: 'Monitoring',
        component: () => import('@/views/MonitoringView.vue'),
      },
      {
        path: 'monitoring/projects/:id',
        name: 'MonitoringProjectDetail',
        component: () => import('@/views/MonitoringProjectDetailView.vue'),
      },
    ],
  },

  // 404 页面
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFoundView.vue'),
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const userStore = useUserStore()

  // 初始化用户信息
  if (!userStore.user && userStore.token) {
    userStore.initialize()
  }

  const requiresAuth = to.meta.requiresAuth !== false // 默认需要认证

  if (requiresAuth && !userStore.isAuthenticated) {
    // 需要认证但未登录，跳转到登录页
    next({ name: 'Login', query: { redirect: to.fullPath } })
  } else if (!requiresAuth && userStore.isAuthenticated && (to.name === 'Login' || to.name === 'Register')) {
    // 已登录用户访问登录/注册页，跳转到仪表板
    next({ name: 'Dashboard' })
  } else {
    next()
  }
})

export default router

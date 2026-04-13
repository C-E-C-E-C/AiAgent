import { createRouter, createWebHistory } from 'vue-router';
import LoginView from '../views/LoginView.vue';
import HomeView from '../views/HomeView.vue';
import GetMapView from '../views/GetMapView.vue';
import AiChatView from '../views/AiChatView.vue';
import ElmView from '../views/ElmView.vue';
import DeptView from '../views/DeptView.vue';
import UserView from '../views/UserView.vue';
import RoleView from '../views/RoleView.vue';
import { clearAuthStorage } from '../utils/authStorage';
import { validateBackendLogin } from '../utils/authApi';
const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      alias: '/login',
      name: 'login',
      component: LoginView,
    },
    {
      path: '/home',
      name: 'home',
      component: HomeView,
      meta: { requiresAuth: true },
    },
    {
      path:'/getmap',
      name: 'getmap',
      component:GetMapView,
      meta: { requiresAuth: true }
    },
    {
      path: '/aichat',
      name: 'aichat',
      component: AiChatView,
      meta: { requiresAuth: true }
    },
    {
      path:'/elm',
      name:'elm',
      component: ElmView,
      meta: { requiresAuth: true }
    },
    {
      path:'/dept',
      name:'dept',
      component: DeptView,
      meta: { requiresAuth: true }
    },
    {
      path:'/user',
      name:'user',
      component: UserView,
      meta: { requiresAuth: true }
    },
    {
      path:'/role',
      name:'role',
      component: RoleView,
      meta: { requiresAuth: true }
    }
  ],
});

router.beforeEach(async (to) => {
  const token = localStorage.getItem('sa-token');
  
  if (to.meta.requiresAuth && !token) {
    return { name: 'login' };
  }

  if (to.meta.requiresAuth && token) {
    const isValid = await validateBackendLogin(token);
    if (!isValid) {
      clearAuthStorage();
      return { name: 'login' };
    }
  }

  if (to.name === 'login' && token) {
    const isValid = await validateBackendLogin(token);
    if (!isValid) {
      clearAuthStorage();
      return true;
    }
    return { name: 'home' };
  }
  return true;
});

export default router;

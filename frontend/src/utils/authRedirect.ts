import { ElMessage } from 'element-plus';
import router from '../router';
import { clearAuthStorage } from './authStorage';

export function forceLogout(message = '登录已失效，请重新登录') {
  clearAuthStorage();
  ElMessage.error(message);

  if (router.currentRoute.value.name !== 'login') {
    router.replace({ name: 'login' });
  }
}
import { validateBackendLogin } from './authApi';
import { forceLogout } from './authRedirect';

export async function authRequest(input: RequestInfo | URL, init: RequestInit = {}) {
  const token = localStorage.getItem('sa-token');

  if (!token) {
    forceLogout('登录已失效，请重新登录');
    throw new Error('登录已失效');
  }

  const isValid = await validateBackendLogin(token);
  if (!isValid) {
    forceLogout('登录已失效，请重新登录');
    throw new Error('登录已失效');
  }

  const headers = new Headers(init.headers || {});
  headers.set('Authorization', [Bearer ${token}](http://_vscodecontentref_/10));

  const response = await fetch(input, {
    ...init,
    headers,
  });

  if (response.status === 401) {
    forceLogout('登录已失效，请重新登录');
    throw new Error('登录已失效');
  }

  return response;
}
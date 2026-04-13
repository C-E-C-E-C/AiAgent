export const AUTH_STORAGE_KEYS = {
  token: 'sa-token',
  username: 'username',
  role: 'user-role',
  perms: 'user-perms',
};

export function clearAuthStorage() {
  localStorage.removeItem(AUTH_STORAGE_KEYS.token);
  localStorage.removeItem(AUTH_STORAGE_KEYS.username);
  localStorage.removeItem(AUTH_STORAGE_KEYS.role);
  localStorage.removeItem(AUTH_STORAGE_KEYS.perms);
}
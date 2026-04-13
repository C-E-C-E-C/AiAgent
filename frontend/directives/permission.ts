import type { DirectiveBinding } from 'vue';

function getPerms(): string[] {
  try {
    return JSON.parse(localStorage.getItem('user-perms') || '[]');
  } catch {
    return [];
  }
}

function hasPermission(permission: string): boolean {
  const perms = getPerms();
  return perms.includes(permission);
}

export default {
  mounted(el: HTMLElement, binding: DirectiveBinding<string | string[]>) {
    const value = binding.value;
    const requiredPerms = Array.isArray(value) ? value : [value];
    const allowed = requiredPerms.some(permission => hasPermission(permission));

    if (!allowed) {
      el.parentNode?.removeChild(el);
    }
  }
};
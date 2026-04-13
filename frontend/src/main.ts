import { createApp } from 'vue';
import App from './App.vue';
import router from './router';

import TDesign from 'tdesign-vue-next'
import TDesignChat from '@tdesign-vue-next/chat'
import 'tdesign-vue-next/es/style/index.css'
import '@tdesign-vue-next/chat/es/style/index.css'

import ElementPlus from 'element-plus'

import 'element-plus/dist/index.css'
import permission from '../directives/permission';
import { forceLogout } from './utils/authRedirect';

const originalFetch = window.fetch.bind(window);

window.fetch = async (input, init) => {
	const response = await originalFetch(input, init);

	try {
		const requestUrl = typeof input === 'string' ? input : input instanceof URL ? input.href : input.url;
		const resolvedUrl = new URL(requestUrl, window.location.href);

		if (resolvedUrl.origin === 'http://localhost:8080' && (response.status === 401 || response.status === 403)) {
			forceLogout(response.status === 403 ? '你的权限已变更，请重新登录' : '登录已失效，请重新登录');
		}
	} catch {
		// Ignore malformed URLs and non-backend requests.
	}

	return response;
};


createApp(App).use(router).use(TDesign).use(TDesignChat).use(ElementPlus).directive('permission', permission).mount('#app');

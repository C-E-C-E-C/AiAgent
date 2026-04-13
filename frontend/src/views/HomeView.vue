<template>
  <t-layout style="height: 100vh">
    <t-head-menu v-model="menu1Value" theme="light" @change="changeHandler">
      <template #logo>
        <img height="28" src="https://tdesign.gtimg.com/site/baseLogo-light.png" alt="logo" />
      </template>
      <!-- <t-menu-item value="item1"> 菜单1 </t-menu-item>
      <t-menu-item value="item2"> 菜单2 </t-menu-item>
      <t-menu-item value="item4" :disabled="true"> 禁用菜单 </t-menu-item> -->
      <template #operations>
        <t-button variant="text" shape="square">
          <template #icon><t-icon name="search" /></template>
        </t-button>
        <t-button variant="text" shape="square">
          <template #icon><t-icon name="mail" /></template>
        </t-button>
        <t-button variant="text" shape="square">
          <template #icon><t-icon name="user" /></template>
        </t-button>
         <t-dropdown :options="options" @click="clickHandler">
            <t-button theme="default" variant="outline" shape="square">
                <t-icon name="ellipsis" size="16" />
            </t-button>
    </t-dropdown>
       
      </template>
    </t-head-menu>
    <t-layout>
      <t-aside style="border-top: 1px solid var(--component-border)">
        <t-menu v-model = "activeMenu" theme="light" value="dashboard" style="margin-right: 50px" height="550px" @change="changeHandler">
          <!-- <t-menu-item value="aichat">
            <template #icon>
              <t-icon name="dashboard" />
            </template>
            智能体对话
          </t-menu-item>
          <t-menu-item value="getmap">
            <template #icon>
              <t-icon name="server" />
            </template>
            智能旅行地图
          </t-menu-item>
          <t-menu-item value="control-platform">
            <template #icon>
              <t-icon name="control-platform" />
            </template>
            调度平台
          </t-menu-item>
          <t-menu-item value="precise-monitor">
            <template #icon>
              <t-icon name="precise-monitor" />
            </template>
            精准监控
          </t-menu-item>
          <t-menu-item value="mail">
            <template #icon>
              <t-icon name="mail" />
            </template>
            消息区
          </t-menu-item>
          <t-menu-item value="user-circle">
            <template #icon>
              <t-icon name="user-circle" />
            </template>
            个人资料
          </t-menu-item> -->

          <t-menu-item v-for="item in visibleMenus" 
          :key = "item.value"
          :value = "item.value"
          >
          <template #icon>
            <t-icon :name="item.icon"></t-icon>
          </template>
          {{ item.label }}
          </t-menu-item>
        </t-menu>
      </t-aside>
      <t-layout style="height:100vh;overflow-y: auto;">
        <t-content>
            <component :is="currentComponent" />
        </t-content>
      </t-layout>
    </t-layout>
  </t-layout>
</template>

<script setup>
import { useRouter } from 'vue-router';

import { computed, ref } from 'vue';
import { clearAuthStorage } from '../utils/authStorage';

import getmap from './GetMapView.vue';
import aichat from './AiChatView.vue';
import elm from './ElmView.vue';
import dept from './DeptView.vue';
import user from './UserView.vue';
import role from './RoleView.vue';

const menuList = [
  { value: 'aichat', label: '智能体对话', icon: 'chat', roles: ['admin', 'operator','sales'] },
  { value: 'getmap', label: '智能旅行地图', icon: 'map', roles: ['admin', 'operator', 'sales'] },
  { value: 'elm', label: '员工管理', icon: 'control-platform', roles: ['admin','sales'] },
  { value: 'dept', label: '部门管理', icon: 'user', roles: ['admin', 'hr'] },
  { value: 'user', label: '用户管理', icon: 'user', roles: ['admin'] },
  { value: 'role', label: '角色管理', icon: 'user-setting', roles: ['admin'] },
  { value: 'precise-monitor', label: '精准监控', icon: 'precise-monitor', roles: ['admin'] },
  { value: 'mail', label: '消息区', icon: 'mail', roles: ['admin', 'operator', 'sales'] },
  { value: 'user-circle', label: '个人资料', icon: 'user-circle', roles: ['admin', 'operator', 'sales'] },
];

const router = useRouter();
const menu1Value = ref('item1');
const activeMenu = ref('getmap');

// 选项组
const options = ref([
  { content: '个人中心', value: 'profile' },
  { content: '设置', value: 'settings' },
  { content: '退出登录', value: 'logout' },
]);

const clickHandler = (value) => {
  console.log('value:',value.value);
  
  if (value.value === 'logout') {
    console.log('执行退出登录');
    
    islogout();
  } else {
    console.log('Clicked option:', value);
  }
};

// 获取用户角色
const userRole = localStorage.getItem('user-role') || 'viewer'; 
console.log('用户角色:!!',userRole);


// 根据用户角色过滤菜单项
const visibleMenus = computed (()=>{
  return menuList.filter(item => item.roles.includes(userRole));
})


const islogout = async () => {
    try {
        const response = await fetch('http://localhost:8080/api/logout', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        const data = await response.json();
        console.log('Logout response:', data);
        if(data.msg == '退出成功'){
            console.log('Logout successful:', response);
          clearAuthStorage();
            //退出登录成功  跳转LoginView 
          await router.push({ name: 'login' });
        } else {
            console.error('Logout failed:', response.statusText);
        }
    } catch (error) {
        console.error('Logout error:', error);
    }
}

const componentsMap = {
  getmap,
  aichat,
  elm,
  dept,
  user,
  role,
}

const currentComponent = computed(() =>{
  return componentsMap[activeMenu.value] || aichat
});

const changeHandler = (value) => {
  activeMenu.value = value;
}
</script>
<style scoped>

</style>

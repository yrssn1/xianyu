<template>
  <!-- 登录页面不显示布局 -->
  <router-view v-if="route.path === '/login'" />

  <!-- 主布局 -->
  <a-layout v-else class="app-layout">
    <a-layout-sider v-model:collapsed="collapsed" :trigger="null" collapsible width="220">
      <div class="logo">
        <h2 v-if="!collapsed">闲鱼自动化</h2>
        <h2 v-else>鱼</h2>
      </div>
      <a-menu theme="dark" mode="inline" v-model:selectedKeys="selectedKeys" @click="handleMenuClick">
        <a-menu-item key="products">
          <template #icon><ShopOutlined /></template>
          <span>商品管理</span>
        </a-menu-item>
        <a-menu-item key="publish">
          <template #icon><SendOutlined /></template>
          <span>发布管理</span>
        </a-menu-item>
        <a-menu-item key="accounts">
          <template #icon><UserOutlined /></template>
          <span>账号管理</span>
        </a-menu-item>
        <a-menu-item key="settings">
          <template #icon><SettingOutlined /></template>
          <span>系统设置</span>
        </a-menu-item>
      </a-menu>
    </a-layout-sider>
    <a-layout>
      <a-layout-header class="app-header">
        <menu-unfold-outlined v-if="collapsed" class="trigger" @click="() => (collapsed = !collapsed)" />
        <menu-fold-outlined v-else class="trigger" @click="() => (collapsed = !collapsed)" />
        <div class="header-right">
          <a-dropdown>
            <a class="user-info" @click.prevent>
              <UserOutlined />
              <span style="margin-left: 6px">管理员</span>
            </a>
            <template #overlay>
              <a-menu>
                <a-menu-item key="logout" @click="handleLogout">
                  <LogoutOutlined />
                  <span style="margin-left: 6px">退出登录</span>
                </a-menu-item>
              </a-menu>
            </template>
          </a-dropdown>
        </div>
      </a-layout-header>
      <a-layout-content class="app-content">
        <router-view />
      </a-layout-content>
    </a-layout>
  </a-layout>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import {
  MenuUnfoldOutlined,
  MenuFoldOutlined,
  ShopOutlined,
  SendOutlined,
  UserOutlined,
  SettingOutlined,
  LogoutOutlined,
} from '@ant-design/icons-vue'

const router = useRouter()
const route = useRoute()
const collapsed = ref(false)
const selectedKeys = ref(['products'])

const handleMenuClick = ({ key }) => {
  router.push({ name: key })
}

const handleLogout = () => {
  localStorage.removeItem('token')
  router.push('/login')
}
</script>

<style>
body {
  margin: 0;
  padding: 0;
}

.app-layout {
  min-height: 100vh;
}

.logo {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
}

.logo h2 {
  margin: 0;
  color: #fff;
  font-size: 18px;
}

.app-header {
  background: #fff;
  padding: 0 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
}

.header-right {
  display: flex;
  align-items: center;
}

.user-info {
  color: #333;
  cursor: pointer;
}

.trigger {
  font-size: 18px;
  cursor: pointer;
  transition: color 0.3s;
}

.trigger:hover {
  color: #1890ff;
}

.app-content {
  margin: 24px;
  padding: 24px;
  background: #fff;
  border-radius: 8px;
  min-height: 280px;
}
</style>

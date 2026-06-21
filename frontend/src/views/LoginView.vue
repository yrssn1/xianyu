<template>
  <div class="login-container">
    <div class="login-card">
      <div class="login-header">
        <h1>闲鱼自动化系统</h1>
        <p>请登录以继续</p>
      </div>
      <a-form
        :model="formData"
        :rules="rules"
        ref="formRef"
        layout="vertical"
        @finish="handleLogin"
      >
        <a-form-item label="用户名" name="username">
          <a-input
            v-model:value="formData.username"
            placeholder="请输入用户名"
            size="large"
            :prefix="h(UserOutlined)"
          />
        </a-form-item>
        <a-form-item label="密码" name="password">
          <a-input-password
            v-model:value="formData.password"
            placeholder="请输入密码"
            size="large"
            :prefix="h(LockOutlined)"
          />
        </a-form-item>
        <a-form-item>
          <a-button type="primary" html-type="submit" :loading="loading" block size="large">
            登 录
          </a-button>
        </a-form-item>
      </a-form>
      <div class="login-footer">
        <span>默认账号：admin / admin123</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, h } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { UserOutlined, LockOutlined } from '@ant-design/icons-vue'
import { login } from '../api/auth'

const router = useRouter()
const formRef = ref(null)
const loading = ref(false)

const formData = reactive({
  username: '',
  password: '',
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

async function handleLogin() {
  loading.value = true
  try {
    const res = await login(formData)
    console.log('[Login] 响应:', res.data)
    localStorage.setItem('token', res.data.access_token)
    console.log('[Login] Token已存储:', localStorage.getItem('token'))
    message.success('登录成功')
    router.push('/')
  } catch (err) {
    const detail = err.response?.data?.detail || '登录失败'
    message.error(detail)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-card {
  width: 400px;
  padding: 40px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
}

.login-header {
  text-align: center;
  margin-bottom: 32px;
}

.login-header h1 {
  margin: 0 0 8px 0;
  font-size: 24px;
  color: #1a1a1a;
}

.login-header p {
  margin: 0;
  color: #666;
  font-size: 14px;
}

.login-footer {
  text-align: center;
  margin-top: 16px;
  color: #999;
  font-size: 12px;
}
</style>

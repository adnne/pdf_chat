<template>
<div class="login-container">
  <div class="login-card">
    <div class="card-content">
      <div class="logo-container mb-6">
        <h1 class="text-center font-bold text-5xl mb-3 text-white">PDF Chat</h1>
        <p class="text-center text-gray-300 text-lg">Sign in to your account</p>
      </div>
      <form @submit.prevent="login" class="flex flex-column gap-5">
        <div class="flex flex-column gap-2">
          <label for="email" class="font-medium text-gray-300 text-sm mb-1">Email</label>
          <InputText id="email" v-model="email" type="text" class="w-full custom-input" placeholder="Enter your email" required />
        </div>
        <div class="flex flex-column gap-2">
          <label for="password" class="font-medium text-gray-300 text-sm mb-1">Password</label>
          <InputText id="password" v-model="password" type="password" class="w-full custom-input" placeholder="Enter your password" required />
        </div>
        <small v-if="error" class="p-error mt-2 text-sm">{{ error }}</small>
        <Button type="submit" label="Sign In" class="w-full custom-button mt-2" :loading="loading" />
      </form>
    </div>
  </div>
</div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const email = ref<string>('')
const password = ref<string>('')
const error = ref<string>('')
const loading = ref<boolean>(false)

async function login(): Promise<void> {
  if (!email.value || !password.value) {
    error.value = 'Please enter both email and password'
    return
  }

  loading.value = true
  error.value = ''

  try {
    await authStore.login(email.value, password.value)
    // Redirect to dashboard is handled in the auth store
  } catch (err) {
    console.error('Login error:', err)
    error.value = err.response?.data?.detail || 'Invalid credentials. Please try again.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: #000000;
  color: #ffffff;
}

.login-card {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  padding: 3rem;
  width: 420px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
}

.card-content {
  width: 100%;
}

.custom-input {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  padding: 0.875rem;
  font-size: 1rem;
  color: #ffffff;
  transition: all 0.3s ease;
}

.custom-input:focus {
  border-color: #ffffff;
  box-shadow: 0 0 0 2px rgba(255, 255, 255, 0.1);
  outline: none;
}

.custom-input::placeholder {
  color: rgba(255, 255, 255, 0.5);
}

.custom-button {
  background: #ffffff;
  border: none;
  border-radius: 8px;
  padding: 0.875rem;
  font-weight: 600;
  font-size: 1rem;
  letter-spacing: 0.5px;
  color: #000000;
  transition: all 0.3s ease;
}

.custom-button:hover {
  background: rgba(255, 255, 255, 0.9);
  transform: translateY(-1px);
}

.custom-button:focus {
  box-shadow: 0 0 0 2px rgba(255, 255, 255, 0.2);
  outline: none;
}

.custom-button:active {
  transform: translateY(1px);
}
</style>
<template>
  <div class="app-container">
    <Toast />
    <router-view />
  </div>
</template>

<script setup>
// App.vue is the main component that contains the router view
</script>

<style>
/* Global styles */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body {
  height: 100%;
  width: 100%;
  font-family: var(--font-family);
  background-color: var(--surface-ground);
}

.app-container {
  height: 100vh;
  width: 100vw;
  display: flex;
  flex-direction: column;
}

/* Custom scrollbar styles */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: var(--surface-100);
}

::-webkit-scrollbar-thumb {
  background: var(--primary-300);
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: var(--primary-400);
}
</style>
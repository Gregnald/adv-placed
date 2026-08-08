<script setup>
import { computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';

const route = useRoute();
const router = useRouter();

const requestedPath = computed(() => route.fullPath || '/');

const goBack = () => {
  if (window.history.length > 1) {
    router.back();
  } else {
    router.push({ name: 'home' });
  }
};

const goHome = () => router.push({ name: 'home' });
</script>

<template>
  <div class="not-found">
    <div class="card">
      <h1>404</h1>
      <h2>Page not found</h2>
      <p>The page <strong>{{ requestedPath }}</strong> does not exist.</p>
      <div class="actions">
        <button class="btn btn-primary" @click="goBack">Go to previous page</button>
        <button class="btn btn-secondary" @click="goHome">Go to home</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.not-found {
  min-height: 100vh;
  display: grid;
  place-items: center;
  background: linear-gradient(135deg, #f8fafc, #eef2ff);
  padding: 24px;
}

.card {
  background: white;
  border-radius: 16px;
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.12);
  padding: 32px;
  text-align: center;
  max-width: 480px;
  width: 100%;
}

h1 {
  font-size: 4rem;
  margin: 0 0 8px;
  color: #1f2937;
}

h2 {
  margin: 0 0 12px;
  color: #374151;
}

p {
  color: #6b7280;
  margin-bottom: 24px;
}

.actions {
  display: flex;
  gap: 12px;
  justify-content: center;
  flex-wrap: wrap;
}

.btn {
  border: none;
  border-radius: 999px;
  padding: 10px 16px;
  cursor: pointer;
  font-weight: 600;
}

.btn-primary {
  background: #2563eb;
  color: white;
}

.btn-secondary {
  background: #e5e7eb;
  color: #111827;
}
</style>

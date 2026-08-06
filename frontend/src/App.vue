<script setup>
import { RouterView } from 'vue-router';
import Header from '@/components/Header.vue';
import Footer from '@/components/Footer.vue';
</script>

<template>
  <div class="app">
    <Header />

    <main class="content">
      <RouterView />
    </main>

    <Footer />
  </div>
</template>

<style scoped>
</style>

<script setup>
import { ref, onMounted } from 'vue';
import router from '@/router';
import AdminDashboard from '@/components/AdminDashboard.vue';
import CompanyDashboard from '@/components/CompanyDashboard.vue';
import StudentDashboard from '@/components/StudentDashboard.vue';

// const userType = ref(localStorage.getItem('userType') || 'admin');
const userType = ref('company')

onMounted(() => {
  const userID = localStorage.getItem('userID');
  if (!userID) router.push({ name: 'home' });
});
</script>

<template>
  <div class="dashboard-container">
    <AdminDashboard v-if="userType === 'admin'" />
    <CompanyDashboard v-if="userType === 'company'" />
    <StudentDashboard v-if="userType === 'student'" />
  </div>
</template>

<style scoped>
    .dashboard-container{
        display: flex;
        border-radius: 15px;
        flex-direction: column;
        background-color: whitesmoke;
        min-height: 75vh;
        width: 85%;
        padding: 30px;
        /* justify-content: center;
        align-items: center; */
    }
</style>
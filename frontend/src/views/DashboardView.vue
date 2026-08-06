<script setup>
    import { ref,onMounted } from 'vue';
    import router from '@/router';
    import AdminDashboard from '@/components/AdminDashboard.vue';
    import StudentDashboard from '@/components/StudentDashboard.vue';

    onMounted(() => {
        const userID = ref(localStorage.getItem("userID"));
        if(!userID.value)router.push({name:'home'})
    });

    const userType = ref('admin');
</script>

<template>
    <div class="dashboard-container">
        <AdminDashboard v-if="userType=='admin'"/>
        <StudentDashboard v-if="userType=='student'"/>
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
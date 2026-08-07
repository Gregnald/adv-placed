<script setup>
import { ref, onMounted } from 'vue';
import { RouterLink } from 'vue-router';

const userID = ref(localStorage.getItem('userID'));

const updateUserID = () => {
  userID.value = localStorage.getItem('userID');
};

onMounted(() => {
  window.addEventListener('user-storage-updated', updateUserID);
});
</script>
<template>
    <header>
        <a href="/">
            <img src="@/assets/iitm_logo.svg" alt="iitm_logo"/>
        </a>
        <h3>IITM Placement Portal</h3>
        <nav>
            <RouterLink class="nav-button" to="/">Home</RouterLink>
            <RouterLink v-if="userID" class="nav-button" to="/dashboard">Dashboard</RouterLink>
            <RouterLink v-if="!userID" class="nav-button" to="/login">Login</RouterLink>
            <RouterLink v-if="!userID" class="nav-button" to="/signup">Sign-up</RouterLink>
        </nav>
    </header>
</template>

<style scoped>
   header {
    position: fixed;
    display: flex;
    align-items: center;
    justify-content: space-between;
    background:white;
    height: max-content;
    width:100%;
    top: 0;
   }
    header img {
        width: 200px;
        height: auto;
        margin-left:20px;
        padding:10px 0px 10px 0px;
    }
    nav {
    display: flex;
    /* margin-right: 20px; */
    }
    .nav-button {
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 20px 15px;
        text-decoration: none;
        color: black;

        background: white;
    }

    .nav-button:hover {
        background-color: rgba(159, 159, 159, 0.276);
    }
    .router-link-active {
    background: rgba(159, 159, 159, 0.276);
    border-bottom: 4px inset rgba(159, 159, 159, 0.539);
}
</style>
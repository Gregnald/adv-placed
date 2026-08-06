<script setup>
import { ref } from "vue";

const year = ref("2026");
</script>

<template>
    <footer>
        <span>Copyright &copy; {{ year }}</span>
    </footer>
</template>

<style scoped>
footer {
    width: 100%;
    background: white;
    text-align: center;
    padding: 8px 0;
}

span {
    display: block;
}
</style>
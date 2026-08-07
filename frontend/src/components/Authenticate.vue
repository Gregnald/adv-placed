<script setup>
import { ref, defineProps, onMounted } from 'vue';
import router from '@/router';
import { api } from '@/services/api';

onMounted(() => {
    const sessionId = ref(localStorage.getItem('sessionId'));
    if(sessionId.value)router.push({name:'dashboard'})
});

const props = defineProps({
    // true for sign-ups
    registering:{
        type:Boolean,
        default:false,
    }
});

const user = ref('student');
const username = ref('');
const password = ref('');
const message = ref('');
const companyName = ref('');
const companyHRMail = ref('');

const changeUser = (newUser) => {
    user.value = newUser;
};


const handleSubmit = async function(){
    if(props.registering && user.value === 'admin'){
        message.value = "Can't sign-up as Admin";
        return;
    }
    if (!username.value || !password.value) {
        message.value = 'Please enter username and password.';
        return;
    }

    try {
        const payload = {
            username: username.value,
            password: password.value,
            role: user.value
        };

        if (user.value === 'company') {
            if (!companyName.value || !companyHRMail.value) {
                message.value = 'Please provide company name and HR mail.';
                return;
            }
            payload.companyName = companyName.value;
            payload.companyHRMail = companyHRMail.value;
        }

        const response = props.registering ? await api.register(payload) : await api.login(payload);
        localStorage.setItem('sessionId', response.sessionId || response.session?.sessionId || '');
        localStorage.removeItem('userID');
        localStorage.setItem('userType', response.user.role);
        if (response.user.role === 'company' && response.profile) {
            localStorage.setItem('companyName', response.profile.employer);
            localStorage.setItem('companyHRMail', response.profile.hr_mail);
        }
        window.dispatchEvent(new Event('user-storage-updated'));
        router.push({ name: 'dashboard' });
    } catch (error) {
        message.value = error.message || 'Something went wrong.';
    }
}
</script>

<template>
    <div class="form-container">
        <form v-on:submit.prevent="handleSubmit" class="auth-form">
            <h2 v-if="!registering">Login</h2> 
            <h2 v-else>Sign-up</h2> 
            <div id="user-btns">
            <button v-if="!registering" v-on:click.prevent="changeUser('admin')" :class="['user-btn',{active:user === 'admin'}]">Admin</button>
            <button v-on:click.prevent="changeUser('student')" :class="['user-btn',{active:user === 'student'}]">Student</button>
            <button v-on:click.prevent="changeUser('company')" :class="['user-btn',{active:user === 'company'}]">Company</button>
        </div>
            <div class="form-row">
                <label for="username">Username</label>
                <input v-model="username" id="username" type="text">
            </div>

            <div class="form-row">
                <label for="password">Password</label>
                <input v-model="password" id="password" type="password">
            </div>
            <div v-if="registering && user === 'company'" class="form-row">
                <label for="company-name">Company Name</label>
                <input v-model="companyName" id="company-name" type="text" />
            </div>
            <div v-if="registering && user === 'company'" class="form-row">
                <label for="hr-mail">HR Mail</label>
                <input v-model="companyHRMail" id="hr-mail" type="email" />
            </div>
            <div v-if="message" class="message error">
                {{ message }}
            </div>
            <button v-on:click="" type="submit" id="submit">Submit</button>
        </form>
    </div>
</template>

<style scoped>
    .jd-checkbox {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    white-space: nowrap;
    }

    .message{
        padding-bottom: 10px;
    }
    .success {
        color: green;
    }

    .error {
        color: red;
    }
    #user-btns{
        display: flex;
        width: 100%;
        justify-content: center;
        margin: -10px 0px 10px 0px;
    }
    .user-btn{
        border: none;
    }
    .user-btn:hover{
        cursor: pointer;
    }
    .user-btn.active{
        background-color: rgba(187, 187, 187, 0.464);
    }
    .form-container{
        min-height: 100%;
        display: flex;
        align-items: center;
        min-height: calc(100vh - 96px);
        justify-self: center;
    }
    .auth-form{
        margin-top: 20px;
        margin-bottom: 20px;
        background-color: whitesmoke;
        display: flex;
        flex-direction: column;
        width: auto;
        min-height: max-content;
        align-items: center;
        justify-content: center;
        padding: 0px 2% 1% 0%;
        border-radius: 5%;
        box-shadow: 15px 15px 10px;
    }
    .form-row {
        display: flex;
        align-items: center;
        margin-bottom: 15px;
    }

    label {
        width: 120px;
        text-align: right;
        margin-right: 20px;
    }

    input {
        width: 250px;
    }
    #submit{
        font-size: larger;
        font-family: 'Franklin Gothic Medium', 'Arial Narrow', Arial, sans-serif;
        padding: 2% 2%;
        margin-top: 1%;
        bottom: 0;
        border-radius: 12px;
        background-color: #A0322C;
        color:aliceblue;
    }
    #submit:hover{
        cursor: pointer;
        background-color: #be1c14;
    }
</style>
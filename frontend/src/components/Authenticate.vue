<script setup>
import {ref,computed,watch,defineProps,onMounted} from 'vue';
import JD from '@/components/JD.vue'
import router from '@/router';

onMounted(() => {
    const userID = ref(localStorage.getItem("userID"));
    if(userID.value)router.push({name:'dashboard'})
});

const props = defineProps({
    // true for sign-ups
    registering:{
        type:Boolean,
        default:false,
    }
});

const showJD = ref(false);
const user = ref('student');
const username = ref('');
const password = ref('');
const message = ref('');
const status = ref();
const jobRef = ref(null);

const changeUser = (newUser) => {
    user.value = newUser;
};

const linkJD = computed(function(){
    console.log(user.value=="company" && props.registering);
    return user.value=="company" && props.registering;
})

watch(linkJD, (newValue) => {
    showJD.value = newValue;
})

const handleSubmit = function(){
    if(props.registering && user.value=='admin'){
        message.value="Can't sign-up as Admin";
        console.log(message);
        return;
    }
    console.log(`registering = ${props.registering} user = ${user.value}`)
    console.log(`Username: ${username.value} Password: ${password.value}`)
    console.log(props.registering);
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
            <div v-if="message" :class="['message',status===200?'success':'error']">
                {{ message }}
            </div>
            <label v-if="linkJD" class="jd-checkbox">
                <input v-model="showJD" type="checkbox" />I want to add JD
            </label>
            <JD v-if="linkJD && showJD" :showJD="true" ref="jobRef"/>
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
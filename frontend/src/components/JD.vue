<script setup>
import { ref,defineProps } from 'vue';

const props = defineProps({
    showJD:{
        type: Boolean,
        default: false
    }
});

const jobTitle = ref('');
const jobDescription = ref('');
const jobCompensation = ref('');
const companyName = ref('');
const companyWebsite = ref('');
const hrMail = ref('');

function getJobData(){
    return [
        jobTitle,
        jobDescription,
        jobCompensation,
        companyName,
        companyWebsite,
        hrMail
    ];
}

defineExpose({
    getJobData
});

</script>

<template>
    <br/>
    <div v-if= "showJD" class="jd-form">
        <br/>
        <label for="job-title">Job Title</label><br/>
        <input required id="job-title" v-model="jobTitle" placeholder="Enter the Title"/><br/><br/>
        <hr>
        <br/>
        <label for="description-box">Job Description</label>
        <textarea required id="description-box" v-model="jobDescription" rows="5" cols="40" placeholder="Enter the description..."></textarea>
        <hr/>
        <br/>
        <label for="compensation">Compensation</label><br/>
        <textarea required id="compensation" v-model="jobCompensation" rows="5" cols="40" placeholder="Enter compensation details for the job..."></textarea>
        <hr>
        <br/>
        <label for="company-name">Company Name</label><br/>
        <input required id="company-name" v-model="companyName" placeholder="Enter company's name"/><br/><br/>
        <hr>
        <br/>
        <label for="company-website">Company Website</label><br/>
        <input required id="company-website" v-model="companyWebsite" placeholder="Enter wompany's website"/><br/><br/>
        <hr>
        <br/>
        <label for="hr-mail">HR Mail</label><br/>
        <input required id="hr-mail" v-model="hrMail" placeholder="Enter HR's mail"/><br/><br/>
        <hr>
        <br/>
    </div>
</template>

<style scoped>
    .jd-form{
        font-family: 'Gill Sans', 'Gill Sans MT', Calibri, 'Trebuchet MS', sans-serif;
        background-color: white;
        padding: 20px 25px;
        padding-top: 5px;
        border-radius: 15px;
        margin-left: 10px;
    }

    textarea{
        margin-top: 6px;
        width: 100%;
        resize: vertical;
        border: none;
    }

    :focus{
        outline: none;
    }

    input{
        margin-top: 6px;
        border: none;
    }
</style>
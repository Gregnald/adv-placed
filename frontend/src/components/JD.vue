<script setup>
import { ref,defineProps, onMounted } from 'vue';

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
const applicationDeadline = ref('');
const minCgpa = ref('');
const eligibleBranches = ref('');
const eligibleYears = ref('');
const startDate = ref('');
const endDate = ref('');

function getJobData(){
    return {
        jobTitle: jobTitle.value,
        jobDescription: jobDescription.value,
        jobCompensation: jobCompensation.value,
        companyName: companyName.value,
        companyWebsite: companyWebsite.value,
        hrMail: hrMail.value,
        applicationDeadline: applicationDeadline.value,
        minCgpa: minCgpa.value,
        eligibleBranches: eligibleBranches.value.split(',').map((branch) => branch.trim()).filter(Boolean),
        eligibleYears: eligibleYears.value.split(',').map((year) => year.trim()).filter(Boolean),
        startDate: startDate.value,
        endDate: endDate.value
    };
}

defineExpose({
    getJobData
});

onMounted(() => {
    const storedName = localStorage.getItem('companyName');
    const storedHR = localStorage.getItem('companyHRMail');
    if (storedName) companyName.value = storedName;
    if (storedHR) hrMail.value = storedHR;
});

</script>

<template>
    <div v-if="showJD" class="jd-form">
        <div class="form-row">
            <label for="job-title">Job Title</label>
            <input required id="job-title" v-model="jobTitle" placeholder="Enter the Title" />
        </div>
        <div class="form-row">
            <label for="description-box">Job Description</label>
            <textarea required id="description-box" v-model="jobDescription" rows="5" placeholder="Enter the description..."></textarea>
        </div>
        <div class="form-row">
            <label for="compensation">Compensation</label>
            <textarea required id="compensation" v-model="jobCompensation" rows="3" placeholder="Enter compensation details for the job..."></textarea>
        </div>
        <div class="form-row">
            <label for="start-date">Start Date</label>
            <input required type="date" id="start-date" v-model="startDate" />
        </div>
        <div class="form-row">
            <label for="end-date">End Date</label>
            <input required type="date" id="end-date" v-model="endDate" />
        </div>
        <div class="form-row">
            <label for="deadline">Application Deadline</label>
            <input required type="date" id="deadline" v-model="applicationDeadline" />
        </div>
        <div class="form-row">
            <label for="min-cgpa">Min CGPA</label>
            <input required type="number" id="min-cgpa" step="0.1" v-model="minCgpa" placeholder="e.g. 7.5" />
        </div>
        <div class="form-row">
            <label for="eligible-branches">Eligible Branches</label>
            <input id="eligible-branches" v-model="eligibleBranches" placeholder="e.g. CSE, ECE" />
        </div>
        <div class="form-row">
            <label for="eligible-years">Eligible Years</label>
            <input id="eligible-years" v-model="eligibleYears" placeholder="e.g. 3rd Year, 4th Year" />
        </div>
        <div class="form-row">
            <label for="company-name">Company Name</label>
            <input required id="company-name" v-model="companyName" placeholder="Enter company's name" />
        </div>
        <div class="form-row">
            <label for="company-website">Company Website</label>
            <input required id="company-website" v-model="companyWebsite" placeholder="Enter company's website" />
        </div>
        <div class="form-row">
            <label for="hr-mail">HR Mail</label>
            <input required id="hr-mail" v-model="hrMail" placeholder="Enter HR's mail" />
        </div>
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
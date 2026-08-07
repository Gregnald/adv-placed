<script setup>
import { ref, computed, onMounted } from 'vue';
import router from '@/router';
import dp from '@/assets/dp-placeholder.png';
import Companies from './Companies.vue';
import Drives from './Drives.vue';
import Students from './Students.vue';
import { api } from '@/services/api';

const companies = ref([]);
const students = ref([]);
const drives = ref([]);
const reports = ref({
  totalStudents: 0,
  totalCompanies: 0,
  totalDrives: 0,
  pendingCompanies: 0,
  rejectedDrives: 0,
  approvedDrives: 0,
  placedStudents: 0,
  blacklistedCompanies: 0,
  blacklistedStudents: 0
});

const user = ref({ name: '', userType: 'Admin' });
const selectedTab = ref('Companies');
const searchQuery = ref('');

const loadDashboard = async () => {
  const payload = await api.getAdminDashboard();
  user.value = payload.user || user.value;
  companies.value = payload.companies || [];
  students.value = payload.students || [];
  drives.value = payload.drives || [];
  reports.value = payload.reports || reports.value;
};

const componentTabs = { Companies, Drives, Students };
const tabs = ['Companies', 'Drives', 'Students', 'Reports'];

const currentTabComponent = computed(() => componentTabs[selectedTab.value] || null);

const reportStats = computed(() => reports.value);

const searchPlaceholder = computed(() => {
  if (selectedTab.value === 'Students') return 'Search students by name or enrollment…';
  if (selectedTab.value === 'Companies') return 'Search companies by name or HR mail…';
  if (selectedTab.value === 'Drives') return 'Search drives by ID or company…';
  return 'Search reports…';
});

onMounted(() => {
  loadDashboard().catch((err) => {logout(),router.push({ name: 'home' })});
});

const handleCompanyUpdated = async ({ companyName, payload }) => {
  await api.updateCompany(companyName, payload);
  await loadDashboard();
};

const handleStudentUpdated = async ({ enrollment, payload }) => {
  await api.updateStudent(enrollment, payload);
  await loadDashboard();
};

const handleDriveUpdated = async ({ driveId, payload }) => {
  await api.updateDrive(driveId, payload);
  await loadDashboard();
};

const logout = async () => {
  try {
    await api.logout();
  } finally {
    localStorage.removeItem('sessionId');
    localStorage.removeItem('userType');
    localStorage.removeItem('companyName');
    localStorage.removeItem('companyHRMail');
    await router.push({ name: 'home' });
    window.location.reload();
  }
};
</script>

<template>
  <div class="admin-dashboard">
    <div class="dash-head">
      <h1>Admin</h1>
      <button class="logout-button" @click="logout">Logout</button>
    </div>
    <hr>
    <div class="admin-info">
      <img :src="dp" alt="dp" id="profile-pic" />
      <div class="admin-header-text">
        <h2>{{ user.name }}</h2>
        <p class="admin-role">Administrator</p>
      </div>
    </div>
    <div class="admin-summary">
      <div class="summary-card">
        <h3>Total Students</h3>
        <p>{{ reportStats.totalStudents }}</p>
      </div>
      <div class="summary-card">
        <h3>Total Companies</h3>
        <p>{{ reportStats.totalCompanies }}</p>
      </div>
      <div class="summary-card">
        <h3>Total Drives</h3>
        <p>{{ reportStats.totalDrives }}</p>
      </div>
      <div class="summary-card">
        <h3>Pending Companies</h3>
        <p>{{ reportStats.pendingCompanies }}</p>
      </div>
    </div>

    <div class="data-container">
      <hr />
      <nav class="data-nav">
        <button
          v-for="tab in tabs"
          :key="tab"
          :class="['nav-btn', { active: selectedTab === tab }]"
          @click="selectedTab = tab"
        >
          {{ tab }}
        </button>
      </nav>
      <hr />
      <div class="admin-search" v-if="selectedTab !== 'Reports'">
        <input v-model="searchQuery" :placeholder="searchPlaceholder" />
      </div>
      <div class="tab-container">
        <component
          v-if="currentTabComponent"
          :is="currentTabComponent"
          :searchQuery="searchQuery"
          :companies="companies"
          :drives="drives"
          :students="students"
          @company-updated="handleCompanyUpdated"
          @student-updated="handleStudentUpdated"
          @drive-updated="handleDriveUpdated"
        />
        <div v-else class="reports-panel">
          <h2>Placement Reports</h2>
          <div class="reports-grid">
            <div class="report-card">
              <h4>Approved Drives</h4>
              <p>{{ reportStats.approvedDrives }}</p>
            </div>
            <div class="report-card">
              <h4>Rejected Drives</h4>
              <p>{{ reportStats.rejectedDrives }}</p>
            </div>
            <div class="report-card">
              <h4>Placed Students</h4>
              <p>{{ reportStats.placedStudents }}</p>
            </div>
            <div class="report-card">
              <h4>Blacklisted Companies</h4>
              <p>{{ reportStats.blacklistedCompanies }}</p>
            </div>
            <div class="report-card">
              <h4>Blacklisted Students</h4>
              <p>{{ reportStats.blacklistedStudents }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
  .dash-head {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 16px;
  }

  .admin-info {
    display: flex;
    align-items: center;
    justify-content: flex-start;
    gap: 16px;
    margin: 24px 0;
    flex-wrap: wrap;
  }

  .admin-info img {
    max-width: 100px;
    border-radius: 50%;
  }

  .admin-header-text h2 {
    margin: 0;
    font-size: 2rem;
  }

  .admin-role {
    margin: 4px 0 0;
    color: #666;
    font-weight: 600;
  }

  h1 {
    font-size: 3em;
  }

  .logout-button {
    border: none;
    background: #d32f2f;
    color: white;
    padding: 10px 16px;
    border-radius: 10px;
    cursor: pointer;
  }

  .logout-button:hover {
    background: #a12722;
  }

  hr {
    border: none;
    height: 2px;
    background: black;
    width: 100%;
  }

  .admin-summary {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 16px;
    margin-bottom: 20px;
  }

  .summary-card {
    background: #ffffff;
    border: 1px solid #e0e0e0;
    border-radius: 12px;
    padding: 16px;
    text-align: center;
  }

  .summary-card h3 {
    margin: 0 0 8px;
    font-size: 1rem;
    color: #444;
  }

  .summary-card p {
    margin: 0;
    font-size: 2rem;
    font-weight: 700;
    color: #1f8a21;
  }

  .data-container {
    margin: 1vh;
    min-height: 48vh;
  }

  .data-container hr {
    border: none;
    height: 1px;
    background: grey;
    width: 100%;
    opacity: 35%;
    margin: 0px;
  }

  .admin-search {
    margin: 18px 0;
  }

  .admin-search input {
    width: 100%;
    padding: 10px 14px;
    border-radius: 10px;
    border: 1px solid #ccc;
    font-size: 1rem;
  }

  .data-nav {
    display: flex;
    justify-content: space-around;
  }

  .nav-btn {
    border: none;
    padding: 0.5%;
    background: none;
    text-decoration: none;
    color: black;
  }

  .nav-btn.active {
    background-color: rgba(128, 128, 128, 0.192);
  }

  .nav-btn.active {
    background-color: rgba(128, 128, 128, 0.192);
  }

  .nav-btn:hover {
    cursor: pointer;
  }
</style>
<script setup>
import { ref, computed, onMounted } from 'vue';
import router from '@/router';
import dp from '@/assets/dp-placeholder.png';
import Companies from './Companies.vue';
import Drives from './Drives.vue';
import Students from './Students.vue';

const validationResp = () => ({ status: 200 });

const defaultUser = {
  name: 'John Doe',
  userType: 'Admin'
};

const companies = ref([
  { employer: 'Google Inc.', website: 'www.google.com', hr_mail: 'gmail', status: 'active', blacklisted: false },
  { employer: 'Apple Inc.', website: 'www.apple.com', hr_mail: 'apple_mail', status: 'requested', blacklisted: false },
  { employer: 'Microsoft Inc.', website: 'www.microsoft.com', hr_mail: 'M_mail', status: 'active', blacklisted: false },
  { employer: 'Skyroot', website: 'www.skyroot.com', hr_mail: 'sky_mail', status: 'denied', blacklisted: true }
]);

const students = ref([
  { enrollment: 'ENR001', name: 'Aisha Patel', course: 'MBA', status: 'active', blacklisted: false },
  { enrollment: 'ENR002', name: 'Rohan Singh', course: 'BTech', status: 'Placed', blacklisted: false },
  { enrollment: 'ENR003', name: 'Maya Rao', course: 'BBA', status: 'active', blacklisted: true },
  { enrollment: 'ENR004', name: 'Kabir Shah', course: 'MCA', status: 'active', blacklisted: false }
]);

const drives = ref([
  {
    driveId: 'DRV001',
    companyName: 'Google Inc.',
    startDate: '2026-09-01',
    endDate: '2026-09-10',
    studentsParticipating: 45,
    status: 'Approved',
    expanded: false
  },
  {
    driveId: 'DRV002',
    companyName: 'Microsoft Inc.',
    startDate: '2026-10-05',
    endDate: '2026-10-12',
    studentsParticipating: 32,
    status: 'Rejected',
    expanded: false
  },
  {
    driveId: 'DRV003',
    companyName: 'Skyroot',
    startDate: '2026-11-01',
    endDate: '2026-11-08',
    studentsParticipating: 12,
    status: 'Approved',
    expanded: false
  }
]);

const user = ref({ ...defaultUser, ...validationResp() });
const selectedTab = ref('Companies');
const searchQuery = ref('');

const componentTabs = { Companies, Drives, Students };
const tabs = ['Companies', 'Drives', 'Students', 'Reports'];

const currentTabComponent = computed(() => componentTabs[selectedTab.value] || null);

const reportStats = computed(() => ({
  totalStudents: students.value.length,
  totalCompanies: companies.value.length,
  totalDrives: drives.value.length,
  pendingCompanies: companies.value.filter((c) => c.status === 'requested').length,
  rejectedDrives: drives.value.filter((d) => d.status === 'Rejected').length,
  approvedDrives: drives.value.filter((d) => d.status === 'Approved').length,
  placedStudents: students.value.filter((s) => s.status.toLowerCase() === 'placed').length,
  blacklistedCompanies: companies.value.filter((c) => c.blacklisted).length,
  blacklistedStudents: students.value.filter((s) => s.blacklisted).length
}));

const searchPlaceholder = computed(() => {
  if (selectedTab.value === 'Students') return 'Search students by name or enrollment…';
  if (selectedTab.value === 'Companies') return 'Search companies by name or HR mail…';
  if (selectedTab.value === 'Drives') return 'Search drives by ID or company…';
  return 'Search reports…';
});

onMounted(() => {
  if (validationResp().status !== 200) router.push({ name: 'home' });
});
</script>

<template>
  <div class="admin-dashboard">
    <div class="dash-head"><h1>Admin</h1></div>
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
          :students="students"
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
    justify-content: center;
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
<script setup>
import { ref, computed, onMounted } from 'vue';
import router from '@/router';
import dp from '@/assets/dp-placeholder.png';
import StudentDrives from './StudentDrives.vue';
import StudentApplied from './StudentApplied.vue';
import { api } from '@/services/api';

const profile = ref({
  name: '',
  username: '',
  enrollment: '',
  firstName: '',
  surname: '',
  email: '',
  course: '',
  year: '',
  userType: 'Student',
  status: 'Active',
  resumeFileName: ''
});




const selectedResume = ref({
  fileName: '',
  file: null
});

const editingProfile = ref(false);
const selectedTab = ref('Drives');
const isBlacklisted = ref(false);

const tabs = {
  Drives: StudentDrives,
  Applied: StudentApplied
};

const allDrives = ref([]);

const getToday = () => {
  const t = new Date();
  t.setHours(0, 0, 0, 0);
  return t;
};

const today = getToday();

const activeDrives = computed(() =>
  allDrives.value
    .filter((drive) => drive.status === 'Approved')
    .map((drive) => ({
      ...drive,
      visibility: getDriveVisibility(drive)
    }))
);

const appliedDrives = computed(() =>
  allDrives.value.filter((drive) => drive.applied)
);

const loadDashboard = async () => {
  const payload = await api.getStudentDashboard();
  profile.value = { ...profile.value, ...(payload.profile || {}) };
  isBlacklisted.value = profile.value.blacklisted || false;
  if (isBlacklisted.value) return;
  selectedResume.value.fileName = profile.value.resumeFileName;
  allDrives.value = (payload.activeDrives || []).map((drive) => ({ ...drive, expanded: false }));
  const applied = payload.appliedDrives || [];
  const appliedMap = new Map(applied.map((drive) => [drive.driveId, drive]));
  allDrives.value = allDrives.value.map((drive) => ({
    ...drive,
    ...(appliedMap.get(drive.driveId) || {})
  }));
};

function getDriveVisibility(drive) {
  const start = new Date(drive.startDate);
  const end = new Date(drive.endDate);
  start.setHours(0, 0, 0, 0);
  end.setHours(0, 0, 0, 0);
  if (end < today) return 'Past';
  if (start > today) return 'Upcoming';
  return 'Active';
}

const toggleExpand = (driveId) => {
  allDrives.value = allDrives.value.map((drive) => {
    if (drive.driveId === driveId) {
      return { ...drive, expanded: !drive.expanded };
    }
    return drive;
  });
};

const handleResumeUpload = (event) => {
  const file = event.target.files?.[0];
  if (file) {
    selectedResume.value = { fileName: file.name, file };
    profile.value.resumeFileName = file.name;
  }
};

const applyToDrive = async (driveId) => {
  if (!profile.value.resumeFileName) return;
  await api.applyToDrive(driveId, {
    resumeFileName: profile.value.resumeFileName
  });
  await loadDashboard();
};

const saveProfile = async () => {
  await api.updateStudentProfile({
    name: profile.value.name,
    username: profile.value.username,
    enrollment: profile.value.enrollment,
    firstName: profile.value.firstName,
    surname: profile.value.surname,
    email: profile.value.email,
    course: profile.value.course,
    year: profile.value.year,
    status: profile.value.status,
    resumeFileName: profile.value.resumeFileName
  });
  editingProfile.value = false;
};




const toggleStatus = async () => {
  profile.value.status = profile.value.status === 'Active' ? 'Inactive' : 'Active';
  await api.updateStudentProfile({
    status: profile.value.status
  });
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

const exporting = ref(false);

const exportCurrentTab = async () => {
  exporting.value = true;
  try {
    const entity = selectedTab.value === 'Drives' ? 'student_active_drives' : 'student_applied_drives';
    const filename = selectedTab.value === 'Drives' ? 'active_drives.csv' : 'applied_drives.csv';
    await api.exportAndDownload(entity, '', filename);
  } catch (err) {
    alert('Failed to export CSV: ' + err.message);
  } finally {
    exporting.value = false;
  }
};

onMounted(() => {
  loadDashboard().catch(() => {
    allDrives.value = [];
  });
});
</script>


<template>
  <div class="student-dashboard">
    <div class="dash-head">
      <h1>Student</h1>
      <button class="logout-button" @click="logout">Logout</button>
    </div>
    <hr />

    <div v-if="isBlacklisted" class="blacklist-message">
      <div class="blacklist-container">
        <h2>Access Denied</h2>
        <p>You are blacklisted. Kindly contact the institution for more information.</p>
      </div>
    </div>

    <div v-if="!isBlacklisted" class="student-info">
      <img :src="dp" alt="profile" id="profile-pic" />
      <div class="profile-details">
        <div class="profile-row">
          <div>
            <h2>{{ profile.name || profile.username }}</h2>
            <p><strong>Username:</strong> {{ profile.username || 'N/A' }}</p>
            <p><strong>Enrollment:</strong> {{ profile.enrollment || 'N/A' }}</p>
            <p><strong>Email:</strong> {{ profile.email || 'N/A' }}</p>
            <p>{{ profile.course }}</p>
            <p>{{ profile.year }}</p>
            <p><strong>Latest Resume:</strong> {{ profile.resumeFileName || 'None uploaded' }}</p>
          </div>
          <div class="profile-badge-group">
            <button :class="['status-pill', { inactive: profile.status === 'Inactive' }]" @click="toggleStatus">
              {{ profile.status }}
            </button>
          </div>
        </div>

        <div v-if="editingProfile" class="edit-form">
          <label>First Name</label>
          <input v-model="profile.firstName" />
          <label>Surname</label>
          <input v-model="profile.surname" />
          <label>Enrollment</label>
          <input v-model="profile.enrollment" />
          <label>Email</label>
          <input v-model="profile.email" type="email" />
          <label>Course</label>
          <input v-model="profile.course" />
          <label>Year</label>
          <input v-model="profile.year" />
          <label>Upload Resume</label>
          <input type="file" @change="handleResumeUpload" />
          <div class="resume-file">Latest: {{ profile.resumeFileName || 'None' }}</div>
        </div>




        <button class="edit-button" @click="editingProfile = !editingProfile">
          {{ editingProfile ? 'Cancel' : 'Edit Profile' }}
        </button>
        <button v-if="editingProfile" class="save-button" @click="saveProfile">Save</button>
      </div>
    </div>

    <div v-if="!isBlacklisted" class="data-container">
      <hr />
      <nav class="data-nav">
        <button
          v-for="tab in Object.keys(tabs)"
          :key="tab"
          :class="['nav-btn', { active: selectedTab === tab }]"
          @click="selectedTab = tab"
        >
          {{ tab }}
        </button>
      </nav>
      <hr />
      <div class="action-bar">
        <button class="export-btn" :disabled="exporting" @click="exportCurrentTab">
          {{ exporting ? 'Exporting...' : 'Export CSV' }}
        </button>
      </div>



      <div class="tab-container">
        <component
          :is="tabs[selectedTab]"
          :drives="selectedTab === 'Drives' ? activeDrives : appliedDrives"
          :resumeFileName="profile.resumeFileName"
          :isStudentActive="profile.status === 'Active'"
          @apply="applyToDrive"
        />

        <div v-if="selectedTab === 'Drives' && !activeDrives.length" class="empty-state">No approved drives available.</div>
        <div v-if="selectedTab === 'Applied' && !appliedDrives.length" class="empty-state">No applied drives yet.</div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.student-dashboard {
  margin: 1vh;
  font-family: 'Times New Roman', Georgia, Times, serif;
}

.dash-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
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

.blacklist-message {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 60vh;
  background: linear-gradient(135deg, #f5f5f5 0%, #efefef 100%);
  border-radius: 10px;
  margin: 2vh;
}

.blacklist-container {
  text-align: center;
  padding: 40px;
  background: white;
  border-radius: 10px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  max-width: 500px;
}

.blacklist-container h2 {
  color: #d32f2f;
  font-size: 2em;
  margin: 0 0 16px 0;
}

.blacklist-container p {
  color: #666;
  font-size: 1.1em;
  margin: 0;
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
  margin: 0;
}

.student-info {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
  margin: 24px 0;
  flex-wrap: wrap;
}

#profile-pic {
  max-width: 120px;
  border-radius: 50%;
}

.profile-details {
  flex: 1;
  min-width: 280px;
}

.profile-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.profile-badge-group {
  display: flex;
  align-items: center;
  gap: 12px;
}

.profile-badge {
  background: rgba(31, 139, 33, 0.12);
  color: #1f8a21;
  border-radius: 24px;
  padding: 8px 14px;
  font-weight: 700;
}

.status-pill {
  border: 1px solid #1f8a21;
  background: #1f8a21;
  color: white;
  padding: 8px 14px;
  border-radius: 24px;
  font-weight: 700;
  cursor: pointer;
}

.status-pill:hover {
  background: #166f19;
}

.status-pill.inactive {
  background: #d32f2f;
  border-color: #d32f2f;
}

.status-pill.inactive:hover {
  background: #a12722;
}

.edit-button,
.save-button {
  border: none;
  background: #1f8a21;
  color: white;
  padding: 10px 16px;
  border-radius: 8px;
  margin-top: 16px;
  cursor: pointer;
}

.save-button {
  margin-left: 12px;
  background: #2d6cdf;
}

.edit-form {
  display: grid;
  gap: 10px;
  margin-top: 16px;
}

.edit-form label {
  font-weight: 600;
}

.edit-form input {
  width: 100%;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 8px;
}

.data-container {
  min-height: 48vh;
}

.data-container hr {
  border: none;
  height: 1px;
  background: grey;
  width: 100%;
  opacity: 35%;
  margin: 0;
}

.action-bar {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  margin: 12px 0;
}

.data-nav {
  display: flex;
  justify-content: space-around;
}

.export-btn {
  background: #2196f3;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  white-space: nowrap;
}

.export-btn:hover {
  background: #1976d2;
}

.export-btn:disabled {
  background: #90caf9;
  cursor: not-allowed;
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

.nav-btn:hover {
  cursor: pointer;
}


.drives {
  width: 100%;
  border-collapse: collapse;
  margin-top: 16px;
}

.drives th,
.drives td {
  text-align: center;
  vertical-align: middle;
  padding: 12px;
  border: 1px solid #e0e0e0;
}

.table-head {
  background-color: #f4f6f8;
}

.table-entries {
  cursor: pointer;
}

.table-entries:hover {
  background-color: #fbfbfb;
}

.drive-status {
  font-weight: 700;
}

.status-active {
  color: #1f8a21;
}

.status-upcoming {
  color: #d9821f;
}

.status-past {
  color: #6c757d;
}

.details-row {
  background-color: #fafafa;
}

.details-cell {
  text-align: left;
  padding: 16px;
}

.details-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 24px;
}

.details-grid h4 {
  margin-bottom: 8px;
}

.details-grid p {
  margin: 6px 0;
  word-break: break-word;
}

.empty-state {
  text-align: center;
  margin-top: 24px;
  color: #666;
}

hr {
  border: none;
  height: 2px;
  background: black;
  width: 100%;
}
</style>

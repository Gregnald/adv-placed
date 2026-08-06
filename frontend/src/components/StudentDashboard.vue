<script setup>
import { ref, computed } from 'vue';
import dp from '@/assets/dp-placeholder.png';
import StudentDrives from './StudentDrives.vue';
import StudentApplied from './StudentApplied.vue';

const profile = ref({
  name: 'Ananya Sharma',
  course: 'B.Tech Computer Science',
  year: '3rd Year',
  userType: 'Student',
  status: 'Active',
  resumeFileName: 'ananya-sharma-resume.pdf'
});

const selectedResume = ref({
  fileName: profile.value.resumeFileName,
  file: null
});

const editingProfile = ref(false);
const selectedTab = ref('Drives');

const tabs = {
  Drives: StudentDrives,
  Applied: StudentApplied
};

const allDrives = ref([
  {
    driveId: 'DRV101',
    companyName: 'Google Inc.',
    startDate: '2026-09-10',
    endDate: '2026-09-14',
    studentsParticipating: 48,
    status: 'Approved',
    expanded: false,
    accepted: true,
    jdInfo: {
      jobTitle: 'Software Engineer Intern',
      jobDescription: 'Build scalable systems and contribute to product development.',
      jobCompensation: 'Stipend with relocation support.',
      companyWebsite: 'www.google.com',
      hrMail: 'recruiting@google.com'
    }
  },
  {
    driveId: 'DRV102',
    companyName: 'Microsoft Inc.',
    startDate: '2026-09-25',
    endDate: '2026-09-28',
    studentsParticipating: 38,
    status: 'Approved',
    expanded: false,
    accepted: false,
    jdInfo: {
      jobTitle: 'Cloud Solutions Associate',
      jobDescription: 'Support Azure deployment and collaboration with engineering teams.',
      jobCompensation: 'Competitive stipend and benefits.',
      companyWebsite: 'www.microsoft.com',
      hrMail: 'careers@microsoft.com'
    }
  },
  {
    driveId: 'DRV103',
    companyName: 'Skyroot',
    startDate: '2026-08-05',
    endDate: '2026-08-07',
    studentsParticipating: 16,
    status: 'Approved',
    expanded: false,
    accepted: true,
    jdInfo: {
      jobTitle: 'Aerospace Systems Intern',
      jobDescription: 'Support launch vehicle development and validation.',
      jobCompensation: 'Stipend plus travel reimbursement.',
      companyWebsite: 'www.skyroot.com',
      hrMail: 'jobs@skyroot.com'
    }
  },
  {
    driveId: 'DRV104',
    companyName: 'ByteWave',
    startDate: '2026-07-01',
    endDate: '2026-07-03',
    studentsParticipating: 22,
    status: 'Rejected',
    expanded: false,
    accepted: false,
    jdInfo: {
      jobTitle: 'Frontend Developer Intern',
      jobDescription: 'Work on user-facing web applications and UI features.',
      jobCompensation: 'Monthly stipend with learning allowance.',
      companyWebsite: 'www.bytewave.com',
      hrMail: 'talent@bytewave.com'
    }
  }
]);

const today = new Date();

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

function getDriveVisibility(drive) {
  const start = new Date(drive.startDate);
  const end = new Date(drive.endDate);
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

const applyToDrive = (driveId) => {
  allDrives.value = allDrives.value.map((drive) => {
    if (drive.driveId === driveId && profile.value.resumeFileName) {
      return {
        ...drive,
        applied: true,
        appliedResume: profile.value.resumeFileName,
        applicationStatus: 'Pending'
      };
    }
    return drive;
  });
};

const saveProfile = () => {
  editingProfile.value = false;
};

const toggleStatus = () => {
  profile.value.status = profile.value.status === 'Active' ? 'Inactive' : 'Active';
};
</script>

<template>
  <div class="student-dashboard">
    <div class="dash-head"><h1>Student</h1></div>
    <hr />

    <div class="student-info">
      <img :src="dp" alt="profile" id="profile-pic" />
      <div class="profile-details">
        <div class="profile-row">
          <div>
            <h2>{{ profile.name }}</h2>
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
          <label>Name</label>
          <input v-model="profile.name" />
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

    <div class="data-container">
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

      <div class="tab-container">
        <component
          :is="tabs[selectedTab]"
          :drives="selectedTab === 'Drives' ? activeDrives : appliedDrives"
          :resumeFileName="profile.resumeFileName"
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
  justify-content: center;
}

h1 {
  font-size: 3em;
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

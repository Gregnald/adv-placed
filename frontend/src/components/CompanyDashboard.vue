<script setup>
import { ref, computed } from 'vue';
import JD from './JD.vue';

const jobRef = ref(null);
const showCreateForm = ref(false);
const company = ref({
  name: localStorage.getItem('companyName') || 'Skyroot Technologies',
  approvalStatus: 'Approved'
});

const drives = ref([
  {
    driveId: 'DRV201',
    companyName: company.value.name,
    jobTitle: 'Aerospace Systems Intern',
    startDate: '2026-10-01',
    endDate: '2026-10-10',
    status: 'Approved',
    studentsParticipating: 34,
    applicationDeadline: '2026-09-25',
    minCgpa: 8.0,
    eligibleBranches: ['Aerospace', 'Mechanical'],
    eligibleYears: ['3rd Year'],
    jdInfo: {
      jobTitle: 'Aerospace Systems Intern',
      jobDescription: 'Support launch vehicle development and test operations.',
      jobCompensation: 'Internship stipend with travel allowance.',
      companyWebsite: 'www.skyroot.com',
      hrMail: 'jobs@skyroot.com'
    }
  },
  {
    driveId: 'DRV202',
    companyName: company.value.name,
    jobTitle: 'Propulsion Analyst Trainee',
    startDate: '2026-11-05',
    endDate: '2026-11-15',
    status: 'Pending',
    studentsParticipating: 0,
    applicationDeadline: '2026-10-28',
    minCgpa: 7.5,
    eligibleBranches: ['Aerospace', 'Mechanical'],
    eligibleYears: ['3rd Year', '4th Year'],
    jdInfo: {
      jobTitle: 'Propulsion Analyst Trainee',
      jobDescription: 'Analyze propulsion subsystem performance and support design decisions.',
      jobCompensation: 'Competitive stipend and learning support.',
      companyWebsite: 'www.skyroot.com',
      hrMail: 'recruiting@skyroot.com'
    }
  }
]);

const selectedDriveId = ref(drives.value[0]?.driveId || null);

const applications = ref([
  { applicationId: 'APP301', studentName: 'Aisha Patel', driveId: 'DRV201', status: 'Applied', resume: 'ananya-sharma-resume.pdf' },
  { applicationId: 'APP302', studentName: 'Rohan Singh', driveId: 'DRV201', status: 'Shortlisted', resume: 'rohan-singh-resume.pdf' },
  { applicationId: 'APP303', studentName: 'Maya Rao', driveId: 'DRV202', status: 'Pending', resume: 'maya-rao-resume.pdf' }
]);

const summaryStats = computed(() => ({
  totalDrives: drives.value.length,
  approvedDrives: drives.value.filter((d) => d.status === 'Approved').length,
  pendingDrives: drives.value.filter((d) => d.status === 'Pending').length,
  totalApplications: applications.value.length
}));

const selectedDrive = computed(() => drives.value.find((drive) => drive.driveId === selectedDriveId.value));

const selectedApplications = computed(() =>
  applications.value.filter((application) => application.driveId === selectedDriveId.value)
);

const selectDrive = (driveId) => {
  selectedDriveId.value = driveId;
};

const createDrive = () => {
  if (!jobRef.value) return;
  const data = jobRef.value.getJobData();
  if (!data.jobTitle || !data.startDate || !data.endDate || !data.applicationDeadline) return;

  const nextNumber = drives.value.length + 1;
  const nextId = `DRV${200 + nextNumber}`;
  drives.value.push({
    driveId: nextId,
    companyName: data.companyName || company.value.name,
    jobTitle: data.jobTitle,
    startDate: data.startDate,
    endDate: data.endDate,
    status: 'Pending',
    studentsParticipating: 0,
    applicationDeadline: data.applicationDeadline,
    minCgpa: data.minCgpa,
    eligibleBranches: data.eligibleBranches,
    eligibleYears: data.eligibleYears,
    jdInfo: {
      jobTitle: data.jobTitle,
      jobDescription: data.jobDescription,
      jobCompensation: data.jobCompensation,
      companyWebsite: data.companyWebsite,
      hrMail: data.hrMail
    }
  });
  showCreateForm.value = false;
  selectedDriveId.value = nextId;
};

const updateApplicationStatus = (id, newStatus) => {
  const application = applications.value.find((item) => item.applicationId === id);
  if (application) {
    application.status = newStatus;
  }
};
</script>

<template>
  <div class="company-dashboard">
    <div class="dash-head"><h1>Company</h1></div>
    <hr />

    <div class="company-info">
      <div>
        <h2>{{ company.name }}</h2>
        <p class="company-status">{{ company.approvalStatus }}</p>
      </div>
      <div class="company-actions">
        <button @click="showCreateForm = !showCreateForm">
          {{ showCreateForm ? 'Hide Drive Form' : 'Create Drive' }}
        </button>
      </div>
    </div>

    <div class="summary-row">
      <div class="summary-card">
        <h3>Total Drives</h3>
        <p>{{ summaryStats.totalDrives }}</p>
      </div>
      <div class="summary-card">
        <h3>Approved Drives</h3>
        <p>{{ summaryStats.approvedDrives }}</p>
      </div>
      <div class="summary-card">
        <h3>Pending Drives</h3>
        <p>{{ summaryStats.pendingDrives }}</p>
      </div>
      <div class="summary-card">
        <h3>Total Applications</h3>
        <p>{{ summaryStats.totalApplications }}</p>
      </div>
    </div>

    <div class="data-container">
      

      <div v-if="showCreateForm" class="create-panel">
        <h3>Create Placement Drive</h3>
        <JD :showJD="true" ref="jobRef" />
        <button class="create-button" @click="createDrive">Save Drive</button>
      </div>

      <div class="table-section">
        <h3>My Drives</h3>
        <table class="company-drives">
          <thead>
            <tr>
              <th>Drive ID</th>
              <th>Job Title</th>
              <th>Status</th>
              <th>Start</th>
              <th>End</th>
              <th>Deadline</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="drive in drives" :key="drive.driveId">
              <td>{{ drive.driveId }}</td>
              <td>{{ drive.jobTitle }}</td>
              <td>{{ drive.status }}</td>
              <td>{{ drive.startDate }}</td>
              <td>{{ drive.endDate }}</td>
              <td>{{ drive.applicationDeadline }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="drive-select-wrap">
        <label for="drive-select">Select Drive</label>
        <select id="drive-select" class="drive-select" v-model="selectedDriveId">
          <option disabled value="" v-if="!selectedDriveId">-- choose a drive --</option>
          <option v-for="drive in drives" :key="drive.driveId" :value="drive.driveId">
            {{ drive.driveId }} - {{ drive.jobTitle }}
          </option>
        </select>
      </div>

      <div class="details-panel" v-if="selectedDrive">
        <h3>Applications for {{ selectedDrive.driveId }}</h3>
        <p><strong>Drive:</strong> {{ selectedDrive.jobTitle }}</p>
        <p><strong>Status:</strong> {{ selectedDrive.status }}</p>
        <table class="applications-table">
          <thead>
            <tr>
              <th>Application ID</th>
              <th>Student</th>
              <th>Status</th>
              <th>Resume</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="application in selectedApplications" :key="application.applicationId">
              <td>{{ application.applicationId }}</td>
              <td>{{ application.studentName }}</td>
              <td>{{ application.status }}</td>
              <td>{{ application.resume }}</td>
              <td>
                <button @click="updateApplicationStatus(application.applicationId, 'Shortlisted')">Shortlist</button>
                <button @click="updateApplicationStatus(application.applicationId, 'Selected')">Select</button>
                <button @click="updateApplicationStatus(application.applicationId, 'Rejected')">Reject</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<style scoped>
.company-dashboard {
  margin: 1vh;
}

.dash-head {
  display: flex;
  justify-content: center;
}

h1 {
  font-size: 3em;
}

.company-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 24px 0;
  gap: 16px;
  flex-wrap: wrap;
}

.company-status {
  color: #1f8a21;
  font-weight: 700;
}

.company-actions button,
.create-button,
.applications-table button {
  border: none;
  background: #1f8a21;
  color: white;
  padding: 10px 16px;
  border-radius: 10px;
  cursor: pointer;
}

.company-actions button:hover,
.create-button:hover,
.applications-table button:hover {
  background: #166f19;
}

.summary-row {
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
  display: grid;
  gap: 24px;
}

.drive-nav {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.nav-btn {
  border: none;
  padding: 10px 16px;
  background: #f4f4f4;
  border-radius: 10px;
  text-decoration: none;
  color: black;
}

.nav-btn.active {
  background-color: rgba(128, 128, 128, 0.192);
}

.create-panel {
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 16px;
  padding: 20px;
}

.drive-select-wrap {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.drive-select {
  padding: 8px 12px;
  border-radius: 8px;
  border: 1px solid #dcdcdc;
  background: white;
}

.table-section,
.details-panel {
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 16px;
  padding: 20px;
}

.company-drives,
.applications-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 16px;
}

.company-drives th,
.company-drives td,
.applications-table th,
.applications-table td {
  border: 1px solid #e0e0e0;
  padding: 12px;
  text-align: left;
}

.company-drives th,
.applications-table th {
  background: #f4f6f8;
}

.applications-table button {
  margin-right: 8px;
  margin-bottom: 4px;
}
</style>

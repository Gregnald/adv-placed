<script setup>
import { ref, computed, onMounted } from 'vue';
import router from '@/router';
import JD from './JD.vue';
import { api } from '@/services/api';

const jobRef = ref(null);
const showCreateForm = ref(false);
const company = ref({
  employer: localStorage.getItem('companyName') || '',
  hr_mail: localStorage.getItem('companyHRMail') || '',
  status: 'requested'
});

const drives = ref([]);

const selectedDriveId = ref(null);

const applications = ref([]);

const isBlacklisted = ref(false);

const loadDashboard = async () => {
  const payload = await api.getCompanyDashboard();
  company.value = payload.company || company.value;
  isBlacklisted.value = company.value.blacklisted || false;
  if (isBlacklisted.value) return;
  drives.value = payload.drives || [];
  applications.value = payload.applications || [];
  if (company.value.employer) {
    localStorage.setItem('companyName', company.value.employer);
  }
  if (company.value.hr_mail) {
    localStorage.setItem('companyHRMail', company.value.hr_mail);
  }
  if (!selectedDriveId.value && drives.value.length) {
    selectedDriveId.value = drives.value[0].driveId;
  }
};

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

const toggleCompanyStatus = async () => {
  const current = (company.value.status || '').toLowerCase();
  const nextStatus = current === 'active' ? 'inactive' : 'active';
  try {
    const res = await api.updateCompanyProfile({ status: nextStatus });
    if (res.company) {
      company.value.status = res.company.status;
    }
  } catch (err) {
    alert(err.message || 'Failed to toggle status');
  }
};

const createDrive = async () => {
  if ((company.value.status || '').toLowerCase() !== 'active') {
    alert('Only active companies can create placement drives.');
    return;
  }
  if (!jobRef.value) return;
  const data = jobRef.value.getJobData();
  if (!data.jobTitle || !data.startDate || !data.endDate || !data.applicationDeadline) return;

  await api.createCompanyDrive({
    jobTitle: data.jobTitle,
    jobDescription: data.jobDescription,
    jobCompensation: data.jobCompensation,
    startDate: data.startDate,
    endDate: data.endDate,
    applicationDeadline: data.applicationDeadline,
    minCgpa: data.minCgpa,
    eligibleBranches: data.eligibleBranches,
    eligibleYears: data.eligibleYears,
    companyWebsite: data.companyWebsite,
    hrMail: data.hrMail
  });
  showCreateForm.value = false;
  await loadDashboard();
};


const interviewDates = ref({});

const updateApplicationStatus = async (id, newStatus, dateVal = null) => {
  const payload = { status: newStatus };
  if (dateVal !== null) {
    payload.interviewDate = dateVal;
  } else if (interviewDates.value[id]) {
    payload.interviewDate = interviewDates.value[id];
  }
  await api.updateApplication(id, payload);
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

const exportingDrives = ref(false);
const exportingApps = ref(false);
const generatingReport = ref(false);

const exportDrives = async () => {
  exportingDrives.value = true;
  try {
    await api.exportAndDownload('company_drives', '', 'my_drives.csv');
  } catch (err) {
    alert('Failed to export CSV: ' + err.message);
  } finally {
    exportingDrives.value = false;
  }
};

const exportApplications = async () => {
  exportingApps.value = true;
  try {
    const driveCode = selectedDriveId.value || '';
    await api.exportAndDownload('company_applications', driveCode, `applications_${driveCode || 'all'}.csv`);
  } catch (err) {
    alert('Failed to export CSV: ' + err.message);
  } finally {
    exportingApps.value = false;
  }
};

const generateMonthlyReport = async () => {
  generatingReport.value = true;
  try {
    await api.generateAndDownloadCompanyReport();
  } catch (err) {
    alert('Failed to generate report: ' + err.message);
  } finally {
    generatingReport.value = false;
  }
};

onMounted(() => {
  loadDashboard().catch(() => {
    drives.value = [];
    applications.value = [];
  });
});
</script>


<template>
  <div class="company-dashboard">
    <div class="dash-head">
      <h1>Company</h1>
      <button class="logout-button" @click="logout">Logout</button>
    </div>
    <hr />

    <div v-if="isBlacklisted" class="blacklist-message">
      <div class="blacklist-container">
        <h2>Access Denied</h2>
        <p>You are blacklisted. Kindly contact the institution for more information.</p>
      </div>
    </div>

    <div v-if="!isBlacklisted" class="company-info">
      <div>
        <h2>{{ company.employer }}</h2>
        <div class="status-row">
          <p class="company-status">Status: <strong>{{ company.status }}</strong></p>
          <button
            v-if="!isBlacklisted && ((company.status || '').toLowerCase() === 'active' || (company.status || '').toLowerCase() === 'inactive')"
            :class="['status-pill', { inactive: (company.status || '').toLowerCase() === 'inactive' }]"
            @click="toggleCompanyStatus"
          >
            {{ (company.status || '').toUpperCase() }}
          </button>
        </div>
      </div>
      <div class="company-actions">
        <button class="report-btn" :disabled="generatingReport" @click="generateMonthlyReport">
          {{ generatingReport ? 'Generating Report...' : 'Generate Monthly Report' }}
        </button>
        <button
          :disabled="(company.status || '').toLowerCase() !== 'active'"
          :title="(company.status || '').toLowerCase() !== 'active' ? 'Only active companies can create drives' : ''"
          @click="showCreateForm = !showCreateForm"
        >
          {{ showCreateForm ? 'Hide Drive Form' : 'Create Drive' }}
        </button>
      </div>
    </div>


    <div v-if="!isBlacklisted" class="summary-row">
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

    <div v-if="!isBlacklisted" class="data-container">
      

      <div v-if="showCreateForm" class="create-panel">
        <h3>Create Placement Drive</h3>
        <JD :showJD="true" ref="jobRef" />
        <button class="create-button" @click="createDrive">Save Drive</button>
      </div>

      <div class="table-section">
        <div class="table-header-row">
          <h3>My Drives</h3>
          <button class="export-btn" :disabled="exportingDrives" @click="exportDrives">
            {{ exportingDrives ? 'Exporting...' : 'Export CSV' }}
          </button>
        </div>
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
        <div class="table-header-row">
          <h3>Applications for {{ selectedDrive.driveId }}</h3>
          <button class="export-btn" :disabled="exportingApps" @click="exportApplications">
            {{ exportingApps ? 'Exporting...' : 'Export CSV' }}
          </button>
        </div>

        <p><strong>Drive:</strong> {{ selectedDrive.jobTitle }}</p>
        <p><strong>Status:</strong> {{ selectedDrive.status }}</p>

        <table class="applications-table">
          <thead>
            <tr>
              <th>Application ID</th>
              <th>Student</th>
              <th>Status</th>
              <th>Resume</th>
              <th>Interview Date & Time</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="application in selectedApplications" :key="application.applicationId">
              <td>{{ application.applicationId }}</td>
              <td>{{ application.studentName }}</td>
              <td>
                <span :class="['status-badge', `status-${application.status.toLowerCase()}`]">
                  {{ application.status }}
                </span>
              </td>
              <td>{{ application.resume }}</td>
              <td>
                <div class="interview-schedule-box">
                  <input
                    type="datetime-local"
                    class="interview-input"
                    :value="interviewDates[application.applicationId] || application.interviewDate || ''"
                    @input="interviewDates[application.applicationId] = $event.target.value"
                  />
                  <button
                    v-if="(interviewDates[application.applicationId] || application.interviewDate) && (interviewDates[application.applicationId] !== application.interviewDate)"
                    class="save-date-btn"
                    @click="updateApplicationStatus(application.applicationId, application.status, interviewDates[application.applicationId])"
                  >
                    Save Date
                  </button>
                </div>
              </td>
              <td>
                <div class="action-btn-group">
                  <button
                    class="btn-action btn-shortlist"
                    :class="{ active: application.status === 'Shortlisted' }"
                    @click="updateApplicationStatus(application.applicationId, 'Shortlisted', interviewDates[application.applicationId] || application.interviewDate || '')"
                  >
                    Shortlist
                  </button>
                  <button
                    class="btn-action btn-select"
                    :class="{ active: application.status === 'Selected' }"
                    @click="updateApplicationStatus(application.applicationId, 'Selected')"
                  >
                    Select
                  </button>
                  <button
                    class="btn-action btn-reject"
                    :class="{ active: application.status === 'Rejected' }"
                    @click="updateApplicationStatus(application.applicationId, 'Rejected')"
                  >
                    Reject
                  </button>
                </div>
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

.company-actions {
  display: flex;
  gap: 12px;
  align-items: center;
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

.company-actions button:disabled {
  background: #e0e0e0;
  color: #888888;
  border: 1px solid #cccccc;
  cursor: not-allowed;
  opacity: 0.7;
}

.company-actions button:disabled:hover {
  background: #e0e0e0;
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

.status-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 4px;
}

.status-pill {
  border: 1px solid #1f8a21;
  background: #1f8a21;
  color: white;
  padding: 4px 12px;
  border-radius: 20px;
  font-weight: 700;
  font-size: 0.85rem;
  cursor: pointer;
  transition: background 0.2s ease;
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

.table-header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
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

.status-badge {
  padding: 4px 10px;
  border-radius: 6px;
  font-weight: 600;
  font-size: 0.85rem;
  display: inline-block;
}

.status-badge.status-pending {
  background: #e3f2fd;
  color: #1976d2;
}

.status-badge.status-shortlisted {
  background: #fff3e0;
  color: #e65100;
}

.status-badge.status-selected {
  background: #e8f5e9;
  color: #2e7d32;
}

.status-badge.status-rejected {
  background: #ffebee;
  color: #c62828;
}

.interview-schedule-box {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.interview-input {
  padding: 6px 10px;
  border: 1px solid #dcdcdc;
  border-radius: 6px;
  font-size: 0.85rem;
}

.save-date-btn {
  background: #0288d1 !important;
  color: white;
  padding: 4px 8px !important;
  border-radius: 6px !important;
  font-size: 0.8rem;
}

.action-btn-group {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.btn-action {
  border: none;
  padding: 6px 12px !important;
  border-radius: 6px !important;
  font-weight: 600;
  font-size: 0.82rem;
  cursor: pointer;
  transition: opacity 0.2s ease;
}

.btn-shortlist {
  background: #ff9800 !important;
  color: white !important;
}

.btn-select {
  background: #2e7d32 !important;
  color: white !important;
}

.btn-reject {
  background: #d32f2f !important;
  color: white !important;
}

.btn-action:hover {
  opacity: 0.88;
}

.btn-action.active {
  box-shadow: inset 0 0 0 2px rgba(0, 0, 0, 0.4);
}
</style>


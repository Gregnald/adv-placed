<script setup>
import { ref } from 'vue';

const props = defineProps({
  drives: {
    type: Array,
    default: () => []
  },
  resumeFileName: {
    type: String,
    default: ''
  }
});

const emit = defineEmits(['apply']);

const expandedIds = ref(new Set());

const toggleExpand = (driveId) => {
  if (expandedIds.value.has(driveId)) {
    expandedIds.value.delete(driveId);
  } else {
    expandedIds.value.add(driveId);
  }
};

const isExpanded = (driveId) => expandedIds.value.has(driveId);

const canApply = (drive) => drive.visibility === 'Active' && !drive.applied && props.resumeFileName;

const statusText = (drive) => drive.visibility || drive.status;
</script>

<template>
  <table class="drives">
    <thead>
      <tr class="table-head">
        <th>Drive ID</th>
        <th>Company Name</th>
        <th>Start Date</th>
        <th>End Date</th>
        <th>Students Participating</th>
        <th>Status</th>
        <th>Action</th>
      </tr>
    </thead>
    <tbody>
      <template v-for="drive in drives" :key="drive.driveId">
        <tr class="table-entries" @click="toggleExpand(drive.driveId)">
          <td>{{ drive.driveId }}</td>
          <td>{{ drive.companyName }}</td>
          <td>{{ drive.startDate }}</td>
          <td>{{ drive.endDate }}</td>
          <td>{{ drive.studentsParticipating }}</td>
          <td>
            <span :class="['drive-status', `status-${drive.visibility?.toLowerCase()}`]">
              {{ drive.visibility || drive.status }}
            </span>
          </td>
          <td>
            <button
              class="apply-button"
              :disabled="drive.applied || !canApply(drive)"
              @click.stop="emit('apply', drive.driveId)"
            >
              {{ drive.applied ? 'Applied' : !props.resumeFileName ? 'Upload Resume' : statusText(drive) !== 'Active' ? 'Unavailable' : 'Apply' }}
            </button>
            <p v-if="drive.applied && drive.appliedResume" class="resume-note">Resume: {{ drive.appliedResume }}</p>
          </td>
        </tr>
        <tr v-if="isExpanded(drive.driveId)" class="details-row">
          <td colspan="7" class="details-cell">
            <div class="details-grid">
              <div class="detail-group">
                <h4>Drive Overview</h4>
                <p><strong>Company:</strong> {{ drive.companyName }}</p>
                <p><strong>Start Date:</strong> {{ drive.startDate }}</p>
                <p><strong>End Date:</strong> {{ drive.endDate }}</p>
                <p><strong>Application Deadline:</strong> {{ drive.applicationDeadline || 'N/A' }}</p>
                <p><strong>Minimum CGPA:</strong> {{ drive.minCgpa || 'N/A' }}</p>
                <p><strong>Eligible Branches:</strong> {{ drive.eligibleBranches?.join(', ') || 'All' }}</p>
                <p><strong>Eligible Years:</strong> {{ drive.eligibleYears?.join(', ') || 'All' }}</p>
              </div>
              <div class="detail-group">
                <h4>Job Description</h4>
                <p><strong>Title:</strong> {{ drive.jdInfo.jobTitle }}</p>
                <p><strong>Description:</strong> {{ drive.jdInfo.jobDescription }}</p>
                <p><strong>Compensation:</strong> {{ drive.jdInfo.jobCompensation }}</p>
                <p><strong>Website:</strong> {{ drive.jdInfo.companyWebsite }}</p>
                <p><strong>HR Email:</strong> {{ drive.jdInfo.hrMail }}</p>
              </div>
            </div>
          </td>
        </tr>
      </template>
    </tbody>
  </table>
</template>

<style scoped>
.drives {
  width: 100%;
  border-collapse: collapse;
  margin-top: 16px;
}

.table-head th,
.table-entries td,
.details-cell {
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
  margin-right: 8px;
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
  align-items: start;
}

.detail-group {
  min-width: 0;
}

.apply-button {
  border: 1px solid #1f8a21;
  background: #1f8a21;
  color: white;
  padding: 8px 12px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9rem;
  min-width: 94px;
  transition: background 0.2s ease, border-color 0.2s ease;
}

.apply-button:hover:not(:disabled) {
  background: #166f19;
  border-color: #166f19;
}
    .apply-button:disabled {
        background: #f0f0f0;
        border-color: #d3d3d3;
        color: #7a7a7a;
        cursor: not-allowed;
        opacity: 0.95;
    }

.detail-group p {
  margin: 6px 0;
  word-break: break-word;
}
</style>
<script setup>
import { ref } from 'vue';

const props = defineProps({
  drives: {
    type: Array,
    default: () => []
  }
});

const expandedIds = ref(new Set());

const toggleExpand = (driveId) => {
  if (expandedIds.value.has(driveId)) {
    expandedIds.value.delete(driveId);
  } else {
    expandedIds.value.add(driveId);
  }
};

const isExpanded = (driveId) => expandedIds.value.has(driveId);

const getStatus = (drive) => {
  if (drive.applicationStatus) return drive.applicationStatus;
  if (drive.accepted) return 'Accepted';
  if (drive.status === 'Rejected') return 'Rejected';
  return 'Pending';
};

const statusClass = (drive) => {
  const status = getStatus(drive);
  return {
    'status-accepted': status === 'Accepted',
    'status-rejected': status === 'Rejected',
    'status-pending': status === 'Pending'
  };
};
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
        <th>Application Status</th>
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
          <td :class="statusClass(drive)">{{ getStatus(drive) }}</td>
        </tr>
        <tr v-if="isExpanded(drive.driveId)" class="details-row">
          <td colspan="6" class="details-cell">
            <div class="details-grid">
              <div class="detail-group">
                <h4>Drive Overview</h4>
                <p><strong>Company:</strong> {{ drive.companyName }}</p>
                <p><strong>Start Date:</strong> {{ drive.startDate }}</p>
                <p><strong>End Date:</strong> {{ drive.endDate }}</p>
                <p><strong>Interview Stage:</strong> {{ getStatus(drive) }}</p>
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

.detail-group h4 {
  margin-bottom: 8px;
}

.detail-group p {
  margin: 6px 0;
  word-break: break-word;
}
  .status-accepted {
    color: #1f8a21;
    font-weight: 700;
  }

  .status-rejected {
    color: #d32f2f;
    font-weight: 700;
  }

  .status-pending {
    color: #1f5ec4;
    font-weight: 700;
  }
</style>
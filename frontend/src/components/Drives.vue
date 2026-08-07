<script setup>
import { ref, computed, watch } from 'vue';

const props = defineProps({
  searchQuery: {
    type: String,
    default: ''
  },
  drives: {
    type: Array,
    default: () => []
  }
});

const emit = defineEmits(['drive-updated']);

const table_head = ['Drive ID', 'Company Name', 'Start Date', 'End Date', 'Students Participating', 'Status'];

const localDrives = ref([]);

watch(
  () => props.drives,
  (value) => {
    localDrives.value = (value || []).map((drive) => ({ ...drive, expanded: false }));
  },
  { immediate: true, deep: true }
);

const toggleExpand = (driveId) => {
    localDrives.value = localDrives.value.map((drive) => {
        if (drive.driveId === driveId) {
            return { ...drive, expanded: !drive.expanded };
        }
        return drive;
    });
};

const filteredDrives = computed(() => {
    if (!props.searchQuery) return localDrives.value;
    const query = props.searchQuery.toLowerCase();
    return localDrives.value.filter((drive) =>
        drive.driveId.toLowerCase().includes(query) ||
        drive.companyName.toLowerCase().includes(query) ||
        drive.status.toLowerCase().includes(query)
    );
});

const toggleStatus = (driveId) => {
    const drive = localDrives.value.find((drive) => drive.driveId === driveId);
    if (drive) {
        if (drive.status === 'Approved') {
            drive.status = 'Rejected';
        } else if (drive.status === 'Rejected') {
            drive.status = 'Pending';
        } else {
            drive.status = 'Approved';
        }
        emit('drive-updated', { driveId: drive.driveId, payload: { status: drive.status } });
    }
};
</script>

<template>
    <table class="drives">
        <thead>
            <tr class="table-head">
                <th v-for="head in table_head" :key="head">{{ head }}</th>
            </tr>
        </thead>
        <tbody>
            <template v-for="drive in filteredDrives" :key="drive.driveId">
                <tr class="table-entries" @click="toggleExpand(drive.driveId)">
                    <td>{{ drive.driveId }}</td>
                    <td>{{ drive.companyName }}</td>
                    <td>{{ drive.startDate }}</td>
                    <td>{{ drive.endDate }}</td>
                    <td>{{ drive.studentsParticipating }}</td>
                    <td
                        class="status-cell"
                        :class="`status-${drive.status.toLowerCase()}`"
                        @click.stop="toggleStatus(drive.driveId)"
                    >
                        <span class="drive-status">{{ drive.status }}</span>
                    </td>
                </tr>
                <tr v-if="drive.expanded" class="drive-details-row">
                    <td colspan="6" class="drive-details-cell">
                        <div class="drive-details">
                            <div class="detail-group">
                                <h4>Job Description</h4>
                                <p><strong>Title:</strong> {{ drive.jdInfo.jobTitle }}</p>
                                <p><strong>Description:</strong> {{ drive.jdInfo.jobDescription }}</p>
                                <p><strong>Compensation:</strong> {{ drive.jdInfo.jobCompensation }}</p>
                            </div>
                            <div class="detail-group">
                                <h4>Company Contact</h4>
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
    }

    .table-head th,
    .table-entries td,
    .drive-details-cell {
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

    .status-cell {
        cursor: pointer;
        font-weight: 600;
        padding: 0;
        transition: transform 0.1s ease;
        min-width: 110px;
    }

    .status-cell:hover {
        transform: translateY(-1px);
    }

    .drive-status {
        font-weight: 700;
    }

    .status-approved {
        color: #1f8a21;
        background-color: transparent;
    }

    .status-rejected {
        color: #d32f2f;
        background-color: transparent;
    }

    .status-pending {
        color: #0066cc;
        background-color: transparent;
    }

    .drive-details-row {
        background-color: #fafafa;
    }

    .drive-details {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 24px;
        text-align: left;
        align-items: start;
    }

    .detail-group {
        min-width: 0;
    }

    .detail-group h4 {
        margin: 0 0 8px;
    }

    .detail-group p {
        margin: 4px 0;
    }
</style>
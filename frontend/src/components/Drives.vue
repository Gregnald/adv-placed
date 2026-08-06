<script setup>
import { ref, computed } from 'vue';

const props = defineProps({
  searchQuery: {
    type: String,
    default: ''
  }
});

const table_head = ['Drive ID', 'Company Name', 'Start Date', 'End Date', 'Students Participating', 'Status'];

const drives = ref([
    {
        driveId: 'DRV001',
        companyName: 'Google Inc.',
        startDate: '2026-09-01',
        endDate: '2026-09-10',
        studentsParticipating: 45,
        status: 'Approved',
        expanded: false,
        jdInfo: {
            jobTitle: 'Software Engineer Intern',
            jobDescription: 'Work on core search and AI products with a cross-functional team.',
            jobCompensation: 'Competitive stipend with relocation support.',
            companyWebsite: 'www.google.com',
            hrMail: 'recruiting@google.com'
        }
    },
    {
        driveId: 'DRV002',
        companyName: 'Microsoft Inc.',
        startDate: '2026-10-05',
        endDate: '2026-10-12',
        studentsParticipating: 32,
        status: 'Rejected',
        expanded: false,
        jdInfo: {
            jobTitle: 'Cloud Solutions Associate',
            jobDescription: 'Support Azure deployment and cloud-native service development.',
            jobCompensation: 'Salary plus bonus and benefits package.',
            companyWebsite: 'www.microsoft.com',
            hrMail: 'careers@microsoft.com'
        }
    },
    {
        driveId: 'DRV003',
        companyName: 'Skyroot',
        startDate: '2026-11-01',
        endDate: '2026-11-08',
        studentsParticipating: 12,
        status: 'Approved',
        expanded: false,
        jdInfo: {
            jobTitle: 'Aerospace Systems Intern',
            jobDescription: 'Support launch vehicle development and test operations.',
            jobCompensation: 'Internship stipend with travel allowance.',
            companyWebsite: 'www.skyroot.com',
            hrMail: 'jobs@skyroot.com'
        }
    }
]);

const toggleExpand = (driveId) => {
    drives.value = drives.value.map((drive) => {
        if (drive.driveId === driveId) {
            return { ...drive, expanded: !drive.expanded };
        }
        return drive;
    });
};

const filteredDrives = computed(() => {
    if (!props.searchQuery) return drives.value;
    const query = props.searchQuery.toLowerCase();
    return drives.value.filter((drive) =>
        drive.driveId.toLowerCase().includes(query) ||
        drive.companyName.toLowerCase().includes(query) ||
        drive.status.toLowerCase().includes(query)
    );
});

const toggleStatus = (driveId) => {
    const drive = drives.value.find((drive) => drive.driveId === driveId);
    if (drive) {
        if (drive.status === 'Approved') {
            drive.status = 'Rejected';
        } else if (drive.status === 'Rejected') {
            drive.status = 'Pending';
        } else {
            drive.status = 'Approved';
        }
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
            <template v-for="drive in drives" :key="drive.driveId">
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
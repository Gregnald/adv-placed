<script setup>
import { ref, computed, defineProps, watch } from 'vue';

const props = defineProps({
  searchQuery: {
    type: String,
    default: ''
  },
  students: {
    type: Array,
        default: () => []
  }
});

const emit = defineEmits(['student-updated']);

const table_head = ['Enrollment No', 'Student Name', 'Course', 'Status', 'Blacklisted'];

const localStudents = ref([]);

watch(
    () => props.students,
    (value) => {
        localStudents.value = (value || []).map((student) => ({ ...student }));
    },
    { immediate: true, deep: true }
);

const filteredStudents = computed(() => {
        const source = localStudents.value;
    if (!props.searchQuery) return source;
    const query = props.searchQuery.toLowerCase();
    return source.filter((student) =>
        student.enrollment.toLowerCase().includes(query) ||
        student.name.toLowerCase().includes(query) ||
        student.course.toLowerCase().includes(query) ||
        student.status.toLowerCase().includes(query)
    );
});

const isStatusChangeable = (status) => false;

const changeBlacklisted = (enrollment) => {
    const student = localStudents.value.find((s) => s.enrollment === enrollment);
    if (!student) {
        return;
    }

    const newBlacklisted = !student.blacklisted;
    student.blacklisted = newBlacklisted;

    if (newBlacklisted) {
        if (student.status !== 'denied') {
            student.previousStatus = student.status;
            student.status = 'denied';
        }
    } else if (student.previousStatus) {
        student.status = student.previousStatus;
        delete student.previousStatus;
    }
    emit('student-updated', { enrollment: student.enrollment, payload: { blacklisted: student.blacklisted, status: student.status } });
};

const changeStatus = (enrollment) => {
    const student = localStudents.value.find((s) => s.enrollment === enrollment);
    if (!student || !isStatusChangeable(student.status)) {
        return;
    }
};
</script>

<template>
    <table class="students">
        <thead>
            <tr class="table-head">
                <th v-for="head in table_head" :key="head">
                    {{ head }}
                </th>
            </tr>
        </thead>
        <tbody>
            <tr v-for="student in filteredStudents" :key="student.enrollment" class="table-entries">
                <td>{{ student.enrollment }}</td>
                <td>{{ student.name }}</td>
                <td>{{ student.course }}</td>
                <td
                    class="status-cell"
                    :class="['status-cell', `status-${student.status}`, { 'status-locked': !isStatusChangeable(student.status) }]"
                    @click="changeStatus(student.enrollment)">
                    {{ student.status }}
                </td>
                <td
                    class="blacklisted-cell"
                    :class="student.blacklisted ? 'blacklisted-true' : 'blacklisted-false'"
                    @click="changeBlacklisted(student.enrollment)">
                    {{ student.blacklisted ? 'YES' : 'NO' }}
                </td>
            </tr>
        </tbody>
    </table>
</template>

<style scoped>
    .students {
        width: 100%;
        border-collapse: collapse;
    }

    .table-head th,
    .table-entries td {
        text-align: center;
        vertical-align: middle;
        padding: 10px;
        border: 1px solid #e0e0e0;
    }

    .table-head {
        background-color: #f4f6f8;
    }

    .status-cell {
        cursor: pointer;
        font-weight: 600;
        width: 150px;
    }

    .status-locked {
        cursor: default;
        opacity: 0.8;
    }

    .status-active {
        color: #1f8a21;
    }

    .status-inactive {
        color: #6c757d;
    }

    .status-denied {
        color: #d32f2f;
    }

    .status-placed {
        color: #1f8a21;
    }

    .blacklisted-cell {
        cursor: pointer;
        border-radius: 6px;
        padding: 8px;
        transition: background-color 0.2s ease, color 0.2s ease;
    }

    .blacklisted-true {
        background-color: #c0392b;
        color: #ffffff;
    }

    .blacklisted-false {
        background-color: #ecf0f1;
        color: #2c3e50;
    }
</style>
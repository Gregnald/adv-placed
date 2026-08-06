<script setup>
import { ref, computed } from 'vue';

const props = defineProps({
  searchQuery: {
    type: String,
    default: ''
  }
});

const table_head = ['Employer', 'Website', 'HR Mail', 'Status', 'Blacklisted'];

const companies = ref([
    { employer: 'Google Inc.', website: 'www.google.com', hr_mail: 'gmail', status: 'active', blacklisted: false },
    { employer: 'Apple Inc.', website: 'www.apple.com', hr_mail: 'apple_mail', status: 'requested', blacklisted: false },
    { employer: 'Microsoft Inc.', website: 'www.microsoft.com', hr_mail: 'M_mail', status: 'active', blacklisted: false },
    { employer: 'Skyroot', website: 'www.skyroot.com', hr_mail: 'sky_mail', status: 'denied', blacklisted: false }
]);

const statusOptions = ['active', 'requested', 'inactive', 'denied'];

const normalizeBlacklistedCompanies = () => {
    companies.value.forEach((company) => {
        if (company.blacklisted && company.status !== 'denied') {
            company.previousStatus = company.status;
            company.status = 'denied';
        }
    });
};

normalizeBlacklistedCompanies();

const filteredCompanies = computed(() => {
    if (!props.searchQuery) return companies.value;
    const query = props.searchQuery.toLowerCase();
    return companies.value.filter((company) =>
        company.employer.toLowerCase().includes(query) ||
        company.website.toLowerCase().includes(query) ||
        company.hr_mail.toLowerCase().includes(query) ||
        company.status.toLowerCase().includes(query)
    );
});

const changeBlacklisted = (companyName) => {
    const company = companies.value.find((company) => company.employer === companyName);
    if (!company) {
        return;
    }

    const newBlacklisted = !company.blacklisted;
    company.blacklisted = newBlacklisted;

    if (newBlacklisted) {
        if (company.status !== 'denied') {
            company.previousStatus = company.status;
            company.status = 'denied';
        }
    } else if (company.previousStatus) {
        company.status = company.previousStatus;
        delete company.previousStatus;
    }
};

const changeStatus = (companyName, newStatus) => {
    const company = companies.value.find((company) => company.employer === companyName);
    if (!company) {
        return;
    }

    if (company.blacklisted && newStatus !== 'denied') {
        company.blacklisted = false;
        delete company.previousStatus;
    }

    company.status = newStatus;
};

const denyRequest = (companyName) => {
    const company = companies.value.find((company) => company.employer === companyName);
    if (company && company.status !== 'denied') {
        company.status = 'denied';
        delete company.previousStatus;
        // call API here
        // updateCompany(company)
    }
};

const restoreRequest = (companyName) => {
    const company = companies.value.find((company) => company.employer === companyName);
    if (company && company.status === 'denied') {
        company.status = 'requested';
        // call API here
        // updateCompany(company)
    }
};

</script>

<template>
    <table class="companies">
        <thead>
            <tr class="table-head">
                <th v-for="head in table_head" :key="head">
                    {{ head }}
                </th>
            </tr>
        </thead>
        <tbody>
            <tr v-for="company in filteredCompanies" :key="company.employer" class="table-entries">
                <td>{{ company.employer }}</td>
                <td>{{ company.website }}</td>
                <td>{{ company.hr_mail }}</td>
                <td class="status-cell">
                    <select
                        class="status-select"
                        :class="`status-${company.status}`"
                        v-model="company.status"
                        @change="changeStatus(company.employer, company.status)"
                    >
                        <option v-for="status in statusOptions" :key="status" :value="status">
                            {{ status }}
                        </option>
                    </select>
                </td>
                <td
                    class="blacklisted-cell"
                    :class="company.blacklisted ? 'blacklisted-true' : 'blacklisted-false'"
                    @click="changeBlacklisted(company.employer)">
                    {{ company.blacklisted ? 'YES' : 'NO' }}
                </td>
            </tr>
        </tbody>
    </table>
</template>

<style scoped>
    .companies{
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
        width: 180px;
        padding: 0;
    }

    .status-select {
        width: 100%;
        border: none;
        background: transparent;
        color: inherit !important;
        -webkit-text-fill-color: inherit !important;
        font-weight: 700;
        text-align: center;
        appearance: none;
        cursor: pointer;
        outline: none;
        padding: 6px 10px;
    }

    .status-select.status-active {
        color: #1f8a21 !important;
        -webkit-text-fill-color: #1f8a21 !important;
    }

    .status-select.status-requested {
        color: #d9821f !important;
        -webkit-text-fill-color: #d9821f !important;
    }

    .status-select.status-denied {
        color: #d32f2f !important;
        -webkit-text-fill-color: #d32f2f !important;
    }

    .status-select.status-inactive {
        color: #6c757d !important;
        -webkit-text-fill-color: #6c757d !important;
    }

    .status-select option {
        color: #222;
    }

    .status-select:hover {
        opacity: 0.95;
    }

    .status-select:focus {
        outline: none;
        box-shadow: 0 0 0 3px rgba(21, 156, 228, 0.12);
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
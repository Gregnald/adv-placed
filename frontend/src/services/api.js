const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:5000/api';

async function request(path, options = {}) {
  const sessionId = localStorage.getItem('sessionId') || '';
  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {})
  };
  if (sessionId) {
    headers['X-Session-Id'] = sessionId;
  }

  const response = await fetch(`${API_BASE}${path}`, {
    method: options.method || 'GET',
    headers,
    body: options.body ? JSON.stringify(options.body) : undefined
  });

  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data.message || 'Request failed');
  }
  return data;
}


export const api = {
  login: (payload) => request('/auth/login', { method: 'POST', body: payload }),
  register: (payload) => request('/auth/register', { method: 'POST', body: payload }),
  logout: () => request('/auth/logout', { method: 'POST' }),
  getAdminDashboard: () => request('/admin/dashboard'),
  updateCompany: (companyName, payload) => request(`/admin/companies/${encodeURIComponent(companyName)}`, { method: 'PATCH', body: payload }),
  updateStudent: (enrollment, payload) => request(`/admin/students/${encodeURIComponent(enrollment)}`, { method: 'PATCH', body: payload }),
  updateDrive: (driveId, payload) => request(`/admin/drives/${encodeURIComponent(driveId)}`, { method: 'PATCH', body: payload }),
  getCompanyDashboard: () => request('/company/dashboard'),
  createCompanyDrive: (payload) => request('/company/drives', { method: 'POST', body: payload }),
  updateApplication: (applicationId, payload) => request(`/applications/${encodeURIComponent(applicationId)}`, { method: 'PATCH', body: payload }),
  getStudentDashboard: () => request('/student/dashboard'),
  updateStudentProfile: (payload) => request('/student/profile', { method: 'PATCH', body: payload }),
  applyToDrive: (driveId, payload) => request(`/drives/${encodeURIComponent(driveId)}/apply`, { method: 'POST', body: payload })
};
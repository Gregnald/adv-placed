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
  updateCompanyProfile: (payload) => request('/company/profile', { method: 'PATCH', body: payload }),
  createCompanyDrive: (payload) => request('/company/drives', { method: 'POST', body: payload }),

  updateApplication: (applicationId, payload) => request(`/applications/${encodeURIComponent(applicationId)}`, { method: 'PATCH', body: payload }),
  getStudentDashboard: () => request('/student/dashboard'),
  updateStudentProfile: (payload) => request('/student/profile', { method: 'PATCH', body: payload }),
  applyToDrive: (driveId, payload) => request(`/drives/${encodeURIComponent(driveId)}/apply`, { method: 'POST', body: payload }),

  downloadBlob: (content, filename, mimeType = 'text/csv;charset=utf-8;') => {
    const blob = content instanceof Blob ? content : new Blob([content], { type: mimeType });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.style.display = 'none';
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    setTimeout(() => {
      if (document.body.contains(a)) {
        document.body.removeChild(a);
      }
      window.URL.revokeObjectURL(url);
    }, 200);
  },
  downloadCsv: async (taskId, filename = 'export.csv') => {
    const sessionId = localStorage.getItem('sessionId') || '';
    const res = await fetch(`${API_BASE}/export/download/${taskId}`, {
      headers: { 'X-Session-Id': sessionId }
    });
    if (!res.ok) throw new Error('Failed to download CSV');
    const text = await res.text();
    api.downloadBlob(text, filename, 'text/csv;charset=utf-8;');
  },
  exportAndDownload: async (entity, extraId = '', filename = 'export.csv') => {
    try {
      const { taskId } = await request('/export/csv', { method: 'POST', body: { entity, extraId } });
      let attempts = 0;
      while (attempts < 30) {
        const statusRes = await request(`/export/status/${taskId}`);
        if (statusRes.status === 'SUCCESS') {
          await api.downloadCsv(taskId, filename);
          return;
        }
        await new Promise((r) => setTimeout(r, 300));
        attempts++;
      }
    } catch (e) {
      console.warn('Task export fallback triggered:', e);
    }

    // Direct instant fallback
    const sessionId = localStorage.getItem('sessionId') || '';
    const query = new URLSearchParams({ entity, extraId });
    const res = await fetch(`${API_BASE}/export/direct?${query}`, {
      headers: { 'X-Session-Id': sessionId }
    });
    if (!res.ok) throw new Error('Export failed');
    const text = await res.text();
    api.downloadBlob(text, filename, 'text/csv;charset=utf-8;');
  },
  generateAndDownloadCompanyReport: async (companyId = null) => {
    const body = companyId ? { company_id: companyId } : undefined;
    const { taskId } = await request('/company/report/generate', { method: 'POST', body });
    const sessionId = localStorage.getItem('sessionId') || '';
    let attempts = 0;
    while (attempts < 30) {
      const statusRes = await request(`/export/status/${taskId}`);
      if (statusRes.status === 'SUCCESS') {
        const res = await fetch(`${API_BASE}/company/report/download/${taskId}`, {
          headers: { 'X-Session-Id': sessionId }
        });
        if (!res.ok) throw new Error('Failed to download report');
        const text = await res.text();
        api.downloadBlob(text, `monthly_report_${taskId.slice(0, 8)}.html`, 'text/html;charset=utf-8;');
        return;
      }
      await new Promise((r) => setTimeout(r, 300));
      attempts++;
    }
    throw new Error('Report generation timed out');
  }
};



const API_BASE = 'http://localhost:8000/api';

const handleResponse = async (res) => {
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `HTTP Error ${res.status}: ${res.statusText}`);
  }
  return res.json();
};

export const api = {
  // Health
  async checkHealth() {
    const res = await fetch(`${API_BASE}/health`);
    return handleResponse(res);
  },

  // Settings
  async getSettings() {
    const res = await fetch(`${API_BASE}/settings`);
    return handleResponse(res);
  },

  async updateSetting(key, value) {
    const res = await fetch(`${API_BASE}/settings`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ key, value })
    });
    return handleResponse(res);
  },

  // Profile
  async getProfile() {
    const res = await fetch(`${API_BASE}/profile`);
    return handleResponse(res);
  },

  async uploadResume(file) {
    const formData = new FormData();
    formData.append('file', file);
    const res = await fetch(`${API_BASE}/profile/upload`, {
      method: 'POST',
      body: formData
    });
    return handleResponse(res);
  },

  async saveProfile(profileData) {
    const res = await fetch(`${API_BASE}/profile/save`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(profileData)
    });
    return handleResponse(res);
  },

  // Jobs Scraper / Aggregator
  async triggerScan(keywords = null, locations = null) {
    const res = await fetch(`${API_BASE}/jobs/scrape`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ keywords, locations })
    });
    return handleResponse(res);
  },

  async pasteJobUrl(url) {
    const res = await fetch(`${API_BASE}/jobs/pasted`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url })
    });
    return handleResponse(res);
  },

  async getJobs(status = null) {
    let url = `${API_BASE}/jobs`;
    if (status) url += `?status=${status}`;
    const res = await fetch(url);
    return handleResponse(res);
  },

  async updateJobStatus(jobId, status) {
    const res = await fetch(`${API_BASE}/jobs/${jobId}/status`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status })
    });
    return handleResponse(res);
  },

  // ATS Optimization
  async optimizeJobAssets(jobId) {
    const res = await fetch(`${API_BASE}/jobs/${jobId}/optimize`, {
      method: 'POST'
    });
    return handleResponse(res);
  },

  async getApplicationAssets(jobId) {
    const res = await fetch(`${API_BASE}/applications/${jobId}`);
    return handleResponse(res);
  },

  async saveApplicationNotes(jobId, notesData) {
    const res = await fetch(`${API_BASE}/applications/${jobId}/save_notes`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(notesData)
    });
    return handleResponse(res);
  },

  // Playwright Automation Engine
  async executeApply(jobId, mode = 'interactive') {
    const res = await fetch(`${API_BASE}/jobs/${jobId}/apply`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ mode })
    });
    return handleResponse(res);
  },

  // Stats
  async getStats() {
    const res = await fetch(`${API_BASE}/dashboard/stats`);
    return handleResponse(res);
  }
};

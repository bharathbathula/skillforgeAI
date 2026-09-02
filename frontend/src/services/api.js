const API_BASE_URL = '/api/v1';

// Token helpers
export const getToken = () => localStorage.getItem('skillforge_token');
export const setToken = (token) => localStorage.setItem('skillforge_token', token);
export const removeToken = () => localStorage.removeItem('skillforge_token');

// Generic Fetch wrapper with Authorization header
async function request(endpoint, options = {}) {
  const token = getToken();
  const headers = {
    ...options.headers,
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  if (!(options.body instanceof FormData) && !headers['Content-Type']) {
    headers['Content-Type'] = 'application/json';
  }

  const config = {
    ...options,
    headers,
  };

  const response = await fetch(`${API_BASE_URL}${endpoint}`, config);
  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(data.detail || 'An error occurred with the request');
  }

  return data;
}

// 1. Authentication API
export const authService = {
  register: (userData) => request('/auth/register', {
    method: 'POST',
    body: JSON.stringify({
      email: userData.email,
      password: userData.password,
      full_name: userData.fullname || userData.full_name
    })
  }),
  login: (credentials) => request('/auth/login/json', {
    method: 'POST',
    body: JSON.stringify(credentials)
  }),
  getMe: () => request('/auth/me', { method: 'GET' }),
};

// 2. Resume API
export const resumeService = {
  upload: (formData) => request('/resumes/upload', { method: 'POST', body: formData }),
  getHistory: () => request('/resumes/', { method: 'GET' }),
  getResume: (id) => request(`/resumes/${id}`, { method: 'GET' }),
  deleteResume: (id) => request(`/resumes/${id}`, { method: 'DELETE' }),
};

// 3. Job Description API
export const jobDescService = {
  create: (data) => request('/jobdescription/', { method: 'POST', body: JSON.stringify(data) }),
  getJobDesc: (id) => request(`/jobdescription/${id}`, { method: 'GET' }),
  deleteJobDesc: (id) => request(`/jobdescription/${id}`, { method: 'DELETE' }),
};

// 4. Analysis Pipeline API
export const analysisService = {
  startAnalysis: (resumeId, payload = {}) => request(`/analysis/${resumeId}`, {
    method: 'POST',
    body: JSON.stringify(payload)
  }),
  getAnalysis: (resumeId) => request(`/analysis/${resumeId}`, { method: 'GET' }),
  getStatus: (resumeId) => request(`/analysis/${resumeId}/status`, { method: 'GET' }),
};

// 5. ATS Report API
export const atsService = {
  getScore: (resumeId) => request(`/ats/${resumeId}`, { method: 'GET' }),
  getReport: (resumeId) => request(`/ats/${resumeId}/report`, { method: 'GET' }),
};

// 6. Dashboard API
export const dashboardService = {
  getDashboard: async () => {
    const resumes = await resumeService.getHistory();
    const recent = resumes.length > 0 ? resumes[0] : null;
    return {
      total_resumes: resumes.length,
      recent_resume: recent,
      recent_job_description: recent?.job_descriptions?.[0] || null
    };
  },
};

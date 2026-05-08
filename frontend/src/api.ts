import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'https://healthcare-api-sv6r.onrender.com/api/v1';

export const apiClient = axios.create({
  baseURL: API_URL,
  headers: { 'Content-Type': 'application/json' },
});

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export const authAPI = {
  login: async (email: string, password: string) => {
    const form = new FormData();
    form.append('username', email);
    form.append('password', password);
    const { data } = await apiClient.post('/auth/login', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    localStorage.setItem('token', data.access_token);
    return data;
  },
  logout: () => localStorage.removeItem('token'),
};

export const patientAPI = {
  list: (search?: string, skip = 0, limit = 50) =>
    apiClient.get('/patients/', { params: { search, skip, limit } }).then(r => r.data),
  get: (id: string) =>
    apiClient.get(`/patients/${id}`).then(r => r.data),
};

export const riskAPI = {
  predict: (patientId: string) =>
    apiClient.post(`/risk/predict/${patientId}`).then(r => r.data),
  getHistory: (patientId: string) =>
    apiClient.get(`/risk/scores/${patientId}`).then(r => r.data),
};

export const analyticsAPI = {
  getPopulation: () =>
    apiClient.get('/analytics/population').then(r => r.data),
  getHighRisk: () =>
    apiClient.get('/analytics/high-risk').then(r => r.data),
  getTrends: () =>
    apiClient.get('/analytics/trends').then(r => r.data),
};
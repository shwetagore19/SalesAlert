import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 20000,
});

export const dashboardApi = {
  getToday: async (dateStr) => {
    const params = dateStr ? { date: dateStr } : {};
    const res = await apiClient.get('/dashboard/today', { params });
    return res.data;
  },
  getTrends: async (days = 30) => {
    const res = await apiClient.get('/dashboard/trends', { params: { days } });
    return res.data.trends || [];
  },
  getMetadata: async () => {
    const res = await apiClient.get('/dashboard/metadata');
    return res.data;
  },
};

export const salesApi = {
  getSales: async (limit = 50, category, region) => {
    const params = { limit };
    if (category) params.category = category;
    if (region) params.region = region;
    const res = await apiClient.get('/sales', { params });
    return res.data;
  },
  getProducts: async (dateStr) => {
    const params = dateStr ? { date: dateStr } : {};
    const res = await apiClient.get('/products/performance', { params });
    return res.data;
  },
  getRegions: async (dateStr) => {
    const params = dateStr ? { date: dateStr } : {};
    const res = await apiClient.get('/regions/performance', { params });
    return res.data;
  },
};

export const alertApi = {
  getAlerts: async (dateStr) => {
    const params = dateStr ? { date: dateStr } : {};
    const res = await apiClient.get('/alerts', { params });
    return res.data.alerts || [];
  },
};

export const reportApi = {
  getLatest: async (dateStr) => {
    const params = dateStr ? { date: dateStr } : {};
    const res = await apiClient.get('/reports/latest', { params });
    return res.data;
  },
  triggerDailyUpdate: async (payload = {}) => {
    const res = await apiClient.post('/daily-update', payload);
    return res.data;
  },
  sendEmail: async (payload = {}) => {
    const res = await apiClient.post('/reports/email', payload);
    return res.data;
  },
  sendWhatsApp: async (payload = {}) => {
    const res = await apiClient.post('/reports/whatsapp', payload);
    return res.data;
  },
};

export const intelligenceApi = {
  getRootCause: async (dateStr) => {
    const params = dateStr ? { date: dateStr } : {};
    const res = await apiClient.get('/intelligence/root-cause', { params });
    return res.data;
  },
  getRecommendations: async (dateStr) => {
    const params = dateStr ? { date: dateStr } : {};
    const res = await apiClient.get('/intelligence/recommendations', { params });
    return res.data.recommendations || [];
  },
  getChannels: async (dateStr) => {
    const params = dateStr ? { date: dateStr } : {};
    const res = await apiClient.get('/intelligence/channels', { params });
    return res.data.channels || [];
  },
  getDiscountImpact: async () => {
    const res = await apiClient.get('/intelligence/discount-impact');
    return res.data;
  },
};


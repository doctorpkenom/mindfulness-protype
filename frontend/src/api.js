import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

export const userApi = {
    getAll: () => api.get('/users/'),
    create: (userData) => api.post('/users/', userData),
    get: (name) => api.get(`/users/${name}`),
    delete: (name) => api.delete(`/users/${name}`),
};

export const researchApi = {
    getStrategies: (tag) => api.get('/research/strategies', { params: { tag } }),
    generatePlan: (context) => api.post('/research/plan/composite', context),
};

export const simulationApi = {
    run: (userName, days = 30) => api.post('/simulation/run', { user_name: userName, days }),
    getHistory: (userName) => api.get(`/simulation/history/${userName}`),
};

export const analyticsApi = {
    getDashboardStats: () => api.get('/analytics/dashboard'),
    getModelMetrics: () => api.get('/analytics/models'),
    getInteractionTrends: (days = 30) => api.get('/analytics/interactions/trends', { params: { days } }),
    getResearchUsage: () => api.get('/analytics/research/usage'),
    getUserInsights: (userId) => api.get(`/analytics/users/${userId}/insights`),
};

export const debugApi = {
    getLogs: (limit = 100, level = null, component = null) => 
        api.get('/debug/logs', { params: { limit, level, component } }),
    createLog: (level, component, message, context = null) =>
        api.post('/debug/logs', { level, component, message, context }),
    testModel: (params) => api.post('/debug/test/model', params),
    testResearchEngine: () => api.get('/debug/test/research'),
    getModelWeights: (modelName) => api.get(`/debug/model/weights/${modelName}`),
    getSystemInfo: () => api.get('/debug/system/info'),
    resetDatabase: (confirm = false) => api.post('/debug/database/reset', null, { params: { confirm } }),
};

export default api;

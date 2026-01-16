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
};

export const researchApi = {
    getStrategies: (tag) => api.get('/research/strategies', { params: { tag } }),
    generatePlan: (context) => api.post('/research/plan/composite', context),
};

export const simulationApi = {
    run: (userName) => api.post('/simulation/run', { user_name: userName }),
};

export default api;

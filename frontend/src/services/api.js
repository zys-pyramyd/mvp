
import axios from 'axios';

// Use environment variable or default to localhost
let backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001/api';
// Ensure the backend URL always points to the /api prefix
if (backendUrl && !backendUrl.endsWith('/api')) {
    backendUrl = `${backendUrl.replace(/\/+$/, '')}/api`;
}
export const API_BASE_URL = backendUrl;

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Add interceptor to include token in requests
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

export default api;

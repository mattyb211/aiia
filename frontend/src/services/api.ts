import axios from 'axios';
import { useAuth } from '../AuthContext';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
});

// Attach token automatically
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token');
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default api;
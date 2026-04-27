import axios from 'axios';
import { auth } from './firebase';

const api = axios.create({
  baseURL: 'https://zh1gkhvulc.execute-api.us-east-1.amazonaws.com',
  headers: { 'Content-Type': 'application/json' },
});

// Attach Firebase ID token to every request.
// getIdToken(true) forces a refresh if the token is within 5 minutes of expiry.
api.interceptors.request.use(async (config) => {
  const user = auth.currentUser;
  if (user) {
    const token = await user.getIdToken(/* forceRefresh= */ false);
    config.headers['Authorization'] = `Bearer ${token}`;
  }
  return config;
});

// If the server returns 401 (expired token), force-refresh once and retry.
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config;
    if (error.response?.status === 401 && !original._retried) {
      original._retried = true;
      const user = auth.currentUser;
      if (user) {
        const token = await user.getIdToken(/* forceRefresh= */ true);
        original.headers['Authorization'] = `Bearer ${token}`;
        return api(original);
      }
    }
    return Promise.reject(error);
  }
);

export const decodeJob = (jobDescription) =>
  api.post('/decode-job', { jobDescription });

export const tailorResume = (jobDescription, resumeText = '') =>
  api.post('/tailor-resume', { jobDescription, resumeText });

export const generateOutreach = (jobDescription, type = 'linkedin', name = '', skills = '') =>
  api.post('/outreach', { jobDescription, type, name, skills });

export const getApplications = () =>
  api.get('/applications');

export const getApplication = (id) =>
  api.get(`/applications/${id}`);

export const createApplication = (data) =>
  api.post('/applications', data);

export const updateApplication = (id, data) =>
  api.put(`/applications/${id}`, data);

export const deleteApplication = (id) =>
  api.delete(`/applications/${id}`);

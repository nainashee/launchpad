import axios from 'axios';
import { auth } from './firebase';

const api = axios.create({
  baseURL: 'https://zh1gkhvulc.execute-api.us-east-1.amazonaws.com',
  headers: { 'Content-Type': 'application/json' },
});

const uid = () => auth.currentUser?.uid ?? 'default';

export const decodeJob = (jobDescription) =>
  api.post('/decode-job', { jobDescription, userId: uid() });

export const tailorResume = (jobDescription, resumeText = '') =>
  api.post('/tailor-resume', { jobDescription, resumeText, userId: uid() });

export const generateOutreach = (jobDescription, type = 'linkedin') =>
  api.post('/outreach', { jobDescription, type, userId: uid() });

export const getApplications = () =>
  api.get('/applications', { params: { userId: uid() } });

export const getApplication = (id) =>
  api.get(`/applications/${id}`, { params: { userId: uid() } });

export const createApplication = (data) =>
  api.post('/applications', { ...data, userId: uid() });

export const updateApplication = (id, data) =>
  api.put(`/applications/${id}`, data, { params: { userId: uid() } });

export const deleteApplication = (id) =>
  api.delete(`/applications/${id}`, { params: { userId: uid() } });

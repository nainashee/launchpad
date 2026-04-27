import axios from 'axios';

const api = axios.create({
  baseURL: 'https://zh1gkhvulc.execute-api.us-east-1.amazonaws.com',
  headers: { 'Content-Type': 'application/json' },
});

export const decodeJob = (jobDescription) =>
  api.post('/decode-job', { jobDescription });

export const tailorResume = (jobDescription, userId = 'default') =>
  api.post('/tailor-resume', { jobDescription, userId });

export const generateOutreach = (jobDescription, userId = 'default') =>
  api.post('/outreach', { jobDescription, userId });

export const getApplications = (userId = 'default') =>
  api.get('/applications', { params: { userId } });

export const getApplication = (id) =>
  api.get(`/applications/${id}`);

export const createApplication = (data) =>
  api.post('/applications', data);

export const updateApplication = (id, data) =>
  api.put(`/applications/${id}`, data);

export const deleteApplication = (id) =>
  api.delete(`/applications/${id}`);

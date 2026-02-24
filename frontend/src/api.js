// api.js — Axios client that talks to our FastAPI backend
import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
    baseURL: API_BASE,
    headers: { 'Content-Type': 'application/json' },
    timeout: 10000,
});

// ── Jobs ──────────────────────────────────────────────────────────────────────
export const triggerBackup = (filters = null) =>
    api.post('/api/v1/jobs/backup', { filters }).then(r => r.data);

export const getJobStatus = (jobId) =>
    api.get(`/api/v1/jobs/${jobId}`).then(r => r.data);

// ── Devices ───────────────────────────────────────────────────────────────────
export const getDevices = () =>
    api.get('/api/v1/devices/').then(r => r.data);

// ── Health ────────────────────────────────────────────────────────────────────
export const getHealth = () =>
    api.get('/health').then(r => r.data);

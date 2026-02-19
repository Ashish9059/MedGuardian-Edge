/**
 * MedGuardian Edge - API Service Layer
 * All communication with the FastAPI backend.
 */

import axios from 'axios';

const api = axios.create({
    baseURL: '/api',
    headers: { 'Content-Type': 'application/json' },
    timeout: 120000, // 2 minutes for LLM inference
});

// ─────────────────────────────────────────────
// 1. Patient Risk Assessment
// ─────────────────────────────────────────────
export const assessRisk = (payload) => api.post('/risk/assess', payload).then((r) => r.data);

// ─────────────────────────────────────────────
// 2. Lab Report Analysis
// ─────────────────────────────────────────────
export const analyzeLab = (payload) => api.post('/lab/analyze', payload).then((r) => r.data);

// ─────────────────────────────────────────────
// 3. Prescription Safety
// ─────────────────────────────────────────────
export const checkPrescription = (payload) =>
    api.post('/prescription/check', payload).then((r) => r.data);

// ─────────────────────────────────────────────
// 4. SOAP Note
// ─────────────────────────────────────────────
export const generateSoap = (payload) =>
    api.post('/documentation/soap', payload).then((r) => r.data);

// ─────────────────────────────────────────────
// 5. Patient Explanation
// ─────────────────────────────────────────────
export const generateExplanation = (payload) =>
    api.post('/documentation/explain', payload).then((r) => r.data);

// ─────────────────────────────────────────────
// Health Check
// ─────────────────────────────────────────────
export const checkHealth = () =>
    axios.get('/health').then((r) => r.data).catch(() => ({ status: 'unreachable' }));

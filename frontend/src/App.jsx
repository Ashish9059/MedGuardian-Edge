import React, { useState, useEffect } from 'react';
import PatientForm from './components/PatientForm';
import LabInput from './components/LabInput';
import PrescriptionInput from './components/PrescriptionInput';
import ResultsPanel from './components/ResultsPanel';
import './index.css';

/**
 * MedGuardian Protocol v3.1 — Humane Clinical Intelligence Suite
 * Focus: Multimodal functionality, human-centered layout, and production-grade stability.
 */

const DevDebugPanel = ({ mode, imageAttached, payloadSize, responseTime }) => {
    return (
        <div className="dev-debug-panel">
            <h5>🛠 System Telemetry (Dev Mode)</h5>
            <div className="debug-grid">
                <div className="debug-item">Mode: <span className="debug-val">{mode}</span></div>
                <div className="debug-item">Vision: <span className="debug-val">{imageAttached ? 'ACTIVE' : 'OFF'}</span></div>
                <div className="debug-item">Payload: <span className="debug-val">{payloadSize} KB</span></div>
                <div className="debug-item">RTT: <span className="debug-val">{responseTime || '---'}s</span></div>
            </div>
        </div>
    );
};

function App() {
    const [patient, setPatient] = useState({
        age: '',
        gender: '',
        symptoms: [],
        comorbidities: [],
        vitals: {}
    });
    const [lab, setLab] = useState({
        lab_text: '',
        patient_context: '',
        image_data: null
    });
    const [prescription, setPrescription] = useState({
        medications: [],
        patient_age: undefined,
        patient_conditions: []
    });

    const [results, setResults] = useState(null);
    const [loading, setLoading] = useState(false);
    const [errors, setErrors] = useState([]);
    const [activeTab, setActiveTab] = useState('risk');
    const [ollamaStatus, setOllamaStatus] = useState('disconnected');
    const [stats, setStats] = useState({ mode: 'TEXT', payloadSize: 0, responseTime: 0 });

    useEffect(() => {
        const checkHealth = async () => {
            try {
                const res = await fetch('http://localhost:8000/health');
                if (res.ok) setOllamaStatus('connected');
                else setOllamaStatus('error');
            } catch {
                setOllamaStatus('disconnected');
            }
        };
        checkHealth();
        const interval = setInterval(checkHealth, 5000);
        return () => clearInterval(interval);
    }, []);

    const handleAnalyze = async () => {
        setLoading(true);
        setErrors([]);
        const startTime = Date.now();

        try {
            const payload = {
                patient,
                lab: {
                    ...lab,
                    image_data: lab.image_data || null
                },
                prescription
            };

            const payloadSize = Math.round(JSON.stringify(payload).length / 1024);

            const response = await fetch('http://localhost:8000/api/v4/analyze/full', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'V4 Analysis Protocol failed');
            }

            const data = await response.json();
            console.log("MedGuardian V4 Response Payload:", data);
            setResults(data);
            setActiveTab('risk');

            setStats({
                mode: lab.image_data ? 'VISION' : 'TEXT',
                payloadSize,
                responseTime: ((Date.now() - startTime) / 1000).toFixed(2)
            });

        } catch (err) {
            setErrors([err.message]);
        } finally {
            setLoading(false);
        }
    };

    const handleReset = () => {
        setPatient({ age: '', gender: '', symptoms: [], comorbidities: [], vitals: {} });
        setLab({ lab_text: '', patient_context: '', image_data: null });
        setPrescription({ medications: [], patient_age: undefined, patient_conditions: [] });
        setResults(null);
        setErrors([]);
        setStats({ mode: 'TEXT', payloadSize: 0, responseTime: 0 });
    };

    return (
        <div className="app">
            <div className="mesh-bg" />
            <div className="glow-anchor" style={{ top: '10%', left: '10%' }} />
            <div className="glow-anchor" style={{ bottom: '20%', right: '15%' }} />

            {loading && (
                <div className="analysis-progress-container">
                    <div className="analysis-progress-bar loading" />
                </div>
            )}

            <header className="app-header entry-fade">
                <div className="header-brand">
                    <span className="header-logo">🛡️</span>
                    <div>
                        <h1>MedGuardian <span className="text-accent">Protocol</span> <span className="tag-v2">v3.1</span></h1>
                        <p className="header-subtitle">Secure Multimodal Clinical Reasoning Suite</p>
                    </div>
                </div>
                <div className={`status-badge ${ollamaStatus}`}>
                    <span className="status-dot" />
                    {ollamaStatus === 'connected' ? 'Clinical Engine Ready' : 'Engine Offline'}
                </div>
            </header>

            <main className="app-main">
                <div className="left-column entry-fade stagger-1">
                    <PatientForm data={patient} onChange={setPatient} />
                    {import.meta.env.DEV && (
                        <DevDebugPanel
                            mode={stats.mode}
                            imageAttached={!!lab.image_data}
                            payloadSize={stats.payloadSize}
                            responseTime={stats.responseTime}
                        />
                    )}
                </div>

                <div className="right-column entry-fade stagger-2">
                    <LabInput data={lab} onChange={setLab} />
                    <PrescriptionInput data={prescription} onChange={setPrescription} />
                </div>
            </main>

            {errors.length > 0 && (
                <div className="validation-errors entry-fade">
                    {errors.map((e, i) => <p key={i}>⚠️ {e}</p>)}
                </div>
            )}

            <div className="action-bar entry-fade stagger-3">
                <button className="btn-reset" onClick={handleReset} disabled={loading}>
                    Reset Protocol
                </button>
                <button
                    className="btn-analyze"
                    onClick={handleAnalyze}
                    disabled={loading || ollamaStatus !== 'connected'}
                >
                    {loading ? (
                        <><span className="spinner" /> Synthesizing Data...</>
                    ) : (
                        <><span className="btn-icon">⚡</span> Execute Clinical Run</>
                    )}
                </button>
            </div>

            <div className="results-container entry-fade">
                <ResultsPanel
                    results={results}
                    activeTab={activeTab}
                    onTabChange={setActiveTab}
                    loading={loading}
                />
            </div>

            <footer className="app-footer entry-fade">
                <p>MedGuardian Protocol v3.1 — Secure Multimodal Clinical Reasoning. Data Processing strictly local.</p>
            </footer>
        </div>
    );
}

export default App;

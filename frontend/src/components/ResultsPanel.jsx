import React, { Component } from 'react';

/**
 * ResultsPanel — Tabbed display for all 5 analysis results.
 */

class ErrorBoundary extends Component {
    constructor(props) {
        super(props);
        this.state = { hasError: false, error: null };
    }
    static getDerivedStateFromError(error) {
        return { hasError: true, error };
    }
    componentDidCatch(error, errorInfo) {
        console.error("ResultsPanel Crash:", error, errorInfo);
    }
    render() {
        if (this.state.hasError) {
            return (
                <div className="alert-box alert-critical">
                    <h4>☢️ Component Render Crash</h4>
                    <p>The UI encountered a failure while processing clinical data.</p>
                    <pre style={{ fontSize: '10px', overflow: 'auto' }}>{this.state.error?.message}</pre>
                    <button className="btn-reset" style={{ marginTop: '1rem' }} onClick={() => window.location.reload()}>
                        Reload Interface
                    </button>
                </div>
            );
        }
        return this.props.children;
    }
}

const TABS = [
    { key: 'risk', label: '🛡️ Risk Profile' },
    { key: 'lab', label: '🧪 Lab Analysis' },
    { key: 'prescription', label: '💊 Drug Safety' },
    { key: 'soap', label: '📖 SOAP Notes' },
    { key: 'explanation', label: '🤝 Patient Guide' },
];

const SEVERITY_CLASS = {
    High: 'badge badge-high',
    Medium: 'badge badge-medium',
    Low: 'badge badge-low',
    Major: 'badge badge-high',
    Moderate: 'badge badge-medium',
    Minor: 'badge badge-low',
    Critical: 'badge badge-high',
};

const SkeletonLoader = () => (
    <div className="skeleton-container entry-fade">
        <div className="skeleton skeleton-title" />
        <div className="skeleton skeleton-text" />
        <div className="skeleton skeleton-text" />
        <div className="skeleton skeleton-rect" />
    </div>
);

function RiskTab({ data, loading }) {
    if (loading) return <SkeletonLoader />;
    if (!data) return <EmptyState />;
    if (data.error) return <div className="alert-box alert-critical"><strong>Protocol Error:</strong> {data.error}</div>;
    const safetyAlerts = data.safety_alerts || [];
    const redFlags = data.red_flags || [];
    const differential = data.differential_diagnosis || [];

    return (
        <div className="result-section entry-fade">
            {safetyAlerts.length > 0 && (
                <div className="alert-box alert-critical">
                    <strong>Critical Protocol Alerts</strong>
                    <ul>
                        {safetyAlerts.map((a, i) => <li key={i}>{a}</li>)}
                    </ul>
                </div>
            )}

            <div className="result-row">
                <div className="result-item">
                    <span className="result-label">Calculated Risk:</span>
                    <span className={SEVERITY_CLASS[data.risk_level] || 'badge'}>{data.risk_level}</span>
                </div>
                <div className="result-item">
                    <span className="result-label">AI Confidence:</span>
                    <span className={SEVERITY_CLASS[data.confidence] || 'badge'}>{data.confidence}</span>
                </div>
            </div>

            {data.red_flags?.length > 0 && (
                <div className="result-block">
                    <h4>🚩 Clinical Red Flags</h4>
                    <ul className="result-list">
                        {data.red_flags.map((f, i) => <li key={i}>{f}</li>)}
                    </ul>
                </div>
            )}

            {data.differential_diagnosis?.length > 0 && (
                <div className="result-block">
                    <h4>🔬 Differential Considerations</h4>
                    <ol className="result-list">
                        {data.differential_diagnosis.map((d, i) => <li key={i}>{d}</li>)}
                    </ol>
                </div>
            )}

            <div className="result-block">
                <h4>✅ Primary Recommendation</h4>
                <p className="result-text">{data.recommended_action}</p>
            </div>
        </div>
    );
}

function LabTab({ data, loading }) {
    if (loading) return <SkeletonLoader />;
    if (!data) return <EmptyState />;
    if (data.error) return <div className="alert-box alert-critical"><strong>Laboratory Protocol Error:</strong> {data.error}</div>;

    const abnormalValues = data.abnormal_values || [];
    return (
        <div className="result-section entry-fade">
            {abnormalValues.length > 0 && (
                <div className="result-block">
                    <h4>📊 Physiological Abnormalities</h4>
                    <table className="clinical-table">
                        <thead>
                            <tr>
                                <th>Parameter</th>
                                <th>Result</th>
                                <th>Ref. Range</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            {abnormalValues.map((v, i) => (
                                <tr key={i}>
                                    <td>{v?.parameter || 'Unknown'} <span className="spark-tag">TELEMETRY</span></td>
                                    <td className="clinical-data"><strong>{v?.value || 'N/A'}</strong></td>
                                    <td className="muted clinical-data">{v?.reference_range || 'N/A'}</td>
                                    <td><span className={SEVERITY_CLASS[v?.status] || 'badge'}>{v?.status || 'NORMAL'}</span></td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}
            <div className="result-block">
                <h4>🔍 Synthesis & Interpretation</h4>
                <p className="result-text">{data.clinical_interpretation}</p>
            </div>
            <div className="result-block">
                <h4>⚠️ Diagnostic Summary</h4>
                <p className="result-text">{data.risk_summary}</p>
            </div>
        </div>
    );
}

function PrescriptionTab({ data, loading }) {
    if (loading) return <SkeletonLoader />;
    if (!data) return <EmptyState />;
    if (data.error) return <div className="alert-box alert-critical"><strong>Medication Check Error:</strong> {data.error}</div>;

    const drugInteractions = data.drug_interactions || [];
    const contraindications = data.contraindications || [];
    const safetyWarnings = data.safety_warnings || [];

    return (
        <div className="result-section entry-fade">
            {drugInteractions.length > 0 && (
                <div className="result-block">
                    <h4>⚡ High-Risk Interactions</h4>
                    {drugInteractions.map((d, i) => (
                        <div key={i} className="interaction-card">
                            <div className="interaction-header">
                                <span className="drug-name">{d?.drug_a || 'Med A'}</span>
                                <span className="interaction-arrow">↔</span>
                                <span className="drug-name">{d?.drug_b || 'Med B'}</span>
                                <span className={SEVERITY_CLASS[d?.severity] || 'badge'}>{d?.severity || 'LOW'}</span>
                            </div>
                            <p className="interaction-desc">{d?.description || 'No description available.'}</p>
                        </div>
                    ))}
                </div>
            )}
            {data.contraindications?.length > 0 && (
                <div className="result-block">
                    <h4>🚫 Absolute Contraindications</h4>
                    <ul className="result-list">
                        {data.contraindications.map((c, i) => <li key={i}>{c}</li>)}
                    </ul>
                </div>
            )}
            {data.safety_warnings?.length > 0 && (
                <div className="result-block">
                    <h4>⚠️ Safety Considerations</h4>
                    <ul className="result-list">
                        {data.safety_warnings.map((w, i) => <li key={i}>{w}</li>)}
                    </ul>
                </div>
            )}
            {!data.drug_interactions?.length && !data.contraindications?.length && !data.safety_warnings?.length && (
                <div className="alert-box alert-safe">✅ Protocol confirmed: No significant interactions detected.</div>
            )}
        </div>
    );
}

function SoapTab({ data, loading }) {
    if (loading) return <SkeletonLoader />;
    if (!data) return <EmptyState />;
    if (data.error) return <div className="alert-box alert-critical"><strong>Documentation Engine Error:</strong> {data.error}</div>;
    const sections = [
        { key: 'subjective', label: 'Subjective Evidence', icon: '📢' },
        { key: 'objective', label: 'Objective Observations', icon: '🧬' },
        { key: 'assessment', label: 'Clinical Assessment', icon: '🧠' },
        { key: 'plan', label: 'Diagnostic & Care Plan', icon: '📝' },
    ];
    return (
        <div className="result-section entry-fade">
            {sections.map(({ key, label, icon }) => (
                <div key={key} className="soap-block">
                    <h4>{icon} {label}</h4>
                    <p className="result-text">{data[key]}</p>
                </div>
            ))}
        </div>
    );
}

function ExplanationTab({ data, loading }) {
    if (loading) return <SkeletonLoader />;
    if (!data) return <EmptyState />;
    if (data.error) return <div className="alert-box alert-critical"><strong>Synthesis Protocol Error:</strong> {data.error}</div>;
    return (
        <div className="result-section entry-fade">
            <div className="result-block">
                <h4>💬 Patient Briefing</h4>
                <p className="result-text">{data.explanation}</p>
            </div>
            {data.key_points?.length > 0 && (
                <div className="result-block">
                    <h4>📌 Essential Points</h4>
                    <ul className="result-list key-points">
                        {data.key_points.map((p, i) => <li key={i}>{p}</li>)}
                    </ul>
                </div>
            )}
            <div className="result-block">
                <h4>➡️ Next Steps for Care</h4>
                <p className="result-text follow-up">{data.follow_up_advice}</p>
            </div>
        </div>
    );
}

function EmptyState() {
    return (
        <div className="empty-state glass-3-0">
            <div className="empty-content">
                <span className="empty-icon">📂</span>
                <p>Clinical Intelligence Standby. Initiate analysis protocol to generate telemetry profiles.</p>
            </div>
        </div>
    );
}

export default function ResultsPanel({ results, activeTab, onTabChange, loading }) {
    // Null guard to prevent crash before results are generated
    const safeResults = results || {
        risk: null,
        lab: null,
        prescription: null,
        soap: null,
        explanation: null
    };

    const tabComponents = {
        risk: <RiskTab data={safeResults.risk} loading={loading} />,
        lab: <LabTab data={safeResults.lab} loading={loading} />,
        prescription: <PrescriptionTab data={safeResults.prescription} loading={loading} />,
        soap: <SoapTab data={safeResults.soap} loading={loading} />,
        explanation: <ExplanationTab data={safeResults.explanation} loading={loading} />,
    };

    return (
        <section className="results-panel glass-3-0 entry-fade">
            <div className="card-header-flex">
                <h2 className="card-title">
                    <span className="icon">🛰️</span> Clinical Intelligence Dashboard
                </h2>
                {loading && <span className="tab-status-loading">Engine Syncing...</span>}
            </div>
            <div className="tabs">
                {TABS.map((tab) => (
                    <button
                        key={tab.key}
                        className={`tab-btn ${activeTab === tab.key ? 'tab-active' : ''}`}
                        onClick={() => !loading && onTabChange(tab.key)}
                        disabled={loading && activeTab !== tab.key}
                    >
                        {tab.label}
                        {safeResults[tab.key] && !loading && <span className="tab-dot" />}
                    </button>
                ))}
            </div>
            <div className="tab-content transition-fade">
                <ErrorBoundary key={activeTab}>
                    {tabComponents[activeTab]}
                </ErrorBoundary>
            </div>
        </section>
    );
}

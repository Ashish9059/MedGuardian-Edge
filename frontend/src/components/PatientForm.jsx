import React from 'react';

/**
 * PatientForm — Left panel for patient demographics, symptoms, vitals, and comorbidities.
 */
export default function PatientForm({ data, onChange }) {
    const handleVital = (field, value) => {
        onChange({
            ...data,
            vitals: { ...data.vitals, [field]: value === '' ? undefined : Number(value) },
        });
    };

    const handleSymptoms = (value) => {
        onChange({ ...data, symptoms: value.split(',').map((s) => s.trim()).filter(Boolean) });
    };

    const handleComorbidities = (value) => {
        onChange({ ...data, comorbidities: value.split(',').map((s) => s.trim()).filter(Boolean) });
    };

    return (
        <section className="card glass-3-0 entry-fade">
            <div className="card-header-flex">
                <h2 className="card-title">
                    <span className="icon">👤</span> Patient Demographics
                </h2>
            </div>

            <div className="form-row">
                <div className="form-group">
                    <label htmlFor="age">Age <span className="hint">(Years)</span></label>
                    <input
                        id="age"
                        type="number"
                        min="0"
                        max="130"
                        placeholder="45"
                        value={data.age}
                        className="clinical-data"
                        onChange={(e) => onChange({ ...data, age: e.target.value })}
                    />
                </div>
                <div className="form-group">
                    <label htmlFor="gender">Gender</label>
                    <select
                        className="clinical-data"
                        value={data.gender}
                        onChange={(e) => onChange({ ...data, gender: e.target.value })}
                    >
                        <option value="">Select...</option>
                        <option value="Male">Male</option>
                        <option value="Female">Female</option>
                        <option value="Other">Other</option>
                    </select>
                </div>
            </div>

            <div className="form-group">
                <label htmlFor="symptoms">Presenting Symptoms <span className="hint">(Comma-separated)</span></label>
                <textarea
                    id="symptoms"
                    rows={3}
                    placeholder="e.g., Acute chest pain, shortness of breath..."
                    value={data.symptoms.join(', ')}
                    onChange={(e) => handleSymptoms(e.target.value)}
                />
            </div>

            <div className="form-group">
                <label htmlFor="comorbidities">Comorbidities <span className="hint">(Clinical History)</span></label>
                <textarea
                    id="comorbidities"
                    rows={2}
                    placeholder="e.g., Type 2 Diabetes, Stage II Hypertension..."
                    value={(data.comorbidities || []).join(', ')}
                    onChange={(e) => handleComorbidities(e.target.value)}
                />
            </div>

            <h3 className="section-subtitle">Clinical Vitals <span className="hint">(Standard observations)</span></h3>
            <div className="vitals-grid">
                <div className="form-group">
                    <label htmlFor="sbp">Systolic BP</label>
                    <input id="sbp" className="clinical-data" type="number" placeholder="120" value={data.vitals?.systolic_bp ?? ''} onChange={(e) => handleVital('systolic_bp', e.target.value)} />
                </div>
                <div className="form-group">
                    <label htmlFor="dbp">Diastolic BP</label>
                    <input id="dbp" className="clinical-data" type="number" placeholder="80" value={data.vitals?.diastolic_bp ?? ''} onChange={(e) => handleVital('diastolic_bp', e.target.value)} />
                </div>
                <div className="form-group">
                    <label htmlFor="hr">Heart Rate</label>
                    <input id="hr" className="clinical-data" type="number" placeholder="72" value={data.vitals?.heart_rate ?? ''} onChange={(e) => handleVital('heart_rate', e.target.value)} />
                </div>
                <div className="form-group">
                    <label htmlFor="temp">Temp (°C)</label>
                    <input id="temp" className="clinical-data" type="number" step="0.1" placeholder="37.0" value={data.vitals?.temperature ?? ''} onChange={(e) => handleVital('temperature', e.target.value)} />
                </div>
                <div className="form-group">
                    <label htmlFor="spo2">SpO₂ (%)</label>
                    <input id="spo2" className="clinical-data" type="number" step="0.1" placeholder="98" value={data.vitals?.spo2 ?? ''} onChange={(e) => handleVital('spo2', e.target.value)} />
                </div>
                <div className="form-group">
                    <label htmlFor="rr">Resp. Rate</label>
                    <input id="rr" className="clinical-data" type="number" placeholder="16" value={data.vitals?.respiratory_rate ?? ''} onChange={(e) => handleVital('respiratory_rate', e.target.value)} />
                </div>
            </div>
        </section>
    );
}

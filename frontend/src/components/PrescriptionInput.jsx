import React from 'react';

/**
 * PrescriptionInput — Input for medication list and patient context.
 */
export default function PrescriptionInput({ data, onChange }) {
    const handleMedications = (value) => {
        onChange({
            ...data,
            medications: value.split(',').map((m) => m.trim()).filter(Boolean),
        });
    };

    const handleConditions = (value) => {
        onChange({
            ...data,
            patient_conditions: value.split(',').map((c) => c.trim()).filter(Boolean),
        });
    };

    return (
        <section className="card glass-3-0 entry-fade">
            <div className="card-header-flex">
                <h2 className="card-title">
                    <span className="icon">💊</span> Medication & Safety Check
                </h2>
            </div>

            <div className="form-group">
                <label htmlFor="medications">
                    Active Medications <span className="hint">(Comma-separated list)</span>
                </label>
                <textarea
                    id="medications"
                    rows={4}
                    placeholder="e.g., Warfarin 5mg, Aspirin 81mg, Metformin 500mg..."
                    value={data.medications.join(', ')}
                    onChange={(e) => handleMedications(e.target.value)}
                />
            </div>

            <div className="form-row">
                <div className="form-group">
                    <label htmlFor="rx-age">Verified Patient Age</label>
                    <input
                        id="rx-age"
                        type="number"
                        placeholder="65"
                        value={data.patient_age ?? ''}
                        onChange={(e) =>
                            onChange({ ...data, patient_age: e.target.value ? Number(e.target.value) : undefined })
                        }
                    />
                </div>
                <div className="form-group">
                    <label htmlFor="rx-conditions">
                        Relevant Conditions <span className="hint">(Clinical context)</span>
                    </label>
                    <input
                        id="rx-conditions"
                        type="text"
                        placeholder="e.g., Chronic Renal Failure, Peptic Ulcer Disease..."
                        value={(data.patient_conditions || []).join(', ')}
                        onChange={(e) => handleConditions(e.target.value)}
                    />
                </div>
            </div>
        </section>
    );
}

import React, { useState } from 'react';

/**
 * LabInput — Enhanced multimodal lab report analysis UI.
 * Features:
 * - Real-time Mode Detection (TEXT vs VISION)
 * - Active Mode Badges
 * - File Preview & Clear
 */
export default function LabInput({ data, onChange }) {
    const [preview, setPreview] = useState(data.image_data ? `data:image/png;base64,${data.image_data}` : null);
    const isVisionMode = !!data.image_data;

    const handleImageChange = (e) => {
        const file = e.target.files[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onloadend = () => {
            const base64Full = reader.result;
            setPreview(base64Full);

            // Extract raw base64 for backend
            const rawBase64 = base64Full.split(',')[1];
            onChange({ ...data, image_data: rawBase64 });
        };
        reader.readAsDataURL(file);
    };

    const clearImage = () => {
        setPreview(null);
        onChange({ ...data, image_data: null });
    };

    return (
        <section className="card glass-3-0 entry-fade">
            <div className="card-header-flex">
                <h2 className="card-title">
                    <span className="icon">🧪</span> Laboratory Analysis
                </h2>
                <div className="mode-status">
                    {isVisionMode ? (
                        <span className="badge badge-vision animate-pulse">Vision Mode Active</span>
                    ) : (
                        <span className="badge badge-text-mode">Standard Text Mode</span>
                    )}
                </div>
            </div>

            <div className="form-group">
                <label>Multimodal Input <span className="hint">(Upload lab report or manually enter findings)</span></label>
                {!preview ? (
                    <div className="upload-zone" onClick={() => document.getElementById('lab-image-input').click()}>
                        <input
                            id="lab-image-input"
                            type="file"
                            accept="image/*"
                            style={{ display: 'none' }}
                            onChange={handleImageChange}
                        />
                        <span className="upload-icon">📸</span>
                        <p>Drop lab results image or click to browse</p>
                        <span className="hint">Supports ECGs, Blood Panels, RX Scans</span>
                    </div>
                ) : (
                    <div className="image-preview-container">
                        <img src={preview} alt="Lab Preview" className="lab-preview-img" />
                        <button className="btn-clear-img" onClick={clearImage}>
                            <span>✕</span> Remove Image
                        </button>
                    </div>
                )}
            </div>

            <div className="form-group">
                <label htmlFor="lab-text">Clinical Text Findings <span className="hint">(Interpretation or OCR verification)</span></label>
                <textarea
                    id="lab-text"
                    rows={4}
                    placeholder="Enter lab values or clinical notes manually..."
                    value={data.lab_text || ''}
                    onChange={(e) => onChange({ ...data, lab_text: e.target.value })}
                    className="clinical-data"
                />
            </div>
        </section>
    );
}

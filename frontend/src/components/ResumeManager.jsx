import React, { useRef, useState } from 'react';
import { Upload, CheckCircle, AlertTriangle, Cpu, Plus, X, Save } from 'lucide-react';
import { api } from '../utils/api';

export default function ResumeManager({ profile, onSaveProfile, onUploadResume, loading }) {
  const fileInputRef = useRef(null);
  const [newSkill, setNewSkill] = useState('');
  const [newTool, setNewTool] = useState('');
  const [newErp, setNewErp] = useState('');
  const [newKpi, setNewKpi] = useState('');

  const [editProfile, setEditProfile] = useState(profile ? { ...profile } : null);

  React.useEffect(() => {
    if (profile) setEditProfile({ ...profile });
  }, [profile]);

  const handleFileChange = async (e) => {
    const file = e.target.files[0];
    if (file) {
      await onUploadResume(file);
    }
  };

  const handleSave = () => {
    if (editProfile) {
      onSaveProfile(editProfile);
    }
  };

  // Add/Remove Tags Helper
  const addTag = (category, value, setter) => {
    if (!value.trim() || !editProfile) return;
    const updated = { ...editProfile };
    if (!updated[category].includes(value.trim())) {
      updated[category] = [...updated[category], value.trim()];
      setEditProfile(updated);
    }
    setter('');
  };

  const removeTag = (category, tag) => {
    if (!editProfile) return;
    const updated = { ...editProfile };
    updated[category] = updated[category].filter(t => t !== tag);
    setEditProfile(updated);
  };

  const handleTextChange = (field, subfield, value) => {
    if (!editProfile) return;
    const updated = { ...editProfile };
    if (subfield) {
      updated[field] = { ...updated[field], [subfield]: value };
    } else {
      updated[field] = value;
    }
    setEditProfile(updated);
  };

  // Heuristic ATS Score calculations for visual feedback
  const getAtsDetails = () => {
    if (!editProfile) return { score: 0, items: [] };
    
    let score = 65;
    const checks = [];

    // 1. Text length check
    const len = editProfile.master_resume_text?.length || 0;
    if (len > 1500 && len < 4000) {
      score += 10;
      checks.push({ name: "Ideal resume length (400-600 words)", passed: true });
    } else {
      checks.push({ name: "Resume word count too short or extremely wordy", passed: false });
    }

    // 2. ERP System check
    if (editProfile.extracted_erps?.length > 0) {
      score += 10;
      checks.push({ name: "ERP System identified (SAP MM / NetSuite)", passed: true });
    } else {
      checks.push({ name: "No ERP systems found (SAP is highly desired for Indian operations)", passed: false });
    }

    // 3. Analytics Tools
    if (editProfile.extracted_tools?.length >= 2) {
      score += 10;
      checks.push({ name: "Solid analytical tools match (Excel + SQL/BI)", passed: true });
    } else {
      checks.push({ name: "Add more tools like SQL or Power BI for logistics dashboards", passed: false });
    }

    // 4. Inventory KPIs
    if (editProfile.extracted_kpis?.length >= 3) {
      score += 5;
      checks.push({ name: "Excellent Inventory KPIs usage (Safety stock, DSI, OTIF)", passed: true });
    } else {
      checks.push({ name: "Ensure KPIs like Safety Stock or DSI are mentioned in achievements", passed: false });
    }

    return { score, checks };
  };

  const { score, checks } = getAtsDetails();

  return (
    <div>
      <div className="header-bar">
        <div>
          <h1 style={{ fontSize: '32px', marginBottom: '8px' }}>Master ATS Resume</h1>
          <p style={{ color: 'var(--text-secondary)' }}>Upload your Master CV to parse keywords, score formatting, and audit logistics competencies.</p>
        </div>
        
        {editProfile && (
          <button onClick={handleSave} className="btn btn-primary" style={{ background: 'var(--primary)', color: 'black' }}>
            <Save size={16} />
            Save Profile Details
          </button>
        )}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 360px', gap: '24px' }}>
        
        {/* Left Side: Profile Editors & Tags */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          
          {/* UPLOAD WIDGET */}
          <div 
            onClick={() => fileInputRef.current?.click()}
            className="card-glass"
            style={{ 
              border: '2px dashed var(--border-glass)', 
              textAlign: 'center', 
              padding: '40px 20px', 
              cursor: 'pointer',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '12px'
            }}
          >
            <input 
              type="file" 
              ref={fileInputRef} 
              onChange={handleFileChange} 
              accept=".pdf,.docx,.txt,.md" 
              style={{ display: 'none' }} 
            />
            <div style={{ width: '64px', height: '64px', borderRadius: '50%', background: 'rgba(16, 185, 129, 0.08)', display: 'flex', alignItems: 'center', justifySelf: 'center', justifyContent: 'center', color: 'var(--primary)' }}>
              <Upload size={28} className={loading ? "pulse-active" : ""} />
            </div>
            <div>
              <h3 style={{ fontSize: '16px', marginBottom: '4px' }}>
                {loading ? "Parsing Resume Heuristics..." : "Upload New CV (PDF, DOCX or TXT)"}
              </h3>
              <p style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>Supports direct ATS scanning of skills, ERP systems, and supply chain achievements</p>
            </div>
          </div>

          {editProfile ? (
            <>
              {/* Domain Competencies (Tags Editors) */}
              <div className="card-glass" style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                <h3 style={{ fontSize: '18px', borderBottom: '1px solid var(--border-glass)', paddingBottom: '12px' }}>Logistics & Operations Competencies</h3>
                
                {/* 1. Inventory KPIs */}
                <div>
                  <label style={{ fontSize: '13px', fontWeight: 'bold', color: 'var(--text-secondary)', display: 'block', marginBottom: '8px' }}>Inventory KPIs Covered</label>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', marginBottom: '10px' }}>
                    {editProfile.extracted_kpis?.map(kpi => (
                      <span key={kpi} className="badge badge-primary" style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', textTransform: 'none' }}>
                        {kpi}
                        <X size={12} style={{ cursor: 'pointer' }} onClick={() => removeTag('extracted_kpis', kpi)} />
                      </span>
                    ))}
                  </div>
                  <div style={{ display: 'flex', gap: '8px' }}>
                    <input 
                      type="text" 
                      value={newKpi} 
                      onChange={e => setNewKpi(e.target.value)} 
                      placeholder="e.g. Safety Stock, OTIF, DSI" 
                      style={{ padding: '8px 12px' }}
                    />
                    <button onClick={() => addTag('extracted_kpis', newKpi, setNewKpi)} className="btn btn-secondary" style={{ padding: '8px 12px' }}><Plus size={16} /></button>
                  </div>
                </div>

                {/* 2. ERP Systems */}
                <div>
                  <label style={{ fontSize: '13px', fontWeight: 'bold', color: 'var(--text-secondary)', display: 'block', marginBottom: '8px' }}>ERP Systems</label>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', marginBottom: '10px' }}>
                    {editProfile.extracted_erps?.map(erp => (
                      <span key={erp} className="badge badge-secondary" style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', textTransform: 'none' }}>
                        {erp}
                        <X size={12} style={{ cursor: 'pointer' }} onClick={() => removeTag('extracted_erps', erp)} />
                      </span>
                    ))}
                  </div>
                  <div style={{ display: 'flex', gap: '8px' }}>
                    <input 
                      type="text" 
                      value={newErp} 
                      onChange={e => setNewErp(e.target.value)} 
                      placeholder="e.g. SAP MM, NetSuite" 
                      style={{ padding: '8px 12px' }}
                    />
                    <button onClick={() => addTag('extracted_erps', newErp, setNewErp)} className="btn btn-secondary" style={{ padding: '8px 12px' }}><Plus size={16} /></button>
                  </div>
                </div>

                {/* 3. Analytical Tools */}
                <div>
                  <label style={{ fontSize: '13px', fontWeight: 'bold', color: 'var(--text-secondary)', display: 'block', marginBottom: '8px' }}>Analytical Tools</label>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', marginBottom: '10px' }}>
                    {editProfile.extracted_tools?.map(tool => (
                      <span key={tool} className="badge badge-secondary" style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', textTransform: 'none', background: 'rgba(6, 182, 212, 0.1)' }}>
                        {tool}
                        <X size={12} style={{ cursor: 'pointer' }} onClick={() => removeTag('extracted_tools', tool)} />
                      </span>
                    ))}
                  </div>
                  <div style={{ display: 'flex', gap: '8px' }}>
                    <input 
                      type="text" 
                      value={newTool} 
                      onChange={e => setNewTool(e.target.value)} 
                      placeholder="e.g. Power BI, Excel, SQL" 
                      style={{ padding: '8px 12px' }}
                    />
                    <button onClick={() => addTag('extracted_tools', newTool, setNewTool)} className="btn btn-secondary" style={{ padding: '8px 12px' }}><Plus size={16} /></button>
                  </div>
                </div>

                {/* 4. Core Skills */}
                <div>
                  <label style={{ fontSize: '13px', fontWeight: 'bold', color: 'var(--text-secondary)', display: 'block', marginBottom: '8px' }}>General Operations Skills</label>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', marginBottom: '10px' }}>
                    {editProfile.extracted_skills?.map(skill => (
                      <span key={skill} className="badge badge-secondary" style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', textTransform: 'none', background: 'rgba(255,255,255,0.05)', color: 'var(--text-secondary)' }}>
                        {skill}
                        <X size={12} style={{ cursor: 'pointer' }} onClick={() => removeTag('extracted_skills', skill)} />
                      </span>
                    ))}
                  </div>
                  <div style={{ display: 'flex', gap: '8px' }}>
                    <input 
                      type="text" 
                      value={newSkill} 
                      onChange={e => setNewSkill(e.target.value)} 
                      placeholder="e.g. Stock Auditing, Sourcing" 
                      style={{ padding: '8px 12px' }}
                    />
                    <button onClick={() => addTag('extracted_skills', newSkill, setNewSkill)} className="btn btn-secondary" style={{ padding: '8px 12px' }}><Plus size={16} /></button>
                  </div>
                </div>

              </div>

              {/* Bio Summary editor */}
              <div className="card-glass" style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                <h3 style={{ fontSize: '18px', borderBottom: '1px solid var(--border-glass)', paddingBottom: '12px' }}>Professional Summary</h3>
                <textarea 
                  value={editProfile.experience_summary?.summary || ''} 
                  onChange={e => handleTextChange('experience_summary', 'summary', e.target.value)}
                  rows={4}
                  placeholder="Paste professional bio"
                />
              </div>
            </>
          ) : (
            <div className="card-glass" style={{ textAlign: 'center', padding: '40px', color: 'var(--text-secondary)' }}>
              No master resume profile detected. Please upload a CV or TXT file above to get started.
            </div>
          )}

        </div>

        {/* Right Side: ATS Audit Board */}
        <div>
          {editProfile && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', position: 'sticky', top: '24px' }}>
              
              {/* ATS SCORE */}
              <div className="card-glass card-glowing-primary" style={{ textAlign: 'center' }}>
                <Cpu size={24} style={{ color: 'var(--primary)', marginBottom: '8px' }} />
                <div style={{ fontSize: '13px', color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>ATS Compliance Score</div>
                
                {/* SVG Progress Circle */}
                <div style={{ display: 'flex', justifyContent: 'center', margin: '20px 0' }}>
                  <svg width="120" height="120" viewBox="0 0 120 120">
                    <circle cx="60" cy="60" r="50" fill="none" stroke="rgba(255,255,255,0.03)" strokeWidth="8" />
                    <circle 
                      cx="60" 
                      cy="60" 
                      r="50" 
                      fill="none" 
                      stroke="var(--primary)" 
                      strokeWidth="8" 
                      strokeDasharray="314" 
                      strokeDashoffset={314 - (314 * score) / 100}
                      strokeLinecap="round"
                      transform="rotate(-90 60 60)"
                      style={{ transition: 'stroke-dashoffset 1s ease-in-out' }}
                    />
                    <text x="60" y="66" textAnchor="middle" fill="white" fontSize="24" fontFamily="var(--font-display)" fontWeight="700">
                      {score}
                    </text>
                  </svg>
                </div>

                <div style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>
                  Your resume is highly optimized for <strong>Inventory & Supply Chain Analysts</strong> in India.
                </div>
              </div>

              {/* Checklist */}
              <div className="card-glass">
                <h3 style={{ fontSize: '16px', marginBottom: '16px' }}>Formatting Compliance</h3>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                  {checks.map((item, idx) => (
                    <div key={idx} style={{ display: 'flex', gap: '10px', alignItems: 'flex-start' }}>
                      {item.passed ? (
                        <CheckCircle size={16} style={{ color: 'var(--primary)', flexShrink: 0, marginTop: '2px' }} />
                      ) : (
                        <AlertTriangle size={16} style={{ color: 'var(--warning)', flexShrink: 0, marginTop: '2px' }} />
                      )}
                      <div style={{ fontSize: '13px', color: item.passed ? 'var(--text-primary)' : 'var(--text-secondary)' }}>
                        {item.name}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

            </div>
          )}
        </div>

      </div>
    </div>
  );
}

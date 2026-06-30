import React, { useState } from 'react';
import { Briefcase, MapPin, ExternalLink, Compass, ShieldCheck, Clipboard, Check, RefreshCw, Send, Play, Terminal, HelpCircle } from 'lucide-react';
import { api } from '../utils/api';

export default function JobFinder({ jobs, selectedJob, onSelectJob, onImportJob, loadingImport, onOptimizeJob, loadingOptimize, assets, onApplyJob, loadingApply }) {
  const [activeTab, setActiveTab] = useState('match'); // 'match', 'resume', 'cover', 'outreach', 'apply'
  const [pastedUrl, setPastedUrl] = useState('');
  const [copiedField, setCopiedField] = useState(null);

  const handleImport = async (e) => {
    e.preventDefault();
    if (!pastedUrl.trim()) return;
    await onImportJob(pastedUrl);
    setPastedUrl('');
  };

  const handleCopy = (text, field) => {
    navigator.clipboard.writeText(text);
    setCopiedField(field);
    setTimeout(() => setCopiedField(null), 2000);
  };

  const triggerOptimize = async () => {
    if (!selectedJob) return;
    await onOptimizeJob(selectedJob.id);
  };

  return (
    <div>
      <div className="header-bar">
        <div>
          <h1 style={{ fontSize: '32px', marginBottom: '8px' }}>Matched Openings</h1>
          <p style={{ color: 'var(--text-secondary)' }}>We parsed and matches jobs &gt;65% score from LinkedIn, Indeed, and Naukri. Excluded senior & IT roles.</p>
        </div>
      </div>

      {/* Split Workspace */}
      <div className="split-view">
        
        {/* Left Panel: Job List Feed & Import URL */}
        <div className="panel-scrollable" style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          
          {/* Import URL Card */}
          <div className="card-glass" style={{ padding: '16px' }}>
            <label style={{ fontSize: '12px', fontWeight: 'bold', color: 'var(--text-secondary)', display: 'block', marginBottom: '6px' }}>Import Job from URL</label>
            <form onSubmit={handleImport} style={{ display: 'flex', gap: '8px' }}>
              <input 
                type="url" 
                value={pastedUrl} 
                onChange={e => setPastedUrl(e.target.value)} 
                placeholder="Paste LinkedIn / Naukri / Career link..." 
                style={{ padding: '8px 12px', flexGrow: 1 }}
              />
              <button disabled={loadingImport} className="btn btn-secondary" style={{ padding: '8px 16px', fontSize: '13px' }}>
                {loadingImport ? "Scraping..." : "Parse link"}
              </button>
            </form>
          </div>

          {/* Job Feed List */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {jobs.length > 0 ? (
              jobs.map(job => {
                const isSelected = selectedJob && selectedJob.id === job.id;
                const isSouth = job.location.toLowerCase().includes('chennai') || job.location.toLowerCase().includes('bangalore') || job.location.toLowerCase().includes('bengaluru');
                
                return (
                  <div 
                    key={job.id} 
                    onClick={() => onSelectJob(job)}
                    className="card-glass"
                    style={{ 
                      padding: '16px', 
                      cursor: 'pointer',
                      borderColor: isSelected ? 'var(--primary)' : 'var(--border-glass)',
                      background: isSelected ? 'rgba(16, 185, 129, 0.05)' : 'var(--card-glass)'
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '8px' }}>
                      <span className="badge badge-primary">{job.match_score}% Match</span>
                      <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>{job.platform}</span>
                    </div>
                    <h4 style={{ fontSize: '15px', color: 'white', marginBottom: '4px' }}>{job.title}</h4>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <div style={{ color: 'var(--text-secondary)', fontSize: '13px' }}>{job.company}</div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '12px', color: isSouth ? 'var(--primary)' : 'var(--text-muted)' }}>
                        <MapPin size={12} />
                        {job.location}
                      </div>
                    </div>
                  </div>
                );
              })
            ) : (
              <div className="card-glass" style={{ textAlign: 'center', padding: '40px', color: 'var(--text-secondary)' }}>
                No active matched roles. Click "Scan & Match India Jobs" in the Dashboard to pull fresh jobs.
              </div>
            )}
          </div>

        </div>

        {/* Right Panel: Interactive Match Workshop */}
        <div className="card-glass panel-scrollable" style={{ padding: '0px', display: 'flex', flexDirection: 'column' }}>
          {selectedJob ? (
            <>
              {/* Header Details */}
              <div style={{ padding: '24px', borderBottom: '1px solid var(--border-glass)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '12px' }}>
                  <div>
                    <h2 style={{ fontSize: '22px', color: 'white', marginBottom: '4px' }}>{selectedJob.title}</h2>
                    <p style={{ color: 'var(--text-secondary)', fontSize: '14px' }}>{selectedJob.company} • {selectedJob.location}</p>
                  </div>
                  
                  <div style={{ display: 'flex', gap: '8px' }}>
                    <a href={selectedJob.url} target="_blank" rel="noreferrer" className="btn btn-secondary" style={{ padding: '8px 12px', fontSize: '13px' }}>
                      <ExternalLink size={14} />
                      View Post
                    </a>
                    
                    {selectedJob.status === 'Identified' && (
                      <button 
                        onClick={triggerOptimize} 
                        disabled={loadingOptimize} 
                        className="btn btn-primary" 
                        style={{ padding: '8px 16px', fontSize: '13px', background: 'var(--primary)', color: 'black' }}
                      >
                        <RefreshCw className={loadingOptimize ? "pulse-active" : ""} size={14} />
                        {loadingOptimize ? "Customizing..." : "Optimize Resume"}
                      </button>
                    )}
                  </div>
                </div>

                {/* Tabs */}
                <div style={{ display: 'flex', gap: '16px', marginTop: '16px' }}>
                  <button 
                    onClick={() => setActiveTab('match')} 
                    className={`btn ${activeTab === 'match' ? 'btn-primary' : 'btn-secondary'}`}
                    style={{ padding: '6px 12px', borderRadius: '20px', fontSize: '12px' }}
                  >
                    Match Analysis
                  </button>
                  <button 
                    onClick={() => { setActiveTab('resume'); if(!assets) triggerOptimize(); }} 
                    className={`btn ${activeTab === 'resume' ? 'btn-primary' : 'btn-secondary'}`}
                    style={{ padding: '6px 12px', borderRadius: '20px', fontSize: '12px' }}
                  >
                    ATS Resume Mod
                  </button>
                  <button 
                    onClick={() => { setActiveTab('cover'); if(!assets) triggerOptimize(); }} 
                    className={`btn ${activeTab === 'cover' ? 'btn-primary' : 'btn-secondary'}`}
                    style={{ padding: '6px 12px', borderRadius: '20px', fontSize: '12px' }}
                  >
                    Cover Letter
                  </button>
                  <button 
                    onClick={() => { setActiveTab('outreach'); if(!assets) triggerOptimize(); }} 
                    className={`btn ${activeTab === 'outreach' ? 'btn-primary' : 'btn-secondary'}`}
                    style={{ padding: '6px 12px', borderRadius: '20px', fontSize: '12px' }}
                  >
                    Recruiter Pitch
                  </button>
                  <button 
                    onClick={() => setActiveTab('apply')} 
                    className={`btn ${activeTab === 'apply' ? 'btn-primary' : 'btn-secondary'}`}
                    style={{ padding: '6px 12px', borderRadius: '20px', fontSize: '12px' }}
                  >
                    Apply Now
                  </button>
                </div>
              </div>

              {/* Tab Workspace Contents */}
              <div style={{ padding: '24px', flexGrow: 1 }}>
                
                {/* 1. MATCH ANALYSIS TAB */}
                {activeTab === 'match' && (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                    <div style={{ display: 'flex', gap: '12px', alignItems: 'center', background: 'rgba(16, 185, 129, 0.08)', padding: '16px', borderRadius: '8px', border: '1px solid var(--border-glass-active)' }}>
                      <ShieldCheck size={24} style={{ color: 'var(--primary)', flexShrink: 0 }} />
                      <div>
                        <h4 style={{ color: 'white', fontSize: '14px', marginBottom: '2px' }}>High-Quality Match Score: {selectedJob.match_score}%</h4>
                        <p style={{ color: 'var(--text-secondary)', fontSize: '13px' }}>This opening matches your 1 year of inventory analytics and operations background.</p>
                      </div>
                    </div>

                    <div>
                      <h3 style={{ fontSize: '16px', marginBottom: '8px' }}>Why this job fits:</h3>
                      <p style={{ color: 'var(--text-secondary)', fontSize: '14px', lineHeight: '1.6' }}>{selectedJob.why_fits || "Analyzing job content..."}</p>
                    </div>

                    <div>
                      <h3 style={{ fontSize: '16px', marginBottom: '12px' }}>Role Specifications & Description</h3>
                      <div style={{ background: 'rgba(0,0,0,0.2)', padding: '16px', borderRadius: '8px', border: '1px solid var(--border-glass)', maxHeight: '200px', overflowY: 'auto', fontSize: '13px', color: 'var(--text-secondary)', lineHeight: '1.6', whiteSpace: 'pre-line' }}>
                        {selectedJob.description}
                      </div>
                    </div>
                  </div>
                )}

                {/* 2. ATS RESUME TAB */}
                {activeTab === 'resume' && (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                    {assets ? (
                      <>
                        <div style={{ display: 'flex', justifyBetween: 'space-between', alignItems: 'center', background: 'rgba(255,255,255,0.02)', padding: '12px', borderRadius: '8px', border: '1px solid var(--border-glass)' }}>
                          <div style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>
                            {assets.ats_improvement || "Optimized profile for matching requirements."}
                          </div>
                        </div>

                        <div>
                          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                            <h3 style={{ fontSize: '15px' }}>Custom Profile Summary</h3>
                            <button onClick={() => handleCopy(assets.optimized_summary, 'summary')} className="btn btn-secondary" style={{ padding: '4px 8px', fontSize: '11px' }}>
                              {copiedField === 'summary' ? <Check size={12} style={{ color: 'var(--primary)' }} /> : <Clipboard size={12} />}
                              {copiedField === 'summary' ? "Copied" : "Copy"}
                            </button>
                          </div>
                          <div style={{ background: 'rgba(0,0,0,0.2)', padding: '16px', borderRadius: '8px', border: '1px solid var(--border-glass)', fontSize: '13px', color: 'white', lineHeight: '1.6' }}>
                            {assets.optimized_summary}
                          </div>
                        </div>

                        <div>
                          <h3 style={{ fontSize: '15px', marginBottom: '10px' }}>Customized Work Experience Accomplishments</h3>
                          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                            {assets.optimized_bullets?.map((bullet, idx) => (
                              <div key={idx} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', background: 'rgba(0,0,0,0.1)', padding: '12px', borderRadius: '8px', border: '1px solid var(--border-glass)' }}>
                                <div style={{ fontSize: '13px', color: 'var(--text-secondary)', lineHeight: '1.5', width: '90%' }}>
                                  • {bullet}
                                </div>
                                <button onClick={() => handleCopy(bullet, `bullet-${idx}`)} className="btn btn-secondary" style={{ padding: '4px 8px', fontSize: '11px', flexShrink: 0 }}>
                                  {copiedField === `bullet-${idx}` ? <Check size={10} style={{ color: 'var(--primary)' }} /> : <Clipboard size={10} />}
                                </button>
                              </div>
                            ))}
                          </div>
                        </div>
                      </>
                    ) : (
                      <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-secondary)' }}>
                        <RefreshCw className="pulse-active" style={{ marginBottom: '10px' }} />
                        <div>Generating optimized resume modules...</div>
                      </div>
                    )}
                  </div>
                )}

                {/* 3. COVER LETTER TAB */}
                {activeTab === 'cover' && (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                    {assets ? (
                      <>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <h3 style={{ fontSize: '16px' }}>Tailored Cover Letter</h3>
                          <button onClick={() => handleCopy(assets.cover_letter, 'cover')} className="btn btn-secondary" style={{ padding: '6px 12px', fontSize: '12px' }}>
                            {copiedField === 'cover' ? <Check size={14} style={{ color: 'var(--primary)' }} /> : <Clipboard size={14} />}
                            {copiedField === 'cover' ? "Copied Cover Letter" : "Copy to Clipboard"}
                          </button>
                        </div>
                        <textarea 
                          readOnly 
                          value={assets.cover_letter} 
                          rows={14} 
                          style={{ fontFamily: 'monospace', fontSize: '13px', background: 'rgba(0,0,0,0.25)', lineHeight: '1.6', resize: 'none' }}
                        />
                      </>
                    ) : (
                      <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-secondary)' }}>
                        <RefreshCw className="pulse-active" style={{ marginBottom: '10px' }} />
                        <div>Drafting custom cover letter...</div>
                      </div>
                    )}
                  </div>
                )}

                {/* 4. RECRUITER OUTREACH TAB */}
                {activeTab === 'outreach' && (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                    {assets ? (
                      <>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <h3 style={{ fontSize: '16px' }}>LinkedIn Recruiter Message</h3>
                          <button onClick={() => handleCopy(assets.recruiter_message, 'outreach')} className="btn btn-secondary" style={{ padding: '6px 12px', fontSize: '12px' }}>
                            {copiedField === 'outreach' ? <Check size={14} style={{ color: 'var(--primary)' }} /> : <Clipboard size={14} />}
                            {copiedField === 'outreach' ? "Copied Note" : "Copy outreach note"}
                          </button>
                        </div>
                        <textarea 
                          readOnly 
                          value={assets.recruiter_message} 
                          rows={8} 
                          style={{ fontSize: '13px', background: 'rgba(0,0,0,0.25)', lineHeight: '1.6', resize: 'none' }}
                        />
                      </>
                    ) : (
                      <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-secondary)' }}>
                        <RefreshCw className="pulse-active" style={{ marginBottom: '10px' }} />
                        <div>Generating recruiter message...</div>
                      </div>
                    )}
                  </div>
                )}

                {/* 5. APPLY AUTOMATION TAB */}
                {activeTab === 'apply' && (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                    <div style={{ background: 'rgba(10, 15, 28, 0.4)', border: '1px solid var(--border-glass)', padding: '20px', borderRadius: '12px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
                      <h3 style={{ fontSize: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <Terminal size={18} style={{ color: 'var(--primary)' }} />
                        Browser Application Engine
                      </h3>
                      <p style={{ fontSize: '13px', color: 'var(--text-secondary)', lineHeight: '1.6' }}>
                        The automation engine uses **Playwright** to open a guided browser session. It will instantly autofill your name, email, contact details, YOE, notice period, and core tools (Excel/SAP) directly onto the job form.
                      </p>

                      <div style={{ display: 'flex', gap: '12px', marginTop: '10px' }}>
                        <button 
                          onClick={() => onApplyJob(selectedJob.id, 'interactive')} 
                          disabled={loadingApply}
                          className="btn btn-primary"
                          style={{ flexGrow: 1, padding: '12px', background: 'var(--primary)', color: 'black' }}
                        >
                          <Play size={16} />
                          {loadingApply ? "Launching browser..." : "Apply with Copilot"}
                        </button>
                      </div>
                      
                      <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '11px', color: 'var(--text-muted)', justifyContent: 'center' }}>
                        <HelpCircle size={12} />
                        Recommended: Launches a headed session to safely bypass Cloudflare/Captchas.
                      </div>
                    </div>
                  </div>
                )}

              </div>
            </>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', padding: '40px', color: 'var(--text-muted)' }}>
              <Compass size={40} style={{ marginBottom: '12px' }} />
              <div>Select a job posting from the feed to launch the optimization workshop.</div>
            </div>
          )}
        </div>

      </div>
    </div>
  );
}

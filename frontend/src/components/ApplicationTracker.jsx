import React, { useState } from 'react';
import { Calendar, User, MessageSquare, ClipboardList, CheckSquare, Award, ArrowRight, ShieldCheck, ChevronRight, X } from 'lucide-react';
import { api } from '../utils/api';

const LANES = [
  { id: 'Identified', name: 'Identified', color: 'var(--text-muted)' },
  { id: 'Optimized', name: 'Optimized', color: 'var(--secondary)' },
  { id: 'Applied', name: 'Applied', color: 'var(--primary)' },
  { id: 'Interviewing', name: 'Interviewing', color: 'var(--warning)' },
  { id: 'Offered', name: 'Offers & Closed', color: 'var(--accent)' }
];

export default function ApplicationTracker({ jobs, onUpdateStatus }) {
  const [selectedAppJob, setSelectedAppJob] = useState(null);
  const [appAssets, setAppAssets] = useState(null);
  const [notesText, setNotesText] = useState('');
  const [loadingAssets, setLoadingAssets] = useState(false);

  // Group jobs by status lane
  const groupedJobs = LANES.reduce((acc, lane) => {
    acc[lane.id] = jobs.filter(j => j.status === lane.id);
    return acc;
  }, {});

  const openAppDetails = async (job) => {
    setSelectedAppJob(job);
    setLoadingAssets(true);
    setAppAssets(null);
    try {
      const data = await api.getApplicationAssets(job.id);
      setAppAssets(data);
      setNotesText(data.notes || '');
    } catch (e) {
      console.log("No application assets yet, since it was not optimized.", e);
      setAppAssets(null);
      setNotesText('');
    } finally {
      setLoadingAssets(false);
    }
  };

  const handleSaveNotes = async () => {
    if (!selectedAppJob) return;
    try {
      await api.saveApplicationNotes(selectedAppJob.id, {
        notes: notesText,
        interview_rounds: appAssets?.interview_rounds || [],
        follow_up_dates: appAssets?.follow_up_dates || []
      });
      alert("Notes updated successfully!");
    } catch (e) {
      alert("Failed to save notes.");
    }
  };

  const moveLane = async (jobId, targetLane) => {
    await onUpdateStatus(jobId, targetLane);
    if (selectedAppJob && selectedAppJob.id === jobId) {
      setSelectedAppJob({ ...selectedAppJob, status: targetLane });
    }
  };

  return (
    <div>
      <div className="header-bar">
        <div>
          <h1 style={{ fontSize: '32px', marginBottom: '8px' }}>Application Tracker</h1>
          <p style={{ color: 'var(--text-secondary)' }}>Organize your applications, scheduled interviews, and outstanding offers.</p>
        </div>
      </div>

      {/* Kanban Board Grid */}
      <div className="kanban-board">
        {LANES.map(lane => (
          <div key={lane.id} className="kanban-lane">
            <div className="kanban-lane-header">
              <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: lane.color }}></span>
                {lane.name}
              </span>
              <span className="badge badge-secondary" style={{ padding: '2px 6px', background: 'rgba(255,255,255,0.05)', color: 'var(--text-secondary)' }}>
                {groupedJobs[lane.id]?.length || 0}
              </span>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', overflowY: 'auto', flexGrow: 1 }}>
              {groupedJobs[lane.id]?.map(job => (
                <div 
                  key={job.id} 
                  onClick={() => openAppDetails(job)}
                  className="kanban-card"
                >
                  <h4 style={{ fontSize: '13px', color: 'white', marginBottom: '4px', fontWeight: '600' }}>{job.title}</h4>
                  <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>{job.company}</div>
                  
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '12px', fontSize: '10px', color: 'var(--text-muted)' }}>
                    <span>{job.location}</span>
                    <span>{job.match_score}% Match</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>

      {/* Modal Detail Slide-over Panel */}
      {selectedAppJob && (
        <div style={{ position: 'fixed', top: 0, right: 0, bottom: 0, width: '560px', background: 'hsl(225, 24%, 6%)', borderLeft: '1px solid var(--border-glass)', boxShadow: '-10px 0 40px rgba(0,0,0,0.8)', zIndex: 1000, display: 'flex', flexDirection: 'column', animation: 'slide-in 0.3s ease-out' }}>
          
          {/* Modal Header */}
          <div style={{ padding: '24px', borderBottom: '1px solid var(--border-glass)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <h2 style={{ fontSize: '20px', color: 'white', marginBottom: '2px' }}>{selectedAppJob.title}</h2>
              <p style={{ color: 'var(--text-secondary)', fontSize: '13px' }}>{selectedAppJob.company} • {selectedAppJob.location}</p>
            </div>
            <button onClick={() => setSelectedAppJob(null)} className="btn btn-secondary" style={{ padding: '6px', borderRadius: '50%' }}>
              <X size={18} />
            </button>
          </div>

          {/* Modal Scrollable Contents */}
          <div style={{ padding: '24px', overflowY: 'auto', flexGrow: 1, display: 'flex', flexDirection: 'column', gap: '24px' }}>
            
            {/* Lane Mover Controls */}
            <div>
              <label style={{ fontSize: '11px', textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--text-muted)', display: 'block', marginBottom: '8px' }}>Pipeline Status</label>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                {LANES.map(lane => (
                  <button 
                    key={lane.id} 
                    onClick={() => moveLane(selectedAppJob.id, lane.id)}
                    className={`btn ${selectedAppJob.status === lane.id ? 'btn-primary' : 'btn-secondary'}`}
                    style={{ padding: '6px 12px', fontSize: '11px', borderRadius: '15px' }}
                  >
                    {lane.name}
                  </button>
                ))}
              </div>
            </div>

            {loadingAssets ? (
              <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-secondary)' }}>
                <RefreshCw className="pulse-active" style={{ marginBottom: '8px' }} />
                <div>Retrieving interview guidelines & optimized credentials...</div>
              </div>
            ) : appAssets ? (
              <>
                {/* Dynamic Interview Prep for this job */}
                <div>
                  <h3 style={{ fontSize: '16px', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <ClipboardList size={18} style={{ color: 'var(--warning)' }} />
                    Job Interview Blueprint
                  </h3>
                  
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                    {appAssets.interview_prep_questions?.map((item, idx) => (
                      <div key={idx} style={{ background: 'rgba(0,0,0,0.2)', padding: '14px', borderRadius: '8px', border: '1px solid var(--border-glass)' }}>
                        <div style={{ fontSize: '13px', fontWeight: 'bold', color: 'white', marginBottom: '6px' }}>Q: {item.question}</div>
                        <div style={{ fontSize: '12px', color: 'var(--text-secondary)', lineHeight: '1.5' }}>A: {item.answer}</div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Cover Letter & Resume backups */}
                <div>
                  <h3 style={{ fontSize: '16px', marginBottom: '12px' }}>Application Assets Backup</h3>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                    <div style={{ background: 'rgba(255,255,255,0.02)', padding: '12px', borderRadius: '8px', border: '1px solid var(--border-glass)', fontSize: '13px' }}>
                      <div style={{ fontWeight: 'bold', marginBottom: '4px' }}>Optimized Summary used:</div>
                      <div style={{ color: 'var(--text-secondary)', fontSize: '12px', lineHeight: '1.5' }}>{appAssets.resume_version_text?.split('\n\n')[0]}</div>
                    </div>
                  </div>
                </div>

                {/* Interactive log sheets / Notes */}
                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                    <h3 style={{ fontSize: '16px' }}>Application logs / HR Details</h3>
                    <button onClick={handleSaveNotes} className="btn btn-secondary" style={{ padding: '4px 8px', fontSize: '11px' }}>
                      Update Log
                    </button>
                  </div>
                  <textarea 
                    value={notesText} 
                    onChange={e => setNotesText(e.target.value)} 
                    rows={6} 
                    placeholder="Enter HR contact name, email, interview schedules, or feedback comments here..." 
                    style={{ fontSize: '13px', background: 'rgba(0,0,0,0.2)', lineHeight: '1.5', resize: 'none' }}
                  />
                </div>
              </>
            ) : (
              <div style={{ background: 'rgba(255, 255, 255, 0.02)', border: '1px solid var(--border-glass)', padding: '20px', borderRadius: '8px', textAlign: 'center', color: 'var(--text-muted)', fontSize: '13px' }}>
                No active optimization logs found. Resume and interview blueprints generate instantly when you optimize this position in the Match panel.
              </div>
            )}

          </div>

        </div>
      )}
    </div>
  );
}

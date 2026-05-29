import React, { useState, useEffect } from 'react';
import { LayoutDashboard, FileText, Briefcase, ListTodo, GraduationCap, Share2, Settings, AlertCircle, RefreshCw, Eye, EyeOff, Save } from 'lucide-react';
import { api } from './utils/api';

// Import sub-components
import DashboardHome from './components/DashboardHome';
import ResumeManager from './components/ResumeManager';
import JobFinder from './components/JobFinder';
import ApplicationTracker from './components/ApplicationTracker';
import InterviewPrep from './components/InterviewPrep';
import NetworkingHub from './components/NetworkingHub';

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [serverOnline, setServerOnline] = useState(true);
  const [loading, setLoading] = useState(true);
  
  // App Global State
  const [profile, setProfile] = useState(null);
  const [settings, setSettings] = useState({});
  const [jobs, setJobs] = useState([]);
  const [dashboardStats, setDashboardStats] = useState({
    stats: {
      total_scraped: 184,
      total_identified: 0,
      total_optimized: 0,
      total_applied: 105,
      total_interviewing: 4,
      total_offers: 1,
      total_rejected: 0,
      applied_today: 12,
      daily_target: 30,
      average_match_score: 84,
      interview_rate: 3.8
    },
    weekly_trend: [
      { day: "Mon", applied: 14 },
      { day: "Tue", applied: 18 },
      { day: "Wed", applied: 22 },
      { day: "Thu", applied: 25 },
      { day: "Fri", applied: 19 },
      { day: "Sat", applied: 8 },
      { day: "Sun", applied: 12 }
    ]
  });

  // Action/Process Loaders
  const [loadingScan, setLoadingScan] = useState(false);
  const [loadingImport, setLoadingImport] = useState(false);
  const [loadingOptimize, setLoadingOptimize] = useState(false);
  const [loadingApply, setLoadingApply] = useState(false);
  
  // Workshop Active States
  const [selectedJob, setSelectedJob] = useState(null);
  const [selectedJobAssets, setSelectedJobAssets] = useState(null);

  // Settings visibility
  const [showApiKey, setShowApiKey] = useState(false);

  // Initial Data Load
  const fetchAllData = async () => {
    try {
      setLoading(true);
      
      // Ping check server
      const health = await api.checkHealth();
      if (health.status !== 'healthy') throw new Error("Server unhealthy");
      setServerOnline(true);

      const parsedProfile = await api.getProfile();
      if (parsedProfile && parsedProfile.name) {
        setProfile(parsedProfile);
      }
      
      const savedSettings = await api.getSettings();
      setSettings(savedSettings);

      const allJobs = await api.getJobs();
      setJobs(allJobs);

      const statsData = await api.getStats();
      setDashboardStats(statsData);

      setServerOnline(true);
    } catch (e) {
      console.log("Backend server offline. Running in premium mock offline mode.", e);
      setServerOnline(false);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAllData();
  }, []);

  // 1. Resume Operations
  const handleUploadResume = async (file) => {
    try {
      setLoading(true);
      const parsed = await api.uploadResume(file);
      setProfile(parsed);
      alert("Resume parsed successfully!");
      fetchAllData();
    } catch (e) {
      alert("Error parsing resume: " + e.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSaveProfile = async (updatedProfile) => {
    try {
      setLoading(true);
      const saved = await api.saveProfile(updatedProfile);
      setProfile(saved);
      alert("Profile competencies saved successfully!");
      fetchAllData();
    } catch (e) {
      alert("Error saving profile.");
    } finally {
      setLoading(false);
    }
  };

  // 2. Job Engine Operations
  const handleTriggerScan = async () => {
    try {
      setLoadingScan(true);
      const res = await api.triggerScan();
      alert(`Job scan completed! Added ${res.count_found} high-match positions (score >75%) to your feed.`);
      fetchAllData();
    } catch (e) {
      alert("Error running job scan.");
    } finally {
      setLoadingScan(false);
    }
  };

  const handleImportJobUrl = async (url) => {
    try {
      setLoadingImport(true);
      const res = await api.pasteJobUrl(url);
      alert(`Job successfully imported! Match compatibility score is ${res.compatibility.score}%.`);
      fetchAllData();
    } catch (e) {
      alert("Error importing URL: " + e.message);
    } finally {
      setLoadingImport(false);
    }
  };

  const handleSelectJob = async (job) => {
    setSelectedJob(job);
    setSelectedJobAssets(null);
    try {
      const assets = await api.getApplicationAssets(job.id);
      setSelectedJobAssets(assets);
    } catch (e) {
      setSelectedJobAssets(null);
    }
  };

  const handleOptimizeJob = async (jobId) => {
    try {
      setLoadingOptimize(true);
      const res = await api.optimizeJobAssets(jobId);
      setSelectedJobAssets(res);
      alert("Resume & cover letter optimized successfully!");
      fetchAllData();
    } catch (e) {
      alert("Error optimizing job assets.");
    } finally {
      setLoadingOptimize(false);
    }
  };

  const handleApplyJob = async (jobId, mode) => {
    try {
      setLoadingApply(true);
      const res = await api.executeApply(jobId, mode);
      if (mode === 'interactive') {
        alert("Playwright headed session successfully started! Verify fields on your screen and submit.");
      } else {
        alert("Background auto-apply successful!");
      }
      fetchAllData();
    } catch (e) {
      alert("Application run error: " + e.message);
    } finally {
      setLoadingApply(false);
    }
  };

  const handleUpdateJobStatus = async (jobId, status) => {
    try {
      await api.updateJobStatus(jobId, status);
      fetchAllData();
    } catch (e) {
      console.log("Error updating job status.");
    }
  };

  // 3. Settings Save
  const handleUpdateSetting = async (key, val) => {
    try {
      const res = await api.updateSetting(key, val);
      setSettings(res.settings);
    } catch (e) {
      alert("Error saving setting.");
    }
  };

  return (
    <div className="app-container">
      
      {/* Premium Glass Sidebar */}
      <nav className="sidebar">
        <div className="sidebar-logo">
          <LayoutDashboard size={22} style={{ color: 'var(--primary)' }} />
          <span>Antigravity JobBot</span>
        </div>

        <ul className="sidebar-menu">
          <li onClick={() => setActiveTab('dashboard')} className={`menu-item ${activeTab === 'dashboard' ? 'active' : ''}`}>
            <LayoutDashboard size={18} />
            Overview
          </li>
          <li onClick={() => setActiveTab('resume')} className={`menu-item ${activeTab === 'resume' ? 'active' : ''}`}>
            <FileText size={18} />
            Master Resume
          </li>
          <li onClick={() => setActiveTab('jobs')} className={`menu-item ${activeTab === 'jobs' ? 'active' : ''}`}>
            <Briefcase size={18} />
            Match workshop
          </li>
          <li onClick={() => setActiveTab('tracker')} className={`menu-item ${activeTab === 'tracker' ? 'active' : ''}`}>
            <ListTodo size={18} />
            Kanban Board
          </li>
          <li onClick={() => setActiveTab('interview')} className={`menu-item ${activeTab === 'interview' ? 'active' : ''}`}>
            <GraduationCap size={18} />
            STAR Simulator
          </li>
          <li onClick={() => setActiveTab('networking')} className={`menu-item ${activeTab === 'networking' ? 'active' : ''}`}>
            <Share2 size={18} />
            Networking Hub
          </li>
          <li onClick={() => setActiveTab('settings')} className={`menu-item ${activeTab === 'settings' ? 'active' : ''}`}>
            <Settings size={18} />
            Settings
          </li>
        </ul>

        {/* Offline Badge */}
        {!serverOnline && (
          <div style={{ display: 'flex', gap: '8px', padding: '12px', background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239,68,68,0.2)', borderRadius: '8px', color: 'var(--danger)', fontSize: '11px', marginTop: 'auto' }}>
            <AlertCircle size={14} style={{ flexShrink: 0 }} />
            <div>
              <strong>Backend Offline</strong>
              <div style={{ opacity: 0.8, marginTop: '2px' }}>Check command console and run run.bat startup. Running mock dashboard mode.</div>
            </div>
          </div>
        )}
      </nav>

      {/* Main Panel Content */}
      <main className="main-content">
        
        {loading && (
          <div style={{ position: 'fixed', top: '20px', right: '40px', background: 'var(--primary)', color: 'black', padding: '8px 16px', borderRadius: '4px', display: 'flex', alignItems: 'center', gap: '8px', zIndex: 1000, fontWeight: 'bold', fontSize: '12px' }}>
            <RefreshCw size={14} className="pulse-active" />
            Synchronizing DB...
          </div>
        )}

        {/* Navigation router views */}
        {activeTab === 'dashboard' && (
          <DashboardHome 
            stats={dashboardStats.stats} 
            weeklyTrend={dashboardStats.weekly_trend}
            onNavigate={setActiveTab}
            onTriggerScan={handleTriggerScan}
            loadingScan={loadingScan}
          />
        )}

        {activeTab === 'resume' && (
          <ResumeManager 
            profile={profile} 
            onSaveProfile={handleSaveProfile} 
            onUploadResume={handleUploadResume}
            loading={loading}
          />
        )}

        {activeTab === 'jobs' && (
          <JobFinder 
            jobs={jobs.filter(j => j.status === 'Identified' || j.status === 'Optimized')} 
            selectedJob={selectedJob}
            onSelectJob={handleSelectJob}
            onImportJob={handleImportJobUrl}
            loadingImport={loadingImport}
            onOptimizeJob={handleOptimizeJob}
            loadingOptimize={loadingOptimize}
            assets={selectedJobAssets}
            onApplyJob={handleApplyJob}
            loadingApply={loadingApply}
          />
        )}

        {activeTab === 'tracker' && (
          <ApplicationTracker 
            jobs={jobs} 
            onUpdateStatus={handleUpdateJobStatus}
          />
        )}

        {activeTab === 'interview' && (
          <InterviewPrep />
        )}

        {activeTab === 'networking' && (
          <NetworkingHub />
        )}

        {activeTab === 'settings' && (
          <div>
            <div className="header-bar">
              <div>
                <h1 style={{ fontSize: '32px', marginBottom: '8px' }}>Application Settings</h1>
                <p style={{ color: 'var(--text-secondary)' }}>Configure API integrations, secure login channels, and daily targets.</p>
              </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 340px', gap: '24px' }}>
              
              {/* Settings Body */}
              <div className="card-glass" style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
                
                {/* 1. API Integration */}
                <div>
                  <h3 style={{ fontSize: '16px', borderBottom: '1px solid var(--border-glass)', paddingBottom: '8px', marginBottom: '16px' }}>AI Integrations</h3>
                  <label style={{ fontSize: '12px', fontWeight: 'bold', color: 'var(--text-secondary)', display: 'block', marginBottom: '6px' }}>Google Gemini API Key (Optional)</label>
                  <div style={{ display: 'flex', gap: '8px', position: 'relative' }}>
                    <input 
                      type={showApiKey ? "text" : "password"} 
                      value={settings.gemini_api_key || ''} 
                      onChange={e => handleUpdateSetting('gemini_api_key', e.target.value)} 
                      placeholder="AI key for custom descriptions..." 
                      style={{ paddingRight: '48px' }}
                    />
                    <button 
                      type="button" 
                      onClick={() => setShowApiKey(!showApiKey)}
                      className="btn btn-secondary" 
                      style={{ position: 'absolute', right: '4px', top: '4px', bottom: '4px', padding: '0 12px', height: 'auto', border: 'none', background: 'transparent' }}
                    >
                      {showApiKey ? <EyeOff size={16} /> : <Eye size={16} />}
                    </button>
                  </div>
                  <span style={{ fontSize: '11px', color: 'var(--text-muted)', display: 'block', marginTop: '6px' }}>Provide a key to unlock deep, custom, YOE-aligned resume revisions. If empty, local NLP optimizer runs.</span>
                </div>

                {/* 2. Automation Preferences */}
                <div>
                  <h3 style={{ fontSize: '16px', borderBottom: '1px solid var(--border-glass)', paddingBottom: '8px', marginBottom: '16px' }}>Automation Engine Controls</h3>
                  
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                    
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <div>
                        <div style={{ fontSize: '14px', fontWeight: 'bold' }}>Default Apply Mode</div>
                        <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Launch headed browser guided copilot (prevents anti-bot blocks)</div>
                      </div>
                      <label className="switch">
                        <input 
                          type="checkbox" 
                          checked={settings.automation_mode === 'interactive'} 
                          onChange={e => handleUpdateSetting('automation_mode', e.target.checked ? 'interactive' : 'headless')}
                        />
                        <span className="slider"></span>
                      </label>
                    </div>

                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <div>
                        <div style={{ fontSize: '14px', fontWeight: 'bold' }}>Daily Application Target</div>
                        <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Target applications limit warning check</div>
                      </div>
                      <input 
                        type="number" 
                        value={settings.daily_target || 30} 
                        onChange={e => handleUpdateSetting('daily_target', e.target.value)} 
                        style={{ width: '80px', padding: '8px', textAlign: 'center' }}
                      />
                    </div>

                  </div>
                </div>

              </div>

              {/* Secure Credentials Sidebar */}
              <div className="card-glass" style={{ height: 'fit-content' }}>
                <h3 style={{ fontSize: '16px', borderBottom: '1px solid var(--border-glass)', paddingBottom: '8px', marginBottom: '16px' }}>Board Login Channels</h3>
                <p style={{ fontSize: '12px', color: 'var(--text-secondary)', marginBottom: '16px', lineHeight: '1.5' }}>
                  Store credentials to support quick-fill automation. Details remain in your secure offline SQLite database.
                </p>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                  <div style={{ padding: '10px', background: 'rgba(255,255,255,0.02)', border: '1px solid var(--border-glass)', borderRadius: '6px', fontSize: '12px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <strong>Naukri Channel</strong>
                    <span style={{ color: 'var(--primary)' }}>Locked (Local Only)</span>
                  </div>
                  <div style={{ padding: '10px', background: 'rgba(255,255,255,0.02)', border: '1px solid var(--border-glass)', borderRadius: '6px', fontSize: '12px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <strong>LinkedIn Session</strong>
                    <span style={{ color: 'var(--primary)' }}>Session Active</span>
                  </div>
                  <div style={{ padding: '10px', background: 'rgba(255,255,255,0.02)', border: '1px solid var(--border-glass)', borderRadius: '6px', fontSize: '12px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <strong>Indeed Channel</strong>
                    <span style={{ color: 'var(--text-muted)' }}>Configured</span>
                  </div>
                </div>
              </div>

            </div>
          </div>
        )}

      </main>
    </div>
  );
}

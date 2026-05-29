import React from 'react';
import { Briefcase, BarChart2, CheckCircle, Calendar, RefreshCw, AlertCircle, ArrowRight } from 'lucide-react';

export default function DashboardHome({ stats, weeklyTrend, onNavigate, onTriggerScan, loadingScan }) {
  const {
    total_scraped,
    total_identified,
    total_optimized,
    total_applied,
    total_interviewing,
    total_offers,
    applied_today,
    daily_target,
    average_match_score,
    interview_rate
  } = stats;

  const pctApplied = Math.min(Math.round((applied_today / daily_target) * 100), 100);

  return (
    <div>
      <div className="header-bar">
        <div>
          <h1 style={{ fontSize: '32px', marginBottom: '8px' }}>Pipeline Dashboard</h1>
          <p style={{ color: 'var(--text-secondary)' }}>Welcome back! You are logged in as <strong>Inventory Analyst (1 YOE)</strong>.</p>
        </div>
        <button 
          onClick={onTriggerScan} 
          disabled={loadingScan}
          className="btn btn-primary"
        >
          <RefreshCw className={loadingScan ? "pulse-active" : ""} size={16} />
          {loadingScan ? "Aggregating Fresh Jobs..." : "Scan & Match India Jobs"}
        </button>
      </div>

      {/* Stats Grid */}
      <div className="stats-grid">
        <div className="card-glass stat-card card-glowing-primary">
          <div className="stat-icon primary">
            <CheckCircle size={22} />
          </div>
          <div>
            <div className="stat-lbl">Daily Quota Applied</div>
            <div className="stat-val" style={{ display: 'flex', alignItems: 'baseline', gap: '4px' }}>
              {applied_today} <span style={{ fontSize: '14px', color: 'var(--text-muted)' }}>/ {daily_target}</span>
            </div>
            <div style={{ width: '120px', background: 'rgba(255,255,255,0.05)', height: '4px', borderRadius: '2px', marginTop: '6px', overflow: 'hidden' }}>
              <div style={{ width: `${pctApplied}%`, background: 'var(--primary)', height: '100%' }}></div>
            </div>
          </div>
        </div>

        <div className="card-glass stat-card">
          <div className="stat-icon secondary">
            <BarChart2 size={22} />
          </div>
          <div>
            <div className="stat-lbl">Avg Compatibility</div>
            <div className="stat-val">{average_match_score}%</div>
            <div style={{ fontSize: '11px', color: 'var(--primary)', marginTop: '4px', fontWeight: 'bold' }}>All matches &gt;75%</div>
          </div>
        </div>

        <div className="card-glass stat-card">
          <div className="stat-icon accent">
            <Briefcase size={22} />
          </div>
          <div>
            <div className="stat-lbl">Active Applications</div>
            <div className="stat-val">{total_applied}</div>
            <div style={{ fontSize: '11px', color: 'var(--text-secondary)', marginTop: '4px' }}>Across LinkedIn & portals</div>
          </div>
        </div>

        <div className="card-glass stat-card">
          <div className="stat-icon warning">
            <Calendar size={22} />
          </div>
          <div>
            <div className="stat-lbl">Interview Rate</div>
            <div className="stat-val">{interview_rate}%</div>
            <div style={{ fontSize: '11px', color: 'var(--warning)', marginTop: '4px', fontWeight: 'bold' }}>{total_interviewing} Active Rounds</div>
          </div>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 340px', gap: '24px', marginBottom: '32px' }}>
        
        {/* Weekly Trend Chart */}
        <div className="card-glass">
          <h3 style={{ fontSize: '18px', marginBottom: '24px' }}>Weekly Application Activity</h3>
          
          <div style={{ height: '240px', display: 'flex', alignItems: 'flex-end', justifyContent: 'space-between', padding: '10px 20px 20px 20px', position: 'relative' }}>
            {/* SVG Background grids */}
            <div style={{ position: 'absolute', top: 0, left: 0, right: 0, bottom: 20, display: 'flex', flexDirection: 'column', justifyContent: 'space-between', opacity: 0.05, pointerEvents: 'none' }}>
              <div style={{ borderBottom: '1px solid white', width: '100%', height: '1px' }}></div>
              <div style={{ borderBottom: '1px solid white', width: '100%', height: '1px' }}></div>
              <div style={{ borderBottom: '1px solid white', width: '100%', height: '1px' }}></div>
              <div style={{ borderBottom: '1px solid white', width: '100%', height: '1px' }}></div>
            </div>

            {weeklyTrend.map((item, idx) => {
              const maxVal = Math.max(...weeklyTrend.map(t => t.applied), 10);
              const heightPct = (item.applied / maxVal) * 160; // Max height 160px
              return (
                <div key={idx} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', width: '12%', gap: '8px', zIndex: 1 }}>
                  <div style={{ color: 'var(--primary)', fontSize: '12px', fontWeight: 'bold' }}>{item.applied}</div>
                  
                  {/* Visual Glowing SVG bar */}
                  <div style={{ 
                    width: '100%', 
                    height: `${heightPct}px`, 
                    background: 'linear-gradient(180deg, var(--primary), var(--secondary))',
                    borderRadius: '6px 6px 0 0',
                    boxShadow: '0 0 15px rgba(16, 185, 129, 0.25)',
                    transition: 'height 0.8s cubic-bezier(0.4, 0, 0.2, 1)'
                  }}></div>
                  
                  <div style={{ color: 'var(--text-secondary)', fontSize: '11px', fontWeight: '600' }}>{item.day}</div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Action Center Sidebar */}
        <div className="card-glass" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
          <div>
            <h3 style={{ fontSize: '18px', marginBottom: '16px' }}>Application Engine</h3>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              <div style={{ display: 'flex', gap: '10px', background: 'rgba(255,255,255,0.02)', padding: '12px', borderRadius: '8px', border: '1px solid var(--border-glass)' }}>
                <AlertCircle size={18} style={{ color: 'var(--warning)', flexShrink: 0 }} />
                <div style={{ fontSize: '13px' }}>
                  <div style={{ fontWeight: '600', marginBottom: '2px' }}>Resume score is 82/100</div>
                  <div style={{ color: 'var(--text-secondary)' }}>You are missing keyword <strong>OTIF</strong> in Logistics. <span onClick={() => onNavigate('resume')} style={{ color: 'var(--primary)', cursor: 'pointer', textDecoration: 'underline' }}>Optimize now</span>.</div>
                </div>
              </div>

              <div style={{ display: 'flex', gap: '10px', background: 'rgba(255,255,255,0.02)', padding: '12px', borderRadius: '8px', border: '1px solid var(--border-glass)' }}>
                <CheckCircle size={18} style={{ color: 'var(--primary)', flexShrink: 0 }} />
                <div style={{ fontSize: '13px' }}>
                  <div style={{ fontWeight: '600', marginBottom: '2px' }}>Chennai/Bangalore Targets</div>
                  <div style={{ color: 'var(--text-secondary)' }}>Filters locked to prioritize South India tech & logistics clusters.</div>
                </div>
              </div>
            </div>
          </div>

          <button 
            onClick={() => onNavigate('jobs')} 
            className="btn btn-primary" 
            style={{ width: '100%', marginTop: '24px' }}
          >
            Review High-Match Jobs
            <ArrowRight size={16} />
          </button>
        </div>
      </div>

      {/* Match Pipeline funnel */}
      <div className="card-glass">
        <h3 style={{ fontSize: '18px', marginBottom: '20px' }}>Match Pipeline Funnel</h3>
        <div style={{ display: 'flex', width: '100%', justifyContent: 'space-between', background: 'rgba(10, 15, 28, 0.4)', borderRadius: '12px', padding: '24px', border: '1px solid var(--border-glass)' }}>
          <div style={{ width: '18%', textAlign: 'center' }}>
            <div style={{ fontSize: '24px', fontWeight: 'bold', color: 'var(--text-primary)' }}>{total_scraped || 184}</div>
            <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '4px' }}>Jobs Scraped</div>
            <div style={{ height: '4px', background: 'rgba(255,255,255,0.1)', borderRadius: '2px', marginTop: '12px' }}>
              <div style={{ width: '100%', background: 'rgba(255,255,255,0.4)', height: '100%', borderRadius: '2px' }}></div>
            </div>
          </div>
          
          <div style={{ display: 'flex', alignItems: 'center', color: 'var(--text-muted)' }}><ArrowRight size={16} /></div>

          <div style={{ width: '18%', textAlign: 'center' }}>
            <div style={{ fontSize: '24px', fontWeight: 'bold', color: 'var(--secondary)' }}>{total_identified || 52}</div>
            <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '4px' }}>High Match (&gt;75%)</div>
            <div style={{ height: '4px', background: 'rgba(255,255,255,0.1)', borderRadius: '2px', marginTop: '12px' }}>
              <div style={{ width: '65%', background: 'var(--secondary)', height: '100%', borderRadius: '2px' }}></div>
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', color: 'var(--text-muted)' }}><ArrowRight size={16} /></div>

          <div style={{ width: '18%', textAlign: 'center' }}>
            <div style={{ fontSize: '24px', fontWeight: 'bold', color: 'var(--accent)' }}>{total_optimized || 18}</div>
            <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '4px' }}>Custom Optimized</div>
            <div style={{ height: '4px', background: 'rgba(255,255,255,0.1)', borderRadius: '2px', marginTop: '12px' }}>
              <div style={{ width: '40%', background: 'var(--accent)', height: '100%', borderRadius: '2px' }}></div>
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', color: 'var(--text-muted)' }}><ArrowRight size={16} /></div>

          <div style={{ width: '18%', textAlign: 'center' }}>
            <div style={{ fontSize: '24px', fontWeight: 'bold', color: 'var(--primary)' }}>{total_applied || 12}</div>
            <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '4px' }}>Applied (Daily Target)</div>
            <div style={{ height: '4px', background: 'rgba(255,255,255,0.1)', borderRadius: '2px', marginTop: '12px' }}>
              <div style={{ width: '25%', background: 'var(--primary)', height: '100%', borderRadius: '2px' }}></div>
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', color: 'var(--text-muted)' }}><ArrowRight size={16} /></div>

          <div style={{ width: '18%', textAlign: 'center' }}>
            <div style={{ fontSize: '24px', fontWeight: 'bold', color: 'var(--warning)' }}>{total_interviewing || 4}</div>
            <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '4px' }}>Interviewing</div>
            <div style={{ height: '4px', background: 'rgba(255,255,255,0.1)', borderRadius: '2px', marginTop: '12px' }}>
              <div style={{ width: '10%', background: 'var(--warning)', height: '100%', borderRadius: '2px' }}></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

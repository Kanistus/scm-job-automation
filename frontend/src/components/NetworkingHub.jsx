import React, { useState } from 'react';
import { Send, Clipboard, Check, Users, MessageCircle } from 'lucide-react';

export default function NetworkingHub() {
  const [recName, setRecName] = useState('HR Manager');
  const [compName, setCompName] = useState('TVS Logistics');
  const [roleTitle, setRoleTitle] = useState('Inventory Analyst');
  const [jobLoc, setJobLoc] = useState('Chennai');
  const [copiedField, setCopiedField] = useState(null);

  const handleCopy = (text, field) => {
    navigator.clipboard.writeText(text);
    setCopiedField(field);
    setTimeout(() => setCopiedField(null), 2000);
  };

  const getLinkedInInvite = () => {
    return `Hi ${recName},\n\nI noticed your focus on logistics recruitment at ${compName}. I'm an Inventory Analyst with 1 year of experience auditing stock, optimizing replenishment cycles, and leveraging SAP MM/Excel. I just applied for the ${roleTitle} role in ${jobLoc} and would love to connect. Thanks!`;
  };

  const getColdOutreach = () => {
    return `Dear ${recName},\n\nI hope this message finds you well.\n\nI recently submitted my application for the ${roleTitle} opening at ${compName} in ${jobLoc}. With 1 year of professional experience as an Inventory Analyst managing stock audits, cycle counts, and safety stock levels, I wanted to reach out to express my enthusiasm directly.\n\nIn my current capacity, I use Advanced Excel (XLOOKUP, Pivot Tables) and SAP MM to optimize warehouse replenishment planning. I have a track record of identifying stock discrepancies and collaborating with suppliers to reduce order lead times by 14% while keeping inventory accuracies above 98%.\n\nI would love the opportunity to share how my analytics skills can benefit ${compName}'s supply chain efficiency. I've attached my resume for your review.\n\nThank you for your time and consideration.\n\nBest regards,\nCandidate Name\nemail@candidate.com | 9876543210`;
  };

  const getFollowUp = () => {
    return `Dear ${recName},\n\nI hope you are having a productive week.\n\nI am writing to briefly follow up on my application for the ${roleTitle} position (Ref: Applied last week). I remain highly interested in joining the SCM operations team at ${compName} in ${jobLoc}.\n\nHaving recently audited our local warehouse stock accuracies and improved safety stock levels by 15%, I am eager to apply my 1 YOE logistics analyst background to support your distribution networks.\n\nPlease let me know if you require any additional details or references. I look forward to hearing from you.\n\nBest regards,\nCandidate Name\nemail@candidate.com`;
  };

  return (
    <div>
      <div className="header-bar">
        <div>
          <h1 style={{ fontSize: '32px', marginBottom: '8px' }}>Networking Hub</h1>
          <p style={{ color: 'var(--text-secondary)' }}>Draft customized HR cold outreach letters, LinkedIn connection notes, and follow-up templates.</p>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '320px 1fr', gap: '24px' }}>
        
        {/* Left Side: Parameters Customizer */}
        <div className="card-glass" style={{ display: 'flex', flexDirection: 'column', gap: '16px', height: 'fit-content' }}>
          <h3 style={{ fontSize: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Users size={16} style={{ color: 'var(--primary)' }} />
            Outreach Parameters
          </h3>
          
          <div>
            <label style={{ fontSize: '12px', fontWeight: 'bold', color: 'var(--text-secondary)', display: 'block', marginBottom: '6px' }}>Recruiter Name</label>
            <input type="text" value={recName} onChange={e => setRecName(e.target.value)} placeholder="e.g. Priya" />
          </div>

          <div>
            <label style={{ fontSize: '12px', fontWeight: 'bold', color: 'var(--text-secondary)', display: 'block', marginBottom: '6px' }}>Company Name</label>
            <input type="text" value={compName} onChange={e => setCompName(e.target.value)} placeholder="e.g. TVS Logistics" />
          </div>

          <div>
            <label style={{ fontSize: '12px', fontWeight: 'bold', color: 'var(--text-secondary)', display: 'block', marginBottom: '6px' }}>Target Role</label>
            <input type="text" value={roleTitle} onChange={e => setRoleTitle(e.target.value)} placeholder="e.g. Inventory Analyst" />
          </div>

          <div>
            <label style={{ fontSize: '12px', fontWeight: 'bold', color: 'var(--text-secondary)', display: 'block', marginBottom: '6px' }}>Job Location</label>
            <input type="text" value={jobLoc} onChange={e => setJobLoc(e.target.value)} placeholder="e.g. Chennai" />
          </div>
        </div>

        {/* Right Side: Generated Templates */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          
          {/* LinkedIn Invite */}
          <div className="card-glass">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
              <h3 style={{ fontSize: '15px', color: 'white', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <MessageCircle size={16} style={{ color: 'var(--secondary)' }} />
                LinkedIn Invite Note (300 Char Limit)
              </h3>
              <button onClick={() => handleCopy(getLinkedInInvite(), 'invite')} className="btn btn-secondary" style={{ padding: '6px 12px', fontSize: '12px' }}>
                {copiedField === 'invite' ? <Check size={14} style={{ color: 'var(--primary)' }} /> : <Clipboard size={14} />}
                {copiedField === 'invite' ? "Copied invite" : "Copy text"}
              </button>
            </div>
            <textarea 
              readOnly 
              value={getLinkedInInvite()} 
              rows={4} 
              style={{ fontSize: '13px', background: 'rgba(0,0,0,0.2)', lineHeight: '1.5', resize: 'none' }}
            />
          </div>

          {/* Cold Outreach */}
          <div className="card-glass">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
              <h3 style={{ fontSize: '15px', color: 'white', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Send size={14} style={{ color: 'var(--primary)' }} />
                Email / LinkedIn InMail Cold Pitch
              </h3>
              <button onClick={() => handleCopy(getColdOutreach(), 'cold')} className="btn btn-secondary" style={{ padding: '6px 12px', fontSize: '12px' }}>
                {copiedField === 'cold' ? <Check size={14} style={{ color: 'var(--primary)' }} /> : <Clipboard size={14} />}
                {copiedField === 'cold' ? "Copied Pitch" : "Copy text"}
              </button>
            </div>
            <textarea 
              readOnly 
              value={getColdOutreach()} 
              rows={12} 
              style={{ fontSize: '13px', background: 'rgba(0,0,0,0.2)', lineHeight: '1.5', resize: 'none' }}
            />
          </div>

          {/* Follow-Up Letter */}
          <div className="card-glass">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
              <h3 style={{ fontSize: '15px', color: 'white' }}>Post-Application Follow-Up</h3>
              <button onClick={() => handleCopy(getFollowUp(), 'follow')} className="btn btn-secondary" style={{ padding: '6px 12px', fontSize: '12px' }}>
                {copiedField === 'follow' ? <Check size={14} style={{ color: 'var(--primary)' }} /> : <Clipboard size={14} />}
                {copiedField === 'follow' ? "Copied Letter" : "Copy text"}
              </button>
            </div>
            <textarea 
              readOnly 
              value={getFollowUp()} 
              rows={10} 
              style={{ fontSize: '13px', background: 'rgba(0,0,0,0.2)', lineHeight: '1.5', resize: 'none' }}
            />
          </div>

        </div>

      </div>
    </div>
  );
}

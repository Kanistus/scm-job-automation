import React, { useState } from 'react';
import { HelpCircle, FileText, Database, Layers, CheckSquare } from 'lucide-react';

const SECTIONS = [
  { id: 'kpis', name: 'Inventory & KPIs', icon: HelpCircle },
  { id: 'excel', name: 'Excel & Analytics', icon: FileText },
  { id: 'sap', name: 'SAP ERP T-Codes', icon: Database },
  { id: 'star', name: 'STAR Case Studies', icon: Layers }
];

const KPIS_QS = [
  {
    q: "How do you calculate safety stock? What inputs do you use?",
    a: "Safety Stock = (Max Daily Sales * Max Lead Time) - (Average Daily Sales * Average Lead Time). Inputs needed are: 1) Daily demand logs, 2) Vendor lead times, and 3) Target service level (standard is 95-98%). I use safety stock to buffer against seasonal peaks or logistics delays without overstocking warehouse capital."
  },
  {
    q: "What is Inventory Turnover Ratio, and why is it important?",
    a: "Inventory Turnover Ratio = Cost of Goods Sold (COGS) / Average Inventory Value. It measures how many times inventory is sold and replaced over a period. A high ratio indicates strong sales velocity and efficient capital locking; a low ratio suggests slow-moving stock, obsolete items, or warehouse bottlenecks."
  },
  {
    q: "Explain OTIF and DSI. What do they tell you about the supply chain?",
    a: "1) OTIF (On-Time In-Full) measures the percentage of vendor shipments delivered within the slot and with complete quantities. It audits supplier reliability. 2) DSI (Days Sales of Inventory) = (Average Inventory / COGS) * 365. It represents the average number of days it takes to turn inventory into sales. High DSI signals cash flow blockages."
  },
  {
    q: "How do you handle a critical inventory discrepancy during stock auditing?",
    a: "I execute a 4-step reconciliation: 1) Verify physical count across all warehouse bins, 2) Audit material document transaction logs (MIGO/GRN records) in the ERP for the last 30 days to check for shipping or receipt errors, 3) Cross-reference supplier delivery slips, and 4) Once identified, log the variance, correct the ledger, and implement a scanning check to prevent reoccurrence."
  }
];

const EXCEL_QS = [
  {
    q: "Why is XLOOKUP preferred over VLOOKUP for matching inventory lists?",
    a: "XLOOKUP is superior because: 1) It can search to the left (VLOOKUP only searches right), 2) It defaults to an exact match, 3) It has a built-in fallback value if a match isn't found, preventing #N/A errors, and 4) It doesn't break if columns are inserted or deleted in the target sheet."
  },
  {
    q: "How would you use Pivot Tables to audit slow-moving inventory?",
    a: "I load the stock aging report into Excel. In the Pivot Table: 1) Drag 'Item Category' to Rows, 2) Drag 'Months in Stock' to Columns, 3) Drag 'Inventory Value' to Values. I apply conditional formatting (red gradient) to cells where stock has aged >6 months to instantly spot dead stock locking capital."
  },
  {
    q: "What is the function of SUMIFS in a supply chain dashboard?",
    a: "SUMIFS sums values in a range that meet multiple criteria. For example: SUMIFS(StockValueRange, CategoryRange, \"Electronics\", LocationRange, \"Chennai Warehouse\"). This lets me dynamically calculate category values for specific locations."
  }
];

const SAP_TCODES = [
  { code: "MMBE", name: "Stock Overview", desc: "Allows looking up stock levels of a specific material code across all plants, storage locations, and batches in real-time." },
  { code: "MB51", name: "Material Document List", desc: "Displays historical material transaction ledger. Essential for auditing cycle count variances, goods receipts (GRN), and warehouse transfers." },
  { code: "LS24", name: "WM Stock per Bin", desc: "Used in Warehouse Management module to identify which specific rack, row, and bin number a particular SKU is located in." },
  { code: "MIGO", name: "Goods Movements", desc: "Used to post Goods Receipt (GRN) from purchase orders, log warehouse transfers, or record stock adjustments." },
  { code: "MD04", name: "Stock/Requirements List", desc: "Shows real-time supply and demand status, material reservations, purchase requisitions, and safety stock levels for forecasting replenishment." }
];

const STAR_CASES = [
  {
    title: "15% Reduction in Order Lead-Times",
    s: "At the warehouse, logistics dispatch delays were causing replenishment cycles to drag, resulting in a low OTIF score of 88%.",
    t: "Identify bottleneck reasons in purchase order release and transit loops, and streamline the logistics process.",
    a: "I pulled 6 months of vendor transit records into Excel, performed a regression analysis on dispatch loops, and found a 3-day delay in our manual GRN validation. I integrated a quick barcode scanning scan-in step in our ERP workflow.",
    r: "Slashing manual validation times by 80%, reducing total order lead-time by 15%, and restoring vendor OTIF scores to 97.4%."
  },
  {
    title: "Reconciling a 12% Cycle Count Variance",
    s: "During a major annual stock audit, a critical electronics SKU showed a 12% inventory discrepancy, locking operations.",
    t: "Locate the discrepancy source and correct our ERP ledgers without interrupting daily warehouse dispatches.",
    a: "I ran an audit of MB51 material documents and cross-referenced warehouse bins (LS24). I tracked the error to a warehouse transfer slip that was received physically but unposted in the ERP MM system.",
    r: "Re-posted the transactions, reconciled the ledger back to 100% accuracy, and set up a daily automatic ledger audit email."
  }
];

export default function InterviewPrep() {
  const [activeSection, setActiveSection] = useState('kpis');

  return (
    <div>
      <div className="header-bar">
        <div>
          <h1 style={{ fontSize: '32px', marginBottom: '8px' }}>Interview Preparation</h1>
          <p style={{ color: 'var(--text-secondary)' }}>Master standard supply chain equations, Excel analysis tools, SAP ERP codes, and STAR structural achievements.</p>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '260px 1fr', gap: '24px' }}>
        
        {/* Navigation Sidebar */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {SECTIONS.map(sec => {
            const Icon = sec.icon;
            return (
              <button 
                key={sec.id}
                onClick={() => setActiveSection(sec.id)}
                className={`btn ${activeSection === sec.id ? 'btn-primary' : 'btn-secondary'}`}
                style={{ justifyContent: 'flex-start', padding: '12px 16px', fontSize: '13px' }}
              >
                <Icon size={16} />
                {sec.name}
              </button>
            );
          })}
        </div>

        {/* Content Workspace Panel */}
        <div className="card-glass">
          
          {/* KPIS */}
          {activeSection === 'kpis' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
              <h2 style={{ fontSize: '20px', borderBottom: '1px solid var(--border-glass)', paddingBottom: '12px' }}>Inventory & Logistics KPIs Q&A</h2>
              
              <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                {KPIS_QS.map((item, idx) => (
                  <div key={idx} style={{ background: 'rgba(255,255,255,0.02)', padding: '16px', borderRadius: '8px', border: '1px solid var(--border-glass)' }}>
                    <div style={{ fontWeight: 'bold', fontSize: '14px', color: 'white', marginBottom: '8px' }}>{idx + 1}. {item.q}</div>
                    <div style={{ fontSize: '13px', color: 'var(--text-secondary)', lineHeight: '1.6' }}>{item.a}</div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* EXCEL */}
          {activeSection === 'excel' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
              <h2 style={{ fontSize: '20px', borderBottom: '1px solid var(--border-glass)', paddingBottom: '12px' }}>Excel & SCM Data Analysis Q&A</h2>
              
              <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                {EXCEL_QS.map((item, idx) => (
                  <div key={idx} style={{ background: 'rgba(255,255,255,0.02)', padding: '16px', borderRadius: '8px', border: '1px solid var(--border-glass)' }}>
                    <div style={{ fontWeight: 'bold', fontSize: '14px', color: 'white', marginBottom: '8px' }}>{idx + 1}. {item.q}</div>
                    <div style={{ fontSize: '13px', color: 'var(--text-secondary)', lineHeight: '1.6' }}>{item.a}</div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* SAP ERP */}
          {activeSection === 'sap' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
              <h2 style={{ fontSize: '20px', borderBottom: '1px solid var(--border-glass)', paddingBottom: '12px' }}>Core SAP ERP Transaction Codes (T-Codes)</h2>
              
              <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '12px' }}>
                {SAP_TCODES.map((item, idx) => (
                  <div key={idx} style={{ display: 'flex', gap: '16px', background: 'rgba(255,255,255,0.02)', padding: '16px', borderRadius: '8px', border: '1px solid var(--border-glass)' }}>
                    <div style={{ background: 'rgba(16, 185, 129, 0.08)', border: '1px solid rgba(16, 185, 129, 0.2)', color: 'var(--primary)', padding: '6px 12px', borderRadius: '6px', fontWeight: 'bold', fontSize: '14px', height: 'fit-content', display: 'flex', alignItems: 'center', width: '80px', justifyContent: 'center' }}>
                      {item.code}
                    </div>
                    <div>
                      <h4 style={{ color: 'white', fontSize: '14px', marginBottom: '4px' }}>{item.name}</h4>
                      <p style={{ color: 'var(--text-secondary)', fontSize: '12px', lineHeight: '1.5' }}>{item.desc}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* STAR CASES */}
          {activeSection === 'star' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
              <h2 style={{ fontSize: '20px', borderBottom: '1px solid var(--border-glass)', paddingBottom: '12px' }}>STAR-formatted Case Studies (1 YOE Portfolio)</h2>
              
              <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                {STAR_CASES.map((item, idx) => (
                  <div key={idx} style={{ background: 'rgba(255,255,255,0.02)', padding: '20px', borderRadius: '8px', border: '1px solid var(--border-glass)' }}>
                    <h3 style={{ color: 'white', fontSize: '16px', marginBottom: '14px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <CheckSquare size={16} style={{ color: 'var(--primary)' }} />
                      {item.title}
                    </h3>
                    
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', fontSize: '13px' }}>
                      <div>
                        <strong style={{ color: 'var(--danger)' }}>Situation:</strong>
                        <span style={{ color: 'var(--text-secondary)', marginLeft: '6px' }}>{item.s}</span>
                      </div>
                      <div>
                        <strong style={{ color: 'var(--warning)' }}>Task:</strong>
                        <span style={{ color: 'var(--text-secondary)', marginLeft: '6px' }}>{item.t}</span>
                      </div>
                      <div>
                        <strong style={{ color: 'var(--secondary)' }}>Action:</strong>
                        <span style={{ color: 'var(--text-secondary)', marginLeft: '6px' }}>{item.a}</span>
                      </div>
                      <div>
                        <strong style={{ color: 'var(--primary)' }}>Result:</strong>
                        <span style={{ color: 'white', marginLeft: '6px', fontWeight: 'bold' }}>{item.r}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

        </div>

      </div>
    </div>
  );
}

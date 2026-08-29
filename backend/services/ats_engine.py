import re
import json
import os
import warnings
try:
    from google import genai
    genai_legacy = False
except ImportError:
    genai_legacy = True
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=FutureWarning)
            import google.generativeai as genai
    except ImportError:
        genai = None

# Comprehensive Domain keyword database matching candidate's new resume & search objective
KEYWORDS_DB = {
    "supply_chain": [
        "supply chain", "logistics", "inventory", "demand planning", "procurement", 
        "fulfillment", "warehouse", "reverse logistics", "3pl", "sourcing", 
        "replenishment", "stock auditing", "purchase order", "lead time", "shipping"
    ],
    "process_improvement": [
        "process improvement", "process optimization", "continuous improvement", 
        "operational excellence", "process excellence", "lean", "six sigma", "kaizen", 
        "root cause analysis", "rca", "process mapping", "workflow mapping", "sop", 
        "productivity improvement", "bottleneck", "turnaround time", "cycle time"
    ],
    "analytics": [
        "excel", "advanced excel", "sql", "dashboard", "kpi", "forecasting", 
        "data analysis", "performance analysis", "reporting", "power bi", "tableau", "metrics", "dsi", "otif"
    ],
    "automation": [
        "automation", "ai", "ai automation", "workflow automation", "process mining", 
        "digital transformation", "erp", "sap", "sap mm", "wms", "digital supply chain", "technology"
    ]
}

PRIORITY_TITLES = [
    "supply chain analyst", "supply chain process analyst", "supply chain operations analyst",
    "supply chain improvement analyst", "supply chain excellence analyst", "process improvement analyst",
    "process excellence analyst", "operations excellence analyst", "operational excellence analyst",
    "business process analyst", "process analyst", "continuous improvement analyst",
    "supply chain optimization analyst", "supply chain planning analyst", "logistics process analyst",
    "supply chain performance analyst", "reverse logistics analyst", "process automation analyst"
]

SECONDARY_TITLES = [
    "supply chain associate", "supply chain specialist", "supply chain executive",
    "operations analyst", "operations specialist", "logistics analyst", "logistics operations analyst",
    "warehouse operations analyst", "inventory analyst", "inventory optimization analyst",
    "demand planning analyst", "procurement analyst", "fulfillment analyst",
    "continuous improvement specialist", "process improvement specialist", "process excellence specialist",
    "digital supply chain", "supply chain transformation"
]

EXCLUDED_TERMS = [
    "inside sales", "business development executive", "telecaller", "field sales", 
    "customer service representative", "call center", "driver", "delivery rider", 
    "pure data entry", "manpower supervisor", "software developer", "java developer", 
    "react", "node.js", "frontend", "backend", "full stack"
]

def clean_text(text):
    return re.sub(r'\s+', ' ', text.lower().strip())

def calculate_compatibility(profile, job_description, title, location):
    """
    Calculates job compatibility score (0-100) based on strict 6-part weighted criteria:
    1. Supply Chain Relevance (25 pts)
    2. Process Improvement & Excellence (25 pts)
    3. Analytics (15 pts)
    4. Automation / Technology (15 pts)
    5. Career Growth / Title Fit (10 pts)
    6. Experience & Location Fit (10 pts)
    """
    jd_clean = clean_text(job_description)
    title_clean = clean_text(title)
    loc_clean = clean_text(location)
    
    reasons = []
    matched_keywords = []
    missing_keywords = []
    
    # 0. Check Rejection Guardrails (-60 pts penalty)
    is_rejected = any(term in title_clean or term in jd_clean for term in EXCLUDED_TERMS)
    if is_rejected:
        return {
            "score": 15,
            "fits": False,
            "reasons": ["Excluded: Role matches generic sales, telecalling, customer support, or non-analytical manual supervision."],
            "matched_keywords": [],
            "missing_keywords": ["Supply Chain Process Improvement"]
        }

    # 1. Supply Chain Relevance (Max 25 pts)
    sc_score = 0
    for kw in KEYWORDS_DB["supply_chain"]:
        if kw in jd_clean or kw in title_clean:
            sc_score += 3
            matched_keywords.append(kw.title())
    sc_score = min(25, sc_score)
    if sc_score >= 15:
        reasons.append("High Match: Directly involves Supply Chain, Inventory, 3PL, or Logistics operations (25/25).")
    else:
        reasons.append("Moderate Match: Partial supply chain domain overlap.")

    # 2. Process Improvement & Operational Excellence (Max 25 pts)
    pi_score = 0
    for kw in KEYWORDS_DB["process_improvement"]:
        if kw in jd_clean or kw in title_clean:
            pi_score += 4
            matched_keywords.append(kw.title())
    pi_score = min(25, pi_score)
    if pi_score >= 16:
        reasons.append("High Match: Strong focus on Process Improvement, RCA, Six Sigma, and Operational Excellence (25/25).")
    elif pi_score > 0:
        reasons.append("Moderate Match: Mentions process optimization or KPI tracking.")
    else:
        missing_keywords.append("Process Improvement / Lean Six Sigma")

    # 3. Analytics & Data Tools (Max 15 pts)
    an_score = 0
    for kw in KEYWORDS_DB["analytics"]:
        if kw in jd_clean or kw in title_clean:
            an_score += 3
            matched_keywords.append(kw.title())
    an_score = min(15, an_score)
    if an_score >= 9:
        reasons.append("High Match: Strong alignment with Excel, SQL, KPI dashboards, and data analytics (15/15).")

    # 4. Automation & Technology (Max 15 pts)
    auto_score = 0
    for kw in KEYWORDS_DB["automation"]:
        if kw in jd_clean or kw in title_clean:
            auto_score += 4
            matched_keywords.append(kw.title())
    auto_score = min(15, auto_score)
    if auto_score >= 8:
        reasons.append("High Match: Involves AI, process automation, ERP systems (SAP/WMS), or digital transformation.")

    # 5. Career Growth / Priority Title Alignment (Max 10 pts)
    title_score = 0
    if any(p_title in title_clean for p_title in PRIORITY_TITLES):
        title_score = 10
        reasons.append("Priority Title Match: Directly aligns with Supply Chain + Process Improvement career path.")
    elif any(s_title in title_clean for s_title in SECONDARY_TITLES):
        title_score = 7
        reasons.append("Secondary Title Match: Highly relevant operational role.")
    else:
        title_score = 4

    # 6. Experience Fit & Location (Max 10 pts)
    exp_loc_score = 0
    if "bengaluru" in loc_clean or "bangalore" in loc_clean:
        exp_loc_score += 5
        reasons.append("Location Match: Bengaluru (Priority #1 Location).")
    elif "remote" in loc_clean or "hybrid" in loc_clean or "chennai" in loc_clean or "india" in loc_clean:
        exp_loc_score += 4
        reasons.append(f"Location Match: {location} (Acceptable Indian location).")
    else:
        exp_loc_score += 2

    # Check Experience level
    if any(term in jd_clean or term in title_clean for term in ["0-2", "1-3", "0-3", "entry", "associate", "analyst", "executive", "junior"]):
        exp_loc_score += 5
    elif any(term in title_clean for term in ["director", "vp", "head of", "principal", "chief"]):
        exp_loc_score -= 5
        reasons.append("Experience Caution: Senior leadership role.")
    else:
        exp_loc_score += 3

    total_score = sc_score + pi_score + an_score + auto_score + title_score + exp_loc_score
    total_score = max(0, min(100, total_score))

    matched_keywords = list(set(matched_keywords))
    
    # Fill missing keywords list
    for category in KEYWORDS_DB.values():
        for kw in category:
            if kw not in jd_clean and len(missing_keywords) < 8:
                missing_keywords.append(kw.title())

    return {
        "score": total_score,
        "fits": total_score >= 70,
        "reasons": list(set(reasons)),
        "matched_keywords": matched_keywords[:12],
        "missing_keywords": list(set(missing_keywords))[:8]
    }

def generate_optimized_assets(profile, job, settings):
    """
    Generates customized resume modifications, cover letter, recruiter pitches,
    and interview prep tailored to candidate's Flipkart reverse logistics & process improvement background.
    """
    api_key = settings.get("gemini_api_key", "")
    
    jd = job.get("description", "")
    title = job.get("title", "")
    company = job.get("company", "")
    location = job.get("location", "")
    
    if api_key and genai:
        try:
            if not genai_legacy:
                client = genai.Client(api_key=api_key)
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=f"Optimize ATS resume & cover letter for {title} at {company}. JD: {jd}. Candidate: {json.dumps(profile)}"
                )
                raw_text = response.text.strip()
            else:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content(f"Optimize ATS resume for {title}. Profile: {json.dumps(profile)}")
                raw_text = response.text.strip()
                
            if raw_text.startswith("```json"):
                raw_text = raw_text[7:]
            if raw_text.endswith("```"):
                raw_text = raw_text[:-3]
            return json.loads(raw_text.strip())
        except Exception as e:
            print(f"Gemini AI optimization failed, running local engine: {e}")

    # Local Engine (Tailored to Kanistus VM's new Flipkart + Bluewave profile)
    matched_data = calculate_compatibility(profile, jd, title, location)
    missing = matched_data["missing_keywords"][:5]
    
    injected_str = ", ".join(missing) if missing else "Process Improvement, Root Cause Analysis, 3PL Coordination"
    improvement = f"Optimized by injecting high-priority ATS keywords matching '{title}': {injected_str}. Customized achievements from Flipkart reverse logistics and Bluewave inventory operations."
    
    summary = (
        f"Supply Chain & Operations Analyst with experience in process improvement, reverse logistics, warehouse operations, "
        f"and supply chain analytics. Proven track record at Flipkart managing 3PL coordination, return-order workflows, "
        f"and root-cause analysis. Expert in Advanced Excel, SAP MM, Lean Six Sigma, and AI automation to improve turnaround times for {company}."
    )
    
    bullets = [
        f"Managed reverse logistics operations at Flipkart, resolving shipment exceptions, invoice discrepancies, and 3PL pickup delays to improve return turnaround time.",
        f"Performed root-cause analysis (RCA) and implemented corrective actions to eliminate operational bottlenecks, driving process efficiency across logistics partners.",
        f"Led 10+ process improvement projects at Bluewave Infotech, deploying a QR-based tracking system that increased inventory accuracy from 85% to 97%."
    ]
    
    cover_letter = f"""Dear Hiring Team at {company},

I am writing to express my enthusiastic interest in the {title} role at {company}. With a career focus on Supply Chain Optimization, Process Improvement, and Operations Excellence, I bring hands-on experience from Flipkart (Bengaluru) managing reverse logistics, 3PL partner coordination, and root-cause problem solving.

In my current position as Executive at Flipkart, I oversee end-to-end return-order processing, monitor operational performance metrics, and execute root-cause analysis to resolve recurring logistics bottlenecks. Previously at Bluewave Infotech, I led 10+ process improvement projects across procurement, warehouse inventory, and dispatch, successfully designing a QR-based tracking system that boosted inventory accuracy from 85% to 97%.

My technical skills span Advanced Excel, SAP MM, Lean Six Sigma principles, and process mapping (BPMN/Workflow mapping). What excites me about {company} is the opportunity to apply data-driven process optimization and automation to strengthen your supply chain operations.

Thank you for your consideration. I look forward to discussing how my process improvement background can support {company}'s strategic goals.

Sincerely,
{profile.get('name', 'Kanistus VM')}
{profile.get('email', 'kanistusvm@gmail.com')} | {profile.get('phone', '+91 6383441249')}
Bengaluru, Karnataka, India"""

    rec_pitch = (
        f"Hi [Recruiter Name],\n\nI noticed your opening for {title} at {company}. "
        f"I'm a Supply Chain & Process Improvement Analyst with hands-on experience at Flipkart (Bengaluru) "
        f"in reverse logistics, 3PL coordination, and root-cause analysis. I specialize in Lean Six Sigma, "
        f"Advanced Excel, and process automation. I've applied via the portal and would love to connect! "
        f"\n\nBest regards,\nKanistus VM\n+91 6383441249"
    )
    
    domain_qs = [
        {
            "question": "How do you approach Root Cause Analysis (RCA) in supply chain operations?",
            "answer": "At Flipkart, when encountering recurring return-order delays or address mismatch exceptions, I use the 5 Whys framework and Ishikawa (Fishbone) diagrams to isolate whether issues stem from 3PL courier handoffs, seller labeling errors, or warehouse receiving bottlenecks. Once isolated, I implement corrective SOP updates to eliminate recurring failures."
        },
        {
            "question": "Describe a process improvement project where you reduced turnaround time.",
            "answer": "At Bluewave Infotech, I led an initiative to streamline procurement-production-dispatch schedules. By mapping the end-to-end workflow and introducing a QR-based tracking system, we improved inventory accuracy from 85% to 97% and cut order processing cycle times by 14%."
        }
    ]
    
    tool_qs = [
        {
            "question": "How do you utilize Advanced Excel and ERP systems for operational reporting?",
            "answer": "I combine SAP MM document queries with Advanced Excel (XLOOKUP, Pivot Tables, SUMIFS) to track inventory DSI, OTIF vendor fulfillment rates, and reverse logistics return volume. This allows real-time visibility into operational bottlenecks."
        }
    ]

    return {
        "ats_score_improvement": improvement,
        "optimized_summary": summary,
        "optimized_experience_bullets": bullets,
        "cover_letter": cover_letter,
        "recruiter_message": rec_pitch,
        "interview_prep": {
            "domain_questions": domain_qs,
            "tool_questions": tool_qs
        }
    }

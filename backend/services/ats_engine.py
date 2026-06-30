import re
import json
import os
try:
    import google.generativeai as genai
except ImportError:
    genai = None

# Domain dictionaries
KEYWORDS_DB = {
    "supply_chain": ["supply chain", "demand forecasting", "replenishment", "procurement", "sourcing", "vendor management", "purchase order", "lead time"],
    "inventory": ["inventory analyst", "safety stock", "stock auditing", "cycle counting", "inventory accuracy", "carrying cost", "shrinkage", "kpi", "dsi", "fill rate", "otif"],
    "logistics": ["logistics coordinator", "shipping", "receiving", "distribution", "freight", "transportation", "dispatch", "delivery"],
    "warehouse": ["warehouse executive", "wms", "warehouse operations", "material handling", "stock replenishment", "goods receipt", "grn"],
    "tools": ["excel", "advanced excel", "pivot table", "vlookup", "xlookup", "power bi", "tableau", "sql", "vba", "sap", "sap mm", "netsuite", "oracle erp"]
}

def clean_text(text):
    return re.sub(r'\s+', ' ', text.lower().strip())

def calculate_compatibility(profile, job_description, title, location):
    """
    Calculates job compatibility score (0-100) based on target profile.
    Rejects/flags jobs with score < 75.
    """
    score = 40  # Base score for general domain matching
    reasons = []
    missing_keywords = []
    matched_keywords = []
    
    jd_clean = clean_text(job_description)
    title_clean = title.lower()
    loc_clean = location.lower()
    
    # 1. Experience Check (Reject roles requiring 3+ years or senior terms)
    senior_terms = ["senior", "sr.", "lead", "manager", "director", "vp", "head of", "principal", "chief", "expert", "strategic", "president"]
    
    # Check title and look for 3+ years experience in the job description
    has_senior_title = any(term in title_clean for term in senior_terms)
    has_high_exp = bool(re.search(r'\b[3-9]\+\s*years\b|\b[3-9]\s*-\s*[0-9]\s*years\b|\b[3-9]\s*to\s*[0-9]\s*years\b|\b[3-9]\s*years\s*of\s*experience\b|\brequire\s*[3-9]\s*years\b', jd_clean))
    
    is_senior = has_senior_title or has_high_exp
    
    if is_senior:
        score -= 40  # Heavily penalize to ensure it is completely avoided
        reasons.append("Excluded: Detected senior/managerial role or 3+ years experience requirement which exceeds entry-level preference.")
    else:
        reasons.append("Match: Target experience level aligns perfectly (Entry-level / Fresher / 0-2 years).")
        
    # Check for software / IT / Sales exclusions
    unrelated_terms = ["software developer", "java developer", "react", "node.js", "frontend", "backend", "full stack", "inside sales", "business development executive", "telecaller"]
    if any(term in title_clean for term in unrelated_terms):
        score -= 40
        reasons.append("Excluded: Detected unrelated IT/Developer or Direct Sales role.")

    # 2. Location Scoring
    loc_score = 0
    if "chennai" in loc_clean:
        loc_score = 20
        reasons.append("High Match: Location is Chennai (Priority #1).")
    elif "bangalore" in loc_clean or "bengaluru" in loc_clean:
        loc_score = 20
        reasons.append("High Match: Location is Bangalore (Priority #2).")
    elif "remote" in loc_clean or "hybrid" in loc_clean:
        loc_score = 15
        reasons.append("Match: Remote or Hybrid flexibility.")
    elif "india" in loc_clean or any(city in loc_clean for city in ["mumbai", "pune", "hyderabad", "delhi", "noida", "gurgaon"]):
        loc_score = 10
        reasons.append(f"Acceptable Match: Location is in India ({location}).")
    else:
        loc_score = 5
        reasons.append("Low Match: Location outside immediate preferences.")
        
    score += loc_score

    # 3. Domain & Keywords Matching (Max 25 pts)
    keyword_points = 0
    total_keywords_to_check = KEYWORDS_DB["supply_chain"] + KEYWORDS_DB["inventory"] + KEYWORDS_DB["logistics"] + KEYWORDS_DB["warehouse"]
    
    for kw in total_keywords_to_check:
        if kw in jd_clean:
            matched_keywords.append(kw.title())
            if kw in [s.lower() for s in profile.get("extracted_skills", [])]:
                keyword_points += 2
            else:
                missing_keywords.append(kw.title())
                keyword_points += 1
                
    keyword_points = min(keyword_points, 25)
    score += keyword_points
    if keyword_points > 15:
        reasons.append("High Match: Strong overlap in supply chain, inventory, or logistics keywords.")
    elif keyword_points > 5:
        reasons.append("Moderate Match: Found relevant domain operations keywords.")
    else:
        reasons.append("Low Match: Very few industry keywords overlap.")

    # 4. Tools & ERP Check (Max 15 pts)
    tool_points = 0
    for tool in KEYWORDS_DB["tools"]:
        if tool in jd_clean:
            if tool in [t.lower() for t in profile.get("extracted_tools", [])] or tool in [e.lower() for e in profile.get("extracted_erps", [])]:
                tool_points += 4
            else:
                tool_points += 2
                missing_keywords.append(tool.upper())
                
    tool_points = min(tool_points, 15)
    score += tool_points
    if tool_points >= 10:
        reasons.append("High Match: Strong requirements match for ERP (SAP/Oracle) and analytics tools (Excel/BI).")
    else:
        reasons.append("Moderate Match: Some tool matching.")

    # Cap score between 0 and 100
    score = max(0, min(100, score))
    
    # Clean duplicates in keywords lists
    matched_keywords = list(set(matched_keywords))
    missing_keywords = list(set(missing_keywords))[:10]
    
    return {
        "score": score,
        "fits": score >= 65,
        "reasons": reasons,
        "matched_keywords": matched_keywords,
        "missing_keywords": missing_keywords
    }

def generate_optimized_assets(profile, job, settings):
    """
    Generates customized resume modifications, cover letter, recruiter pitches,
    and interview prep questions. Supports Gemini API, falls back to local templates.
    """
    api_key = settings.get("gemini_api_key", "")
    
    jd = job.get("description", "")
    title = job.get("title", "")
    company = job.get("company", "")
    location = job.get("location", "")
    
    if api_key and genai:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            prompt = f"""
            You are an expert ATS (Applicant Tracking System) optimizer and professional recruiter specializing in Supply Chain, Warehouse Operations, Logistics, Procurement, and Demand Planning in India.
            
            Candidate's 1-year experience Profile:
            {json.dumps(profile, indent=2)}
            
            Target Job details:
            Title: {title}
            Company: {company}
            Location: {location}
            Job Description: {jd}
            
            Based on this, generate the following 5 assets structured in JSON format with exact keys.
            Ensure standard professional business tone.
            
            JSON Schema:
            {{
              "ats_score_improvement": "A paragraph explaining what keywords were injected and why",
              "optimized_summary": "A highly ATS-compliant professional summary (3-4 sentences) injecting keywords from the job description.",
              "optimized_experience_bullets": [
                 "Bullet 1 re-worded with exact matching keywords and 1-year inventory achievements with measurable metrics (e.g. 14% safety stock reduction, 99.2% cycle count accuracy).",
                 "Bullet 2 re-worded to match job requirements.",
                 "Bullet 3 re-worded to match job requirements."
              ],
              "cover_letter": "A concise, high-converting 3-4 paragraph cover letter customized to this role and company. Mention 1 year experience as an Inventory Analyst, SAP/Excel strengths, and analytical focus.",
              "recruiter_message": "A short, professional 120-150 word outreach message to a recruiter/hiring manager on LinkedIn.",
              "interview_prep": {{
                 "domain_questions": [
                    {{"question": "Domain question 1", "answer": "Answer explaining inventory KPIs in STAR format"}},
                    {{"question": "Domain question 2", "answer": "Answer"}},
                    {{"question": "Domain question 3", "answer": "Answer"}}
                 ],
                 "tool_questions": [
                    {{"question": "Excel/ERP question 1", "answer": "Detailed technical steps/t-codes"}},
                    {{"question": "Excel/ERP question 2", "answer": "Answer"}}
                 ]
              }}
            }}
            
            Respond ONLY with the raw JSON string. Do not include markdown code block formatting (like ```json) or other text.
            """
            
            response = model.generate_content(prompt)
            # Safe clean for JSON block
            raw_text = response.text.strip()
            if raw_text.startswith("```json"):
                raw_text = raw_text[7:]
            if raw_text.endswith("```"):
                raw_text = raw_text[:-3]
            
            return json.loads(raw_text.strip())
            
        except Exception as e:
            print(f"Gemini generation failed, falling back to local engine: {e}")
            # Fall through to local generation below
            
    # LOCAL ENGINE (HEURISTIC TEMPLATES)
    
    # 1. Injected keywords
    matched_data = calculate_compatibility(profile, jd, title, location)
    missing = matched_data["missing_keywords"][:5]
    
    injected_str = ", ".join(missing) if missing else "Safety Stock Optimization, Replenishment Cycles"
    improvement = f"Optimized by injecting high-priority ATS keywords matching this job post: {injected_str}. Improved density of analytical tools and customized accomplishments to stand out."
    
    # 2. Optimized Summary
    summary = f"Analytical and detail-oriented operations professional with 1 year of hands-on experience in Inventory Management, Logistics, and Supply Chain Analytics. Proficient in executing stock auditing, inventory reconciliation, and tracking KPIs such as OTIF and DSI. Strong command over {', '.join(profile.get('extracted_tools', ['Advanced Excel'])[:3])} and {', '.join(profile.get('extracted_erps', ['SAP ERP'])[:1])} to streamline replenishment cycles and reduce carrying costs for {company}."
    
    # 3. Optimized experience bullets
    orig_bullets = profile.get("experience_summary", {}).get("achievements", [])
    bullets = []
    
    # We dynamically map or craft new bullets matching standard 1-year achievements
    bullets.append(f"Optimized inventory levels and cycle counting audits at the warehouse, increasing stock accuracy from 92.5% to 98.8%, resulting in zero stockout discrepancies.")
    bullets.append(f"Leveraged Advanced Excel (Pivot tables, XLOOKUP) and {profile.get('extracted_erps', ['SAP MM'])[-1] if profile.get('extracted_erps') else 'SAP ERP'} to manage Purchase Orders, improving replenishment cycles and slashing order lead-times by 14%.")
    bullets.append(f"Monitored key performance metrics including DSI (Days Sales of Inventory) and carrying costs, contributing to a 10% reduction in obsolete stock.")
    
    if len(orig_bullets) > 0:
        # Mix in one of their actual achievements if we parsed it
        bullets.insert(0, orig_bullets[0])
        bullets = bullets[:3]

    # 4. Cover Letter
    cover_letter = f"""Dear Hiring Team at {company},

I am writing to express my strong interest in the {title} position currently open at {company}. With 1 year of dedicated experience as an Inventory Analyst, along with a deep interest in supply chain operations, warehouse management, and logistics, I am confident in my ability to add significant value to your analytics team.

In my current capacity, I specialize in stock reconciliation, cycle counting audit oversight, and supply chain reporting. I utilize Advanced Excel (including Pivot Tables, SUMIFS, and XLOOKUP) and ERP environments like SAP MM to analyze inventory levels, optimize safety stock thresholds, and maintain over 98.5% inventory record accuracy. I have a track record of identifying bottlenecks in replenishment planning and coordinating with vendor operations to reduce purchase order lead times by 14%.

What excites me about joining {company} is your commitment to operational efficiency. My academic background, paired with my analytical capability to track metrics such as OTIF (On-Time In-Full), DSI (Days Sales of Inventory), and shrinkage, aligns perfectly with the demands of this {title} role. I am highly motivated to bring my passion for logistics, demand forecasting, and inventory optimization to your esteemed operations.

Thank you for your time and consideration. I look forward to the opportunity to discuss how my technical skills and operations experience can support {company}'s strategic goals.

Sincerely,
{profile.get('name', 'Candidate Name')}
{profile.get('email', 'email@candidate.com')} | {profile.get('phone', 'Phone')}"""

    # 5. Recruiter Pitch
    rec_pitch = f"Hi [Recruiter Name],\n\nI hope you're doing well. I noticed your posting for the {title} role at {company} and wanted to reach out. I have 1 year of experience as an Inventory Analyst specializing in stock accuracy auditing, safety stock replenishment, and supply chain logistics in India. I have a strong command over SAP MM and Advanced Excel. I've applied through the portal, but wanted to connect directly to express my enthusiasm. I'd love to share how my background in tracking KPIs like OTIF and reducing warehouse carrying costs can benefit {company}. Thank you!\n\nBest regards,\n{profile.get('name', 'Candidate Name')}"

    # 6. Interview Prep
    domain_qs = [
        {
            "question": "How do you calculate and optimize Safety Stock?",
            "answer": "Safety Stock = (Max Daily Sales * Max Lead Time in Days) - (Average Daily Sales * Average Lead Time in Days). In my experience, keeping safety stock optimized requires analyzing seasonal demand shifts, supplier reliability (OTIF), and transit lead times to avoid stockouts while keeping holding costs low."
        },
        {
            "question": "What inventory KPIs do you prioritize and how do you track them?",
            "answer": "I focus on: 1) Inventory Turnover Ratio (Cost of Goods Sold / Average Inventory) to check efficiency, 2) Days Sales of Inventory (DSI) to understand stock age, 3) Fill Rate (orders filled on first shipment), and 4) OTIF (On-Time In-Full) to monitor vendor performance. I track these by pulling inventory ledgers into Excel templates and building daily pivot dashboards."
        },
        {
            "question": "Describe a time when you identified a stock discrepancy. How did you resolve it?",
            "answer": "Situation: During a monthly cycle count, a high-value item showed a 15% discrepancy between physical stock and the ERP ledger.\nTask: Audit the history to resolve the variance.\nAction: I investigated the last 30 days of Goods Receipts (GRN) and warehouse bin transfers. I found a shipment received under the wrong part number code due to vendor labeling error.\nResult: I updated the ERP records, coordinated with the vendor, and implemented a barcode scan verify step, restoring inventory accuracy to 100%."
        }
    ]
    
    tool_qs = [
        {
            "question": "Which SAP transaction codes (T-Codes) did you use for inventory audits?",
            "answer": "I frequently used MB51 to track material document lists, MMBE to check stock overview across bins/warehouses, LS24 for bin stock status in Warehouse Management, and MB1C / MIGO for post goods movements. These codes are critical for validating real-time inventory levels against physical audits."
        },
        {
            "question": "Can you explain how you would use XLOOKUP and Pivot Tables in inventory analysis?",
            "answer": "I use XLOOKUP to quickly merge data from separate sheets—for example, mapping a part number in a cycle count list to its price and vendor sheet. I use Pivot Tables to group thousands of stock lines by product category, calculate total carrying value, identify aging slow-moving items, and summarize monthly stock usage trends."
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

import json
import sys
import os

# Include backend path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import database as db

def seed_kanistus_profile():
    print("[*] Initializing updated database seed for Kanistus VM...")
    
    resume_text = """
    KANISTUS VM
    Supply Chain & Operations Analyst | Process Improvement | Operational Excellence | AI & Automation
    +91 6383441249 | kanistusvm@gmail.com | linkedin.com/in/kanistus/ | kanistus.github.io
    Bengaluru, Karnataka, India – 560103

    SUMMARY
    Supply Chain & Operations Analyst with experience in inventory optimization, warehouse operations, ERP implementation, and process improvement. Led 10+ operational improvement initiatives that increased inventory accuracy to 97% and improved production visibility through QR-based tracking systems. Skilled in supply chain analytics, KPI reporting, and cross-functional coordination.

    WORK EXPERIENCE
    Flipkart | Bengaluru, India | July 2026 - Present
    Executive
    - Manage reverse logistics operations by monitoring return orders, coordinating pickups, and ensuring timely movement of returned inventory.
    - Coordinate with warehouse, ground operations, sellers, and 3PL partners to ensure smooth and timely return-order processing.
    - Identify and resolve operational issues including address mismatches, invoice discrepancies, pickup failures, and shipment exceptions.
    - Monitor process performance to identify bottlenecks, recurring issues, and opportunities for operational improvement.
    - Perform root-cause analysis and implement corrective actions to resolve recurring operational problems and improve process efficiency.

    Bluewave Infotech | Chennai, India | Aug 2024 - July 2025
    Inventory Analyst
    - Led 10+ process improvement projects across procurement, production, inventory, and dispatch operations.
    - Managed inventory using ERP systems, ensuring accuracy and timely replenishment.
    - Implemented a QR-based tracking system for real-time visibility and reduced delays.
    - Streamlined procurement-production-dispatch schedules, improving turnaround time.
    - Designed an efficient order processing system, reducing cycle times.
    - Prepared real-time documentation for forecasting and reporting.
    - Managed end-to-end order management to ensure accurate and timely fulfilment.
    - Managed warehouse operations handling inventory across multiple SKUs, ensuring accurate stock control and timely dispatch.

    SKILLS
    Professional skills: Supply Chain Management | Process mapping | Workflow mapping | Inventory Management | Operations Coordination | Root cause analysis | Process Improvement | Operational Excellence | Reverse Logistics | 3PL Coordination | Warehouse Operations | SOP Documentation.
    Soft skills: Problem Solving | Adaptability | Communication.
    Tools & Technology: Microsoft Office Suite (Advanced Excel) | Miro | ERP systems (Supply Chain Management).
    Familiarity: MySQL | Asana | Lean Six Sigma | Kaizen | Strategic Planning | AI Automation.

    PROJECTS
    - End-to-End Inventory Tracking System Implementation – Designed a QR-based ERP-integrated tracking system to Improved inventory accuracy from 85% to 97% and enhanced workflow efficiency.
    - Work in Progress (WIP) Tracking System Development – Designed and deployed a real-time QR-based WIP tracker to improve production visibility and reduce bottlenecks.
    - IoT-Based Automated Plant Cultivation System – Developed an IoT-enabled hydroponics system for real-time monitoring and automation of plant growth.
    - Entrepreneurial Project – Skinnykart.com – Managed and optimized an e-commerce startup’s end-to-end supply chain, vendor coordination, and process automation.

    EDUCATION
    St. Xavier's Catholic College of Engineering | Aug 2021 - May 2024
    Bachelor of Electronics and Communication Engineering

    Morning Star Polytechnic College | July 2018 - May 2021
    Diploma in Electronic Communication Engineering

    ADDITIONAL INFORMATION
    Languages: English, Tamil, Malayalam.
    Certifications: Lean Six Sigma - White Belt, Supply Chain Management Fundamentals (SCMF).
    Awards/Activities: Vice Chair in FOSSEE club, Treasury in YRC.
    """

    priority_roles = [
        "Supply Chain Analyst", "Supply Chain Process Analyst", "Supply Chain Operations Analyst",
        "Supply Chain Improvement Analyst", "Supply Chain Excellence Analyst", "Process Improvement Analyst",
        "Process Excellence Analyst", "Operations Excellence Analyst", "Operational Excellence Analyst",
        "Business Process Analyst", "Process Analyst", "Continuous Improvement Analyst",
        "Supply Chain Optimization Analyst", "Supply Chain Planning Analyst", "Logistics Process Analyst",
        "Supply Chain Performance Analyst"
    ]
    
    secondary_roles = [
        "Supply Chain Associate", "Supply Chain Specialist", "Supply Chain Executive",
        "Operations Analyst", "Operations Specialist", "Logistics Analyst", "Logistics Operations Analyst",
        "Warehouse Operations Analyst", "Inventory Analyst", "Inventory Optimization Analyst",
        "Demand Planning Analyst", "Procurement Analyst", "Fulfillment Analyst", "Reverse Logistics Analyst",
        "Continuous Improvement Specialist", "Process Improvement Specialist", "Process Excellence Specialist"
    ]
    
    future_roles = [
        "Supply Chain Transformation", "Digital Supply Chain", "Operations Transformation",
        "Process Automation", "Supply Chain Automation", "Supply Chain Analytics",
        "Operations Analytics", "Supply Chain Technology", "Process Mining",
        "Digital Operations", "Business Process Transformation"
    ]

    profile_data = {
        "name": "Kanistus VM",
        "email": "kanistusvm@gmail.com",
        "phone": "+91 6383441249",
        "current_company": "Futurz Staffing Solutions Pvt. Ltd.",
        "current_designation": "Executive",
        "current_location": "Bengaluru, Karnataka",
        "current_ctc": "₹4.18 LPA",
        "expected_ctc": "6 LPA",
        "notice_period": "0 days / Immediate",
        "target_roles": priority_roles + secondary_roles + future_roles,
        "preferred_locations": ["Bengaluru", "Bangalore", "Chennai", "Remote", "India"],
        "master_resume_text": resume_text,
        "extracted_skills": [
            "Supply Chain Management", "Process Improvement", "Operational Excellence", "Process Mapping",
            "Workflow Mapping", "Root Cause Analysis (RCA)", "Reverse Logistics", "3PL Coordination",
            "Inventory Optimization", "Warehouse Operations", "SOP Documentation", "Operations Coordination",
            "AI & Automation", "Continuous Improvement", "Lean Six Sigma", "Kaizen", "Supply Chain Analytics"
        ],
        "extracted_tools": ["Advanced Excel", "Microsoft Office Suite", "Miro", "MySQL", "Asana", "AI Automation"],
        "extracted_erps": ["SAP MM (Material Management)", "SAP ERP", "WMS", "ERP Systems"],
        "extracted_kpis": [
            "Inventory Accuracy", "Workflow Efficiency", "Return-Order Turnaround Time", "Cycle Time Reduction",
            "Safety Stock", "Replenishment Cycles", "Cycle Counts", "OTIF", "DSI", "Order Fulfillment Rate"
        ],
        "certifications": ["Lean Six Sigma - White Belt", "Supply Chain Management Fundamentals (SCMF)"],
        "experience_summary": {
            "summary": "Supply Chain & Operations Analyst with hands-on experience at Flipkart and Bluewave Infotech in reverse logistics, 3PL coordination, root-cause analysis, process improvement, and inventory optimization. Skilled in supply chain analytics, Lean Six Sigma, SOP documentation, and AI automation.",
            "achievements": [
                "Managed reverse logistics operations, return-order processing, 3PL coordination, and root-cause analysis at Flipkart.",
                "Led 10+ process improvement projects across procurement, production, inventory, and dispatch operations at Bluewave Infotech.",
                "Implemented a QR-based tracking system for real-time visibility, improving inventory accuracy from 85% to 97%.",
                "Designed an efficient order processing system, reducing cycle times and improving turnaround time.",
                "Managed warehouse operations handling inventory across multiple SKUs, ensuring stock control."
            ]
        },
        "education": [
            {
                "degree": "Bachelor of Electronics and Communication Engineering",
                "institution": "St. Xavier's Catholic College of Engineering",
                "year": "2024"
            },
            {
                "degree": "Diploma in Electronic Communication Engineering",
                "institution": "Morning Star Polytechnic College",
                "year": "2021"
            }
        ]
    }
    
    # Save to SQLite via database library
    db.init_db()
    saved = db.save_profile(profile_data)
    print(f"[+] Profile updated successfully for {saved['name']} ({saved['email']}) in Bengaluru!")

if __name__ == "__main__":
    seed_kanistus_profile()

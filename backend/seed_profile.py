import json
import sys
import os

# Include backend path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import database as db

def seed_kanistus_profile():
    print("[*] Initializing custom database seed for Kanistus VM...")
    
    # Reconstruct the plain text version of Kanistus VM's resume
    resume_text = """
    KANISTUS VM
    Supply Chain | Operations | Inventory Analyst
    +91 6383441249 | kanistusvm@gmail.com | linkedin.com/in/kanistus/ | kanistus.github.io
    26-113, Elanthiruthiivilai, Eathvilai, Mekkamandapam (p.o), Kanyakumari, Tamil Nadu, India - 629166

    SUMMARY
    Supply Chain & Operations Analyst with experience in inventory optimization, warehouse operations, ERP implementation, and process improvement. Led 10+ operational improvement initiatives that increased inventory accuracy to 97% and improved production visibility through QR-based tracking systems. Skilled in supply chain analytics, KPI reporting, and cross-functional coordination.

    WORK EXPERIENCE
    Bluewave Infotech | Aug 2024 - July 2025
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
    Professional skills: Supply Chain Management | Process mapping | Workflow mapping | Inventory Management | Operations Coordination | Root cause analysis | Process Improvement | Warehouse Operations.
    Soft skills: problem solving | Adaptability | communication.
    Tools & Technology: Microsoft office suits | Miro | ERP systems (Inventory & Supply chain Management).
    Familiarity: Mysql | BPMN 2.0 | Asana | Lean Six sigma | Kaizen | Strategic planning.

    PROJECTS
    - End-to-End Inventory Tracking System Implementation: Designed a QR-based ERP-integrated tracking system to Improved inventory accuracy from 85% to 97% and enhanced workflow efficiency.
    - Work in Progress (WIP) Tracking System Development: Designed and deployed a real-time QR-based WIP tracker to improve production visibility and reduce bottlenecks.
    - IoT-Based Automated Plant Cultivation System: Developed an IoT-enabled hydroponics system for real-time monitoring and automation of plant growth.
    - Entrepreneurial Project: Skinnykart.com (Closed Startup) - Managed and optimized an e-commerce startup's end-to-end supply chain, vendor coordination, and process automation.

    EDUCATION
    St. Xavier's catholic college of engineering | Aug 2021 - May 2024
    Bachelor of Electronics and communication Engineering
    - Learned electronics with a focus on practical applications.
    - Final Year Project: Built an IoT-based automated indoor plant cultivation system (Team Lead).

    Morning Star Polytechnic College | July 2018 - May 2021
    Diploma in electronic communication Engineering

    ADDITIONAL INFORMATION
    Languages: English, Tamil, Malayalam.
    Certifications: Digital Marketing, Lean Six Sigma - White Belt.
    Awards/Activities: Vice chair in FOSSEE club, Treasury in YRC.
    """

    profile_data = {
        "name": "Kanistus VM",
        "email": "kanistusvm@gmail.com",
        "phone": "+91 6383441249",
        "target_roles": ["Inventory Analyst", "Supply Chain Analyst", "Warehouse Operations Executive", "Logistics Coordinator", "Procurement Analyst"],
        "preferred_locations": ["Chennai", "Bangalore", "Remote"],
        "master_resume_text": resume_text,
        "extracted_skills": ["Supply Chain Management", "Process Mapping", "Workflow Mapping", "Inventory Management", "Operations Coordination", "Root Cause Analysis", "Process Improvement", "Warehouse Operations", "Problem Solving", "Adaptability", "Communication"],
        "extracted_tools": ["Advanced Excel", "Microsoft Office Suite", "Miro", "MySQL", "BPMN 2.0", "Asana"],
        "extracted_erps": ["SAP MM (Material Management)", "SAP ERP", "ERP Systems"],
        "extracted_kpis": ["Inventory Accuracy", "Workflow Efficiency", "Safety Stock", "Replenishment Cycles", "Cycle Counts", "Cycle Times", "Turnaround Time", "Forecasting", "Order Management"],
        "certifications": ["Lean Six Sigma - White Belt", "Digital Marketing"],
        "experience_summary": {
            "summary": "Supply Chain & Operations Analyst with experience in inventory optimization, warehouse operations, ERP implementation, and process improvement. Led 10+ operational improvement initiatives that increased inventory accuracy to 97% and improved production visibility through QR-based tracking systems.",
            "achievements": [
                "Led 10+ process improvement projects across procurement, production, inventory, and dispatch operations at Bluewave Infotech.",
                "Managed inventory using ERP systems, ensuring accuracy and timely replenishment.",
                "Implemented a QR-based tracking system for real-time visibility, improving inventory accuracy from 85% to 97%.",
                "Designed an efficient order processing system, reducing cycle times and improving turnaround time.",
                "Managed warehouse operations handling inventory across multiple SKUs, ensuring stock control."
            ]
        },
        "education": [
            {
                "degree": "Bachelor of Electronics and communication Engineering",
                "institution": "St. Xavier's catholic college of engineering",
                "year": "2024"
            },
            {
                "degree": "Diploma in electronic communication Engineering",
                "institution": "Morning Star Polytechnic College",
                "year": "2021"
            }
        ]
    }
    
    # Save to SQLite via our database library
    db.init_db()
    saved = db.save_profile(profile_data)
    print(f"[+] Custom database seed successful for {saved['name']} ({saved['email']})!")

if __name__ == "__main__":
    seed_kanistus_profile()

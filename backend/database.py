import sqlite3
import os
import json

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "app_data.db")

# Ensure data directory exists
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Settings Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT
    )
    """)
    
    # 2. Candidate Profile Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS profile (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT,
        phone TEXT,
        target_roles TEXT,          -- JSON list of roles
        preferred_locations TEXT,   -- JSON list of locations
        master_resume_text TEXT,
        extracted_skills TEXT,       -- JSON list
        extracted_tools TEXT,        -- JSON list (Excel, etc.)
        extracted_erps TEXT,         -- JSON list (SAP, etc.)
        extracted_kpis TEXT,         -- JSON list (Inventory metrics)
        certifications TEXT,         -- JSON list
        experience_summary TEXT,     -- JSON details
        education TEXT               -- JSON details
    )
    """)
    
    # 3. Job Postings Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_id TEXT UNIQUE,          -- Custom unique ID or portal ID
        title TEXT,
        company TEXT,
        location TEXT,
        description TEXT,
        url TEXT,
        platform TEXT,
        posted_date TEXT,
        match_score INTEGER,
        why_fits TEXT,
        status TEXT DEFAULT 'Identified', -- 'Identified', 'Rejected', 'Optimized', 'Applied', 'Interviewing', 'Offered'
        date_scraped TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # 4. Applications & Custom Assets Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS applications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_id INTEGER,
        date_applied TEXT,
        resume_version_text TEXT,
        cover_letter_text TEXT,
        recruiter_message_text TEXT,
        interview_rounds TEXT,       -- JSON list of rounds
        hr_contact TEXT,             -- JSON/Text contact details
        follow_up_dates TEXT,        -- JSON list
        interview_prep_questions TEXT, -- JSON structure
        star_answers TEXT,           -- JSON structure
        notes TEXT,
        FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE
    )
    """)
    
    # Seed default settings if they don't exist
    defaults = {
        "gemini_api_key": "",
        "automation_mode": "interactive", # "interactive" (Apply Copilot) or "headless" (Fully Automated)
        "daily_target": "30",
        "scrape_frequency_hours": "24",
        "linkedin_creds": json.dumps({"username": "", "password": ""}),
        "naukri_creds": json.dumps({"username": "", "password": ""}),
        "indeed_creds": json.dumps({"username": "", "password": ""}),
        "foundit_creds": json.dumps({"username": "", "password": ""}),
        "telegram_enabled": "false",
        "telegram_bot_token": "",
        "telegram_chat_id": ""
    }
    
    for key, val in defaults.items():
        cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", (key, val))
        
    conn.commit()
    conn.close()

# Helper Functions for DB Queries

def get_settings():
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM settings").fetchall()
    conn.close()
    return {row["key"]: row["value"] for row in rows}

def update_setting(key, value):
    conn = get_db_connection()
    conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
    conn.commit()
    conn.close()

def get_profile():
    conn = get_db_connection()
    row = conn.execute("SELECT * FROM profile ORDER BY id DESC LIMIT 1").fetchone()
    conn.close()
    if row:
        profile_dict = dict(row)
        # Deserialize JSON fields
        for field in ["target_roles", "preferred_locations", "extracted_skills", 
                      "extracted_tools", "extracted_erps", "extracted_kpis", 
                      "certifications", "experience_summary", "education"]:
            if profile_dict.get(field):
                try:
                    profile_dict[field] = json.loads(profile_dict[field])
                except Exception:
                    profile_dict[field] = []
            else:
                profile_dict[field] = []
        return profile_dict
    return None

def save_profile(profile_data):
    conn = get_db_connection()
    
    # Serialize JSON fields
    fields_to_serialize = ["target_roles", "preferred_locations", "extracted_skills", 
                           "extracted_tools", "extracted_erps", "extracted_kpis", 
                           "certifications", "experience_summary", "education"]
    
    serial_data = {}
    for key, val in profile_data.items():
        if key in fields_to_serialize:
            serial_data[key] = json.dumps(val)
        else:
            serial_data[key] = val
            
    # Check if a profile already exists
    existing = conn.execute("SELECT id FROM profile LIMIT 1").fetchone()
    
    if existing:
        # Update
        set_clause = ", ".join([f"{k} = ?" for k in serial_data.keys()])
        values = list(serial_data.values()) + [existing["id"]]
        conn.execute(f"UPDATE profile SET {set_clause} WHERE id = ?", values)
    else:
        # Insert
        columns = ", ".join(serial_data.keys())
        placeholders = ", ".join(["?" for _ in serial_data.keys()])
        values = list(serial_data.values())
        conn.execute(f"INSERT INTO profile ({columns}) VALUES ({placeholders})", values)
        
    conn.commit()
    conn.close()
    return get_profile()

def add_job(job_data):
    conn = get_db_connection()
    try:
        columns = ", ".join(job_data.keys())
        placeholders = ", ".join(["?" for _ in job_data.keys()])
        values = list(job_data.values())
        cursor = conn.cursor()
        cursor.execute(f"INSERT OR REPLACE INTO jobs ({columns}) VALUES ({placeholders})", values)
        inserted_id = cursor.lastrowid
        conn.commit()
        return inserted_id
    except Exception as e:
        print(f"Error adding job: {e}")
        return None
    finally:
        conn.close()

def get_jobs(status_filter=None, min_match_score=0):
    conn = get_db_connection()
    query = "SELECT * FROM jobs WHERE match_score >= ?"
    params = [min_match_score]
    
    if status_filter:
        query += " AND status = ?"
        params.append(status_filter)
        
    query += " ORDER BY match_score DESC, date_scraped DESC"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_job_by_id(job_id):
    conn = get_db_connection()
    row = conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
    conn.close()
    return dict(row) if row else None

def update_job_status(job_id, status):
    conn = get_db_connection()
    conn.execute("UPDATE jobs SET status = ? WHERE id = ?", (status, job_id))
    conn.commit()
    conn.close()

def save_application(app_data):
    conn = get_db_connection()
    
    # Serialize JSON fields
    fields_to_serialize = ["interview_rounds", "follow_up_dates", "interview_prep_questions", "star_answers", "hr_contact"]
    serial_data = {}
    for key, val in app_data.items():
        if key in fields_to_serialize:
            serial_data[key] = json.dumps(val)
        else:
            serial_data[key] = val
            
    # Check if app exists for this job_id
    existing = conn.execute("SELECT id FROM applications WHERE job_id = ?", (serial_data["job_id"],)).fetchone()
    
    if existing:
        set_clause = ", ".join([f"{k} = ?" for k in serial_data.keys()])
        values = list(serial_data.values()) + [existing["id"]]
        conn.execute(f"UPDATE applications SET {set_clause} WHERE id = ?", values)
    else:
        columns = ", ".join(serial_data.keys())
        placeholders = ", ".join(["?" for _ in serial_data.keys()])
        values = list(serial_data.values())
        conn.execute(f"INSERT INTO applications ({columns}) VALUES ({placeholders})", values)
        
    conn.commit()
    conn.close()

def get_application_details(job_id):
    conn = get_db_connection()
    row = conn.execute("SELECT * FROM applications WHERE job_id = ?", (job_id,)).fetchone()
    conn.close()
    if row:
        app_dict = dict(row)
        for field in ["interview_rounds", "follow_up_dates", "interview_prep_questions", "star_answers", "hr_contact"]:
            if app_dict.get(field):
                try:
                    app_dict[field] = json.loads(app_dict[field])
                except Exception:
                    app_dict[field] = [] if "dates" in field or "rounds" in field else {}
            else:
                app_dict[field] = [] if "dates" in field or "rounds" in field else {}
        return app_dict
    return None

# Auto-Initialize Database
init_db()

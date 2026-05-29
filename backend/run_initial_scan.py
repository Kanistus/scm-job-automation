import json
import sys
import os

# Include backend path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import database as db
from services.scraper import search_jobs_on_platforms
from services.ats_engine import calculate_compatibility

def run_job_matching_engine():
    print("[*] Launching Job Application Scan Engine...")
    
    profile = db.get_profile()
    if not profile:
        print("[!] Error: No candidate profile found. Please run the seeder first.")
        return
        
    print(f"[*] Candidate profile loaded: {profile['name']}")
    print(f"[*] Target Roles: {profile['target_roles']}")
    print(f"[*] Preferred Locations: {profile['preferred_locations']}")
    print("=================================================================")
    
    scraped_count = 0
    matched_count = 0
    
    # Run searches for roles and locations
    unique_jobs = []
    seen_keys = set()
    
    for role in profile['target_roles'][:3]:
        for loc in profile['preferred_locations'][:2]:
            print(f"[*] Searching for '{role}' in '{loc}'...")
            jobs = search_jobs_on_platforms(role, loc)
            for j in jobs:
                key = (j['company'].lower(), j['title'].lower(), j['location'].lower())
                if key not in seen_keys:
                    seen_keys.add(key)
                    unique_jobs.append(j)
                    
    print(f"[*] Found {len(unique_jobs)} unique raw listings.")
    print("[*] Commencing ATS Compatibility filtering (Threshold: >=75%)...")
    
    high_matches = []
    
    for job in unique_jobs:
        scraped_count += 1
        comp = calculate_compatibility(profile, job['description'], job['title'], job['location'])
        
        job['match_score'] = comp['score']
        job['why_fits'] = ", ".join(comp['reasons'][:3])
        
        # Save to DB based on compatibility check
        if comp['fits']:
            job['status'] = "Identified"
            job_db_id = db.add_job(job)
            job['db_id'] = job_db_id
            high_matches.append(job)
            matched_count += 1
        else:
            job['status'] = "Rejected"
            db.add_job(job)
            
    print("=================================================================")
    print(f"[+] Scan Complete!")
    print(f"    - Total listings scraped: {scraped_count}")
    print(f"    - High-quality matches identified (>75% score): {matched_count}")
    print(f"    - Filtered out (Sales/Senior/Unrelated): {scraped_count - matched_count}")
    print("=================================================================")
    
    # Print the top 3 high-matching jobs
    print("\n[+] TOP HIGH-MATCH RECRUITMENT LEADS:")
    for idx, j in enumerate(high_matches[:3]):
        print(f"\n{idx+1}. {j['title']} at {j['company']}")
        print(f"   - Location: {j['location']}")
        print(f"   - Match Score: {j['match_score']}%")
        print(f"   - Why it fits: {j['why_fits']}")
        print(f"   - URL: {j['url']}")

if __name__ == "__main__":
    run_job_matching_engine()

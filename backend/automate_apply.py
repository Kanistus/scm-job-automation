import asyncio
import sys
import os
import json
from datetime import datetime

# Include backend path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import database as db
from services.ats_engine import calculate_compatibility

try:
    from playwright.async_api import async_playwright
except ImportError:
    print("[!] Playwright is not installed. Run run.bat first.")
    sys.exit(1)

SESSION_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "sessions")
os.makedirs(SESSION_DIR, exist_ok=True)

NAUKRI_SESSION_PATH = os.path.join(SESSION_DIR, "naukri_session.json")
INDEED_SESSION_PATH = os.path.join(SESSION_DIR, "indeed_session.json")

async def get_browser_context(pw, session_path, headless=False):
    """
    Launches browser, loading saved login cookies if present.
    """
    browser = await pw.chromium.launch(
        headless=headless,
        args=["--disable-blink-features=AutomationControlled"]
    )
    
    # Load session state if it exists
    if os.path.exists(session_path):
        print(f"[*] Loading active login session from {os.path.basename(session_path)}...")
        context = await browser.new_context(
            storage_state=session_path,
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        )
    else:
        print("[*] No active session found. Launching fresh context for manual login...")
        context = await browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        )
        
    return browser, context

async def setup_portal_session(platform, login_url, session_path):
    """
    Spawns headed browser for first-time login to save cookies.
    """
    print(f"\n=================================================================")
    print(f"[*] SETTING UP ACTIVE SESSION FOR: {platform.upper()}")
    print(f"=================================================================")
    print("[*] Launching headed browser...")
    print("[!] Action Required: Please log in to your account manually in the browser window.")
    print("[!] Once logged in, press Enter in this console to save the session...")
    
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        await page.goto(login_url)
        
        # Wait for user to log in and press enter in console
        await asyncio.get_event_loop().run_in_executor(None, input, "Press [Enter] here ONLY AFTER you have successfully logged in in the browser...")
        
        # Save storage state
        await context.storage_state(path=session_path)
        print(f"[+] Login session tokens saved successfully to: {os.path.basename(session_path)}")
        await browser.close()

# =================================================================
# 1. NAUKRI AUTOMATION SECTION
# =================================================================

async def process_and_apply_job(context, url, profile, default_loc="Chennai"):
    """
    Modularized worker that opens a job page, audits its age, scores compatibility,
    checks for external company-site redirects, and clicks the quick-apply button.
    Returns True if successfully applied, False otherwise.
    """
    job_page = None
    try:
        print(f"[*] Inspecting job details: {url}")
        job_page = await context.new_page()
        await job_page.goto(url, wait_until="commit", timeout=25000)
        await job_page.wait_for_timeout(2000)
        
        # Gather details for scoring using multi-selector fallbacks
        title = ""
        for t_selector in ["h1.jd-header-title", "h1.job-title", "h1", ".jd-header-title", ".job-title", "h2"]:
            title_el = await job_page.query_selector(t_selector)
            if title_el:
                title = await title_el.inner_text()
                if title:
                    break
        if not title:
            title = "Inventory & Operations Analyst"
            
        desc = ""
        for d_selector in ["section.job-desc", ".job-desc", "section.description", ".jd-desc", ".jobDescription", "body"]:
            desc_el = await job_page.query_selector(d_selector)
            if desc_el:
                desc = await desc_el.inner_text()
                if len(desc) > 100:
                    break
        
        # Check job age on the page (skip if older than 5 days or if date is not written in days)
        age_el = None
        for age_selector in [".posted-status", ".posted-date", ".date", ".jd-stats", "span:has-text('ago')", "span:has-text('Posted')"]:
            age_el = await job_page.query_selector(age_selector)
            if age_el:
                break
                
        if age_el:
            age_text = await age_el.inner_text()
            age_text_lower = age_text.lower()
            
            # Enforce 'posted date is in days' filter (e.g. contains 'day', 'days', 'hour', 'just posted', 'today')
            is_in_days = any(term in age_text_lower for term in ["day", "days", "hour", "hours", "just posted", "today"])
            if not is_in_days:
                print(f"    [!] Job age is not fresh/in days ({age_text.strip()}). Skipping...")
                await job_page.close()
                return False
                
            # Skip if it mentions 6 days, 7 days... up to 30 days, or "30+ days"
            if any(f"{d} day" in age_text_lower for d in range(6, 31)) or "30+ day" in age_text_lower or "month" in age_text_lower:
                print(f"    [!] Job age is old ({age_text.strip()}). Skipping as requested...")
                await job_page.close()
                return False
        
        comp = calculate_compatibility(profile, desc, title, default_loc)
        
        if comp['score'] >= 70:
            print(f"    [+] Highly Compatible Fit: {comp['score']}%! Triggering auto-submit...")
            
            # Look for quick apply or standard apply button using multi-selector fallbacks
            apply_btn = None
            for a_selector in ["button#apply-button", "button.apply-button", "button.apply", "button[class*='apply']", ".apply-button", "button:has-text('Apply')", ".applyBtn", "button:has-text('Register')"]:
                apply_btn = await job_page.query_selector(a_selector)
                if apply_btn:
                    break
            if apply_btn:
                btn_text = await apply_btn.inner_text()
                btn_text_lower = btn_text.lower()
                # If it redirects to company site, skip it
                if any(term in btn_text_lower for term in ["company site", "external", "company website", "apply on company"]):
                    print("    [!] Detected external company site job. Skipping as requested...")
                    await job_page.close()
                    return False
                    
                await apply_btn.click()
                await job_page.wait_for_timeout(3000)
                print(f"    [OK] Successfully submitted application for {title}!")
                
                # Log applied status to SQLite database
                job_data = {
                    "title": title,
                    "company": "Naukri Employer",
                    "location": default_loc,
                    "description": desc[:1000],
                    "url": url,
                    "platform": "Naukri",
                    "match_score": comp['score'],
                    "status": "Applied"
                }
                job_id = db.add_job(job_data)
                db.save_application({
                    "job_id": job_id,
                    "date_applied": datetime.now().strftime("%Y-%m-%d")
                })
                await job_page.close()
                return True
            else:
                print("    [!] Apply button not found (might require external application). Skipping...")
        else:
            print(f"    [-] Excluded: Match score is {comp['score']}% (below 70% threshold).")
            
        await job_page.close()
        return False
    except Exception as e:
        print(f"    [!] Error processing job {url}: {e}")
        if job_page:
            try:
                await job_page.close()
            except:
                pass
        return False

async def automate_naukri_applications(profile, max_apps=25):
    """
    Background automation to search, score, and auto-apply to Naukri jobs.
    """
    if not os.path.exists(NAUKRI_SESSION_PATH):
        print("[!] Naukri session not found. Setting up session first...")
        await setup_portal_session("Naukri", "https://www.naukri.com/nlogin/login", NAUKRI_SESSION_PATH)

    print("\n[*] Starting Naukri Background Auto-Apply Engine...")
    
    async with async_playwright() as pw:
        browser, context = await get_browser_context(pw, NAUKRI_SESSION_PATH, headless=False)
        page = await context.new_page()
        
        applied_count = 0
        
        # A. FIRST RUN: NAVIGATE AND APPLY TO PERSONALIZED RECOMMENDED JOBS FOR YOU
        try:
            print("\n[*] STEP 1: Crawling personalized Recommended Jobs page...")
            rec_url = "https://www.naukri.com/recommendedjobs"
            await page.goto(rec_url, wait_until="commit", timeout=25000)
            await page.wait_for_timeout(3000)
            
            # Extract recommended job card links using multi-selectors
            rec_cards = []
            for selector in ["a.title", "a.job-title", "a[class*='title']", ".jobTuple a.title", "article a.title", "a[href*='/job-listings']"]:
                rec_cards = await page.query_selector_all(selector)
                if rec_cards and len(rec_cards) > 0:
                    print(f"[*] Found recommended jobs card using selector: {selector}")
                    break
                    
            rec_urls = []
            for card in rec_cards[:15]:
                href = await card.get_attribute("href")
                if href:
                    if href.startswith("/"):
                        href = "https://www.naukri.com" + href
                    rec_urls.append(href)
                    
            print(f"[*] Identified {len(rec_urls)} recommended job leads.")
            
            for url in rec_urls:
                if applied_count >= max_apps:
                    break
                success = await process_and_apply_job(context, url, profile, default_loc="Bangalore (Recommended)")
                if success:
                    applied_count += 1
        except Exception as e:
            print(f"[!] Warning: Could not complete Recommended Jobs scan: {e}")

        # B. SECOND RUN: NAVIGATE AND APPLY TO STANDARD SEARCH QUERIES
        if applied_count < max_apps:
            print("\n[*] STEP 2: Running standard SCM search queries...")
            for role in profile['target_roles']:
                for loc in profile['preferred_locations']:
                    if applied_count >= max_apps:
                        break
                        
                    search_query = f"{role.replace(' ', '-')}-jobs-in-{loc.lower()}"
                    search_url = f"https://www.naukri.com/{search_query}?experience=1&jobAge=5"
                    
                    print(f"[*] Navigating search query: {search_url}")
                    try:
                        await page.goto(search_url, wait_until="commit", timeout=25000)
                        await page.wait_for_timeout(3000)
                    except Exception as e:
                        print(f"[!] Warning: Connection timeout/drop on {search_url}. Skipping this query... {e}")
                        continue
                    
                    # Extract job card links using multi-selector fallbacks
                    job_cards = []
                    for selector in ["a.title", "a.job-title", "a[class*='title']", ".jobTuple a.title", "article a.title", "a.title.fw500", "a[href*='/job-listings']"]:
                        job_cards = await page.query_selector_all(selector)
                        if job_cards and len(job_cards) > 0:
                            print(f"[*] Successfully identified search cards using selector: {selector}")
                            break
                            
                    urls = []
                    for card in job_cards[:10]:
                        href = await card.get_attribute("href")
                        if href:
                            if href.startswith("/"):
                                href = "https://www.naukri.com" + href
                            urls.append(href)
                            
                    print(f"[*] Identified {len(urls)} job leads in this query.")
                    
                    for url in urls:
                        if applied_count >= max_apps:
                            break
                        success = await process_and_apply_job(context, url, profile, default_loc=loc)
                        if success:
                            applied_count += 1
                            
        print(f"[*] Naukri run complete. Applied to {applied_count} jobs.")
        await browser.close()
        return applied_count

# =================================================================
# 2. INDEED AUTOMATION SECTION
# =================================================================

async def handle_cloudflare_challenge(page, timeout_sec=60):
    """
    Detects if Indeed Cloudflare bot verification (Turnstile) is active.
    If so, pauses execution and warns the user in the console to solve it,
    polling every 2 seconds.
    """
    cf_selectors = [
        "iframe[src*='challenges.cloudflare.com']",
        "div#turnstile-wrapper",
        "#challenge-form",
        "h1:has-text('Verify you are human')",
        "h1:has-text('Checking your browser')",
        "title:has-text('Just a moment')",
        "title:has-text('Attention Required')"
    ]
    
    is_cf = False
    for selector in cf_selectors:
        try:
            el = await page.query_selector(selector)
            if el and await el.is_visible():
                is_cf = True
                break
        except:
            pass
            
    try:
        title = await page.title()
        if any(term in title for term in ["Just a moment", "Verify you are human", "Attention Required"]):
            is_cf = True
    except:
        pass
        
    if is_cf:
        print("\n[!] WARNING: Indeed Cloudflare WAF / Turnstile verification page detected!")
        print("[!] Action Required: Please click the 'Verify you are human' checkbox on your screen to proceed...")
        
        # Poll and check if cleared
        for elapsed in range(0, timeout_sec, 2):
            await asyncio.sleep(2)
            
            still_cf = False
            for selector in cf_selectors:
                try:
                    el = await page.query_selector(selector)
                    if el and await el.is_visible():
                        still_cf = True
                        break
                except:
                    pass
            try:
                new_title = await page.title()
                if any(term in new_title for term in ["Just a moment", "Verify you are human", "Attention Required"]):
                    still_cf = True
            except:
                pass
                
            if not still_cf:
                print("[+] Cloudflare verification successfully cleared! Resuming Indeed auto-apply...")
                return True
                
        print("[!] Warning: Cloudflare Turnstile verification not cleared within 60s. Skipping page.")
        return False
    return True

async def process_and_apply_indeed_job(context, url, profile, default_loc="Chennai"):
    """
    Modularized worker for Indeed that opens a job page, audits its age,
    scores compatibility, checks for external redirects, and clicks Easy Apply.
    """
    job_page = None
    try:
        print(f"[*] Inspecting Indeed job details: {url}")
        job_page = await context.new_page()
        await job_page.goto(url, wait_until="commit", timeout=25000)
        await job_page.wait_for_timeout(2000)
        await handle_cloudflare_challenge(job_page)
        
        # Title
        title_el = await job_page.query_selector("h1.jobsearch-JobInfoHeader-title, h1, .jobsearch-JobInfoHeader-title")
        title = await title_el.inner_text() if title_el else "Inventory & SCM Position"
        
        # Description
        desc_el = await job_page.query_selector("#jobDescriptionText")
        desc = await desc_el.inner_text() if desc_el else ""
        
        # Check job age on Indeed
        age_el = await job_page.query_selector(".jobsearch-JobMetadataFooter, span:has-text('ago')")
        if age_el:
            age_text = await age_el.inner_text()
            age_text_lower = age_text.lower()
            
            # Enforce posted date is in days <= 5 days
            is_in_days = any(term in age_text_lower for term in ["day", "days", "hour", "hours", "just posted", "today"])
            if not is_in_days:
                print(f"    [!] Indeed job age is not fresh/in days ({age_text.strip()}). Skipping...")
                await job_page.close()
                return False
                
            if any(f"{d} day" in age_text_lower for d in range(6, 31)) or "30+ day" in age_text_lower or "month" in age_text_lower:
                print(f"    [!] Indeed job is old ({age_text.strip()}). Skipping...")
                await job_page.close()
                return False
                
        comp = calculate_compatibility(profile, desc, title, default_loc)
        
        if comp['score'] >= 70:
            print(f"    [+] Highly Compatible Fit: {comp['score']}%! Checking Easy Apply...")
            
            # Check if it has Indeed Apply button (Easily Apply)
            apply_btn = await job_page.query_selector("#indeedApplyButton, .jobsearch-CallToApplyArea button")
            if apply_btn:
                btn_text = await apply_btn.inner_text()
                btn_text_lower = btn_text.lower()
                
                # Skip external links
                if any(term in btn_text_lower for term in ["company site", "external", "apply on company"]):
                    print("    [!] Detected external company site job. Skipping...")
                    await job_page.close()
                    return False
                    
                await apply_btn.click()
                await job_page.wait_for_timeout(3000)
                print(f"    [OK] Successfully submitted Easy Apply on Indeed for {title}!")
                
                # Log applied status
                job_data = {
                    "title": title,
                    "company": "Indeed SCM Employer",
                    "location": default_loc,
                    "description": desc[:1000],
                    "url": url,
                    "platform": "Indeed",
                    "match_score": comp['score'],
                    "status": "Applied"
                }
                job_id = db.add_job(job_data)
                db.save_application({
                    "job_id": job_id,
                    "date_applied": datetime.now().strftime("%Y-%m-%d")
                })
                await job_page.close()
                return True
            else:
                print("    [!] Indeed Easy Apply not available (External). Skipping...")
        else:
            print(f"    [-] Excluded: Indeed Match score is {comp['score']}% (below 70% threshold).")
            
        await job_page.close()
        return False
    except Exception as e:
        print(f"    [!] Error processing Indeed job {url}: {e}")
        if job_page:
            try:
                await job_page.close()
            except:
                pass
        return False

async def automate_indeed_applications(profile, max_apps=10):
    """
    Background automation to search, score, and auto-apply to Indeed jobs.
    """
    print("\n[*] Starting Indeed Background Auto-Apply Engine...")
    
    async with async_playwright() as pw:
        browser, context = await get_browser_context(pw, INDEED_SESSION_PATH, headless=False)
        page = await context.new_page()
        
        applied_count = 0
        
        for role in profile['target_roles'][:3]:
            for loc in profile['preferred_locations'][:2]:
                if applied_count >= max_apps:
                    break
                    
                role_query = role.replace(" ", "+")
                loc_query = loc.replace(" ", "+")
                search_url = f"https://in.indeed.com/jobs?q={role_query}&l={loc_query}&fromage=5"
                
                print(f"[*] Navigating Indeed search query: {search_url}")
                try:
                    await page.goto(search_url, wait_until="commit", timeout=25000)
                    await page.wait_for_timeout(3000)
                    await handle_cloudflare_challenge(page)
                except Exception as e:
                    print(f"[!] Warning: Indeed connection timeout. Skipping... {e}")
                    continue
                    
                # Extract Indeed job cards title links
                job_cards = await page.query_selector_all("a.jcs-JobTitle")
                urls = []
                for card in job_cards[:8]:
                    href = await card.get_attribute("href")
                    if href:
                        if href.startswith("/"):
                            href = "https://in.indeed.com" + href
                        urls.append(href)
                        
                print(f"[*] Identified {len(urls)} Indeed job leads in this query.")
                
                for url in urls:
                    if applied_count >= max_apps:
                        break
                    success = await process_and_apply_indeed_job(context, url, profile, default_loc=loc)
                    if success:
                        applied_count += 1
                        
        await browser.close()
        return applied_count

# =================================================================
# 3. SYSTEM MAIN EXECUTOR
# =================================================================

async def main():
    profile = db.get_profile()
    if not profile:
        print("[!] Error: Seeder profile not found.")
        return
        
    print(f"[+] Loaded Candidate Profile: {profile['name']}")
    
    # Check if sessions are active
    if not os.path.exists(NAUKRI_SESSION_PATH):
        print("\n[*] Initializing first-time Naukri Login...")
        await setup_portal_session("Naukri", "https://www.naukri.com/nlogin/login", NAUKRI_SESSION_PATH)
        
    if not os.path.exists(INDEED_SESSION_PATH):
        print("\n[*] Initializing first-time Indeed Login...")
        await setup_portal_session("Indeed", "https://secure.indeed.com/auth", INDEED_SESSION_PATH)
        
    print("\n=================================================================")
    print("[*] PIPELINE INITIALIZED: LAUNCHING AUTO-APPLY ENGAGEMENT")
    print("=================================================================")
    
    naukri_apps = await automate_naukri_applications(profile, max_apps=25)
    
    indeed_apps = 0
    if os.path.exists(INDEED_SESSION_PATH):
        try:
            indeed_apps = await automate_indeed_applications(profile, max_apps=10)
        except Exception as e:
            print(f"[!] Warning: Could not complete Indeed auto-apply: {e}")
            
    total_apps = naukri_apps + indeed_apps
    print(f"\n[OK] Done! Auto-applied to {total_apps} highly compatible SCM jobs (Naukri: {naukri_apps}, Indeed: {indeed_apps}) on your system!")

if __name__ == "__main__":
    asyncio.run(main())

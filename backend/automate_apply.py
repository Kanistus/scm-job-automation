import asyncio
import sys
import os
import json
from datetime import datetime

# Include backend path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import database as db
from services.ats_engine import calculate_compatibility
from services.telegram_bot import send_telegram_message

try:
    from playwright.async_api import async_playwright
    from camoufox.async_api import AsyncCamoufox
except ImportError:
    print("[!] Playwright or Camoufox is not installed.")
    sys.exit(1)

SESSION_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "sessions")
os.makedirs(SESSION_DIR, exist_ok=True)

NAUKRI_SESSION_PATH = os.path.join(SESSION_DIR, "naukri_session.json")
INDEED_SESSION_PATH = os.path.join(SESSION_DIR, "indeed_session.json")

cancel_requested = False

async def get_browser_context(pw, session_path, headless=False):
    """
    Launches browser, loading saved login cookies if present.
    """
    from camoufox import AsyncNewBrowser
    browser = await AsyncNewBrowser(pw, headless=headless)
    
    # Load session state if it exists
    if os.path.exists(session_path):
        print(f"[*] Loading active login session from {os.path.basename(session_path)}...")
        context = await browser.new_context(
            storage_state=session_path,
            viewport={"width": 1280, "height": 800}
        )
    else:
        print("[*] No active session found. Launching fresh context for manual login...")
        context = await browser.new_context(
            viewport={"width": 1280, "height": 800}
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
    
    async with AsyncCamoufox(headless=False) as browser:
        context = await browser.new_context()
        page = await context.new_page()
        
        await page.goto(login_url)
        
        # Wait for user to log in and press enter in console
        await asyncio.get_event_loop().run_in_executor(None, input, "Press [Enter] here ONLY AFTER you have successfully logged in in the browser...")
        
        # Save storage state
        await context.storage_state(path=session_path)
        print(f"[+] Login session tokens saved successfully to: {os.path.basename(session_path)}")

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
            
            # Enforce 'posted date is in days' filter (e.g. contains 'day', 'days', 'hour', 'hours', 'just posted', 'today')
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
        
        if comp['score'] >= 65:
            print(f"    [+] Highly Compatible Fit: {comp['score']}%! Triggering auto-submit...")
            await send_telegram_message(
                f"🔍 <b>Highly Compatible Naukri Job Fit</b> ({comp['score']}%):\n"
                f"💼 <b>{title}</b>\n"
                f"📍 Location: {default_loc}\n"
                f"Starting auto-apply process..."
            )
            
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
                
                # Handle chatbot questionnaire (Naukri slide-out recruiter chatbot/questions)
                chatbot_active = False
                for step in range(12):
                    # Check if chatbot container is open and visible
                    chatbot_container = None
                    for bot_sel in [".chatbot_InputContainer", "[class*='chatbot']", "[class*='botContainer']", ".drawer", "[class*='drawer']", ".botItem"]:
                        try:
                            el = await job_page.query_selector(bot_sel)
                            if el and await el.is_visible():
                                chatbot_container = el
                                chatbot_active = True
                                break
                        except:
                            pass
                            
                    if not chatbot_active and step == 0:
                        # Wait up to 3 seconds on the first step for the chatbot to possibly slide out
                        for _ in range(3):
                            await job_page.wait_for_timeout(1000)
                            for bot_sel in [".chatbot_InputContainer", "[class*='chatbot']", "[class*='botContainer']", ".drawer", "[class*='drawer']", ".botItem"]:
                                try:
                                    el = await job_page.query_selector(bot_sel)
                                    if el and await el.is_visible():
                                        chatbot_container = el
                                        chatbot_active = True
                                        break
                                except:
                                    pass
                            if chatbot_active:
                                break
                                
                    if not chatbot_active:
                        print("    [Chatbot] No active chatbot container detected. Direct application assumed complete.")
                        break
                        
                    # Query chatbot elements inside the container
                    container_to_query = chatbot_container if chatbot_container else job_page
                    
                    # Check for skip buttons inside chatbot container
                    skip_btn = None
                    for sel in ["span:has-text('Skip')", "a:has-text('Skip')", "button:has-text('Skip')", "div:has-text('Skip')", "text='Skip this question'"]:
                        try:
                            el = await container_to_query.query_selector(sel)
                            if el and await el.is_visible():
                                skip_btn = el
                                break
                        except:
                            pass
                    if skip_btn:
                        print("    [Chatbot] Clicking Skip button...")
                        await skip_btn.click(force=True)
                        await job_page.wait_for_timeout(2500)
                        continue
                        
                    # Check for text inputs or textareas inside chatbot container
                    textarea = await container_to_query.query_selector("div.textArea[contenteditable='true'], div[class*='textArea'][contenteditable='true'], div[contenteditable='true'], textarea, input[type='text']")
                    if textarea and await textarea.is_visible():
                        question_text = ""
                        try:
                            # Try to extract the last question text
                            questions = await container_to_query.query_selector_all(".botMsg span, .botItem span, [class*='question'] span, [class*='msg'] span")
                            if questions:
                                question_text = await questions[-1].inner_text()
                        except:
                            pass
                        
                        q_lower = question_text.lower()
                        answer = "1"
                        if "notice period" in q_lower or "notice" in q_lower:
                            answer = "Immediate"
                        elif "expected" in q_lower and ("ctc" in q_lower or "salary" in q_lower or "lacs" in q_lower or "lpa" in q_lower):
                            answer = "4"
                        elif "current" in q_lower and ("ctc" in q_lower or "salary" in q_lower or "lacs" in q_lower or "lpa" in q_lower):
                            answer = "2"
                        elif "ctc" in q_lower or "salary" in q_lower or "lacs" in q_lower or "lpa" in q_lower:
                            answer = "4" # default expected
                        elif "experience" in q_lower or "years" in q_lower or "po" in q_lower or "procurement" in q_lower or "order" in q_lower:
                            if any(x in q_lower for x in ["years", "total", "number", "how many", "how much", "excel", "procurement", "inventory", "sap"]):
                                answer = "1"
                            else:
                                answer = "one year of experience. I have. If you want more information, you can retrieve it from my resume."
                        elif "location" in q_lower or "city" in q_lower:
                            answer = "Bangalore"
                        elif "travel" in q_lower and ("percentage" in q_lower or "%" in q_lower):
                            answer = "50%"
                        elif "relocate" in q_lower or "shift" in q_lower or "travel" in q_lower or "place" in q_lower or "area" in q_lower or "willing to travel" in q_lower:
                            answer = "Yes"
                        elif "previously employed" in q_lower or "previously worked" in q_lower or "former employee" in q_lower or "ex-employee" in q_lower or "worked here" in q_lower:
                            answer = "No"
                        elif "sap" in q_lower or "excel" in q_lower:
                            answer = "Yes"
                            
                        print(f"    [Chatbot] Answering text question '{question_text.strip()}' with: {answer}")
                        await textarea.focus()
                        await job_page.keyboard.type(answer)
                        await job_page.wait_for_timeout(500)
                        await job_page.keyboard.press("Enter")
                        await job_page.wait_for_timeout(2500)
                        continue
                        
                    # Check for checkboxes inside the chatbot container
                    checkbox_elements = []
                    cb_inputs = await container_to_query.query_selector_all("input[type='checkbox']")
                    for cb in cb_inputs:
                        if await cb.is_visible():
                            checkbox_elements.append(cb)
                    if not checkbox_elements:
                        custom_cbs = await container_to_query.query_selector_all("[role='checkbox'], [class*='checkbox']")
                        for cb in custom_cbs:
                            if await cb.is_visible():
                                checkbox_elements.append(cb)
                                
                    if checkbox_elements:
                        print(f"    [Chatbot] Detected {len(checkbox_elements)} checkbox options.")
                        # Read last question for context
                        question_text = ""
                        try:
                            questions = await container_to_query.query_selector_all(".botMsg span, .botItem span, [class*='question'] span, [class*='msg'] span")
                            if questions:
                                question_text = await questions[-1].inner_text()
                        except:
                            pass
                        q_lower = question_text.lower()
                        
                        clicked_any_cb = False
                        for cb in checkbox_elements:
                            cb_text = ""
                            try:
                                parent = await cb.evaluate_handle("el => el.parentElement")
                                cb_text = (await parent.evaluate("el => el.innerText || el.textContent") or "").strip()
                            except:
                                pass
                            if not cb_text:
                                try:
                                    cb_text = (await cb.inner_text()).strip()
                                except:
                                    pass
                                    
                            cb_text_lower = cb_text.lower()
                            should_check = False
                            
                            # Match based on question type
                            if "categories" in q_lower and ("handled" in q_lower or "purchased" in q_lower or "sourced" in q_lower or "procured" in q_lower):
                                if "raw materials" in cb_text_lower or "commodities" in cb_text_lower:
                                    should_check = True
                            elif "notice period" in q_lower or "notice" in q_lower:
                                if any(term in cb_text_lower for term in ["immediate", "15 days", "less than", "1 month"]):
                                    should_check = True
                            elif "current" in q_lower and ("ctc" in q_lower or "salary" in q_lower):
                                if any(term in cb_text_lower for term in ["2", "2 lakhs", "2 lakh", "2 lpa"]):
                                    should_check = True
                            elif "expected" in q_lower and ("ctc" in q_lower or "salary" in q_lower):
                                if any(term in cb_text_lower for term in ["4", "4 lakhs", "4 lakh", "4 lpa", "4-5"]):
                                    should_check = True
                            elif "ctc" in q_lower or "salary" in q_lower:
                                if any(term in cb_text_lower for term in ["4", "4 lakhs", "4 lakh", "4 lpa", "4-5"]):
                                    should_check = True
                            elif "experience" in q_lower or "years" in q_lower:
                                if any(term in cb_text_lower for term in ["1", "one", "1 year", "1-2", "1-2 years"]):
                                    should_check = True
                            elif "location" in q_lower or "city" in q_lower:
                                if any(term in cb_text_lower for term in ["bangalore", "bengaluru", "chennai", "remote"]):
                                    should_check = True
                            elif "relocate" in q_lower:
                                if any(term in cb_text_lower for term in ["yes", "willing", "ready", "agree"]):
                                    should_check = True
                            elif "shift" in q_lower:
                                if any(term in cb_text_lower for term in ["yes", "night", "willing", "ready", "any", "flexible"]):
                                    should_check = True
                            elif "travel" in q_lower:
                                if "percentage" in q_lower or "%" in q_lower:
                                    if any(term in cb_text_lower for term in ["50%", "60%", "50-60", "50 to 60"]):
                                        should_check = True
                                else:
                                    if any(term in cb_text_lower for term in ["yes", "willing", "ready", "anywhere", "any area"]):
                                        should_check = True
                            elif "previously employed" in q_lower or "previously worked" in q_lower:
                                if any(term in cb_text_lower for term in ["no", "never", "not"]):
                                    should_check = True
                            elif any(term in q_lower for term in ["sap", "excel", "willing", "shift", "possess", "relocate", "travel", "join"]):
                                if any(term in cb_text_lower for term in ["yes", "willing", "agree", "sure", "i have", "i do", "i am", "confirm"]):
                                    should_check = True
                                    
                            # Fallback keyword matching on profile skills/tools/erps
                            if not should_check:
                                profile_terms = (profile.get("extracted_skills", []) + 
                                                 profile.get("extracted_tools", []) + 
                                                 profile.get("extracted_erps", []))
                                for term in profile_terms:
                                    if len(term) > 2 and term.lower() in cb_text_lower:
                                        should_check = True
                                        break
                                        
                            if should_check:
                                is_checked = False
                                try:
                                    is_checked = await cb.evaluate("el => el.checked")
                                except:
                                    try:
                                        checked_attr = await cb.get_attribute("aria-checked")
                                        if checked_attr == "true":
                                            is_checked = True
                                    except:
                                        pass
                                        
                                if not is_checked:
                                    print(f"    [Chatbot] Checking option: '{cb_text}'")
                                    await cb.click(force=True)
                                    await job_page.wait_for_timeout(1000)
                                    clicked_any_cb = True
                                    
                        if not clicked_any_cb and checkbox_elements:
                            # Fallback: check first option if nothing matched
                            print("    [Chatbot] Fallback: No checkbox option matched. Checking first option...")
                            cb = checkbox_elements[0]
                            cb_text = ""
                            try:
                                parent = await cb.evaluate_handle("el => el.parentElement")
                                cb_text = (await parent.evaluate("el => el.innerText || el.textContent") or "").strip()
                            except:
                                pass
                            print(f"    [Chatbot] Checking first option: '{cb_text}'")
                            await cb.click(force=True)
                            await job_page.wait_for_timeout(1000)
                            clicked_any_cb = True
                            
                        if clicked_any_cb:
                            # Click Save/Submit button
                            save_btn = None
                            for sel in ["button:has-text('Save')", "button:has-text('Submit')", "button:has-text('Apply')", ".saveBtn", "[class*='save']", "[class*='submit']"]:
                                try:
                                    el = await container_to_query.query_selector(sel)
                                    if el and await el.is_visible():
                                        save_btn = el
                                        break
                                except:
                                    pass
                            if save_btn:
                                print("    [Chatbot] Clicking Save/Submit after checkboxes...")
                                await save_btn.click(force=True)
                                await job_page.wait_for_timeout(2500)
                            continue

                    # Check for choice chips/options inside the chatbot container
                    options = await container_to_query.query_selector_all("button, div.chip, [class*='option'], [class*='chip'], a")
                    # filter out submit/apply/save/skip/close buttons from options to prevent premature submit clicks
                    filtered_options = []
                    for opt in options:
                        try:
                            opt_text = (await opt.inner_text()).strip().lower()
                            if not any(term in opt_text for term in ["save", "submit", "apply", "skip", "close", "cancel"]):
                                filtered_options.append(opt)
                        except:
                            pass
                            
                    if filtered_options:
                        clicked_option = False
                        # Read last question for context
                        question_text = ""
                        try:
                            questions = await container_to_query.query_selector_all(".botMsg span, .botItem span, [class*='question'] span, [class*='msg'] span")
                            if questions:
                                question_text = await questions[-1].inner_text()
                        except:
                            pass
                        q_lower = question_text.lower()
                        
                        for opt in filtered_options:
                            if await opt.is_visible():
                                opt_text = (await opt.inner_text()).strip()
                                opt_text_lower = opt_text.lower()
                                
                                should_click = False
                                if "categories" in q_lower and ("handled" in q_lower or "purchased" in q_lower or "sourced" in q_lower or "procured" in q_lower):
                                    if "raw materials" in opt_text_lower or "commodities" in opt_text_lower:
                                        should_click = True
                                elif "notice period" in q_lower or "notice" in q_lower:
                                    if any(term in opt_text_lower for term in ["immediate", "15 days", "less than", "1 month"]):
                                        should_click = True
                                elif "current" in q_lower and ("ctc" in q_lower or "salary" in q_lower or "lacs" in q_lower or "lpa" in q_lower):
                                    if any(term in opt_text_lower for term in ["2", "2 lakhs", "2 lakh", "2 lpa", "2.0"]):
                                        should_click = True
                                elif "expected" in q_lower and ("ctc" in q_lower or "salary" in q_lower or "lacs" in q_lower or "lpa" in q_lower):
                                    if any(term in opt_text_lower for term in ["4", "4 lakhs", "4 lakh", "4 lpa", "4.0", "4-5"]):
                                        should_click = True
                                elif "ctc" in q_lower or "salary" in q_lower or "lacs" in q_lower or "lpa" in q_lower:
                                    if any(term in opt_text_lower for term in ["4", "4 lakhs", "4 lakh", "4 lpa", "4.0", "4-5"]):
                                        should_click = True
                                elif "experience" in q_lower or "years" in q_lower or "po" in q_lower or "procurement" in q_lower or "order" in q_lower:
                                    if any(term in opt_text_lower for term in ["1", "one", "1 year", "1-2", "1-2 years"]):
                                        should_click = True
                                elif "location" in q_lower or "city" in q_lower:
                                    if any(term in opt_text_lower for term in ["bangalore", "bengaluru", "chennai", "remote"]):
                                        should_click = True
                                elif "travel" in q_lower and ("percentage" in q_lower or "%" in q_lower):
                                    if any(term in opt_text_lower for term in ["50%", "60%", "50-60", "50 to 60", "50-75", "50 to 75"]):
                                        should_click = True
                                    elif any(term in opt_text_lower for term in ["50", "60"]):
                                        should_click = True
                                elif "relocate" in q_lower:
                                    if any(term in opt_text_lower for term in ["yes", "willing", "ready", "agree", "sure", "okay", "ok"]):
                                        should_click = True
                                elif "shift" in q_lower:
                                    if any(term in opt_text_lower for term in ["yes", "night", "willing", "ready", "agree", "sure", "okay", "ok", "any"]):
                                        should_click = True
                                elif "travel" in q_lower or "place" in q_lower or "area" in q_lower or "willing to travel" in q_lower:
                                    if any(term in opt_text_lower for term in ["yes", "willing", "ready", "agree", "sure", "okay", "ok", "any", "anywhere", "any area"]):
                                        should_click = True
                                elif "previously employed" in q_lower or "previously worked" in q_lower or "former employee" in q_lower or "ex-employee" in q_lower or "worked here" in q_lower:
                                    if any(term in opt_text_lower for term in ["no", "never", "not"]):
                                        should_click = True
                                elif any(term in q_lower for term in ["sap", "excel", "willing", "shift", "possess", "relocate", "travel", "join"]):
                                    if any(term in opt_text_lower for term in ["yes", "willing", "okay", "ok", "agree", "sure", "i have", "i do", "i am", "confirm"]):
                                        should_click = True
                                        
                                if not should_click:
                                    if any(term in q_lower for term in ["relocate", "willing", "location", "travel", "shift"]):
                                        if any(term in opt_text_lower for term in ["okay", "ok", "yes", "agree", "sure", "willing", "confirm"]):
                                            should_click = True
                                            
                                if not should_click:
                                    if any(term == opt_text_lower for term in ["yes", "okay", "ok", "agree", "sure", "confirm"]):
                                        should_click = True
                                    elif any(term in opt_text_lower for term in ["yes, i am", "yes, i do", "yes, i'm", "willing to", "ready to"]):
                                        should_click = True
                                        
                                # Fallback keyword matching on profile skills/tools/erps
                                if not should_click:
                                    profile_terms = (profile.get("extracted_skills", []) + 
                                                     profile.get("extracted_tools", []) + 
                                                     profile.get("extracted_erps", []))
                                    for term in profile_terms:
                                        if len(term) > 2 and term.lower() in opt_text_lower:
                                            should_click = True
                                            break
                                            
                                if should_click:
                                    print(f"    [Chatbot] Clicking option chip for question '{question_text.strip()}': {opt_text}")
                                    await opt.click(force=True)
                                    await job_page.wait_for_timeout(2500)
                                    clicked_option = True
                                    break
                                    
                        if not clicked_option and filtered_options:
                            for opt in filtered_options:
                                if await opt.is_visible():
                                    opt_text = (await opt.inner_text()).strip()
                                    print(f"    [Chatbot] Fallback: Clicking first available option chip: {opt_text}")
                                    await opt.click(force=True)
                                    await job_page.wait_for_timeout(2500)
                                    clicked_option = True
                                    break
                        if clicked_option:
                            continue
                            
                    # Check for Save/Submit/Apply button inside chatbot container to finalize
                    save_btn = None
                    for sel in ["button:has-text('Save')", "button:has-text('Submit')", "button:has-text('Apply')", ".saveBtn", "[class*='save']", "[class*='submit']"]:
                        try:
                            el = await container_to_query.query_selector(sel)
                            if el and await el.is_visible():
                                is_disabled = await el.get_attribute("disabled")
                                if is_disabled is None:
                                    save_btn = el
                                    break
                        except:
                            pass
                    if save_btn:
                        print("    [Chatbot] Clicking final Save/Submit button inside chatbot...")
                        await save_btn.click(force=True)
                        await job_page.wait_for_timeout(4000)
                        break
                    else:
                        await job_page.wait_for_timeout(1500)
                        
                # Verify that it didn't reject or get stuck
                page_text = await job_page.evaluate("() => document.body.innerText")
                if "application was not accepted" in page_text or "answer all mandatory questions" in page_text:
                    print(f"    [!] Error: Naukri rejected the application due to missing chatbot answers.")
                    await job_page.close()
                    return False
                    
                print(f"    [OK] Successfully submitted application for {title}!")
                await send_telegram_message(
                    f"✅ <b>Successfully Applied!</b>\n"
                    f"💼 <b>{title}</b> at <b>Naukri Employer</b>\n"
                    f"🎯 Score: {comp['score']}%"
                )
                
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
            print(f"    [-] Excluded: Match score is {comp['score']}% (below 65% threshold).")
            
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
    global cancel_requested
    if not os.path.exists(NAUKRI_SESSION_PATH):
        print("[!] Naukri session not found. Setting up session first...")
        await setup_portal_session("Naukri", "https://www.naukri.com/nlogin/login", NAUKRI_SESSION_PATH)

    print("\n[*] Starting Naukri Background Auto-Apply Engine...")
    
    async with AsyncCamoufox(headless=False) as browser:
        context = await browser.new_context(storage_state=NAUKRI_SESSION_PATH) if os.path.exists(NAUKRI_SESSION_PATH) else await browser.new_context()
        page = await context.new_page()
        
        applied_count = 0
        
        # Get already applied jobs from DB to skip them
        applied_jobs = db.get_jobs(status_filter="Applied")
        applied_urls = {job["url"] for job in applied_jobs if job.get("url")}
        
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
                if cancel_requested:
                    print("[!] Cancellation requested. Stopping Naukri Recommended sweep...")
                    break
                if applied_count >= max_apps:
                    break
                if url in applied_urls:
                    print(f"    [*] Job already applied to. Skipping Recommended URL: {url}")
                    continue
                success = await process_and_apply_job(context, url, profile, default_loc="Bangalore (Recommended)")
                if success:
                    applied_count += 1
        except Exception as e:
            print(f"[!] Warning: Could not complete Recommended Jobs scan: {e}")

        # B. SECOND RUN: NAVIGATE AND APPLY TO STANDARD SEARCH QUERIES
        if applied_count < max_apps and not cancel_requested:
            print("\n[*] STEP 2: Running standard SCM search queries...")
            for role in profile['target_roles']:
                if cancel_requested:
                    break
                for loc in profile['preferred_locations']:
                    if cancel_requested:
                        break
                    for exp in [0, 1, 2]:
                        if cancel_requested:
                            break
                        if applied_count >= max_apps:
                            break
                            
                        search_query = f"{role.replace(' ', '-')}-jobs-in-{loc.lower()}"
                        search_url = f"https://www.naukri.com/{search_query}?experience={exp}&jobAge=5"
                        
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
                        for card in job_cards[:20]:
                            href = await card.get_attribute("href")
                            if href:
                                if href.startswith("/"):
                                    href = "https://www.naukri.com" + href
                                urls.append(href)
                                
                        print(f"[*] Identified {len(urls)} job leads in this query.")
                        
                        for url in urls:
                            if cancel_requested:
                                print("[!] Cancellation requested. Stopping Naukri Search sweep...")
                                break
                            if applied_count >= max_apps:
                                break
                            if url in applied_urls:
                                print(f"    [*] Job already applied to. Skipping Search URL: {url}")
                                continue
                            success = await process_and_apply_job(context, url, profile, default_loc=loc)
                            if success:
                                applied_count += 1
                                
        print(f"[*] Naukri run complete. Applied to {applied_count} jobs.")
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
        await send_telegram_message(
            f"⚠️ <b>Action Required: Indeed Cloudflare Challenge Detected!</b>\n"
            f"Please solve the 'Verify you are human' challenge on your desktop screen to resume."
        )
        
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
        
        if comp['score'] >= 65:
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
                await send_telegram_message(
                    f"✅ <b>Successfully Applied!</b>\n"
                    f"💼 <b>{title}</b> at <b>Indeed SCM Employer</b>\n"
                    f"🎯 Score: {comp['score']}%"
                )
                
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
            print(f"    [-] Excluded: Indeed Match score is {comp['score']}% (below 65% threshold).")
            
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
    global cancel_requested
    print("\n[*] Starting Indeed Background Auto-Apply Engine...")
    
    async with AsyncCamoufox(headless=False) as browser:
        context = await browser.new_context(storage_state=INDEED_SESSION_PATH) if os.path.exists(INDEED_SESSION_PATH) else await browser.new_context()
        page = await context.new_page()
        
        applied_count = 0
        
        # Get already applied jobs from DB to skip them
        applied_jobs = db.get_jobs(status_filter="Applied")
        applied_urls = {job["url"] for job in applied_jobs if job.get("url")}
        
        for role in profile['target_roles'][:3]:
            if cancel_requested:
                break
            for loc in profile['preferred_locations'][:2]:
                if cancel_requested:
                    break
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
                    if cancel_requested:
                        print("[!] Cancellation requested. Stopping Indeed sweep...")
                        break
                    if applied_count >= max_apps:
                        break
                    if url in applied_urls:
                        print(f"    [*] Job already applied to. Skipping Indeed URL: {url}")
                        continue
                    success = await process_and_apply_indeed_job(context, url, profile, default_loc=loc)
                    if success:
                        applied_count += 1
                        
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

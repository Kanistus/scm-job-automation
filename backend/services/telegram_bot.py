import asyncio
import os
import sys
import logging
import httpx

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add parent directory to sys.path to allow database and automation imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

import database as db

# Lock to ensure only one automation run executes at any time
_run_lock = asyncio.Lock()
_polling_task = None

async def send_telegram_message(text: str):
    """
    Sends a message to the configured Telegram chat if Telegram alerts are enabled.
    """
    settings = db.get_settings()
    enabled = settings.get("telegram_enabled") == "true"
    token = settings.get("telegram_bot_token", "")
    chat_id = settings.get("telegram_chat_id", "")
    
    if not enabled or not token or not chat_id:
        return False
        
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, json=payload)
            return response.status_code == 200
    except Exception as e:
        logger.error(f"Telegram message delivery failed: {e}")
        return False


class TelegramBotManager:
    def __init__(self):
        self.offset = 0
        self.client = httpx.AsyncClient(timeout=10.0)

    async def send_msg(self, token, chat_id, text):
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        try:
            await self.client.post(url, json={
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "HTML"
            })
        except Exception as e:
            logger.error(f"Telegram bot send_msg failed: {e}")

    async def handle_command(self, token, chat_id, text):
        clean_text = text.lower().strip()
        
        # Command 1: Query applied jobs
        if any(cmd in clean_text for cmd in ["applied", "jobs", "list"]):
            conn = db.get_db_connection()
            rows = conn.execute("""
                SELECT j.title, j.company, a.date_applied 
                FROM applications a 
                JOIN jobs j ON a.job_id = j.id 
                ORDER BY a.id DESC LIMIT 15
            """).fetchall()
            conn.close()
            
            if not rows:
                await self.send_msg(token, chat_id, "ℹ️ No applied jobs found in your database.")
                return
                
            # Request specifies ONLY the job titles
            msg = "<b>📋 Jobs Applied To:</b>\n\n"
            for idx, r in enumerate(rows):
                msg += f"{idx+1}. {r['title']}\n"
            await self.send_msg(token, chat_id, msg)
            
        # Command 2: Trigger automation run
        elif any(cmd in clean_text for cmd in ["run", "start", "execute", "apply"]):
            if _run_lock.locked():
                await self.send_msg(token, chat_id, "⚠️ Automation sweep is already running in the background!")
                return
                
            await self.send_msg(token, chat_id, "🚀 <b>Starting SCM Job Auto-Apply sweep...</b>\nI will send updates as I apply to matching positions.")
            # Trigger background uvicorn task to avoid blocking polling loop
            asyncio.create_task(self.execute_automation_sweep(token, chat_id))
            
        # Command 3: Stop / Cancel run
        elif any(cmd in clean_text for cmd in ["stop", "cancel", "halt", "abort"]):
            import automate_apply
            if not _run_lock.locked():
                await self.send_msg(token, chat_id, "ℹ️ No automation sweep is currently running.")
                return
                
            automate_apply.cancel_requested = True
            await self.send_msg(token, chat_id, "🛑 <b>Stopping the active automation sweep...</b>\nI will terminate the job applying loops shortly.")
            
        # Command 4: Help/Default
        else:
            help_text = (
                "🤖 <b>SCM Job Automation Bot</b>\n\n"
                "Available commands:\n"
                "• <b>run the bot</b> / <b>run the automation</b> - Start automatic Naukri/Indeed sweeps\n"
                "• <b>stop the bot</b> / <b>cancel</b> - Stop the active automation sweep\n"
                "• <b>applied jobs</b> / <b>list</b> - Show the list of recently applied job titles\n"
                "• <b>help</b> - Display this help guide"
            )
            await self.send_msg(token, chat_id, help_text)

    async def execute_automation_sweep(self, token, chat_id):
        async with _run_lock:
            try:
                # Reset cancellation flag
                import automate_apply
                automate_apply.cancel_requested = False
                
                # Fetch profile from DB
                profile = db.get_profile()
                if not profile:
                    await self.send_msg(token, chat_id, "❌ Error: Seeder profile not found. Please upload your resume first.")
                    return
                
                # Import main application sweep tasks
                from automate_apply import automate_naukri_applications, automate_indeed_applications
                
                # 1. Run Naukri sweep
                await self.send_msg(token, chat_id, "🔍 <i>Scanning Naukri SCM jobs...</i>")
                naukri_count = await automate_naukri_applications(profile, max_apps=25)
                await self.send_msg(token, chat_id, f"✅ Naukri sweep complete! Applied to <b>{naukri_count}</b> jobs.")
                
                # 2. Run Indeed sweep
                indeed_count = 0
                indeed_session = os.path.join(parent_dir, "data", "sessions", "indeed_session.json")
                if os.path.exists(indeed_session):
                    await self.send_msg(token, chat_id, "🔍 <i>Scanning Indeed SCM jobs...</i>")
                    indeed_count = await automate_indeed_applications(profile, max_apps=10)
                    await self.send_msg(token, chat_id, f"✅ Indeed sweep complete! Applied to <b>{indeed_count}</b> jobs.")
                else:
                    await self.send_msg(token, chat_id, "ℹ️ Indeed session not found. Skipping Indeed sweep.")
                
                total = naukri_count + indeed_count
                await self.send_msg(token, chat_id, f"🎯 <b>Auto-apply sweep completed successfully!</b> Total jobs applied: {total}")
                
            except Exception as e:
                logger.error(f"Error in remote Telegram automation execution: {e}")
                await self.send_msg(token, chat_id, f"❌ Error running automation: {str(e)}")

    async def poll_updates(self):
        logger.info("Starting Telegram Bot getUpdates polling loop...")
        while True:
            try:
                settings = db.get_settings()
                enabled = settings.get("telegram_enabled") == "true"
                token = settings.get("telegram_bot_token", "")
                configured_chat_id = settings.get("telegram_chat_id", "")
                
                if not enabled or not token or not configured_chat_id:
                    await asyncio.sleep(5)
                    continue
                
                url = f"https://api.telegram.org/bot{token}/getUpdates"
                response = await self.client.get(url, params={
                    "offset": self.offset,
                    "timeout": 20
                })
                
                if response.status_code == 200:
                    data = response.json()
                    for update in data.get("result", []):
                        self.offset = update["update_id"] + 1
                        message = update.get("message", {})
                        text = message.get("text", "")
                        sender_chat_id = str(message.get("chat", {}).get("id", ""))
                        
                        if text and sender_chat_id:
                            # Strict Security Check
                            if sender_chat_id != str(configured_chat_id):
                                logger.warning(f"Unauthorized Telegram access blocked from Chat ID: {sender_chat_id}")
                                await self.send_msg(token, sender_chat_id, "🔒 <b>Unauthorized Access</b>\nThis bot is locked to its configured owner's Chat ID.")
                                continue
                                
                            await self.handle_command(token, sender_chat_id, text)
                            
            except httpx.RequestError as e:
                logger.error(f"Telegram connection issue in polling loop: {e}")
                await asyncio.sleep(8)
            except Exception as e:
                logger.error(f"Unexpected error in Telegram polling: {e}")
                await asyncio.sleep(5)
                
            await asyncio.sleep(1)


async def start_telegram_bot():
    global _polling_task
    if _polling_task is not None:
        logger.info("[Telegram] Polling loop is already active.")
        return
        
    bot = TelegramBotManager()
    _polling_task = asyncio.create_task(bot.poll_updates())
    logger.info("[Telegram] Async Bot polling loop spawned successfully.")

async def stop_telegram_bot():
    global _polling_task
    if _polling_task is not None:
        logger.info("[Telegram] Canceling polling loop...")
        _polling_task.cancel()
        try:
            await _polling_task
        except asyncio.CancelledError:
            pass
        _polling_task = None
        logger.info("[Telegram] Polling loop terminated.")

async def restart_telegram_bot():
    await stop_telegram_bot()
    await start_telegram_bot()

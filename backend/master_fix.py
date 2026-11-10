import os, ast, subprocess, sys

print("=" * 60)
print("FACEBOOK MODULE DIAGNOSTIC + AUTO-FIX")
print("=" * 60)

# STEP 1: Selenium check
try:
    import selenium
    print("[1/4] Selenium: OK")
except ImportError:
    print("[1/4] Selenium: MISSING - installing...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "selenium"])

# STEP 2: facebook_agent.py check
if os.path.exists("facebook_agent.py"):
    print("[2/4] facebook_agent.py: EXISTS")
else:
    print("[2/4] facebook_agent.py: MISSING - creating...")
    code = '''import os
import time
from typing import Dict

class FacebookAgent:
    def __init__(self):
        self.profile_dir = os.path.join(os.path.expanduser("~"), ".ada_chrome_profile")
        os.makedirs(self.profile_dir, exist_ok=True)
    def post_status(self, text: str) -> Dict:
        driver = None
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            options = Options()
            options.add_argument(f"--user-data-dir={self.profile_dir}")
            options.add_argument("--start-maximized")
            options.add_argument("--disable-notifications")
            print("[FACEBOOK] Launching Chrome...")
            driver = webdriver.Chrome(options=options)
            wait = WebDriverWait(driver, 30)
            print("[FACEBOOK] Opening facebook.com")
            driver.get("https://www.facebook.com/")
            time.sleep(4)
            if "login" in driver.current_url.lower() or "checkpoint" in driver.current_url.lower():
                print("[FACEBOOK] Login required - 120s wait for manual login...")
                for _ in range(120):
                    time.sleep(1)
                    if "login" not in driver.current_url.lower():
                        break
                else:
                    driver.quit()
                    return {"success": False, "error": "Login timeout"}
                time.sleep(3)
            print("[FACEBOOK] Finding status box...")
            clicked = False
            for sel in ["//div[@role='button' and contains(@aria-label, 'mind')]", "//span[contains(text(), \\"What's on your mind\\")]"]:
                try:
                    el = wait.until(EC.element_to_be_clickable((By.XPATH, sel)))
                    el.click()
                    clicked = True
                    break
                except Exception:
                    continue
            if not clicked:
                driver.quit()
                return {"success": False, "error": "Status box not found"}
            time.sleep(3)
            print(f"[FACEBOOK] Typing: {text[:50]}")
            typed = False
            for sel in ["//div[@role='textbox']", "//div[@contenteditable='true']"]:
                try:
                    ta = wait.until(EC.presence_of_element_located((By.XPATH, sel)))
                    ta.click()
                    time.sleep(1)
                    ta.send_keys(text)
                    typed = True
                    break
                except Exception:
                    continue
            if not typed:
                driver.quit()
                return {"success": False, "error": "Could not type"}
            time.sleep(2)
            print("[FACEBOOK] Clicking Post...")
            posted = False
            for sel in ["//div[@aria-label='Post' and @role='button']", "//span[text()='Post']/ancestor::div[@role='button']"]:
                try:
                    btn = wait.until(EC.element_to_be_clickable((By.XPATH, sel)))
                    btn.click()
                    posted = True
                    break
                except Exception:
                    continue
            if not posted:
                driver.quit()
                return {"success": False, "error": "Post button not found"}
            time.sleep(5)
            print("[FACEBOOK] Status posted!")
            driver.quit()
            return {"success": True, "message": f"Status posted: {text[:80]}"}
        except Exception as e:
            print(f"[FACEBOOK] Error: {e}")
            try:
                if driver: driver.quit()
            except: pass
            return {"success": False, "error": str(e)}

_facebook_agent = None
def get_facebook_agent():
    global _facebook_agent
    if _facebook_agent is None:
        _facebook_agent = FacebookAgent()
    return _facebook_agent
'''
    with open("facebook_agent.py", "w", encoding="utf-8") as f:
        f.write(code)

# STEP 3: ada.py patches
with open("ada.py", "r", encoding="utf-8") as f:
    src = f.read()

needs_tool = "facebook_status_tool" not in src
needs_reg = "screen_read_tool, facebook_status_tool]" not in src
needs_handler = 'fc.name == "facebook_status"' not in src

if needs_tool:
    tool = '''facebook_status_tool = {
    "name": "facebook_status",
    "description": "Posts a status update on Facebook. Use when user says facebook status lagao, facebook pe likho, facebook post karo, or facebook pe status dalo.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "text": {"type": "STRING", "description": "The status text to post"}
        },
        "required": ["text"]
    },
    "behavior": "NON_BLOCKING"
}

'''
    src = src.replace("tools = [", tool + "tools = [", 1)

if needs_reg:
    src = src.replace("screen_read_tool]", "screen_read_tool, facebook_status_tool]", 1)

if needs_handler:
    handler = '''                            elif fc.name == "facebook_status":
                                status_text = fc.args.get("text", "")
                                print(f"[ADA] facebook_status: {status_text[:60]}")
                                try:
                                    from facebook_agent import get_facebook_agent
                                    result = await asyncio.to_thread(get_facebook_agent().post_status, status_text)
                                    result_str = result.get("message") if result.get("success") else result.get("error", "Failed")
                                except Exception as e:
                                    result_str = f"Facebook error: {e}"
                                function_response = types.FunctionResponse(id=fc.id, name=fc.name, response={"result": result_str})
                                function_responses.append(function_response)

'''
    src = src.replace("                        if function_responses:", handler + "                        if function_responses:", 1)

ast.parse(src)
with open("ada.py", "w", encoding="utf-8") as f:
    f.write(src)

print("[3/4] ada.py patches: tool=" + ("ADDED" if needs_tool else "OK") + ", reg=" + ("ADDED" if needs_reg else "OK") + ", handler=" + ("ADDED" if needs_handler else "OK"))

# STEP 4: Verify
with open("ada.py", "r", encoding="utf-8") as f:
    final = f.read()
count = final.count("facebook_status")
print(f"[4/4] ada.py has {count} 'facebook_status' references (need 3+)")

if count >= 3:
    print()
    print("=" * 60)
    print("✅ ALL GOOD - NOW RESTART SERVER: python server.py")
    print("=" * 60)
else:
    print("❌ SOMETHING WRONG - paste this whole output to me")

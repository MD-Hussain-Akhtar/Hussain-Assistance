import os
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
            for sel in ["//div[@role='button' and contains(@aria-label, 'mind')]", "//span[contains(text(), \"What's on your mind\")]"]:
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

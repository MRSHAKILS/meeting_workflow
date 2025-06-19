# create_meeting_app/bot_scripts/google_meet_bot.py

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

def join_meeting(meeting_link: str, bot_name: str):
    # ─── Chrome options ───────────────────────────────────────────────────────────
    options = Options()
    options.add_argument("--use-fake-ui-for-media-stream")     # Auto-allow mic/camera
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--start-maximized")                  # You’ll actually see it

    # ─── Set up Service with webdriver-manager ───────────────────────────────────
    service = Service(ChromeDriverManager().install())
    driver  = webdriver.Chrome(service=service, options=options)

    try:
        # ─── Navigate to Meeting ─────────────────────────────────────────────────
        driver.get(meeting_link)
        print(f"🔗 Navigating to {meeting_link}")
        time.sleep(5)

        # ─── Enter bot’s display name ────────────────────────────────────────────
        wait       = WebDriverWait(driver, 15)
        name_field = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//input[@placeholder='Your name']")))
        name_field.clear()
        name_field.send_keys(bot_name)
        print(f"✍️ Entered name: {bot_name}")

        # ─── Mute mic & camera ────────────────────────────────────────────────────
        try:
            mic_btn = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//button[@aria-label='Turn off microphone']")))
            cam_btn = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//button[@aria-label='Turn off camera']")))
            mic_btn.click(); cam_btn.click()
            print("🤫 Mic & camera disabled")
        except Exception as e:
            print(f"⚠️ Mic/camera skip: {e}")

        # ─── Dismiss overlays ─────────────────────────────────────────────────────
        for btn in driver.find_elements(By.XPATH, "//button[contains(text(), 'Dismiss')]"):
            btn.click()
            print("🚫 Dismissed a pop‑up")

        # ─── Click Join ───────────────────────────────────────────────────────────
        long_wait = WebDriverWait(driver, 30)
        try:
            join_btn = long_wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//span[contains(text(), 'Join now')]")))
        except:
            join_btn = long_wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//span[contains(text(), 'Ask to join')]")))

        driver.execute_script("arguments[0].scrollIntoView(true);", join_btn)
        time.sleep(1)
        driver.execute_script("arguments[0].click();", join_btn)
        print("🚀 Clicked Join/Ask to join")

        # ─── Stay in meeting ───────────────────────────────────────────────────────
        time.sleep(3600)  # 1 hour
    except Exception as err:
        print(f"❌ Bot error: {err}")
        raise
    finally:
        driver.quit()


# ─── Quick test if run directly ────────────────────────────────────────────────
if __name__ == "__main__":
    test_url = "https://meet.google.com/uou-rsvo-epg"
    join_meeting(test_url, "TestBot")

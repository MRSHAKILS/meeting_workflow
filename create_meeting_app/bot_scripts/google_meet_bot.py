from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.webdriver.chrome.options import Options

def join_meeting(meeting_link, bot_name):
    # Set up Chrome options
    options = Options()
    options.add_argument("--use-fake-ui-for-media-stream")  # Auto-allow mic/camera
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--start-maximized")

    driver = webdriver.Chrome(options=options)
    try:
        # Navigate to the meeting link
        driver.get(meeting_link)
        print(f"Navigating to {meeting_link}")
        time.sleep(5)  # Wait for initial page load

        # Wait for the name input field and enter the bot's name
        wait = WebDriverWait(driver, 10)
        name_field = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Your name']")))
        name_field.clear()
        name_field.send_keys(bot_name)
        print(f"Entered name: {bot_name}")

        # Optionally disable microphone and camera
        try:
            mic_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Turn off microphone']")))
            mic_button.click()
            cam_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Turn off camera']")))
            cam_button.click()
            print("Mic and camera disabled")
        except Exception as e:
            print(f"Microphone/camera handling skipped: {e}")

        # Dismiss any overlays or pop-ups
        try:
            dismiss_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'Dismiss')]")
            for button in dismiss_buttons:
                button.click()
                print("Dismissed overlay/pop-up")
        except:
            print("No overlays found to dismiss")

        # Wait for and click "Join now" or "Ask to join"
        wait = WebDriverWait(driver, 30)  # Increased wait time
        try:
            join_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Join now')]")))
        except:
            join_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Ask to join')]")))

        # Ensure the button is visible and clickable
        driver.execute_script("arguments[0].scrollIntoView(true);", join_button)
        time.sleep(1)  # Wait for scroll to complete
        driver.execute_script("arguments[0].click();", join_button)  # Click via JavaScript
        print("Clicked Join/Ask to join button")

        # Stay in the meeting for 1 hour
        time.sleep(3600)
    except Exception as e:
        print(f"Bot error: {str(e)}")
        raise
    finally:
        driver.quit()

# Example usage
if __name__ == "__main__":
    join_meeting("https://meet.google.com/szf-copq-qdf", "ahh")
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
from selenium.webdriver.chrome.options import Options

COMMUNITY_NAME = "AlgoVerse-KPRIT Hackathon"
GROUP_NAME = "Nasscom Blockchain Course Completion"
INVITE_LINK = "https://chat.whatsapp.com/G32WHUNozOEBSAc4hMbluo"

# Load numbers
df = pd.read_csv("numbers.csv")
numbers = df["phone"].astype(str).tolist()

# Prepare logs
added = []
invite_sent = []
failed = []

# Brave browser options (Chromium-based)
options = Options()
options.binary_location = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"

driver = webdriver.Chrome(options=options)
driver.get("https://web.whatsapp.com")

print("Scan QR code and open the group you want to add people to...")
print("You have 60 seconds - open the group and click on the group header to open group info.")
input("Press ENTER when you're ready (group info panel should be open)...")

wait = WebDriverWait(driver, 40)


for number in numbers:
    try:
        # Try adding participant
        driver.find_element(By.XPATH, '//span[text()="Add participant"]').click()
        time.sleep(2)

        search = driver.find_element(By.XPATH, '//input[@type="text"]')
        search.send_keys(number)
        time.sleep(3)

        search.send_keys(Keys.ENTER)
        time.sleep(2)

        driver.find_element(By.XPATH, '//span[text()="Add"]').click()
        time.sleep(10)

        print(f"✅ Added: {number}")
        added.append(number)

    except Exception:
        print(f"⚠️ Cannot add {number}, trying invite link...")

        try:
            # Open personal chat
            driver.get(f"https://wa.me/{number.replace('+', '')}")
            time.sleep(5)

            driver.find_element(By.ID, "action-button").click()
            time.sleep(5)

            driver.find_element(By.XPATH, '//a[contains(@href,"web.whatsapp.com")]').click()
            time.sleep(10)

            message_box = driver.find_element(
                By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]'
            )
            message_box.send_keys(
                f"Hi! This is the link to join the NASSCOM - Algorand Course Completion Group:\n"
                f"Please join the group using this link:\n{INVITE_LINK}"
            )
            message_box.send_keys(Keys.ENTER)

            print(f"📩 Invite sent: {number}")
            invite_sent.append(number)
            time.sleep(12)

        except Exception:
            print(f"❌ Failed completely: {number}")
            failed.append(number)
            time.sleep(8)

# Save logs
pd.DataFrame({"phone": added}).to_csv("added.csv", index=False)
pd.DataFrame({"phone": invite_sent}).to_csv("invite_sent.csv", index=False)
pd.DataFrame({"phone": failed}).to_csv("failed.csv", index=False)

print("\nDONE.")
print(f"Added: {len(added)}")
print(f"Invite sent: {len(invite_sent)}")
print(f"Failed: {len(failed)}")

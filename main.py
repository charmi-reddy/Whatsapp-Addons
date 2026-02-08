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
        # Click "Add" button to open add participant dialog
        add_btn = wait.until(EC.element_to_be_clickable((By.XPATH, '//span[text()="Add"]')))
        add_btn.click()
        time.sleep(2)

        # Find the search input and type the phone number (remove + for search)
        search = wait.until(EC.presence_of_element_located((By.XPATH, '//input[@type="text"]')))
        clean_number = number.replace('+', '').strip()
        search.send_keys(clean_number)
        time.sleep(4)  # Wait for search results

        # Click on the search result (works for unsaved numbers too)
        try:
            # Look for any clickable result in the list
            result = wait.until(EC.element_to_be_clickable((
                By.XPATH, '//div[contains(@class,"_ak8q")]//div[@role="listitem"] | //div[@role="listitem"]//span[contains(text(),"' + clean_number[-10:] + '")]/..'
            )))
            result.click()
            time.sleep(1)
        except:
            # Fallback: try clicking any checkbox or the first result
            try:
                checkbox = driver.find_element(By.XPATH, '//div[@role="checkbox"] | //input[@type="checkbox"]')
                checkbox.click()
            except:
                # Last resort: press Enter
                search.send_keys(Keys.ENTER)
            time.sleep(1)

        # Click the green checkmark button to confirm adding
        time.sleep(1)
        confirm_btn = wait.until(EC.element_to_be_clickable((
            By.XPATH, '//span[@data-icon="checkmark-medium"] | //span[@data-icon="checkmark-light"] | //div[@aria-label="OK"]'
        )))
        confirm_btn.click()
        time.sleep(5)

        # Close any popup by pressing Escape
        try:
            driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
        except:
            pass
        time.sleep(2)

        print(f"✅ Added: {number}")
        added.append(number)

    except Exception as e:
        print(f"⚠️ Cannot add {number}: {e}")
        print("Trying invite link...")
        
        # Press Escape to close any open dialogs
        try:
            driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
            time.sleep(1)
        except:
            pass

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

import time
import asyncio
import websockets
from selenium import webdriver
from selenium.webdriver.common.by import By

# Set up the ChromeDriver with remote debugging enabled
options = webdriver.ChromeOptions()
options.add_argument("--remote-debugging-port=9222")
options.add_experimental_option("prefs", {
    "download.default_directory": "/tmp/",
    "download.prompt_for_download": False,
})

driver = webdriver.Chrome(options=options)

# Open the WellSaid URL with the search query and sp parameter
url = "https://studio.wellsaidlabs.com/dashboard/projects/personal"
driver.get(url)

# Wait for the page to load
time.sleep(1)

# Check if there is a redirect to the login page
if "https://auth.wellsaidlabs.com/login?" in driver.current_url:
    # If redirected to the login page, enter username and password
    username = driver.find_element(By.XPATH, '//*[@id="1-email"]')
    password = driver.find_element(By.XPATH,
                                   '/html/body/div/div/div[2]/form/div/div/div/div[2]/div[2]/span/div/div/div/div/div/div/div/div/div/div/div[2]/div[1]/div/input')
    login_button = driver.find_element(By.XPATH, '//*[@id="wsl-submit-button"]')

    username.send_keys("wianvfi901@munik.edu.pl")
    password.send_keys("at5xp,LRPCf!3/^")
    login_button.click()

    time.sleep(3)

# Remove elements with class names '.MuiPopover-root', '.MuiContainer-root', and '.MuiBackdrop-root'
ad_to_remove = driver.find_element(
    By.CSS_SELECTOR, 'body > div.jss66 > div.jss67.jss68 > div > div > div.MuiBox-root.jss256.jss140 > button')
if ad_to_remove is not None:
    ad_to_remove.click()
    time.sleep(2)

# Find and click on a project link
project_link = driver.find_element(By.CSS_SELECTOR,
                                   '#projects-tabpanel-0 > div > div > div > div > div > div > a')
project_link.click()
time.sleep(4)

# Find the editor element and paste text into it
editor = driver.find_element(By.XPATH, '//*[@id="core-editor"]')
text_to_paste = "This is the text to paste into the editor."
editor.send_keys(text_to_paste)
time.sleep(25)

# Find and click on a button to play the audio
button = driver.find_element(By.XPATH,
                             '//*[@id="page-studio"]/div[5]/div[2]/div/div[1]/div/div/div/div[1]/div/div/div[3]/div[2]/button')
button.click()

# Connect to the Chrome DevTools Protocol using WebSockets
async def cdp_capture_blob():
    uri = "ws://127.0.0.1:9222/devtools/browser"
    async with websockets.connect(uri) as ws:
        # Enable the Network domain
        await ws.send('{"id": 1, "method": "Network.enable", "params": {}}')

        blob_data = b''

        def process_cdp_message(message):
            nonlocal blob_data
            if 'params' in message and 'response' in message['params']:
                response = message['params']['response']
                if 'url' in response and response['url'].startswith("blob:"):
                    blob_url = response['url']
                    print(f"Captured Blob URL: {blob_url}")
                    blob_data += response['response']['body'].encode('utf-8')

        async for message in ws:
            process_cdp_message(message)

        # Disable the Network domain
        await ws.send('{"id": 2, "method": "Network.disable", "params": {}}')

        # Save the captured Blob data as an MP3 file
        with open("output.mp3", "wb") as mp3_file:
            mp3_file.write(blob_data)

asyncio.run(cdp_capture_blob())

time.sleep(15)
driver.quit()

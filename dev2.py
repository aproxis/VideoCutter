import time
import asyncio
import websockets
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import requests



# Set up the ChromeDriver
options = webdriver.ChromeOptions()
options.add_argument("--remote-debugging-port=9222")
driver = webdriver.Chrome(options=options)

driver.get("https://google.com")  # Replace with your target URL


# Send a request to the Chrome DevTools Protocol
def is_debugging_enabled():
    response = requests.get('http://localhost:9222/json')
    targets = response.json()
    
    for target in targets:
        if 'type' in target and target['type'] == 'page':
            # The 'type' is 'page' for tabs associated with web pages
            # You can also check other properties to identify the tab you're interested in
            return True
    
    return False

# Check if debugging mode is active
if is_debugging_enabled():
    print("Debugging mode is active")
else:
    print("Debugging mode is not active")


time.sleep(3)  # Adjust the wait time as needed

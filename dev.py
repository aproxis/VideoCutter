import time
import asyncio
import websockets
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

# Set up the ChromeDriver
options = webdriver.ChromeOptions()
options.add_argument("--remote-debugging-port=9222")
driver = webdriver.Chrome(options=options)

# Start a debugging session with chromewebdriver (Selenium 4)
async def main():
    async with websockets.connect("ws://127.0.0.1:9222/devtools/browser") as ws:
        target = chromedebug.Session(ws)
        await target.send("Target.createTarget", {"url": "about:blank"})  # Create a new tab
        await target.attach()

        # Open your desired URL
        driver.get("https://example.com")  # Replace with your target URL

        # Wait for the page to load
        time.sleep(5)  # Adjust the wait time as needed

        # Trigger Blob Stream (perform the actions that trigger the Blob stream)
        # ...

        # Capture the Blob
        # Add a listener for Network.webSocketFrameSent
        async def on_websocket_frame_sent(msg):
            if 'params' in msg and 'response' in msg['params']:
                response = msg['params']['response']
                if 'url' in response and response['url'].startswith("blob:"):
                    blob_url = response['url']
                    print(f"Captured Blob URL: {blob_url}")

        # Add the listener for Network.webSocketFrameSent
        target.on("Network.webSocketFrameSent", on_websocket_frame_sent)

        # Sleep or wait until the Blob data has been captured
        time.sleep(10)  # Adjust the wait time as needed

        # Clean up and close the browser
        driver.quit()

asyncio.run(main())

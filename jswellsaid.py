import time
import asyncio
from pyppeteer import launch

async def puppeteer_capture_blob():
    # Launch the Puppeteer browser with a custom user agent
    # browser = await launch(headless=False)

    # Define the path to the Google Chrome executable on your system
    chrome_executable_path = '/Applications/Google Chrome for Testing.app'

    # Launch Puppeteer with the custom Chrome executable path
    browser = await launch(
        headless=False,  # Set to True for headless mode
        executablePath=chrome_executable_path,
    )

    page = await browser.newPage()

    # Set the user agent to simulate a MacBook Safari
    await page.setUserAgent('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36')

    # Navigate to the URL
    await page.goto("https://studio.wellsaidlabs.com/dashboard/projects/personal")

    # Wait for the page to load completely
    # await page.waitForSelector('.MuiButtonBase-root.MuiIconButton-root.MuiIconButton-colorInherit')
    await asyncio.sleep(5)

    # Check if there is a redirect to the login page
    if "https://auth.wellsaidlabs.com/login?" in page.url:
        # If redirected to the login page, enter username and password
        await page.type('input[name="email"]', "wianvfi901@munik.edu.pl")
        await page.type('input[name="password"]', "at5xp,LRPCf!3/^")
        await page.click('button[type="submit"]')

        # Wait for login and redirect to complete
        await page.waitForNavigation()
        await asyncio.sleep(5)

    cookie = {
        'name': 'appSession',
        'value': 'eyJhbGciOiJkaXIiLCJlbmMiOiJBMjU2R0NNIiwiaWF0IjoxNjk4MjQ0NTI5LCJ1YXQiOjE2OTgyNzg1NzMsImV4cCI6MTY5ODM2NDk3M30',
        'domain': 'studio.wellsaidlabs.com',  # Replace with the domain you want to set the cookie for
        'path': '/',  # Specify the path for the cookie
        'expires': int(time.time()) + 3600,  # Set the expiration time (in seconds since epoch)
    }

    # Set the cookie for the current page
    await page.setCookie(cookie)

    # Remove elements with class names '.MuiPopover-root', '.MuiContainer-root', and '.MuiBackdrop-root'
    try:
        await page.click('button.MuiButtonBase-root.MuiIconButton-root.MuiIconButton-colorInherit')
    except:
        pass

    # Scroll down to the bottom of the page for full loading
    await page.evaluate('window.scrollTo(0, document.body.scrollHeight);')

    # Find and click on a project link
    await page.waitForSelector('#projects-tabpanel-0 > div > div > div > div > div > div > a')
    await page.click('#projects-tabpanel-0 > div > div > div > div > div > div > a')

    # Wait for the editor element to be present
    editor = await page.waitForSelector('#core-editor')

    # Find the editor element and paste text into it
    text_to_paste = "This is the text to paste into the editor."
    await editor.type(text_to_paste)

    # Find and click on a button to play the audio
    await page.click('#page-studio > div.MuiBox-root.jss505 > div > div > div.MuiBox-root.jss504 > button')

    # Capture Blob using CDP
    cdp_session = await page.target.createCDPSession()

    # Enable the Network domain
    await cdp_session.send('Network.enable')

    blob_data = b''

    def process_cdp_message(msg):
        nonlocal blob_data
        if 'url' in msg and msg['url'].startswith('blob:'):
            print(f"Captured Blob URL: {msg['url']}")
            blob_data += msg['response']['body'].encode('utf-8')

    cdp_session.on('Network.responseReceived', process_cdp_message)

    # Wait for some time to capture the Blob data
    await asyncio.sleep(10)

    # Disable the Network domain
    await cdp_session.send('Network.disable')

    # Save the captured Blob data as an MP3 file
    with open("output.mp3", "wb") as mp3_file:
        mp3_file.write(blob_data)

    # Close Puppeteer
    await browser.close()

asyncio.run(puppeteer_capture_blob())

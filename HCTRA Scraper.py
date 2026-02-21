from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright
import time

def runScraper():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=['--disable-blink-features=AutomationControlled']
        )
        
        page = browser.new_page()
        page.goto('https://www.hctra.org/Login')
        
        time.sleep(3)

        login(page)
    
        loadTolls(page)

        browser.close()

def login(page):
    try:
        page.fill("#usernameTxtBox", "tollaid03")
        page.fill("#passwordTxtBox", "37bq$G8*VkOFZk0")
        page.click("#desktopUiViewRoot > div > login-component > main > page-centered-container > main > div > div:nth-child(2) > card-container > div > div > section > section > form > div.u-spacing__buttonToField--marginTop > button", force=True)
        time.sleep(2)
        print("Login done!")

    except Exception as e:
        print(f"Error during login: {e}")

def loadTolls(page):
    try:
        today = datetime.now()
        last_datetime = today.strftime("%m/%d/%Y")

        time.sleep(3)
        page.click("#desktopUiViewRoot > div > account-dashboard-frame-component > page-centered-dash-container > main > div > section > div.cardsContainer > div.recentTransactionsContainer > card-dash-container > div > div > account-dashboard-recent-transactions-component > div > div > div.u-spacing--widthFill > a")

        time.sleep(5)

        with page.expect_download(timeout=60000) as download_info:
            page.click("text= Excel")

        time.sleep(5)
        download = download_info.value
        file_name = f"HCTRA_Transacts_{last_datetime.replace('/','')}.xls"
        download.save_as(f"C:/Users/limit/Downloads/{file_name}")
        print(f"Report downloaded in: {download.path()}")

    except Exception as e:
        print("An exception happened: {e}")

runScraper()
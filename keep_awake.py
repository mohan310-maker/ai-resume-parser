"""
keep_awake.py
Visits the deployed Streamlit app in a real headless browser to keep it from
going to sleep (Streamlit Community Cloud sleeps apps after 12 hours of no
traffic). Run on a schedule via GitHub Actions - see
.github/workflows/keep-awake.yml
"""

import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

APP_URL = "https://ai-resume-parser-m.streamlit.app"

options = Options()
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--window-size=1280,800")

driver = webdriver.Chrome(options=options)
try:
    driver.get(APP_URL)
    # Give the app time to fully load and establish its WebSocket
    # connection - a bare page fetch alone may not count as real traffic.
    time.sleep(20)
    print(f"Visited app successfully. Page title: {driver.title!r}")
finally:
    driver.quit()

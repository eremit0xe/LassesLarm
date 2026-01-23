import requests
from bs4 import BeautifulSoup
import hashlib
import os

URL = "https://www.rtjamtland.se/larm/2026/01/"
STATE_FILE = "last_alarm.txt"

html = requests.get(URL, timeout=15).text
soup = BeautifulSoup(html, "html.parser")

alarms = soup.select("div.alarms-container ul > li")
if not alarms:
    exit(0)

latest = alarms[0].get_text(" ", strip=True)
latest_hash = hashlib.sha256(latest.encode()).hexdigest()

previous = ""
if os.path.exists(STATE_FILE):
    previous = open(STATE_FILE).read().strip()

if latest_hash != previous:
    open(STATE_FILE, "w").write(latest_hash)
    print(f"NEW::{latest}")
else:
    print("NO_CHANGE")

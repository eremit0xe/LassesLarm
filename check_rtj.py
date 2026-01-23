import requests
from bs4 import BeautifulSoup
import hashlib
import os

# Telegram settings
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

# URL att kolla
URL = "https://www.rtjamtland.se/larm/2026/01/"

STATE_FILE = "last_alarm.txt"

# Hämta sidan
res = requests.get(URL)
res.raise_for_status()
soup = BeautifulSoup(res.text, "html.parser")

# Hitta larmen (ändra detta CSS-selektor efter behov)
alarms = soup.select(".larm")  # <-- kontrollera att det matchar div / klass på sidan
if not alarms:
    print("Ingen larm hittade på sidan.")
    exit()

# Ta det senaste larmet
latest = alarms[0].get_text(" ", strip=True)
latest_hash = hashlib.sha256(latest.encode()).hexdigest()

# Läs tidigare hash
previous_hash = ""
if os.path.exists(STATE_FILE):
    with open(STATE_FILE, "r") as f:
        previous_hash = f.read().strip()

# Skicka notis om nytt
if latest_hash != previous_hash:
    msg = f"🚨 NYTT LARM:\n{latest}"
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": msg}
    r = requests.post(url, data=payload)
    if r.ok:
        print(f"Skickade notis: {latest}")
    else:
        print(f"Fel vid Telegram: {r.text}")

# Uppdatera state-filen
with open(STATE_FILE, "w") as f:
    f.write(latest_hash)

import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime

BOT_TOKEN = os.environ['BOT_TOKEN']
CHAT_ID = os.environ['CHAT_ID']

def get_latest_alarm():
    # Bygg URL baserat pa nuvarande ar och manad
    now = datetime.now()
    url = f"https://www.rtjamtland.se/larm/{now.year}/{now.month:02d}/"
    
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Hitta main-elementet forst
    main = soup.find('main', id='primary')
    
    if main:
        # Hitta ul i main
        ul = main.find('ul')
        if ul:
            # Hitta forsta li i denna ul
            first_alarm = ul.find('li')
            
            if first_alarm:
                # Hitta lanken i h2
                h2 = first_alarm.find('h2')
                if h2:
                    link = h2.find('a')
                    if link and link.get('href'):
                        alarm_url = link.get('href')
                        alarm_title = link.get_text(strip=True)
                        
                        # Hitta info i p-taggen
                        p = first_alarm.find('p')
                        alarm_info = p.get_text(strip=True) if p else ""
                        
                        alarm_text = f"{alarm_title}\n{alarm_info}"
                        
                        return alarm_url, alarm_text
    
    return None, None

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"}
    response = requests.post(url, data=data)
    return response.json()

def main():
    # Las tidigare URL
    try:
        with open('last_alarm.txt', 'r') as f:
            last_url = f.read().strip()
    except FileNotFoundError:
        last_url = ""
    
    print(f"Tidigare URL: '{last_url}'")
    
    # Hamta nytt larm
    alarm_url, alarm_text = get_latest_alarm()
    
    print(f"Hittad URL: '{alarm_url}'")
    print(f"Larmtext: {alarm_text}")
    
    if alarm_url and alarm_url != last_url:
        # Formatera meddelandet
        message = f"🚨 <b>Nytt larm från RTJ Jämtland</b>\n\n{alarm_text}\n\n🔗 <a href='{alarm_url}'>Läs mer</a>"
        result = send_telegram(message)
        
        # Spara ny URL
        with open('last_alarm.txt', 'w') as f:
            f.write(alarm_url)
        
        print(f"✅ Nytt larm skickat: {alarm_url}")
        print(f"Telegram response: {result}")
    else:
        print("ℹ️ Inget nytt larm")

if __name__ == "__main__":
    main()

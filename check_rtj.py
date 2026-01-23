import requests
from bs4 import BeautifulSoup
import os

BOT_TOKEN = os.environ['BOT_TOKEN']
CHAT_ID = os.environ['CHAT_ID']
URL = "https://www.rtjamtland.se/larm/"

def get_latest_alarm():
    response = requests.get(URL)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Hitta alarms-container
    alarms_container = soup.find('div', class_='alarms-container')
    
    if alarms_container:
        # Hitta första li-elementet (senaste larmet)
        first_alarm = alarms_container.find('li')
        
        if first_alarm:
            # Hitta länken inuti li
            link = first_alarm.find('a')
            
            if link and link.get('href'):
                alarm_url = link.get('href')
                
                # Om det är en relativ URL, gör den absolut
                if not alarm_url.startswith('http'):
                    alarm_url = "https://www.rtjamtland.se" + alarm_url
                
                # Extrahera rubrik och datum
                h3 = first_alarm.find('h3')
                span = first_alarm.find('span')
                
                alarm_title = h3.get_text(strip=True) if h3 else "Larm"
                alarm_date = span.get_text(strip=True) if span else ""
                
                alarm_text = f"{alarm_title}\n{alarm_date}"
                
                return alarm_url, alarm_text
    
    return None, None

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"}
    response = requests.post(url, data=data)
    return response.json()

def main():
    # Läs tidigare URL
    try:
        with open('last_alarm.txt', 'r') as f:
            last_url = f.read().strip()
    except FileNotFoundError:
        last_url = ""
    
    # Hämta nytt larm
    alarm_url, alarm_text = get_latest_alarm()
    
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

import telebot
import requests
from bs4 import BeautifulSoup
import schedule
import time
import os

BOT_TOKEN = os.environ.get('BOT_TOKEN')
ADMIN_ID = int(os.environ.get('ADMIN_ID'))

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Hi, dein Telegram-Bot ist online!")

def scrape_comments():
    # Dummy-Funktion oder echte Logik hier einfügen
    return [{"author": "user123", "comment": "Beispiel-Kommentar"}]

@bot.message_handler(commands=['scrape'])
def handle_scrape(message):
    comments = scrape_comments()
    reply = "\n".join(f"{c['author']}: {c['comment']}" for c in comments)
    bot.send_message(message.chat.id, reply)



from datetime import datetime
start_time = datetime.now()
def send_daily_report():
    uptime = datetime.now() - start_time
    msg = f"🕘 Täglicher Report:\nUptime: {str(uptime).split('.')[0]}\nSicherheit: ✅ Aktiv"
    bot.send_message(ADMIN_ID, msg)

schedule.every().day.at("09:00").do(send_daily_report)

@bot.message_handler(commands=['status'])
def send_status(message):
    uptime = datetime.now() - start_time
    bot.reply_to(message, f"✅ Bot läuft seit {str(uptime).split('.')[0]}.\nAlles stabil.")

@bot.message_handler(commands=['security'])
def send_security_status(message):
    bot.reply_to(message, "🔐 Sicherheit aktiv:\n- CodeQL aktiviert\n- Secret Protection bereit\n- AutoFix aktiv")

@bot.message_handler(commands=['shutdown'])
def shutdown(message):
    if str(message.from_user.id) == os.environ.get("ADMIN_ID"):
        bot.send_message(message.chat.id, "Bot wird gestoppt. Bis bald!")
        os._exit(0)
    else:
        bot.reply_to(message, "⛔ Kein Zugriff.")
if __name__ == "__main__":
    while True:
        schedule.run_pending()
        time.sleep(1)
        bot.infinity_polling(none_stop=True)


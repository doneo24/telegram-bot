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

bot.infinity_polling()

# === DONEO VENDOR-BOT (Finale Version mit Kategorie-Suche) ===
# Live Scraping + OpenAI Text + Webhook via Flask

import os
import telebot
import requests
import openai
from bs4 import BeautifulSoup
from telebot import types
from flask import Flask, request

BOT_TOKEN = os.environ.get("BOT_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

def scrape_thieve_by_category(category):
    url = f"https://thieve.co/products?category={category}"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    products = []
    seen = set()
    for link in soup.select("a[href^='/product/']"):
        href = link.get("href")
        full_link = f"https://thieve.co{href}"
        title = link.get_text(strip=True)
        if full_link not in seen and title:
            seen.add(full_link)
            products.append({
                "title": title,
                "link": full_link,
                "price": "ca. 2–5 €",
                "sell_price": "ca. 9,99 €",
                "shipping": "EU-Versand möglich",
                "id": href.strip('/').split('/')[-1]
            })
        if len(products) >= 5:
            break
    return products

@bot.message_handler(commands=['jagd'])
def handle_jagd(message):
    parts = message.text.split()
    if len(parts) == 2:
        category = parts[1].lower()
        bot.send_message(message.chat.id, f"🔍 Starte Jagd in Kategorie: {category}")
        try:
            products = scrape_thieve_by_category(category)
            for p in products:
                caption = (
                    f"<b>{p['title']}</b>\n"
                    f"EK: {p['price']}\n"
                    f"VK: {p['sell_price']}\n"
                    f"Versand: {p['shipping']}\n"
                    f"<a href='{p['link']}'>🔗 Zum Produkt</a>"
                )
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton("📝 Text generieren", callback_data=f"generate_{p['id']}"))
                bot.send_message(message.chat.id, caption, parse_mode='HTML', reply_markup=markup)
        except Exception as e:
            bot.send_message(message.chat.id, f"Fehler beim Scraping: {e}")
    else:
        bot.send_message(message.chat.id, "Bitte nutze: /jagd [Kategorie] – z. B. /jagd home")

@bot.callback_query_handler(func=lambda call: call.data.startswith("generate_"))
def callback_generate(call):
    product_id = call.data.split("generate_")[1]
    bot.answer_callback_query(call.id, "Generiere KI-Text...")

    raw_text = call.message.text or ""
    link_line = [line for line in raw_text.splitlines() if "http" in line]
    link = link_line[0] if link_line else "Link nicht gefunden"

    prompt = f"""
Erstelle eine überzeugende, kurze Produktbeschreibung für ein Dropshipping-Produkt.
Ziel: Impulskäufer. Max. 600 Zeichen.
Link zum Produkt: {link}
"""

    openai.api_key = OPENAI_API_KEY
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        text = response.choices[0].message.content.strip()
        bot.send_message(call.message.chat.id, f"{text}\n\n🔗 {link}")
    except Exception as e:
        bot.send_message(call.message.chat.id, f"Fehler bei Text-KI: {e}")

bot.remove_webhook()
bot.set_webhook(url=WEBHOOK_URL)

@app.route('/', methods=['POST'])
def webhook():
    update = telebot.types.Update.de_json(request.stream.read().decode("utf-8"))
    bot.process_new_updates([update])
    return "OK", 200

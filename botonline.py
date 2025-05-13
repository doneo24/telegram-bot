# VENDOR-BOT: /jagd all mit Live-Scraping von thieve.co

import telebot
import requests
from bs4 import BeautifulSoup
from telebot import types
import os

# === KONFIGURATION ===
BOT_TOKEN = os.environ.get("BOT_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

bot = telebot.TeleBot(BOT_TOKEN)

# === SCRAPER ===
def scrape_thieve_products():
    url = "https://thieve.co/products?sort=trending"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    products = []
    seen = set()
    for link in soup.select("a[href*='/product/']"):
        href = link.get("href")
        full_link = f"https://thieve.co{href}"
        title = link.get_text(strip=True)
        if full_link not in seen and title:
            seen.add(full_link)
            products.append({
                "title": title,
                "link": full_link,
                "price": "ca. 2–5 € (AliExpress geschätzt)",
                "sell_price": "ca. 9,99 €",
                "shipping": "EU-Versand möglich (AliExpress prüfen)",
                "id": href.split("/")[-1]
            })
        if len(products) >= 5:
            break
    return products

# === JAGD COMMAND ===
@bot.message_handler(commands=['jagd'])
def handle_jagd(message):
    if "all" in message.text.lower():
        bot.send_message(message.chat.id, "🦊 Starte Jagd auf Thieve-Produkte...")
        try:
            products = scrape_thieve_products()
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

# === CALLBACK: TEXT GENERIEREN ===
@bot.callback_query_handler(func=lambda call: call.data.startswith("generate_"))
import openai

@bot.callback_query_handler(func=lambda call: call.data.startswith("generate_"))
def callback_generate(call):
    product_id = call.data.split("generate_")[1]
    bot.answer_callback_query(call.id, "Generiere KI-Text...")

    # Hier holen wir die Originalnachricht raus (da ist der Produkttext & Link schon drin)
    raw_text = call.message.text or ""
    link_line = [line for line in raw_text.splitlines() if "http" in line]
    link = link_line[0] if link_line else "Produktlink nicht gefunden"

    prompt = f"""
Erstelle eine überzeugende, kurze Produktbeschreibung für ein Dropshipping-Produkt.
Verkaufe es an impulsive Käufer. Bleibe unter 600 Zeichen.

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
        bot.send_message(call.message.chat.id, f"Fehler bei der Textgenerierung: {e}")


# === BOT START ===


bot.remove_webhook()
bot.set_webhook(url=WEBHOOK_URL)
from flask import Flask, request

app = Flask(__name__)

WEBHOOK_URL = "https://dein-bot.onrender.com/"  # <- Ersetze mit deiner echten Render-URL

bot.remove_webhook()
bot.set_webhook(url=WEBHOOK_URL)

@app.route('/', methods=['POST'])
def webhook():
    update = telebot.types.Update.de_json(request.stream.read().decode("utf-8"))
    bot.process_new_updates([update])
    return "OK", 200


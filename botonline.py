# Telegram Bot mit Webhook statt Polling (409-frei)
import telebot
import os
from flask import Flask, request

BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = os.environ.get("ADMIN_ID")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")  # z. B. https://doneo24.onrender.com/

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# === Telegram-Befehle ===
@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.reply_to(message, "Hi, ich bin dein Doneo24-Bot – jetzt über Webhook online!")

@bot.message_handler(commands=['status'])
def handle_status(message):
    bot.reply_to(message, "✅ Bot läuft stabil über Webhook!")

import requests

@bot.message_handler(commands=['tiktokstats'])
def handle_tiktokstats(message):
    try:
        username = message.text.split(" ")[1]
    except IndexError:
        bot.reply_to(message, "❗ Bitte gib einen TikTok-Benutzernamen an. Beispiel:\n`/tiktokstats charlidamelio`", parse_mode="Markdown")
        return

    bot.reply_to(message, f"🔍 TikTok-Daten für @{username} werden geladen...")

    # Direkte Anfrage an die TokAPI
    url = f"https://tokapi-mobile-version.vercel.app/api/user/{username}"
    try:
        response = requests.get(url)
        data = response.json()

        user = data.get("userInfo", {})

        stats = (
            f"📊 TikTok Stats für @{username}\n"
            f"- 👥 Follower: {user.get('followerCount', '—')}\n"
            f"- ❤️ Likes: {user.get('heart', '—')}\n"
            f"- 🎥 Videos: {user.get('video', '—')}\n"
            f"- 📝 Bio: {user.get('signature', '—')}"
        )
        bot.send_message(message.chat.id, stats)

    except Exception as e:
        bot.reply_to(message, f"🚫 Fehler bei TikTok-Anfrage: {str(e)}")




# === Webhook-Endpunkt ===
@app.route("/" + BOT_TOKEN, methods=['POST'])
def webhook():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "", 200

# === Setup Webhook ===
@app.route("/")
def index():
    return "Webhook läuft!", 200

if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL + BOT_TOKEN)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

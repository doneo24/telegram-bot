import os
import telebot
from flask import Flask, request

BOT_TOKEN = os.environ.get("BOT_TOKEN")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")  # z. B. https://dein-bot.onrender.com/

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# Telegram-Befehle
@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.reply_to(message, "Hi, ich bin dein Doneo24-Bot – jetzt über Webhook online!")

@bot.message_handler(commands=['status'])
def handle_status(message):
    bot.reply_to(message, "✅ Bot läuft stabil über Webhook!")

# Webhook-Endpunkt
@app.route("/" + BOT_TOKEN, methods=['POST'])
def webhook():
    update = telebot.types.Update.de_json(request.get_data().decode("utf-8"))
    bot.process_new_updates([update])
    return "", 200

@app.route("/")
def index():
    return "Bot läuft.", 200

if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL + BOT_TOKEN)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

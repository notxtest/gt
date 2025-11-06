from pyrogram import Client
from config import API_ID, API_HASH, BOT_TOKEN
import logging
from handlers import register_all_handlers
import threading
import os
from flask import Flask

# ✅ Uptime Robot ke liye Flask server
web_app = Flask(__name__)

@web_app.route('/')
def home():
    return "🤖 File Store Bot is Alive!"

@web_app.route('/health')
def health():
    return "OK"

# ✅ Background mein web server start karo
def start_web_server():
    port = int(os.environ.get("PORT", 5000))
    web_app.run(host='0.0.0.0', port=port)

# ✅ Server ko background thread mein chalao
server_thread = threading.Thread(target=start_web_server)
server_thread.daemon = True
server_thread.start()

logging.basicConfig(level=logging.INFO)

app = Client(
    "file_store_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

register_all_handlers(app)

print("🤖 File Store Bot is starting...")
print("✅ Uptime Robot support added!")

# ✅ Bot start karo
app.run()
print("🤖 File Store Bot started successfully!")
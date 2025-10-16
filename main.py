# ============================================================
# Group Manager Bot
# Author: Notxkrishna (https://github.com/notxkrishnaa) 
# Support: https://t.me/
# Channel: https://t.me/
# License: Private-source (keep credits, no resale)
# ============================================================

from pyrogram import Client
from config import API_ID, API_HASH, BOT_TOKEN
import logging
from handlers import register_all_handlers
from db import db

logging.basicConfig(level=logging.INFO)

app = Client(
    "group_manger_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

register_all_handlers(app)

print("Bot is starting... ")

app.run()

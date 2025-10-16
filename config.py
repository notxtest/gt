# ==========================================================
# Group Manager Bot
# Author: notxkrishna (https://github.com/notxkrishnaa)
# Support: https://t.me/
# Channel: https://t.me/
# License: Private-source (keep credits, no resale)
# ==========================================================

import os

# Required configurations with default values
API_ID = int(os.getenv("API_ID", 23640310))
API_HASH = os.getenv("API_HASH", "079f8339732e35e032a64ee020e0b90b")
BOT_TOKEN = os.getenv("BOT_TOKEN", "8021675724:AAGjIVhXqfJkEdu5cVdyIEaHVC5mglns9_U")
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://rj5706603:O95nvJYxapyDHfkw@cluster0.fzmckei.mongodb.net/?retryWrites=true&w=majority")
DB_NAME = os.getenv("DB_NAME", "Cluster0")

# Owner and bot details
OWNER_ID = int(os.getenv("OWNER_ID", 7171541681))
BOT_USERNAME = os.getenv("BOT_USERNAME", "Alltestworkingbot")

# Links and visuals
SUPPORT_GROUP = os.getenv("SUPPORT_GROUP", "https://t.me/")
UPDATE_CHANNEL = os.getenv("UPDATE_CHANNEL", "https://t.me/")
START_IMAGE = os.getenv("START_IMAGE", "https://graph.org/file/8d63d03924571351497a6-33a4c24198b5d9e254.jpg")

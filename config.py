import os

# ==========================================================
# 🔑 TELEGRAM API CREDENTIALS
# ==========================================================
API_ID = int(os.getenv("API_ID", 23640310))
API_HASH = os.getenv("API_HASH", "079f8339732e35e032a64ee020e0b90b")

# ==========================================================
# 🤖 PRIMARY BOT CONFIGURATION
# ==========================================================
OWNER_ID = 7171541681
BOT_TOKEN = os.getenv("BOT_TOKEN")  # Primary bot token
BOT_NAME = "Anime File Store"
CREATOR_USERNAME = "@YourCreatorUsername"
OWNER_USERNAME = "@YourOwnerUsername"
START_IMAGE = "https://telegra.ph/file/your-start-image.jpg"  # Default image

# ==========================================================
# 🗄️ DATABASE CONFIGURATION
# ==========================================================
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://rj5706603:O95nvJYxapyDHfkw@cluster0.fzmckei.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
DB_NAME = os.getenv("DB_NAME", "file_store_bot")
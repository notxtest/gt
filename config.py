import os

# ==========================================================
# 🔑 TELEGRAM API CREDENTIALS
# ==========================================================
API_ID = int(os.getenv("API_ID", 12345678))
API_HASH = os.getenv("API_HASH", "your_api_hash_here")

# ==========================================================
# 🤖 PRIMARY BOT CONFIGURATION
# ==========================================================
BOT_TOKEN = os.getenv("BOT_TOKEN")  # Primary bot token
BOT_NAME = "Anime File Store"
CREATOR_USERNAME = "@YourCreatorUsername"
OWNER_USERNAME = "@YourOwnerUsername"
START_IMAGE = "https://telegra.ph/file/your-start-image.jpg"  # Default image

# ==========================================================
# 🗄️ DATABASE CONFIGURATION
# ==========================================================
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "file_store_bot")

# ==========================================================
# ⚙️ BOT SETTINGS
# ==========================================================
MAX_BOTS = 50  # Maximum 50 bots allowed
SUPPORTED_FORMATS = ['mp4', 'mkv', 'avi', 'mov', 'wmv', 'flv', 'webm']
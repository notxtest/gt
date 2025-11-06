import os

# ==========================================================
# 🔑 TELEGRAM API CREDENTIALS
# ==========================================================
API_ID = int(os.getenv("API_ID", 12345678))
API_HASH = os.getenv("API_HASH", "your_api_hash_here")

# ==========================================================
# 👑 BOT OWNER CONFIGURATION
# ==========================================================
BOT_OWNER_ID = int(os.getenv("BOT_OWNER_ID", 123456789))  # Your Telegram ID
BOT_TOKEN = os.getenv("BOT_TOKEN")  # Primary bot token

# ==========================================================
# ⚙️ DEFAULT BOT SETTINGS
# ==========================================================
DEFAULT_BOT_NAME = "Anime File Store"
DEFAULT_CREATOR = "@CreatorUsername" 
DEFAULT_OWNER = "@OwnerUsername"
DEFAULT_START_IMAGE = "https://telegra.ph/file/default-start-image.jpg"

# ==========================================================
# 🗄️ DATABASE CONFIGURATION
# ==========================================================
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "file_store_bot")

# ==========================================================
# ⚡ BOT LIMITS
# ==========================================================
MAX_BOTS = 50
MAX_FILES_PER_BOT = 10000
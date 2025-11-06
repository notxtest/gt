import motor.motor_asyncio
from config import MONGO_URI, DB_NAME, MAX_BOTS
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)

try:
    client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
    db = client[DB_NAME]
    logging.info("✅ MongoDB connected!")
except Exception as e:
    logging.error(f"❌ MongoDB error: {e}")

# ==========================================================
# 🤖 BOT MANAGEMENT SYSTEM
# ==========================================================

async def add_bot_to_db(bot_token: str, bot_username: str, added_by: int, bot_name: str = None, creator: str = None, owner: str = None, start_image: str = None):
    """New bot add karega database mein"""
    
    # Check if maximum limit reached
    total_bots = await db.bots.count_documents({})
    if total_bots >= MAX_BOTS:
        return False, "❌ Maximum bot limit reached! (50 bots max)"
    
    # Check if bot already exists
    existing_bot = await db.bots.find_one({
        "$or": [
            {"bot_token": bot_token},
            {"bot_username": bot_username}
        ]
    })
    
    if existing_bot:
        return False, "❌ Bot already exists in database!"
    
    # Add new bot
    bot_data = {
        "bot_token": bot_token,
        "bot_username": bot_username,
        "bot_name": bot_name or "Anime File Store",
        "creator": creator or "@Creator",
        "owner": owner or "@Owner",
        "start_image": start_image or "https://telegra.ph/file/default-start-image.jpg",
        "added_by": added_by,
        "added_at": datetime.now(),
        "is_active": True,
        "files_count": 0,
        "users_count": 0
    }
    
    await db.bots.insert_one(bot_data)
    return True, "✅ Bot added successfully!"

async def remove_bot_from_db(bot_username: str, removed_by: int):
    """Bot remove karega database se"""
    result = await db.bots.delete_one({"bot_username": bot_username})
    if result.deleted_count > 0:
        # Bot ke saare files bhi delete karo
        await db.files.delete_many({"bot_username": bot_username})
        return True, "✅ Bot removed successfully!"
    return False, "❌ Bot not found!"

async def get_bot_by_token(bot_token: str):
    """Bot details get karega token se"""
    return await db.bots.find_one({"bot_token": bot_token})

async def get_bot_by_username(bot_username: str):
    """Bot details get karega username se"""
    return await db.bots.find_one({"bot_username": bot_username})

async def get_all_bots():
    """Saare active bots get karega"""
    cursor = db.bots.find({"is_active": True})
    return await cursor.to_list(length=MAX_BOTS)

async def update_bot_settings(bot_username: str, settings: dict):
    """Bot ki settings update karega"""
    await db.bots.update_one(
        {"bot_username": bot_username},
        {"$set": settings}
    )

async def is_bot_owner(user_id: int, bot_username: str):
    """Check karega if user is bot owner"""
    bot = await db.bots.find_one({"bot_username": bot_username})
    if bot:
        return bot.get("added_by") == user_id
    return False

# ==========================================================
# 📊 BOT STATS SYSTEM
# ==========================================================

async def get_bot_stats(bot_username: str):
    """Bot ke stats get karega"""
    stats_data = await db.bot_stats.find_one({"bot_username": bot_username})
    if stats_data:
        return stats_data
    
    # Default stats agar nahi hai to
    default_stats = {
        "bot_username": bot_username,
        "force_sub_count": 3,
        "admin_count": 3,
        "banned_users": 1,
        "auto_delete": "ᴇɴᴀʙʟᴇᴅ",
        "protect_content": "ᴅɪsᴀʙʟᴇᴅ",
        "hide_caption": "ᴅɪsᴀʙʟᴇᴅ",
        "channel_button": "ᴅɪsᴀʙʟᴇᴅ",
        "request_fsub": "ᴇɴᴀʙʟᴇᴅ",
        "total_files": 0,
        "total_users": 0
    }
    return default_stats

async def update_bot_stats(bot_username: str, stats: dict):
    """Bot stats update karega"""
    await db.bot_stats.update_one(
        {"bot_username": bot_username},
        {"$set": stats},
        upsert=True
    )

# ==========================================================
# 📁 FILE STORAGE SYSTEM
# ==========================================================

async def save_file(bot_username: str, file_data: dict):
    """File save karega with bot username"""
    file_data["bot_username"] = bot_username
    file_data["uploaded_at"] = datetime.now()
    
    await db.files.insert_one(file_data)
    
    # Bot ke file count update karo
    await db.bots.update_one(
        {"bot_username": bot_username},
        {"$inc": {"files_count": 1}}
    )

async def get_bot_files(bot_username: str, limit=50):
    """Specific bot ki files get karega"""
    cursor = db.files.find({"bot_username": bot_username}).sort("uploaded_at", -1).limit(limit)
    return await cursor.to_list(length=limit)

async def search_bot_files(bot_username: str, query: str):
    """Specific bot ki files search karega"""
    cursor = db.files.find({
        "bot_username": bot_username,
        "$or": [
            {"file_name": {"$regex": query, "$options": "i"}},
            {"caption": {"$regex": query, "$options": "i"}}
        ]
    }).sort("uploaded_at", -1).limit(50)
    return await cursor.to_list(length=50)

async def get_file_by_id(file_id: str, bot_username: str):
    """File get karega ID se"""
    return await db.files.find_one({"file_id": file_id, "bot_username": bot_username})
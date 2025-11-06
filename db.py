import motor.motor_asyncio
from config import MONGO_URI, DB_NAME
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
# 👤 USER MANAGEMENT SYSTEM
# ==========================================================

async def add_user(user_id: int, username: str = None, first_name: str = None):
    """User ko database mein add karega"""
    user_data = {
        "user_id": user_id,
        "username": username,
        "first_name": first_name,
        "first_seen": datetime.now(),
        "last_seen": datetime.now(),
        "is_active": True
    }
    
    await db.users.update_one(
        {"user_id": user_id},
        {"$set": user_data},
        upsert=True
    )

async def update_user_activity(user_id: int):
    """User ki last seen update karega"""
    await db.users.update_one(
        {"user_id": user_id},
        {"$set": {"last_seen": datetime.now()}}
    )

async def get_user(user_id: int):
    """User details get karega"""
    return await db.users.find_one({"user_id": user_id})

async def get_total_users():
    """Total users count get karega"""
    return await db.users.count_documents({"is_active": True})

# ==========================================================
# 👥 GROUP MANAGEMENT SYSTEM
# ==========================================================

async def add_group(chat_id: int, title: str = None, username: str = None):
    """Group ko database mein add karega"""
    group_data = {
        "chat_id": chat_id,
        "title": title,
        "username": username,
        "added_date": datetime.now(),
        "is_active": True
    }
    
    await db.groups.update_one(
        {"chat_id": chat_id},
        {"$set": group_data},
        upsert=True
    )

async def get_group(chat_id: int):
    """Group details get karega"""
    return await db.groups.find_one({"chat_id": chat_id})

async def get_total_groups():
    """Total groups count get karega"""
    return await db.groups.count_documents({"is_active": True})

# ==========================================================
# 📊 BOT STATS SYSTEM
# ==========================================================

async def get_bot_stats():
    """Bot ke overall stats get karega"""
    total_users = await get_total_users()
    total_groups = await get_total_groups()
    
    stats = {
        "total_users": total_users,
        "total_groups": total_groups,
        "last_updated": datetime.now()
    }
    
    return stats
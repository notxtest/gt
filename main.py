import logging
import asyncio
from pyrogram import Client
from config import API_ID, API_HASH, BOT_TOKEN
from db import get_all_bots, add_bot_to_db
from handlers import register_all_handlers
import threading
import os
from flask import Flask

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Uptime Robot ke liye Flask server
web_app = Flask(__name__)

@web_app.route('/')
def home():
    return "🤖 Multi-Bot File Store is Alive!"

@web_app.route('/health')
def health():
    return "OK"

def start_web_server():
    port = int(os.environ.get("PORT", 5000))
    web_app.run(host='0.0.0.0', port=port)

# Background thread for web server
server_thread = threading.Thread(target=start_web_server)
server_thread.daemon = True
server_thread.start()

async def create_bot_app(bot_token: str, bot_username: str = None):
    """Create and configure bot app"""
    try:
        app = Client(
            f"bot_{bot_username}" if bot_username else "bot_session",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=bot_token,
            plugins=dict(root="handlers")
        )
        
        return app
    except Exception as e:
        logger.error(f"Failed to create bot app: {e}")
        return None

async def main():
    """Main function to start all bots"""
    
    # Start primary bot
    primary_app = await create_bot_app(BOT_TOKEN)
    if primary_app:
        register_all_handlers(primary_app)
        await primary_app.start()
        bot_me = await primary_app.get_me()
        logger.info(f"✅ Primary bot started: @{bot_me.username}")
        
        # Add primary bot to database if not exists
        existing_bot = await get_bot_by_username(f"@{bot_me.username}")
        if not existing_bot:
            await add_bot_to_db(
                bot_token=BOT_TOKEN,
                bot_username=f"@{bot_me.username}",
                added_by=(await primary_app.get_me()).id,
                bot_name="Anime File Store",
                creator="@Creator",
                owner="@Owner",
                start_image="https://telegra.ph/file/default-start-image.jpg"
            )
            logger.info("✅ Primary bot added to database!")
    else:
        logger.error("❌ Failed to start primary bot!")
        return
    
    # Start additional bots from database
    additional_bots = await get_all_bots()
    active_apps = [primary_app]
    
    for bot in additional_bots:
        if bot['bot_token'] != BOT_TOKEN:  # Skip primary bot
            try:
                bot_app = await create_bot_app(bot['bot_token'], bot['bot_username'])
                if bot_app:
                    register_all_handlers(bot_app)
                    await bot_app.start()
                    active_apps.append(bot_app)
                    logger.info(f"✅ Additional bot started: {bot['bot_username']}")
            except Exception as e:
                logger.error(f"❌ Failed to start bot {bot['bot_username']}: {e}")
    
    logger.info(f"🚀 Total {len(active_apps)} bots running!")
    
    # Keep all bots running
    try:
        await asyncio.gather(*[app.idle() for app in active_apps])
    except KeyboardInterrupt:
        logger.info("🛑 Shutting down bots...")
    finally:
        # Stop all bots
        for app in active_apps:
            await app.stop()

if __name__ == "__main__":
    asyncio.run(main())
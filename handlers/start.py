import logging
import time
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from config import BOT_NAME, CREATOR_USERNAME, OWNER_USERNAME, START_IMAGE
from db import add_user, add_group, get_bot_stats

logger = logging.getLogger(__name__)

# Bot start time for uptime calculation
start_time = time.time()

def format_uptime(seconds):
    """Uptime ko readable format mein convert karega"""
    days = seconds // (24 * 3600)
    seconds %= (24 * 3600)
    hours = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    
    if days > 0:
        return f"{days}d {hours}h {minutes}m {seconds}s"
    elif hours > 0:
        return f"{hours}h {minutes}m {seconds}s"
    else:
        return f"{minutes}m {seconds}s"

def register_handlers(app: Client):
    
    # ==========================================================
    # 🏠 START COMMAND
    # ==========================================================
    
    @app.on_message(filters.command("start"))
    async def start_command(client, message: Message):
        try:
            user_id = message.from_user.id
            first_name = message.from_user.first_name
            
            # User ko database mein add karo
            await add_user(user_id, message.from_user.username, first_name)
            
            # Agar group hai to group bhi add karo
            if message.chat.type != "private":
                await add_group(message.chat.id, message.chat.title, message.chat.username)
            
            caption = f"""
<blockquote>›› ʜᴇʏ!!, {first_name}~

ʟᴏᴠᴇ ᴛᴏ ᴡᴀᴛᴄʜ ᴀɴɪᴍᴇ sᴇʀɪᴇs ᴀɴᴅ ᴍᴏᴠɪᴇs? ɪ ᴀᴍ ᴍᴀᴅᴇ ᴛᴏ ʜᴇʟᴘ ʏᴏᴜ ᴛᴏ ғɪɴᴅ ᴡʜᴀᴛ ʏᴏᴜ'ʀᴇ ʟᴏᴏᴋɪɴɢ ꜰᴏʀ.</blockquote>
"""
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🔍 ꜰᴏʀ ᴍᴏʀᴇ", callback_data="more_info")],
                [
                    InlineKeyboardButton("⚙️ ꜱᴇᴛᴛɪɴɢꜱ", callback_data="settings"),
                    InlineKeyboardButton("📂 ʀᴇᴘᴏ", url="https://github.com")
                ]
            ])
            
            await client.send_photo(
                chat_id=message.chat.id,
                photo=START_IMAGE,
                caption=caption,
                reply_markup=keyboard,
                message_effect_id="5104841245755180586"  # Fire Effect
            )
            
        except Exception as e:
            logger.error(f"Start command error: {e}")
            await message.reply_text("❌ Error occurred!")

    # ==========================================================
    # 📊 BSTATS COMMAND (Yahi pe vo configurations dikhao)
    # ==========================================================
    
    @app.on_message(filters.command("bstats"))
    async def bot_stats_command(client, message: Message):
        try:
            # Bot stats get karo
            stats = await get_bot_stats()
            
            # Uptime calculate karo
            current_time = time.time()
            uptime_seconds = int(current_time - start_time)
            uptime_str = format_uptime(uptime_seconds)
            
            text = f"""
» **Cᴏɴғɪɢᴜʀᴀᴛɪᴏɴs**
» ᴛᴏᴛᴀʟ ғᴏʀᴄᴇ sᴜʙ ᴄʜᴀɴɴᴇʟ:  {stats.get('force_sub_count', 3)}
» ᴛᴏᴛᴀʟ ᴀᴅᴍɪɴs:  {stats.get('admin_count', 3)}
» ᴛᴏᴛᴀʟ ʙᴀɴɴᴇᴅ ᴜsᴇʀs:  {stats.get('banned_users', 1)}
» ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ ᴍᴏᴅᴇ:  {stats.get('auto_delete', 'ᴇɴᴀʙʟᴇᴅ')}
» ᴘʀᴏᴛᴇᴄᴛ ᴄᴏɴᴛᴇɴᴛ:  {stats.get('protect_content', 'ᴅɪsᴀʙʟᴇᴅ')}
» ʜɪᴅᴇ ᴄᴀᴘᴛɪᴏɴ:  {stats.get('hide_caption', 'ᴅɪsᴀʙʟᴇᴅ')}
» ᴄʜᴀɴɴᴇʟ ʙᴜᴛᴛᴏɴ:  {stats.get('channel_button', 'ᴅɪsᴀʙʟᴇᴅ')}
» ʀᴇǫᴜᴇsᴛ ғsᴜʙ ᴍᴏᴅᴇ: {stats.get('request_fsub', 'ᴇɴᴀʙʟᴇᴅ')}
» 👥 ᴛᴏᴛᴀʟ ᴜsᴇʀs: {stats['total_users']}
» 👥 ᴛᴏᴛᴀʟ ɢʀᴏᴜᴘs: {stats['total_groups']}
» ⏰ ᴜᴘᴛɪᴍᴇ: {uptime_str}
"""
            await message.reply_text(text)
            
        except Exception as e:
            logger.error(f"Stats command error: {e}")
            await message.reply_text("❌ Error fetching stats!")

    # ==========================================================
    # 🔘 CALLBACK QUERIES HANDLING
    # ==========================================================
    
    @app.on_callback_query()
    async def handle_callbacks(client, call: CallbackQuery):
        try:
            if call.data == "more_info":
                await show_more_info(client, call)
            elif call.data == "settings":
                await show_settings(client, call)
            elif call.data == "stats":
                await show_stats(client, call)
            elif call.data == "back_to_main":
                await back_to_main(client, call)
            elif call.data == "close_message":
                await close_message(client, call)
                
        except Exception as e:
            logger.error(f"Callback error: {e}")
            await call.answer("❌ Error occurred!", show_alert=True)

    # ==========================================================
    # 🔍 MORE INFO FUNCTION
    # ==========================================================
    
    async def show_more_info(client, call: CallbackQuery):
        more_info_text = f"""
<blockquote>🤖 ᴍʏ ɴᴀᴍᴇ: {BOT_NAME}
» ᴄʀᴇᴀᴛᴏʀ: {CREATOR_USERNAME}
» ᴀɴɪᴍᴇ ᴄʜᴀɴɴᴇʟ : ᴀɴɪᴍᴇ ʜɪɴᴅɪ
» ᴏɴɢᴏɪɴɢ ᴄʜᴀɴɴᴇʟ : 𝐎ɴɢᴏɪɴɢ 𝐌ᴜʟᴛɪᴠᴇʀsᴇ
» sᴜᴘᴘᴏʀᴛ ᴄʜᴀᴛ : 𝐌ᴜʟᴛɪᴠᴇʀsᴇ 𝐆ᴄ
» ᴏᴡɴᴇʀ : {OWNER_USERNAME}</blockquote>
"""
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="back_to_main"),
                InlineKeyboardButton("📊 ꜱᴛᴀᴛꜱ", callback_data="stats")
            ]
        ])
        
        await call.message.edit_caption(
            caption=more_info_text,
            reply_markup=keyboard
        )
        await call.answer()

    # ==========================================================
    # 📊 STATS FUNCTION (Yeh callback wala simple rahega)
    # ==========================================================
    
    async def show_stats(client, call: CallbackQuery):
        # Get stats from database
        stats = await get_bot_stats()
        
        stats_text = f"""
<blockquote>» 📊 ʙᴏᴛ sᴛᴀᴛɪsᴛɪᴄs
» 👥 ᴛᴏᴛᴀʟ ᴜsᴇʀs: {stats['total_users']}
» 👥 ᴛᴏᴛᴀʟ ɢʀᴏᴜᴘs: {stats['total_groups']}
» 📅 ʟᴀsᴛ ᴜᴘᴅᴀᴛᴇᴅ: {stats['last_updated'].strftime('%H:%M:%S')}</blockquote>
"""
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="more_info"),
                InlineKeyboardButton("❌ ᴄʟᴏsᴇ", callback_data="close_message")
            ]
        ])
        
        await call.message.edit_caption(
            caption=stats_text,
            reply_markup=keyboard
        )
        await call.answer()

    # ==========================================================
    # ⚙️ SETTINGS FUNCTION (Yeh bhi configurations dikhayega)
    # ==========================================================
    
    async def show_settings(client, call: CallbackQuery):
        # Get stats from database
        stats = await get_bot_stats()
        
        settings_text = f"""
<blockquote>» **Cᴏɴғɪɢᴜʀᴀᴛɪᴏɴs**
» ᴛᴏᴛᴀʟ ғᴏʀᴄᴇ sᴜʙ ᴄʜᴀɴɴᴇʟ:  {stats.get('force_sub_count', 3)}
» ᴛᴏᴛᴀʟ ᴀᴅᴍɪɴs:  {stats.get('admin_count', 3)}
» ᴛᴏᴛᴀʟ ʙᴀɴɴᴇᴅ ᴜsᴇʀs:  {stats.get('banned_users', 1)}
» ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ ᴍᴏᴅᴇ:  {stats.get('auto_delete', 'ᴇɴᴀʙʟᴇᴅ')}
» ᴘʀᴏᴛᴇᴄᴛ ᴄᴏɴᴛᴇɴᴛ:  {stats.get('protect_content', 'ᴅɪsᴀʙʟᴇᴅ')}
» ʜɪᴅᴇ ᴄᴀᴘᴛɪᴏɴ:  {stats.get('hide_caption', 'ᴅɪsᴀʙʟᴇᴅ')}
» ᴄʜᴀɴɴᴇʟ ʙᴜᴛᴛᴏɴ:  {stats.get('channel_button', 'ᴅɪsᴀʙʟᴇᴅ')}
» ʀᴇǫᴜᴇsᴛ ғsᴜʙ ᴍᴏᴅᴇ: {stats.get('request_fsub', 'ᴇɴᴀʙʟᴇᴅ')}</blockquote>
"""
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="back_to_main"),
                InlineKeyboardButton("❌ ᴄʟᴏsᴇ", callback_data="close_message")
            ]
        ])
        
        await call.message.edit_caption(
            caption=settings_text,
            reply_markup=keyboard
        )
        await call.answer()

    # ==========================================================
    # 🔙 BACK TO MAIN FUNCTION
    # ==========================================================
    
    async def back_to_main(client, call: CallbackQuery):
        first_name = call.from_user.first_name
        
        caption = f"""
<blockquote>›› ʜᴇʏ!!, {first_name}~

ʟᴏᴠᴇ ᴛᴏ ᴡᴀᴛᴄʜ ᴀɴɪᴍᴇ sᴇʀɪᴇs ᴀɴᴅ ᴍᴏᴠɪᴇs? ɪ ᴀᴍ ᴍᴀᴅᴇ ᴛᴏ ʜᴇʟᴘ ʏᴏᴜ ᴛᴏ ғɪɴᴅ ᴡʜᴀᴛ ʏᴏᴜ'ʀᴇ ʟᴏᴏᴋɪɴɢ ꜰᴏʀ.</blockquote>
"""
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔍 ꜰᴏʀ ᴍᴏʀᴇ", callback_data="more_info")],
            [
                InlineKeyboardButton("⚙️ ꜱᴇᴛᴛɪɴɢꜱ", callback_data="settings"),
                InlineKeyboardButton("📂 ʀᴇᴘᴏ", url="https://github.com")
            ]
        ])
        
        await call.message.edit_caption(
            caption=caption,
            reply_markup=keyboard
        )
        await call.answer()

    # ==========================================================
    # ❌ CLOSE MESSAGE FUNCTION
    # ==========================================================
    
    async def close_message(client, call: CallbackQuery):
        await call.message.delete()
        await call.answer("Message closed!")
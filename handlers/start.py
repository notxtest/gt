import logging
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from db import get_bot_by_token, get_bot_stats

logger = logging.getLogger(__name__)

def register_handlers(app: Client):
    
    # Bot username get karo
    bot_username = f"@{app.me.username}" if app.me else "unknown"
    
    # ==========================================================
    # 🏠 START COMMAND
    # ==========================================================
    
    @app.on_message(filters.command("start"))
    async def start_command(client, message: Message):
        try:
            first_name = message.from_user.first_name
            
            # Bot configuration get karo
            bot_config = await get_bot_by_username(bot_username)
            if not bot_config:
                # Agar config nahi hai to default use karo
                bot_name = "Anime File Store"
                start_image = "https://telegra.ph/file/default-start-image.jpg"
            else:
                bot_name = bot_config.get("bot_name", "Anime File Store")
                start_image = bot_config.get("start_image", "https://telegra.ph/file/default-start-image.jpg")
            
            # Welcome message with HTML formatting
            caption = f"""
<blockquote>›› ʜᴇʏ!!, {first_name}~

ʟᴏᴠᴇ ᴛᴏ ᴡᴀᴛᴄʜ ᴀɴɪᴍᴇ sᴇʀɪᴇs ᴀɴᴅ ᴍᴏᴠɪᴇs? ɪ ᴀᴍ ᴍᴀᴅᴇ ᴛᴏ ʜᴇʟᴘ ʏᴏᴜ ᴛᴏ ғɪɴᴅ ᴡʜᴀᴛ ʏᴏᴜ'ʀᴇ ʟᴏᴏᴋɪɴɢ ꜰᴏʀ.</blockquote>
"""
            # Keyboard buttons
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🔍 ꜰᴏʀ ᴍᴏʀᴇ", callback_data="more_info")],
                [
                    InlineKeyboardButton("⚙️ ꜱᴇᴛᴛɪɴɢꜱ", callback_data="settings"),
                    InlineKeyboardButton("📂 ʀᴇᴘᴏ", url="https://github.com")
                ]
            ])
            
            # Send photo with caption
            await client.send_photo(
                chat_id=message.chat.id,
                photo=start_image,
                caption=caption,
                reply_markup=keyboard
            )
            
        except Exception as e:
            logger.error(f"Start command error: {e}")
            await message.reply_text("❌ Error occurred!")

    # ==========================================================
    # 🔘 CALLBACK QUERIES HANDLING
    # ==========================================================
    
    @app.on_callback_query()
    async def handle_callbacks(client, call: CallbackQuery):
        try:
            if call.data == "more_info":
                await show_more_info(client, call, bot_username)
            elif call.data == "settings":
                await show_settings(client, call, bot_username)
            elif call.data == "stats":
                await show_stats(client, call, bot_username)
            elif call.data == "back_to_main":
                await back_to_main(client, call, bot_username)
            elif call.data == "close_message":
                await close_message(client, call)
                
        except Exception as e:
            logger.error(f"Callback error: {e}")
            await call.answer("❌ Error occurred!", show_alert=True)

    # ==========================================================
    # 🔍 MORE INFO FUNCTION
    # ==========================================================
    
    async def show_more_info(client, call: CallbackQuery, current_bot_username: str):
        # Bot configuration get karo
        bot_config = await get_bot_by_username(current_bot_username)
        if not bot_config:
            bot_name = "Anime File Store"
            creator = "@Creator"
            owner = "@Owner"
        else:
            bot_name = bot_config.get("bot_name", "Anime File Store")
            creator = bot_config.get("creator", "@Creator")
            owner = bot_config.get("owner", "@Owner")
        
        more_info_text = f"""
<blockquote>🤖 ᴍʏ ɴᴀᴍᴇ: {bot_name}
» ᴄʀᴇᴀᴛᴏʀ: {creator}
» ᴀɴɪᴍᴇ ᴄʜᴀɴɴᴇʟ : ᴀɴɪᴍᴇ ʜɪɴᴅɪ
» ᴏɴɢᴏɪɴɢ ᴄʜᴀɴɴᴇʟ : 𝐎ɴɢᴏɪɴɢ 𝐌ᴜʟᴛɪᴠᴇʀsᴇ
» sᴜᴘᴘᴏʀᴛ ᴄʜᴀᴛ : 𝐌ᴜʟᴛɪᴠᴇʀsᴇ 𝐆ᴄ
» ᴏᴡɴᴇʀ : {owner}</blockquote>
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
    # 📊 STATS FUNCTION
    # ==========================================================
    
    async def show_stats(client, call: CallbackQuery, current_bot_username: str):
        # Get stats from database for this specific bot
        stats_data = await get_bot_stats(current_bot_username)
        
        stats_text = f"""
<blockquote>»  Cᴏɴғɪɢᴜʀᴀᴛɪᴏɴs
» ᴛᴏᴛᴀʟ ғᴏʀᴄᴇ sᴜʙ ᴄʜᴀɴɴᴇʟ:  {stats_data.get('force_sub_count', 3)}
» ᴛᴏᴛᴀʟ ᴀᴅᴍɪɴs:  {stats_data.get('admin_count', 3)}
» ᴛᴏᴛᴀʟ ʙᴀɴɴᴇᴅ ᴜsᴇʀs:  {stats_data.get('banned_users', 1)}
» ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ ᴍᴏᴅᴇ:  {stats_data.get('auto_delete', 'ᴇɴᴀʙʟᴇᴅ')}
» ᴘʀᴏᴛᴇᴄᴛ ᴄᴏɴᴛᴇɴᴛ:  {stats_data.get('protect_content', 'ᴅɪsᴀʙʟᴇᴅ')}
» ʜɪᴅᴇ ᴄᴀᴘᴛɪᴏɴ:  {stats_data.get('hide_caption', 'ᴅɪsᴀʙʟᴇᴅ')}
» ᴄʜᴀɴɴᴇʟ ʙᴜᴛᴛᴏɴ:  {stats_data.get('channel_button', 'ᴅɪsᴀʙʟᴇᴅ')}
» ʀᴇǫᴜᴇsᴛ ғsᴜʙ ᴍᴏᴅᴇ: {stats_data.get('request_fsub', 'ᴇɴᴀʙʟᴇᴅ')}</blockquote>
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
    # ⚙️ SETTINGS FUNCTION
    # ==========================================================
    
    async def show_settings(client, call: CallbackQuery, current_bot_username: str):
        # Get settings from database for this specific bot
        stats_data = await get_bot_stats(current_bot_username)
        
        settings_text = f"""
<blockquote>»  Cᴏɴғɪɢᴜʀᴀᴛɪᴏɴs
» ᴛᴏᴛᴀʟ ғᴏʀᴄᴇ sᴜʙ ᴄʜᴀɴɴᴇʟ:  {stats_data.get('force_sub_count', 3)}
» ᴛᴏᴛᴀʟ ᴀᴅᴍɪɴs:  {stats_data.get('admin_count', 3)}
» ᴛᴏᴛᴀʟ ʙᴀɴɴᴇᴅ ᴜsᴇʀs:  {stats_data.get('banned_users', 1)}
» ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ ᴍᴏᴅᴇ:  {stats_data.get('auto_delete', 'ᴇɴᴀʙʟᴇᴅ')}
» ᴘʀᴏᴛᴇᴄᴛ ᴄᴏɴᴛᴇɴᴛ:  {stats_data.get('protect_content', 'ᴅɪsᴀʙʟᴇᴅ')}
» ʜɪᴅᴇ ᴄᴀᴘᴛɪᴏɴ:  {stats_data.get('hide_caption', 'ᴅɪsᴀʙʟᴇᴅ')}
» ᴄʜᴀɴɴᴇʟ ʙᴜᴛᴛᴏɴ:  {stats_data.get('channel_button', 'ᴅɪsᴀʙʟᴇᴅ')}
» ʀᴇǫᴜᴇsᴛ ғsᴜʙ ᴍᴏᴅᴇ: {stats_data.get('request_fsub', 'ᴇɴᴀʙʟᴇᴅ')}</blockquote>
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
    
    async def back_to_main(client, call: CallbackQuery, current_bot_username: str):
        first_name = call.from_user.first_name
        
        # Bot configuration get karo
        bot_config = await get_bot_by_username(current_bot_username)
        if not bot_config:
            start_image = "https://telegra.ph/file/default-start-image.jpg"
        else:
            start_image = bot_config.get("start_image", "https://telegra.ph/file/default-start-image.jpg")
        
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
import logging
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from db import add_bot_to_db, remove_bot_from_db, get_all_bots, is_bot_owner, MAX_BOTS

logger = logging.getLogger(__name__)

def register_bot_management_handlers(app: Client):
    
    bot_username = f"@{app.me.username}" if app.me else "unknown"
    
    # ==========================================================
    # ➕ ADD BOT COMMAND
    # ==========================================================
    
    @app.on_message(filters.command("addbot"))
    async def add_bot_command(client, message: Message):
        try:
            # Check if user is bot owner
            if not await is_bot_owner(message.from_user.id, bot_username):
                await message.reply_text("❌ Only bot owner can add new bots!")
                return
            
            # Check command format
            if len(message.command) < 2:
                await message.reply_text(
                    "**🤖 Add New Bot**\n\n"
                    "**Usage:** `/addbot <bot_token>`\n\n"
                    "**Example:** `/addbot 1234567890:ABCDEFGHIJKLMNOPQRSTUVWXYZ`\n\n"
                    "After adding token, you'll be asked for bot details."
                )
                return
            
            bot_token = message.command[1]
            
            # Validate token format
            if ':' not in bot_token or len(bot_token) < 30:
                await message.reply_text("❌ Invalid bot token format!")
                return
            
            # Store token temporarily and ask for bot username
            await client.send_message(
                chat_id=message.chat.id,
                text="✅ Bot token received! Now send me the bot username (with @):\n\n"
                     "**Example:** @YourBotUsername"
            )
            
            # Store in temporary storage (you can use database for this)
            # For now, we'll handle in conversation
            
        except Exception as e:
            logger.error(f"Addbot command error: {e}")
            await message.reply_text("❌ Error occurred while adding bot!")
    
    # ==========================================================
    # 🗑️ REMOVE BOT COMMAND
    # ==========================================================
    
    @app.on_message(filters.command("removebot"))
    async def remove_bot_command(client, message: Message):
        try:
            # Check if user is bot owner
            if not await is_bot_owner(message.from_user.id, bot_username):
                await message.reply_text("❌ Only bot owner can remove bots!")
                return
            
            if len(message.command) < 2:
                # Show list of bots to remove
                bots = await get_all_bots()
                if not bots:
                    await message.reply_text("❌ No bots found in database!")
                    return
                
                bot_list = "**🤖 Your Bots:**\n\n"
                keyboard = []
                
                for bot in bots:
                    bot_list += f"• {bot['bot_username']} - {bot['bot_name']}\n"
                    keyboard.append([InlineKeyboardButton(
                        f"Remove {bot['bot_username']}", 
                        callback_data=f"remove_{bot['bot_username']}"
                    )])
                
                await message.reply_text(
                    bot_list + "\nClick below to remove a bot:",
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
                return
            
            bot_username_to_remove = message.command[1]
            success, result_msg = await remove_bot_from_db(bot_username_to_remove, message.from_user.id)
            await message.reply_text(result_msg)
            
        except Exception as e:
            logger.error(f"Removebot command error: {e}")
            await message.reply_text("❌ Error occurred while removing bot!")
    
    # ==========================================================
    # 📋 LIST BOTS COMMAND
    # ==========================================================
    
    @app.on_message(filters.command("mybots"))
    async def list_bots_command(client, message: Message):
        try:
            # Check if user is bot owner
            if not await is_bot_owner(message.from_user.id, bot_username):
                await message.reply_text("❌ Only bot owner can view bots!")
                return
            
            bots = await get_all_bots()
            if not bots:
                await message.reply_text("❌ No bots found in database!")
                return
            
            bot_list = f"**🤖 Your Bots ({len(bots)}/{MAX_BOTS}):**\n\n"
            
            for bot in bots:
                bot_list += (
                    f"**Bot:** {bot['bot_name']}\n"
                    f"**Username:** {bot['bot_username']}\n"
                    f"**Files:** {bot.get('files_count', 0)}\n"
                    f"**Added:** {bot['added_at'].strftime('%Y-%m-%d')}\n"
                    f"────────────────\n"
                )
            
            await message.reply_text(bot_list)
            
        except Exception as e:
            logger.error(f"List bots command error: {e}")
            await message.reply_text("❌ Error occurred while fetching bots!")
    
    # ==========================================================
    # 🔧 BOT SETTINGS COMMAND
    # ==========================================================
    
    @app.on_message(filters.command("botsettings"))
    async def bot_settings_command(client, message: Message):
        try:
            # Check if user is bot owner
            if not await is_bot_owner(message.from_user.id, bot_username):
                await message.reply_text("❌ Only bot owner can change settings!")
                return
            
            if len(message.command) < 2:
                await message.reply_text(
                    "**⚙️ Bot Settings**\n\n"
                    "**Usage:** `/botsettings <bot_username> <setting> <value>`\n\n"
                    "**Available Settings:**\n"
                    "• `name` - Change bot name\n"
                    "• `image` - Change start image URL\n"
                    "• `creator` - Change creator username\n"
                    "• `owner` - Change owner username\n\n"
                    "**Examples:**\n"
                    "`/botsettings @YourBot name \"New Bot Name\"`\n"
                    "`/botsettings @YourBot image https://new-image.jpg`"
                )
                return
            
            target_bot = message.command[1]
            if len(message.command) < 4:
                await message.reply_text("❌ Please provide setting and value!")
                return
            
            setting = message.command[2].lower()
            value = ' '.join(message.command[3:])
            
            valid_settings = ['name', 'image', 'creator', 'owner']
            if setting not in valid_settings:
                await message.reply_text(f"❌ Invalid setting! Use: {', '.join(valid_settings)}")
                return
            
            # Update setting in database
            from db import update_bot_settings
            await update_bot_settings(target_bot, {f"bot_{setting}" if setting != 'image' else 'start_image': value})
            
            await message.reply_text(f"✅ {setting.capitalize()} updated successfully!")
            
        except Exception as e:
            logger.error(f"Bot settings command error: {e}")
            await message.reply_text("❌ Error occurred while updating settings!")
    
    # ==========================================================
    # 🔘 CALLBACK QUERIES FOR BOT MANAGEMENT
    # ==========================================================
    
    @app.on_callback_query(filters.regex(r"^remove_"))
    async def handle_remove_callback(client, call):
        try:
            bot_username_to_remove = call.data.replace("remove_", "")
            success, result_msg = await remove_bot_from_db(bot_username_to_remove, call.from_user.id)
            
            await call.message.edit_text(result_msg)
            await call.answer()
            
        except Exception as e:
            logger.error(f"Remove callback error: {e}")
            await call.answer("❌ Error occurred!", show_alert=True)
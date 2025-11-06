import logging
import re
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from config import BOT_OWNER_ID, BOT_NAME, CREATOR_USERNAME, OWNER_USERNAME, START_IMAGE, MAX_BOTS
from db import (
    add_bot_to_db, remove_bot_from_db, get_all_bots, get_bot_by_username,
    update_bot_settings, is_bot_running, start_bot_instance, stop_bot_instance,
    get_bot_by_token
)

logger = logging.getLogger(__name__)

# Temporary storage for bot creation process
bot_creation_sessions = {}

def register_bot_management_handlers(app: Client):
    
    # ==========================================================
    # 🔧 HELPER FUNCTIONS
    # ==========================================================
    
    def is_owner(user_id: int) -> bool:
        """Check if user is bot owner"""
        return user_id == BOT_OWNER_ID
    
    async def delete_user_message(client, message: Message):
        """Delete user message to reduce spam"""
        try:
            await message.delete()
        except:
            pass
    
    async def show_add_bot_menu(client, chat_id: int, message_id: int = None):
        """Show add bot main menu"""
        text = """
🤖 **Add New Bot**

Here you can add a new bot to your system. 
Click **ADD** to start the process.
        """
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ ADD BOT", callback_data="addbot_start")],
            [InlineKeyboardButton("❌ CLOSE", callback_data="close_panel")]
        ])
        
        if message_id:
            await client.edit_message_text(chat_id, message_id, text, reply_markup=keyboard)
        else:
            await client.send_message(chat_id, text, reply_markup=keyboard)
    
    async def ask_for_bot_token(client, chat_id: int, message_id: int = None):
        """Ask for bot token"""
        text = """
📝 **Step 1: Bot Token**

Please send me the bot token:

**Format:** `1234567890:ABCDEFGHIJKLMNOPQRSTUVWXYZ`

You can get this from @BotFather
        """
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("◀️ BACK", callback_data="addbot_main")],
            [InlineKeyboardButton("❌ CLOSE", callback_data="close_panel")]
        ])
        
        if message_id:
            await client.edit_message_text(chat_id, message_id, text, reply_markup=keyboard)
        else:
            await client.send_message(chat_id, text, reply_markup=keyboard)
    
    async def show_bot_management_panel(client, chat_id: int, bot_username: str, message_id: int = None):
        """Show bot management panel"""
        bot_data = await get_bot_by_username(bot_username)
        if not bot_data:
            await client.send_message(chat_id, "❌ Bot not found!")
            return
        
        is_running = await is_bot_running(bot_username)
        
        status_icon = "🟢" if is_running else "🔴"
        status_text = "Running" if is_running else "Stopped"
        
        text = f"""
🤖 **Bot Management Panel**

**Bot:** {bot_data['bot_name']}
**Username:** {bot_data['bot_username']}
**Status:** {status_icon} {status_text}
**Files:** {bot_data.get('files_count', 0)}
**Users:** {bot_data.get('users_count', 0)}

What would you like to do?
        """
        
        start_stop_text = "🟢 START BOT" if not is_running else "🔴 STOP BOT"
        start_stop_data = f"start_{bot_username}" if not is_running else f"stop_{bot_username}"
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(start_stop_text, callback_data=start_stop_data)],
            [InlineKeyboardButton("✏️ EDIT SETTINGS", callback_data=f"edit_{bot_username}")],
            [InlineKeyboardButton("🗑️ DELETE BOT", callback_data=f"delete_{bot_username}")],
            [InlineKeyboardButton("❌ CLOSE", callback_data="close_panel")]
        ])
        
        if message_id:
            await client.edit_message_text(chat_id, message_id, text, reply_markup=keyboard)
        else:
            await client.send_message(chat_id, text, reply_markup=keyboard)
    
    async def show_edit_bot_menu(client, chat_id: int, bot_username: str, message_id: int = None):
        """Show edit bot settings menu"""
        bot_data = await get_bot_by_username(bot_username)
        if not bot_data:
            return
        
        # Truncate long image URLs for display
        start_image = bot_data['start_image']
        if len(start_image) > 30:
            start_image = start_image[:27] + "..."
        
        text = f"""
⚙️ **Edit Bot Settings**

**🤖 Bot Name:** `{bot_data['bot_name']}`
**👑 Owner:** `{bot_data['owner']}`
**👨‍💻 Creator:** `{bot_data['creator']}`
**🖼️ Start Image:** `{start_image}`

Click on any setting to edit it:
        """
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🤖 Bot Name", callback_data=f"edit_name_{bot_username}"),
                InlineKeyboardButton("👑 Owner", callback_data=f"edit_owner_{bot_username}")
            ],
            [
                InlineKeyboardButton("👨‍💻 Creator", callback_data=f"edit_creator_{bot_username}"),
                InlineKeyboardButton("🖼️ Image", callback_data=f"edit_image_{bot_username}")
            ],
            [InlineKeyboardButton("◀️ BACK", callback_data=f"manage_{bot_username}")]
        ])
        
        if message_id:
            await client.edit_message_text(chat_id, message_id, text, reply_markup=keyboard)
        else:
            await client.send_message(chat_id, text, reply_markup=keyboard)
    
    async def show_input_prompt(client, chat_id: int, field: str, bot_username: str, message_id: int = None):
        """Show input prompt for specific field"""
        field_info = {
            "name": {"display": "Bot Name", "example": "Anime File Store Pro"},
            "owner": {"display": "Owner Username", "example": "@YourUsername"},
            "creator": {"display": "Creator Username", "example": "@CreatorUsername"},
            "image": {"display": "Start Image URL", "example": "https://telegra.ph/file/your-image.jpg"},
            "token": {"display": "Bot Token", "example": "1234567890:ABCDEF..."}
        }
        
        info = field_info.get(field, {"display": field, "example": "value"})
        
        text = f"""
📝 **Set {info['display']}**

Please send me the {info['display'].lower()}:

**Example:** `{info['example']}`
        """
        
        if field == "token":
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("◀️ BACK", callback_data="addbot_main")],
                [InlineKeyboardButton("❌ CLOSE", callback_data="close_panel")]
            ])
        else:
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("◀️ BACK", callback_data=f"edit_{bot_username}")],
                [InlineKeyboardButton("🔄 DEFAULT", callback_data=f"default_{field}_{bot_username}")]
            ])
        
        if message_id:
            await client.edit_message_text(chat_id, message_id, text, reply_markup=keyboard)
        else:
            await client.send_message(chat_id, text, reply_markup=keyboard)
    
    async def process_bot_token(client, message: Message):
        """Process bot token and create bot"""
        try:
            bot_token = message.text.strip()
            
            # Validate token format
            if not re.match(r'^\d+:[A-Za-z0-9_-]+$', bot_token):
                await message.reply_text("❌ Invalid bot token format!")
                return
            
            # Check if bot already exists
            existing_bot = await get_bot_by_token(bot_token)
            if existing_bot:
                await message.reply_text("❌ This bot is already in the system!")
                return
            
            # Store token in session
            user_id = message.from_user.id
            bot_creation_sessions[user_id] = {
                'token': bot_token,
                'step': 'username'
            }
            
            # Ask for bot username
            await show_input_prompt(client, message.chat.id, "username", "new")
            await delete_user_message(client, message)
            
        except Exception as e:
            logger.error(f"Token processing error: {e}")
            await message.reply_text("❌ Error processing token!")
    
    async def process_bot_username(client, message: Message):
        """Process bot username"""
        try:
            bot_username = message.text.strip()
            
            # Validate username format
            if not bot_username.startswith('@'):
                await message.reply_text("❌ Username must start with @")
                return
            
            user_id = message.from_user.id
            if user_id not in bot_creation_sessions:
                await message.reply_text("❌ Session expired. Start over with /addbot")
                return
            
            # Check if username already exists
            existing_bot = await get_bot_by_username(bot_username)
            if existing_bot:
                await message.reply_text("❌ Bot with this username already exists!")
                return
            
            # Update session
            bot_creation_sessions[user_id]['username'] = bot_username
            bot_creation_sessions[user_id]['step'] = 'name'
            
            # Ask for bot name
            await show_input_prompt(client, message.chat.id, "name", bot_username)
            await delete_user_message(client, message)
            
        except Exception as e:
            logger.error(f"Username processing error: {e}")
            await message.reply_text("❌ Error processing username!")
    
    async def process_bot_name(client, message: Message):
        """Process bot name and complete bot creation"""
        try:
            bot_name = message.text.strip()
            
            user_id = message.from_user.id
            if user_id not in bot_creation_sessions:
                await message.reply_text("❌ Session expired. Start over with /addbot")
                return
            
            session = bot_creation_sessions[user_id]
            
            # Add bot to database with default values
            success, result = await add_bot_to_db(
                bot_token=session['token'],
                bot_username=session['username'],
                added_by=user_id,
                bot_name=bot_name,
                creator=CREATOR_USERNAME,
                owner=OWNER_USERNAME,
                start_image=START_IMAGE
            )
            
            if success:
                # Clear session
                del bot_creation_sessions[user_id]
                
                # Show management panel
                await show_bot_management_panel(client, message.chat.id, session['username'])
                await delete_user_message(client, message)
            else:
                await message.reply_text(f"❌ {result}")
                
        except Exception as e:
            logger.error(f"Bot creation error: {e}")
            await message.reply_text("❌ Error creating bot!")
    
    async def process_setting_value(client, message: Message, field: str, bot_username: str):
        """Process setting value from user"""
        try:
            value = message.text.strip()
            
            # Field-specific validation
            if field == "owner" or field == "creator":
                if not value.startswith('@'):
                    await message.reply_text("❌ Username must start with @")
                    return
            
            elif field == "image":
                if not value.startswith(('http://', 'https://')):
                    await message.reply_text("❌ Invalid URL format")
                    return
            
            # Update setting in database
            db_field = f"bot_{field}" if field != "image" else "start_image"
            await update_bot_settings(bot_username, {db_field: value})
            
            # Show success and go back to edit menu
            await message.reply_text(f"✅ {field.replace('_', ' ').title()} updated successfully!")
            await show_edit_bot_menu(client, message.chat.id, bot_username)
            await delete_user_message(client, message)
            
        except Exception as e:
            logger.error(f"Setting update error: {e}")
            await message.reply_text("❌ Error updating setting!")
    
    # ==========================================================
    # ➕ ADD BOT COMMAND
    # ==========================================================
    
    @app.on_message(filters.command("addbot"))
    async def add_bot_command(client, message: Message):
        try:
            if not is_owner(message.from_user.id):
                await message.reply_text("❌ Only bot owner can use this command!")
                return
            
            await delete_user_message(client, message)
            await show_add_bot_menu(client, message.chat.id)
            
        except Exception as e:
            logger.error(f"Addbot command error: {e}")
            await message.reply_text("❌ Error occurred!")
    
    # ==========================================================
    # 🔘 CALLBACK QUERY HANDLERS
    # ==========================================================
    
    @app.on_callback_query()
    async def handle_callbacks(client, call: CallbackQuery):
        try:
            if not is_owner(call.from_user.id):
                await call.answer("❌ Only owner can use this!", show_alert=True)
                return
            
            data = call.data
            
            # Add Bot Flow
            if data == "addbot_start":
                await ask_for_bot_token(client, call.message.chat.id, call.message.id)
            
            elif data == "addbot_main":
                await show_add_bot_menu(client, call.message.chat.id, call.message.id)
            
            # Bot Management Flow  
            elif data.startswith("manage_"):
                bot_username = data.replace("manage_", "")
                await show_bot_management_panel(client, call.message.chat.id, bot_username, call.message.id)
            
            # Edit Bot Flow
            elif data.startswith("edit_"):
                if any(data.startswith(f"edit_{field}_") for field in ["name", "owner", "creator", "image"]):
                    # Field-specific edit
                    parts = data.split("_")
                    field = parts[1]
                    bot_username = "_".join(parts[2:])
                    
                    # Store in session for message handler
                    bot_creation_sessions[call.from_user.id] = {
                        'editing': True,
                        'field': field,
                        'bot_username': bot_username,
                        'step': f'edit_{field}'
                    }
                    
                    await show_input_prompt(client, call.message.chat.id, field, bot_username, call.message.id)
                else:
                    # General edit menu
                    bot_username = data.replace("edit_", "")
                    await show_edit_bot_menu(client, call.message.chat.id, bot_username, call.message.id)
            
            # Start/Stop Bot
            elif data.startswith("start_"):
                bot_username = data.replace("start_", "")
                success = await start_bot_instance(bot_username)
                if success:
                    await call.answer("✅ Bot started successfully!")
                    await show_bot_management_panel(client, call.message.chat.id, bot_username, call.message.id)
                else:
                    await call.answer("❌ Failed to start bot!", show_alert=True)
            
            elif data.startswith("stop_"):
                bot_username = data.replace("stop_", "")
                success = await stop_bot_instance(bot_username)
                if success:
                    await call.answer("✅ Bot stopped successfully!")
                    await show_bot_management_panel(client, call.message.chat.id, bot_username, call.message.id)
                else:
                    await call.answer("❌ Failed to stop bot!", show_alert=True)
            
            # Delete Bot
            elif data.startswith("delete_"):
                bot_username = data.replace("delete_", "")
                success, result = await remove_bot_from_db(bot_username, call.from_user.id)
                if success:
                    await call.answer("✅ Bot deleted successfully!")
                    await call.message.edit_text("🗑️ Bot deleted successfully!")
                else:
                    await call.answer(f"❌ {result}", show_alert=True)
            
            # Default Values
            elif data.startswith("default_"):
                parts = data.split("_")
                field = parts[1]
                bot_username = "_".join(parts[2:])
                
                default_values = {
                    "owner": OWNER_USERNAME,
                    "creator": CREATOR_USERNAME,
                    "image": START_IMAGE
                }
                
                if field in default_values:
                    db_field = f"bot_{field}" if field != "image" else "start_image"
                    await update_bot_settings(bot_username, {db_field: default_values[field]})
                    await call.answer("✅ Set to default value!")
                    await show_edit_bot_menu(client, call.message.chat.id, bot_username, call.message.id)
            
            # Close Panel
            elif data == "close_panel":
                await call.message.delete()
                await call.answer()
            
            await call.answer()
            
        except Exception as e:
            logger.error(f"Callback error: {e}")
            await call.answer("❌ Error occurred!", show_alert=True)
    
    # ==========================================================
    # 📝 MESSAGE HANDLERS FOR INPUT
    # ==========================================================
    
    @app.on_message(filters.private & filters.text)
    async def handle_text_messages(client, message: Message):
        try:
            if not is_owner(message.from_user.id):
                return
            
            user_id = message.from_user.id
            
            # Check if user is in bot creation session
            if user_id in bot_creation_sessions:
                session = bot_creation_sessions[user_id]
                
                if session.get('step') == 'token':
                    await process_bot_token(client, message)
                
                elif session.get('step') == 'username':
                    await process_bot_username(client, message)
                
                elif session.get('step') == 'name':
                    await process_bot_name(client, message)
                
                elif session.get('editing'):
                    await process_setting_value(client, message, session['field'], session['bot_username'])
                    # Clear editing session
                    del bot_creation_sessions[user_id]
            
        except Exception as e:
            logger.error(f"Message handler error: {e}")
    
    # ==========================================================
    # 🗑️ CLEANUP OLD SESSIONS
    # ==========================================================
    
    @app.on_message(filters.command("clearsessions"))
    async def clear_sessions_command(client, message: Message):
        if is_owner(message.from_user.id):
            bot_creation_sessions.clear()
            await message.reply_text("✅ All sessions cleared!")
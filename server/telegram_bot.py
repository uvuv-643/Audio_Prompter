import asyncio
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class ScreenshotTelegramBot:
    def __init__(self, screenshot_server):
        self.screenshot_server = screenshot_server
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.application = None
        
        if not self.bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN not found in environment variables")
    
    def _create_keyboard(self):
        return [
            [
                InlineKeyboardButton("⏪", callback_data='press_left'),
                InlineKeyboardButton("⏯️", callback_data='press_space'),
                InlineKeyboardButton("📸", callback_data='take_screenshot')
            ]
        ]
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        logger.info(f"Start command received from user {update.effective_user.id}")
        
        keyboard = self._create_keyboard()
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "🎬 Управление переводом",
            reply_markup=reply_markup
        )
        logger.info("Start command response sent")
    
    async def pause_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        logger.info(f"Pause command received from user {update.effective_user.id}")
        await self.take_screenshot(update, context)
    

    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        logger.info(f"Button callback received: {query.data} from user {update.effective_user.id}")
        await query.answer()
        
        if query.data == 'take_screenshot':
            await self.take_screenshot(update, context)
        elif query.data == 'press_space':
            await self.press_space(update, context)
        elif query.data == 'press_left':
            await self.press_left(update, context)

    
    async def take_screenshot(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            telegram_user_id = update.effective_user.id
            await self.screenshot_server.broadcast_screenshot_command(telegram_user_id)
            
            keyboard = self._create_keyboard()
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            message = f"📸 Перевод выполнен!"
            
            if hasattr(update, 'callback_query'):
                try:
                    await update.callback_query.edit_message_text(
                        message,
                        reply_markup=reply_markup
                    )
                except Exception as edit_error:
                    if "Message is not modified" in str(edit_error):
                        await update.callback_query.answer("✅ Перевод выполнен!")
                    else:
                        raise edit_error
            else:
                await update.message.reply_text(
                    message,
                    reply_markup=reply_markup
                )
            
            logger.info(f"Screenshot command sent via Telegram by user {update.effective_user.id}")
        
        except Exception as e:
            error_msg = f"❌ Ошибка: {str(e)}"
            keyboard = self._create_keyboard()
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            if hasattr(update, 'callback_query'):
                try:
                    await update.callback_query.edit_message_text(
                        error_msg,
                        reply_markup=reply_markup
                    )
                except Exception as edit_error:
                    if "Message is not modified" in str(edit_error):
                        await update.callback_query.answer("❌ Ошибка!")
                    else:
                        raise edit_error
            else:
                await update.message.reply_text(
                    error_msg,
                    reply_markup=reply_markup
                )
            logger.error(f"Telegram bot error: {e}")
    
    async def press_space(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            telegram_user_id = update.effective_user.id
            await self.screenshot_server.broadcast_space_key_command(telegram_user_id)
            
            keyboard = self._create_keyboard()
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            message = f"⏯️ Пауза выполнена!"
            
            if hasattr(update, 'callback_query'):
                try:
                    await update.callback_query.edit_message_text(
                        message,
                        reply_markup=reply_markup
                    )
                except Exception as edit_error:
                    if "Message is not modified" in str(edit_error):
                        await update.callback_query.answer("✅ Пауза выполнена!")
                    else:
                        raise edit_error
            else:
                await update.message.reply_text(
                    message,
                    reply_markup=reply_markup
                )
            
            logger.info(f"Space key command sent via Telegram by user {update.effective_user.id}")
        
        except Exception as e:
            error_msg = f"❌ Ошибка: {str(e)}"
            keyboard = self._create_keyboard()
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            if hasattr(update, 'callback_query'):
                try:
                    await update.callback_query.edit_message_text(
                        error_msg,
                        reply_markup=reply_markup
                    )
                except Exception as edit_error:
                    if "Message is not modified" in str(edit_error):
                        await update.callback_query.answer("❌ Ошибка!")
                    else:
                        raise edit_error
            else:
                await update.message.reply_text(
                    error_msg,
                    reply_markup=reply_markup
                )
            logger.error(f"Telegram bot error: {e}")
    
    async def press_left(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            telegram_user_id = update.effective_user.id
            await self.screenshot_server.broadcast_left_key_command(telegram_user_id)
            
            keyboard = self._create_keyboard()
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            message = f"⏪ Перемотка назад выполнена!"
            
            if hasattr(update, 'callback_query'):
                try:
                    await update.callback_query.edit_message_text(
                        message,
                        reply_markup=reply_markup
                    )
                except Exception as edit_error:
                    if "Message is not modified" in str(edit_error):
                        await update.callback_query.answer("✅ Перемотка выполнена!")
                    else:
                        raise edit_error
            else:
                await update.message.reply_text(
                    message,
                    reply_markup=reply_markup
                )
            
            logger.info(f"Left key command sent via Telegram by user {update.effective_user.id}")
        
        except Exception as e:
            error_msg = f"❌ Ошибка: {str(e)}"
            keyboard = self._create_keyboard()
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            if hasattr(update, 'callback_query'):
                try:
                    await update.callback_query.edit_message_text(
                        error_msg,
                        reply_markup=reply_markup
                    )
                except Exception as edit_error:
                    if "Message is not modified" in str(edit_error):
                        await update.callback_query.answer("❌ Ошибка!")
                    else:
                        raise edit_error
            else:
                await update.message.reply_text(
                    error_msg,
                    reply_markup=reply_markup
                )
            logger.error(f"Telegram bot error: {e}")
    
    async def send_subtitle_response(self, telegram_user_id, subtitle_text):
        logger.info(f"Subtitle response logged for user {telegram_user_id}: {subtitle_text}")
    
    async def send_key_response(self, telegram_user_id, key_type):
        logger.info(f"Key response logged for user {telegram_user_id}: {key_type}")
    

    
    async def start(self):
        if not self.bot_token:
            logger.error("Telegram bot token not configured")
            return
        
        logger.info(f"Initializing Telegram bot with token: {self.bot_token[:10]}...")
        self.application = Application.builder().token(self.bot_token).build()
        
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("pause", self.pause_command))
        self.application.add_handler(CallbackQueryHandler(self.button_callback))
        
        logger.info("Starting Telegram bot...")
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling()
        logger.info("Telegram bot started successfully")
        
        # Keep the bot running
        try:
            await self.application.updater.idle()
        except asyncio.CancelledError:
            pass
    
    async def stop(self):
        if self.application:
            logger.info("Stopping Telegram bot...")
            await self.application.updater.stop()
            await self.application.stop()
            await self.application.shutdown()
            logger.info("Telegram bot stopped") 
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
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        logger.info(f"Start command received from user {update.effective_user.id}")
        
        keyboard = [
            [InlineKeyboardButton("📸 Сделать скриншот", callback_data='take_screenshot')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "🎬 Бот управления скриншотами\n\n"
            "Нажмите кнопку ниже, чтобы сделать скриншот:",
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
    
    async def take_screenshot(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            await self.screenshot_server.broadcast_screenshot_command()
            
            keyboard = [
                [InlineKeyboardButton("📸 Сделать скриншот", callback_data='take_screenshot')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            message = "📸 Команда скриншота отправлена всем подключенным клиентам!"
            
            if hasattr(update, 'callback_query'):
                await update.callback_query.edit_message_text(
                    message,
                    reply_markup=reply_markup
                )
            else:
                await update.message.reply_text(
                    message,
                    reply_markup=reply_markup
                )
            
            logger.info(f"Screenshot command sent via Telegram by user {update.effective_user.id}")
        
        except Exception as e:
            error_msg = f"❌ Ошибка отправки команды скриншота: {str(e)}"
            keyboard = [
                [InlineKeyboardButton("📸 Сделать скриншот", callback_data='take_screenshot')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            if hasattr(update, 'callback_query'):
                await update.callback_query.edit_message_text(
                    error_msg,
                    reply_markup=reply_markup
                )
            else:
                await update.message.reply_text(
                    error_msg,
                    reply_markup=reply_markup
                )
            logger.error(f"Telegram bot error: {e}")
    

    
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
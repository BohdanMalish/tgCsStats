"""
Головний файл CS2 Stats Telegram Bot
"""
import asyncio
import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telegram import Bot

# Імпорти наших модулів
from src.models.user import UserDatabase
from src.services.steam_api import SteamAPI
from src.services.daily_reports import DailyReportsService
from src.services.scheduler import TaskScheduler
from src.handlers.bot_handlers import BotHandlers

# Конфігурація
import os

# Завжди використовуємо змінні оточення (для Railway/Docker)
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
STEAM_API_KEY = os.getenv("STEAM_API_KEY")
DATABASE_PATH = os.getenv("DATABASE_PATH", "/app/data/bot_database.db")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
DAILY_REPORT_TIME = os.getenv("DAILY_REPORT_TIME", "10:00")

# Додаткова діагностика
print(f"🔍 DEBUG: os.environ keys: {list(os.environ.keys())}")
print(f"🔍 DEBUG: TELEGRAM_BOT_TOKEN exists: {'TELEGRAM_BOT_TOKEN' in os.environ}")
print(f"🔍 DEBUG: STEAM_API_KEY exists: {'STEAM_API_KEY' in os.environ}")

# Fallback для локальної розробки
if not TELEGRAM_BOT_TOKEN:
    try:
        from config import TELEGRAM_BOT_TOKEN, STEAM_API_KEY
    except ImportError:
        TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN"
        STEAM_API_KEY = "YOUR_STEAM_API_KEY"


def setup_logging():
    """Налаштування логування"""
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=getattr(logging, LOG_LEVEL, logging.INFO)
    )
    
    # Зменшуємо логи від httpx та telegram
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('telegram').setLevel(logging.WARNING)
    
    return logging.getLogger(__name__)


async def error_handler(update, context):
    """Обробник помилок"""
    logger = logging.getLogger(__name__)
    logger.error(f"Update {update} caused error {context.error}")
    
    if update and update.message:
        await update.message.reply_text(
            "😅 Вибач, сталася помилка! Спробуй пізніше або зверніться до розробника."
        )


def main():
    """Головна функція запуску бота"""
    logger = setup_logging()
    
    # Діагностика змінних оточення
    logger.info(f"🔍 Діагностика змінних оточення:")
    logger.info(f"   TELEGRAM_BOT_TOKEN: {'✅ Встановлено' if TELEGRAM_BOT_TOKEN and TELEGRAM_BOT_TOKEN != 'YOUR_BOT_TOKEN' else '❌ Не встановлено'}")
    logger.info(f"   STEAM_API_KEY: {'✅ Встановлено' if STEAM_API_KEY and STEAM_API_KEY != 'YOUR_STEAM_API_KEY' else '❌ Не встановлено'}")
    logger.info(f"   DATABASE_PATH: {DATABASE_PATH}")
    logger.info(f"   LOG_LEVEL: {LOG_LEVEL}")
    logger.info(f"   DAILY_REPORT_TIME: {DAILY_REPORT_TIME}")
    
    # Перевіряємо конфігурацію
    if not TELEGRAM_BOT_TOKEN or TELEGRAM_BOT_TOKEN == "YOUR_BOT_TOKEN":
        logger.error("❌ Не встановлено TELEGRAM_BOT_TOKEN! Перевір змінні оточення в Railway")
        return
    
    if not STEAM_API_KEY or STEAM_API_KEY == "YOUR_STEAM_API_KEY":
        logger.error("❌ Не встановлено STEAM_API_KEY! Перевір змінні оточення в Railway")
        return
    
    logger.info("🚀 Запускаю CS2 Stats Bot...")
    
    # Ініціалізуємо компоненти
    user_db = UserDatabase(DATABASE_PATH)
    steam_api = SteamAPI(STEAM_API_KEY)
    
    # Створюємо додаток
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Ініціалізуємо сервіс щоденних звітів
    daily_reports_service = DailyReportsService(user_db, steam_api, application.bot)
    bot_handlers = BotHandlers(user_db, steam_api, daily_reports_service)
    
    # Ініціалізуємо планувальник
    scheduler = TaskScheduler(daily_reports_service)
    
    # Реєструємо обробники команд
    application.add_handler(CommandHandler("start", bot_handlers.start_command))
    application.add_handler(CommandHandler("help", bot_handlers.help_command))
    application.add_handler(CommandHandler("steam", bot_handlers.steam_command))
    application.add_handler(CommandHandler("stats", bot_handlers.stats_command))
    application.add_handler(CommandHandler("detailed_stats", bot_handlers.detailed_stats_command))
    application.add_handler(CommandHandler("add_friend", bot_handlers.add_friend_command))
    application.add_handler(CommandHandler("remove_friend", bot_handlers.remove_friend_command))
    application.add_handler(CommandHandler("friends_stats", bot_handlers.friends_stats_command))
    application.add_handler(CommandHandler("compare", bot_handlers.compare_command))
    application.add_handler(CommandHandler("daily_report", bot_handlers.daily_report_command))
    application.add_handler(CommandHandler("report_settings", bot_handlers.report_settings_command))
    application.add_handler(CommandHandler("about", bot_handlers.about_command))
    
    # Обробник помилок
    application.add_error_handler(error_handler)
    
    logger.info("✅ Бот налаштовано! Доступні команди:")
    logger.info("   /start - початок роботи")
    logger.info("   /help - довідка")
    logger.info("   /steam - встановити Steam ID")
    logger.info("   /stats - базова статистика")
    logger.info("   /detailed_stats - детальна статистика")
    logger.info("   /add_friend - додати друга")
    logger.info("   /remove_friend - видалити друга")
    logger.info("   /friends_stats - рейтинг друзів")
    logger.info("   /compare - порівняти з гравцем")
    logger.info("   /daily_report - щоденний звіт")
    logger.info("   /report_settings - налаштування звітів")
    logger.info("   /about - про бота")
    
    # Запускаємо планувальник
    try:
        scheduler.start(DAILY_REPORT_TIME)
    except Exception as e:
        logger.warning(f"⚠️ Не вдалося запустити планувальник: {e}")
    
    # Запускаємо бота
    try:
        logger.info("🎮 Бот запущено! Натисни Ctrl+C для зупинки")
        application.run_polling(allowed_updates=['message', 'callback_query'])
    except KeyboardInterrupt:
        logger.info("🛑 Бот зупинено користувачем")
        scheduler.stop()
    except Exception as e:
        logger.error(f"❌ Критична помилка: {e}")
        scheduler.stop()


if __name__ == '__main__':
    main()

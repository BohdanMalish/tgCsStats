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

# Хардкодимо змінні для тестування
TELEGRAM_BOT_TOKEN = "8343208198:AAE3dC1er-xa9risTj26IEA6b-A4vPGjxWQ"
STEAM_API_KEY = "6629403219DD2ADCA0D3F552F03F92A8"
DATABASE_PATH = os.getenv("DATABASE_PATH", "/app/data/bot_database.db")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
DAILY_REPORT_TIME = os.getenv("DAILY_REPORT_TIME", "10:00")

# Автоматично визначаємо Railway домен
def get_railway_domain():
    project_name = os.getenv("RAILWAY_PROJECT_NAME", "")
    environment_name = os.getenv("RAILWAY_ENVIRONMENT_NAME", "")
    if project_name and environment_name:
        return f"{project_name}-{environment_name}.up.railway.app"
    return "adorable-art-production.up.railway.app"  # Fallback

APP_DOMAIN = get_railway_domain()
PORT = int(os.getenv("PORT", "8080"))

print("🔧 Using hardcoded API keys for testing")


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
    logger.info(f"   STEAM_API_KEY: {'✅ Встановлено в коді' if STEAM_API_KEY and STEAM_API_KEY != 'YOUR_STEAM_API_KEY' else '❌ Не встановлено'}")
    logger.info(f"   APP_DOMAIN: {APP_DOMAIN}")
    logger.info(f"   PORT: {PORT}")
    logger.info(f"   DATABASE_PATH: {DATABASE_PATH}")
    logger.info(f"   LOG_LEVEL: {LOG_LEVEL}")
    logger.info(f"   DAILY_REPORT_TIME: {DAILY_REPORT_TIME}")
    
    # Перевіряємо конфігурацію
    if not TELEGRAM_BOT_TOKEN or TELEGRAM_BOT_TOKEN == "YOUR_BOT_TOKEN":
        logger.error("❌ Не встановлено TELEGRAM_BOT_TOKEN! Перевір змінні оточення в Railway")
        return
    
    if not STEAM_API_KEY or STEAM_API_KEY == "YOUR_STEAM_API_KEY":
        logger.error("❌ Не встановлено STEAM_API_KEY! Перевір код в main.py")
        return
    
    logger.info("🚀 Запускаю CS2 Stats Bot...")
    
    # Ініціалізуємо компоненти
    user_db = UserDatabase(DATABASE_PATH)
    steam_api = SteamAPI(STEAM_API_KEY)
    
    # Створюємо додаток
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Ініціалізуємо сервіс щоденних звітів
    daily_reports_service = DailyReportsService(user_db, steam_api, application.bot)
    bot_handlers = BotHandlers(user_db, steam_api, daily_reports_service, APP_DOMAIN, STEAM_API_KEY)
    
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

    application.add_handler(CommandHandler("steam_login", bot_handlers.steam_login_command))
    application.add_handler(CommandHandler("steam_manual", bot_handlers.steam_manual_command))
    application.add_handler(CommandHandler("faceit_stats", bot_handlers.faceit_stats_command))
    application.add_handler(CommandHandler("faceit_matches", bot_handlers.faceit_matches_command))
    
    # Обробник помилок
    application.add_error_handler(error_handler)
    
    logger.info("✅ Бот налаштовано! Доступні команди:")
    logger.info("   /start - початок роботи")
    logger.info("   /help - довідка")
    logger.info("   /steam - встановити Steam ID")
    logger.info("   /stats - Steam статистика")
    logger.info("   /detailed_stats - детальна статистика")
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
    
    # Запускаємо веб-сервер для Steam OAuth
    web_server = None
    try:
        from src.web_server import WebServer
        web_server = WebServer(bot_handlers, STEAM_API_KEY, APP_DOMAIN, PORT)
        logger.info("🌐 Веб-сервер для Steam OAuth готовий")
        
    except Exception as e:
        logger.warning(f"⚠️ Не вдалося налаштувати веб-сервер: {e}")
    
    # Запускаємо бота
    try:
        logger.info("🎮 Бот запущено! Натисни Ctrl+C для зупинки")
        
        # Запускаємо веб-сервер якщо він створений
        if web_server:
            # Для Railway запускаємо веб-сервер як основний процес
            # а бота в окремому потоці
            import threading
            def start_bot():
                try:
                    application.run_polling(allowed_updates=['message', 'callback_query'])
                except Exception as e:
                    logger.error(f"Помилка бота: {e}")
            
            # Запускаємо бота в окремому потоці
            bot_thread = threading.Thread(target=start_bot, daemon=True)
            bot_thread.start()
            logger.info("🤖 Бот запущено в окремому потоці")
            
            # Запускаємо веб-сервер в основному потоці
            import asyncio
            asyncio.run(web_server.start_server())
        else:
            # Запускаємо тільки бота
            application.run_polling(allowed_updates=['message', 'callback_query'])
            
    except KeyboardInterrupt:
        logger.info("🛑 Бот зупинено користувачем")
        scheduler.stop()
    except Exception as e:
        logger.error(f"❌ Критична помилка: {e}")
        scheduler.stop()


if __name__ == '__main__':
    main()

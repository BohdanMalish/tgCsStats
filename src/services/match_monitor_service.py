"""
Сервіс для запуску моніторингу матчів
"""
import asyncio
import os
import sys
from pathlib import Path

# Додаємо кореневу папку проекту до шляху
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.models.user import UserDatabase
from src.services.match_monitor import MatchMonitor


async def start_match_monitoring():
    """Запустити моніторинг матчів"""
    try:
        # Ініціалізуємо базу даних
        db_path = os.path.join(project_root, "data", "users.db")
        user_db = UserDatabase(db_path)
        
        # Отримуємо токен бота з змінних середовища
        bot_token = os.getenv("BOT_TOKEN")
        if not bot_token:
            print("❌ BOT_TOKEN не знайдено в змінних середовища")
            return
        
        # Отримуємо Steam API ключ
        steam_api_key = os.getenv("STEAM_API_KEY")
        if not steam_api_key:
            print("❌ STEAM_API_KEY не знайдено в змінних середовища")
            return
        
        # Створюємо монітор
        monitor = MatchMonitor(steam_api_key, bot_token, user_db)
        
        print("🎮 Запуск моніторингу матчів...")
        print("📊 Перевірка кожні 5 хвилин")
        print("👥 Користувачі з увімкненим моніторингом:")
        
        # Показуємо користувачів з увімкненим моніторингом
        users_with_monitoring = user_db.get_users_with_monitoring()
        if users_with_monitoring:
            for user in users_with_monitoring:
                print(f"   • {user.username or user.telegram_id} (Steam: {user.steam_id})")
        else:
            print("   Немає користувачів з увімкненим моніторингом")
        
        print("\n🔄 Моніторинг запущено. Натисніть Ctrl+C для зупинки.")
        
        # Запускаємо моніторинг
        await monitor.start_monitoring()
        
    except KeyboardInterrupt:
        print("\n🛑 Моніторинг зупинено користувачем")
    except Exception as e:
        print(f"❌ Помилка моніторингу: {e}")


if __name__ == "__main__":
    asyncio.run(start_match_monitoring())

#!/bin/bash

# Швидкий тест Docker образу
echo "🧪 Тестування Docker образу..."

# Збираємо образ
echo "🔨 Збираю образ..."
docker build -t cs2-stats-bot:test .

# Тестуємо основні імпорти
echo "🔍 Тестую імпорти..."
docker run --rm \
  -e TELEGRAM_BOT_TOKEN="test_token" \
  -e STEAM_API_KEY="test_key" \
  -e DATABASE_PATH="/app/data/test.db" \
  --entrypoint="" \
  cs2-stats-bot:test \
  python -c "
import sys
sys.path.append('/app')
try:
    from src.models.user import UserDatabase, User
    from src.services.steam_api import SteamAPI
    from src.services.daily_reports import DailyReportsService
    from src.handlers.bot_handlers import BotHandlers
    print('✅ Всі імпорти працюють')
except ImportError as e:
    print(f'❌ Помилка імпорту: {e}')
    sys.exit(1)
"

if [ $? -eq 0 ]; then
    echo "✅ Docker образ працює правильно!"
    
    # Показуємо розмір образу
    echo "📊 Розмір образу:"
    docker images cs2-stats-bot:test
    
    # Очищаємо тестовий образ
    echo "🧹 Очищаю тестовий образ..."
    docker rmi cs2-stats-bot:test
else
    echo "❌ Помилка в Docker образі!"
    exit 1
fi

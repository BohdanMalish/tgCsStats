#!/bin/bash

# Скрипт для перевірки готовності до Railway деплою

echo "🚂 Перевірка готовності до Railway деплою..."

# Перевіряємо наявність необхідних файлів
echo "📁 Перевіряю файли..."

required_files=(
    "Dockerfile"
    "requirements.txt" 
    "main.py"
    "railway.json"
    "RAILWAY_DEPLOY.md"
)

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ $file - відсутній!"
        exit 1
    fi
done

# Перевіряємо структуру проекту
echo ""
echo "📂 Перевіряю структуру проекту..."

if [ -d "src" ]; then
    echo "✅ src/"
else
    echo "❌ src/ - відсутня!"
    exit 1
fi

if [ -f "src/models/user.py" ] && [ -f "src/services/steam_api.py" ] && [ -f "src/handlers/bot_handlers.py" ]; then
    echo "✅ Всі основні модулі присутні"
else
    echo "❌ Деякі модулі відсутні!"
    exit 1
fi

# Перевіряємо Python залежності
echo ""
echo "🐍 Перевіряю Python залежності..."

if python3 -c "
import sys
sys.path.append('src')
try:
    from models.user import UserDatabase
    from services.steam_api import SteamAPI
    from services.daily_reports import DailyReportsService
    from handlers.bot_handlers import BotHandlers
    print('✅ Всі імпорти працюють')
except ImportError as e:
    print(f'❌ Помилка імпорту: {e}')
    sys.exit(1)
" 2>/dev/null; then
    echo "✅ Python модулі готові"
else
    echo "⚠️ Встанови залежності: pip install -r requirements.txt"
fi

# Перевіряємо Docker
echo ""
echo "🐳 Перевіряю Docker..."

if command -v docker &> /dev/null; then
    echo "✅ Docker встановлено"
    
    # Тестуємо збірку образу
    echo "🔨 Тестую збірку Docker образу..."
    if docker build -t railway-test . &>/dev/null; then
        echo "✅ Docker образ збирається успішно"
        
        # Очищаємо тестовий образ
        docker rmi railway-test &>/dev/null
    else
        echo "❌ Помилка збірки Docker образу"
        exit 1
    fi
else
    echo "⚠️ Docker не встановлено (не критично для Railway)"
fi

# Перевіряємо Git
echo ""
echo "📋 Перевіряю Git..."

if git status &>/dev/null; then
    echo "✅ Git репозиторій ініціалізовано"
    
    # Перевіряємо чи є uncommitted зміни
    if git diff-index --quiet HEAD --; then
        echo "✅ Всі зміни закоммічено"
    else
        echo "⚠️ Є незбережені зміни:"
        git status --porcelain
        echo ""
        echo "💡 Рекомендую закоммітити зміни перед деплоєм:"
        echo "   git add ."
        echo "   git commit -m 'Ready for Railway deploy'"
        echo "   git push origin main"
    fi
else
    echo "❌ Git репозиторій не ініціалізовано"
    echo "💡 Ініціалізуй Git:"
    echo "   git init"
    echo "   git add ."
    echo "   git commit -m 'Initial commit'"
fi

echo ""
echo "🎯 Перевірка завершена!"
echo ""
echo "📋 Наступні кроки для Railway деплою:"
echo "1. 🔑 Отримай ключі:"
echo "   • Telegram Bot Token: https://t.me/BotFather"
echo "   • Steam API Key: https://steamcommunity.com/dev/apikey"
echo ""
echo "2. 🚂 Деплой на Railway:"
echo "   • Йди на https://railway.app"
echo "   • New Project → Deploy from GitHub repo"
echo "   • Вибери цей репозиторій"
echo "   • Встанови змінні оточення"
echo ""
echo "3. 📖 Детальна інструкція:"
echo "   • Читай RAILWAY_DEPLOY.md"
echo ""
echo "✅ Проект готовий до Railway деплою!"

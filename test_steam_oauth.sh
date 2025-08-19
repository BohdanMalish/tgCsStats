#!/bin/bash

echo "🧪 Тестування Steam OAuth локально..."

# Перевіряємо чи запущений Docker
if ! docker ps > /dev/null 2>&1; then
    echo "❌ Docker не запущений!"
    exit 1
fi

# Перевіряємо змінні оточення
if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    echo "❌ TELEGRAM_BOT_TOKEN не встановлено!"
    echo "Встановіть: export TELEGRAM_BOT_TOKEN=your_token"
    exit 1
fi

# Встановлюємо APP_DOMAIN для локального тестування
export APP_DOMAIN="localhost:3000"

echo "✅ Змінні оточення встановлено:"
echo "   TELEGRAM_BOT_TOKEN: ${TELEGRAM_BOT_TOKEN:0:10}..."
echo "   APP_DOMAIN: $APP_DOMAIN"
echo "   STEAM_API_KEY: ✅ Встановлено в коді (main.py)"

# Зупиняємо попередній контейнер якщо є
echo "🛑 Зупиняємо попередній контейнер..."
docker-compose down

# Запускаємо новий контейнер
echo "🚀 Запускаємо бота..."
docker-compose up --build

echo "✅ Бот запущений!"
echo "🌐 Веб-сервер доступний на: http://localhost:3000"
echo "🔐 Steam OAuth callback: http://localhost:3000/steam/callback"
echo ""
echo "📱 Тестування:"
echo "1. Відправ /steam_login боту"
echo "2. Натисни кнопку 'Увійти через Steam'"
echo "3. Авторизуйся в Steam"
echo "4. Перевір callback URL"

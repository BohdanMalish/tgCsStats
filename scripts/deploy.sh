#!/bin/bash

# Скрипт першого деплою CS2 Stats Bot
# Використання: ./scripts/deploy.sh

set -e

echo "🚀 Початок деплою CS2 Stats Bot..."

# Перевіряємо наявність Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker не встановлено!"
    echo "Встанови Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

# Перевіряємо наявність Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose не встановлено!"
    echo "Встанови Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi

# Перевіряємо чи є .env файл
if [ ! -f ".env" ]; then
    echo "⚙️ Створюю .env файл..."
    if [ -f "env.example" ]; then
        cp env.example .env
        echo "✅ Скопійовано env.example в .env"
        echo ""
        echo "🔧 ВАЖЛИВО! Відредагуй файл .env та встав свої ключі:"
        echo "   - TELEGRAM_BOT_TOKEN (отримай у @BotFather)"
        echo "   - STEAM_API_KEY (отримай на https://steamcommunity.com/dev/apikey)"
        echo ""
        echo "Після редагування .env запусти скрипт знову."
        exit 0
    else
        echo "❌ Файл env.example не знайдено!"
        exit 1
    fi
fi

# Перевіряємо чи налаштовані ключі
if grep -q "YOUR_BOT_TOKEN" .env || grep -q "YOUR_STEAM_API_KEY" .env; then
    echo "❌ Потрібно налаштувати ключі в файлі .env!"
    echo "Відредагуй .env та встав:"
    echo "   - TELEGRAM_BOT_TOKEN"
    echo "   - STEAM_API_KEY"
    exit 1
fi

# Створюємо необхідні директорії
echo "📁 Створюю директорії..."
mkdir -p data logs
chmod 755 data logs

# Перевіряємо чи контейнер вже запущений
if docker-compose ps | grep -q "Up"; then
    echo "⚠️ Контейнер вже запущений. Зупиняю..."
    docker-compose down
fi

# Збираємо та запускаємо
echo "🔨 Збираю Docker образ..."
docker-compose build

echo "🚀 Запускаю бота..."
docker-compose up -d

# Чекаємо трохи та перевіряємо статус
echo "⏳ Чекаю запуску..."
sleep 10

if docker-compose ps | grep -q "Up"; then
    echo "✅ Бот успішно запущено!"
    
    echo ""
    echo "📋 Корисні команди:"
    echo "   docker-compose logs -f cs2-stats-bot  # Переглянути логи"
    echo "   docker-compose restart               # Перезапустити"
    echo "   docker-compose down                  # Зупинити"
    echo "   ./scripts/update_bot.sh              # Оновити"
    echo ""
    
    echo "📊 Статус контейнера:"
    docker-compose ps
    
    echo ""
    echo "📋 Останні логи:"
    docker-compose logs --tail=10 cs2-stats-bot
    
else
    echo "❌ Помилка запуску!"
    echo "Перевір логи:"
    docker-compose logs cs2-stats-bot
    exit 1
fi

echo ""
echo "🎉 Деплой завершено! Бот працює 24/7"
echo "🔗 Знайди свого бота в Telegram та надішли /start"

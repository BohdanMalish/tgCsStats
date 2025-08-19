#!/bin/bash

# Скрипт автоматичного оновлення CS2 Stats Bot
# Використання: ./scripts/update_bot.sh

set -e  # Зупинити при помилці

echo "🔄 Початок оновлення CS2 Stats Bot..."

# Перевіряємо чи ми в правильній директорії
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ Помилка: docker-compose.yml не знайдено!"
    echo "Запускай скрипт з кореневої директорії проекту"
    exit 1
fi

# Створюємо backup бази даних
if [ -f "data/bot_database.db" ]; then
    echo "💾 Створюю backup бази даних..."
    BACKUP_NAME="data/backup_$(date +%Y%m%d_%H%M%S).db"
    cp data/bot_database.db "$BACKUP_NAME"
    echo "✅ Backup створено: $BACKUP_NAME"
fi

# Зупиняємо контейнер
echo "🛑 Зупиняю бота..."
docker-compose down

# Оновлюємо код
echo "📥 Завантажую оновлення..."
git fetch origin
git pull origin main

# Перебудовуємо образ
echo "🔨 Перебудовую Docker образ..."
docker-compose build --no-cache

# Запускаємо оновлений бот
echo "🚀 Запускаю оновленого бота..."
docker-compose up -d

# Перевіряємо статус
echo "🔍 Перевіряю статус..."
sleep 5
if docker-compose ps | grep -q "Up"; then
    echo "✅ Бот успішно оновлено та запущено!"
    
    # Показуємо логи останніх 20 рядків
    echo "📋 Останні логи:"
    docker-compose logs --tail=20 cs2-stats-bot
else
    echo "❌ Помилка! Бот не запустився."
    echo "Перевір логи: docker-compose logs cs2-stats-bot"
    exit 1
fi

echo "🎉 Оновлення завершено!"

# 🔐 Налаштування Steam OAuth для Railway

## 📋 Необхідні змінні оточення

Додай ці змінні в Railway Dashboard → Variables:

### Обов'язкові:
```
TELEGRAM_BOT_TOKEN=8343208198:AAE3dC1er-xa9risTj26IEA6b-A4vPGjxWQ
APP_DOMAIN=your-app.railway.app
```

### Опціональні:
```
LOG_LEVEL=INFO
DAILY_REPORT_TIME=10:00
DATABASE_PATH=/app/data/bot_database.db
PORT=3000
```

**ℹ️ Примітка:** `STEAM_API_KEY` вже встановлено в коді (`main.py`), тому не потрібно додавати його як змінну оточення.

## 🔧 Кроки налаштування:

### 1. Отримай свій Railway домен
- Зайди в Railway Dashboard
- Виберіть свій проект
- Скопіюй домен (наприклад: `tg-cs-stats-production.up.railway.app`)

### 2. Встанови змінну APP_DOMAIN
```
APP_DOMAIN=tg-cs-stats-production.up.railway.app
```

### 3. Перезапусти застосунок
- Railway автоматично перезапустить застосунок після зміни змінних

## ✅ Перевірка роботи:

1. Відправ команду `/steam_login` боту
2. Натисни кнопку "🔐 Увійти через Steam"
3. Авторизуйся в Steam
4. Повернися в бота

## 🐛 Якщо не працює:

### Перевір логи:
```bash
railway logs
```

### Перевір змінні:
```bash
railway variables
```

### Тестуй веб-сервер:
```
https://your-app.railway.app/
```
Повинно показати: "CS2 Stats Bot - Steam OAuth Callback Server"

## 🔍 Діагностика:

Бот покаже діагностику при запуску:
```
🔍 Діагностика змінних оточення:
   TELEGRAM_BOT_TOKEN: ✅ Встановлено
   STEAM_API_KEY: ✅ Встановлено  
   APP_DOMAIN: your-app.railway.app
   PORT: 3000
   🌐 Веб-сервер запущено на порту 3000
```

## 🚀 Готово!

Після налаштування Steam OAuth буде повністю функціональним!

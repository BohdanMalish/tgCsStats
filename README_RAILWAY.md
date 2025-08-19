# 🚂 Railway Деплой - CS2 Stats Bot

## ⚡ За 5 хвилин до запуску (БЕЗКОШТОВНО)

### 🎯 Що отримаєш:
- 🤖 **Telegram бот** що працює 24/7
- 📊 **Детальна статистика** CS2 через Steam API
- 🏆 **Рейтинги друзів** та Impact Score
- 📅 **Щоденні звіти** автоматично о 10:00
- 💰 **Безкоштовно** ($5 кредитів/місяць, витрачаєш ~$2-3)

---

## 🚀 Крок 1: Отримай ключі (2 хвилини)

### Telegram Bot Token:
1. Напиши [@BotFather](https://t.me/BotFather)
2. `/newbot` → вибери ім'я бота
3. Скопіюй токен: `1234567890:ABCdef...`

### Steam API Key:
1. [steamcommunity.com/dev/apikey](https://steamcommunity.com/dev/apikey)
2. Domain Name: `localhost`
3. Скопіюй ключ: `1234567890ABCDEF...`

---

## 🚂 Крок 2: Деплой на Railway (3 хвилини)

### 1. Підготовка GitHub
```bash
# Fork цей репозиторій на GitHub
# Або clone собі:
git clone https://github.com/your-username/tg-cs-stats.git
cd tg-cs-stats
git add .
git commit -m "Ready for Railway"
git push origin main
```

### 2. Railway деплой
1. **Йди на** [railway.app](https://railway.app)
2. **Зареєструйся** через GitHub
3. **New Project** → **Deploy from GitHub repo**
4. **Вибери** `tg-cs-stats` репозиторій

### 3. Змінні оточення
У розділі **Variables** додай:

| Змінна | Значення |
|--------|----------|
| `TELEGRAM_BOT_TOKEN` | `твій_токен_від_BotFather` |
| `STEAM_API_KEY` | `твій_ключ_від_Steam` |
| `LOG_LEVEL` | `INFO` |
| `DAILY_REPORT_TIME` | `10:00` |
| `DATABASE_PATH` | `/app/data/bot_database.db` |

### 4. Деплой
- **Натисни** "Deploy"
- **Чекай** 2-3 хвилини
- **Переглядай** логи в розділі "Deployments"

---

## ✅ Крок 3: Тестування

1. **Знайди** бота в Telegram за username
2. **Надішли** `/start`
3. **Встанови** Steam ID: `/steam твій_steam_id`
4. **Переглянь** статистику: `/stats`

### Приклад використання:
```
/start
/steam 76561198123456789
/stats
/add_friend 76561198987654321
/friends_stats
/daily_report
```

---

## 📊 Моніторинг

### Railway Dashboard:
- **Deployments** - статус та логи
- **Metrics** - CPU, RAM, мережа  
- **Usage** - витрачені кредити
- **Variables** - змінні оточення

### Логи бота:
```
🚀 Запускаю CS2 Stats Bot...
✅ Бот налаштовано! Доступні команди:
🎮 Бот запущено!
```

---

## 🔄 Автоматичні оновлення

Railway автоматично оновлює бота:
```bash
# Внеси зміни в код
git add .
git commit -m "Покращення бота"  
git push origin main

# Railway автоматично перезапустить з новими змінами!
```

---

## 💰 Вартість

**Безкоштовний план Railway:**
- 💳 $5 кредитів щомісяця
- 🤖 Твій бот витрачає ~$2-3/місяць
- 💰 **Залишається $2-3** на інші проекти

**Що впливає на вартість:**
- ✅ CPU (мінімальне використання)
- ✅ RAM (~50-100MB)
- ✅ Мережа (тільки API запити)
- ✅ База даних (SQLite в контейнері)

---

## ❓ Troubleshooting

### Бот не запускається:
```bash
# Перевір в Railway логах:
❌ "Invalid token" → перевір TELEGRAM_BOT_TOKEN
❌ "Steam API Key invalid" → перевір STEAM_API_KEY  
❌ "Permission denied" → перевір змінні оточення
```

### Бот не відповідає:
1. Railway Dashboard → Deployments → перевір статус
2. Переглянь останні логи на помилки
3. Restart deployment якщо потрібно

### Закінчились кредити:
1. Usage розділ покаже витрати
2. Можна додати картку для $5/міс
3. Або оптимізувати (наш код вже оптимальний)

---

## 🎉 Готово!

**Твій бот працює 24/7 в хмарі!**

### Що він вміє:
- 📊 Показувати детальну статистику CS2
- 🧠 Рахувати Impact Score (власний алгоритм)
- 👥 Створювати рейтинги друзів
- ⚔️ Порівнювати гравців
- 📅 Відправляти щоденні звіти о 10:00
- 💡 Давати персональні поради для покращення

### Основні команди:
- `/start` - почати роботу
- `/steam STEAM_ID` - встановити Steam ID
- `/stats` - базова статистика  
- `/detailed_stats` - детальна статистика
- `/add_friend STEAM_ID` - додати друга
- `/friends_stats` - рейтинг друзів
- `/daily_report` - щоденний звіт
- `/compare STEAM_ID` - порівняти з гравцем

---

## 🔗 Корисні посилання

- [Railway Dashboard](https://railway.app/dashboard)
- [Telegram BotFather](https://t.me/BotFather)  
- [Steam API Key](https://steamcommunity.com/dev/apikey)
- [Повна документація](README.md)
- [Детальна інструкція](RAILWAY_DEPLOY.md)

---

**🎮 Вітаю! Твій CS2 Stats Bot готовий змагатися! 🏆**

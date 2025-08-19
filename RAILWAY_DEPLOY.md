# 🚂 Деплой CS2 Stats Bot на Railway

## 🎯 Покрокова інструкція (5 хвилин)

### Крок 1: Підготовка ключів

**Отримай Telegram Bot Token:**
1. Напиши [@BotFather](https://t.me/BotFather)
2. Відправ `/newbot`
3. Вибери ім'я та username бота
4. **Скопіюй токен** (виглядає як `1234567890:ABCdef...`)

**Отримай Steam API Key:**
1. Йди на [steamcommunity.com/dev/apikey](https://steamcommunity.com/dev/apikey)
2. Увійди в Steam
3. Заповни форму (Domain Name: `localhost`)
4. **Скопіюй ключ** (виглядає як `1234567890ABCDEF...`)

### Крок 2: Створення проекту на Railway

1. **Відкрий** [railway.app](https://railway.app)
2. **Зареєструйся** через GitHub
3. **Натисни** "New Project"
4. **Вибери** "Deploy from GitHub repo"
5. **Підключи** цей репозиторій `tg-cs-stats`

### Крок 3: Налаштування змінних оточення

У розділі **Variables** додай ці змінні:

```env
TELEGRAM_BOT_TOKEN=твій_токен_від_BotFather
STEAM_API_KEY=твій_ключ_від_Steam
LOG_LEVEL=INFO
DAILY_REPORT_TIME=10:00
DATABASE_PATH=/app/data/bot_database.db
```

**Важливо:** Замість `твій_токен_від_BotFather` та `твій_ключ_від_Steam` встав реальні ключі!

### Крок 4: Деплой

1. **Натисни** "Deploy"
2. Railway автоматично:
   - Знайде Dockerfile
   - Збере образ
   - Запустить бота
3. **Чекай** 2-3 хвилини

### Крок 5: Перевірка

1. **Йди** в розділ "Deployments"
2. **Переглядай** логи - має бути:
   ```
   🚀 Запускаю CS2 Stats Bot...
   ✅ Бот налаштовано! Доступні команди:
   🎮 Бот запущено! Натисни Ctrl+C для зупинки
   ```
3. **Знайди** свого бота в Telegram
4. **Надішли** `/start`

## 🎉 Готово!

Твій бот тепер працює 24/7 на Railway!

## 📊 Моніторинг

### Перегляд логів:
- Відкрий проект на Railway
- Розділ "Deployments" → активний deployment
- Логи оновлюються в реальному часі

### Статистика використання:
- Розділ "Metrics" показує CPU, RAM, мережу
- Розділ "Usage" показує витрачені кредити

## 🔄 Автоматичні оновлення

Railway автоматично оновлює бота при кожному push:

```bash
# Внеси зміни в код
git add .
git commit -m "Покращення бота"
git push origin main

# Railway автоматично перезапустить бота з новими змінами!
```

## 💰 Використання кредитів

**Твій бот витрачає:**
- ~$0.05-0.10 на день
- ~$1.50-3.00 на місяць
- **Залишається $2-3.50** з безкоштовних $5

**Оптимізація:**
- Бот використовує мінімум ресурсів
- SQLite база даних (не потрібна окрема БД)
- Ефективне кешування API запитів

## 🛠 Налаштування домену (опціонально)

Railway надає безкоштовний домен:
1. Розділ "Settings" → "Domains"
2. "Generate Domain" 
3. Отримаєш щось типу `cs2-stats-bot-production.up.railway.app`

*Примітка: Для Telegram ботів домен не потрібен*

## ❓ Troubleshooting

### Бот не запускається:
```bash
# Перевір логи на Railway
# Найчастіші помилки:
❌ Invalid token - перевір TELEGRAM_BOT_TOKEN
❌ Steam API Key invalid - перевір STEAM_API_KEY
❌ Import errors - зв'яжись зі мною
```

### Бот не відповідає:
1. Перевір що deployment активний (зелений статус)
2. Переглянь останні логи на помилки
3. Спробуй команду `/start` ще раз

### Закінчились кредити:
1. Розділ "Usage" покаже витрати
2. Можна додати банківську карту для $5/міс
3. Або оптимізувати код (але наш вже оптимальний)

## 🔗 Корисні посилання

- [Railway Dashboard](https://railway.app/dashboard)
- [Railway Docs](https://docs.railway.app/)
- [Telegram BotFather](https://t.me/BotFather)
- [Steam API Key](https://steamcommunity.com/dev/apikey)

---

**🎮 Вітаю! Твій CS2 Stats Bot працює в хмарі 24/7!**

Тепер можеш:
- Додавати друзів: `/add_friend STEAM_ID`
- Дивитися статистику: `/stats`
- Отримувати щоденні звіти автоматично о 10:00
- Змагатися з друзями в рейтингу!

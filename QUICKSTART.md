# ⚡ Швидкий старт CS2 Stats Bot

## 🚀 За 5 хвилин до запуску!

### Крок 1: Отримай ключі

**Telegram Bot Token:**
1. Напиши [@BotFather](https://t.me/BotFather) в Telegram
2. Відправ `/newbot`
3. Вибери ім'я та username бота
4. Скопіюй токен (виглядає як `1234567890:ABCdef...`)

**Steam API Key:**
1. Йди на [steamcommunity.com/dev/apikey](https://steamcommunity.com/dev/apikey)
2. Увійди в Steam
3. Заповни форму (Domain Name: `localhost`)
4. Скопіюй ключ (виглядає як `1234567890ABCDEF...`)

### Крок 2: Деплой на сервер

#### 🐳 Варіант A: Docker (найпростіший)

```bash
# 1. Клонуй на сервер
git clone https://github.com/your-username/tg-cs-stats.git
cd tg-cs-stats

# 2. Запусти автоматичний деплой
./scripts/deploy.sh

# 3. Введи ключі коли попросить
# 4. Готово! 🎉
```

#### 🚂 Варіант B: Railway (БЕЗКОШТОВНО - рекомендовано)

```bash
# 1. Перевір готовність проекту
./scripts/railway-check.sh

# 2. Закоммітити зміни в GitHub
git add .
git commit -m "Ready for Railway"
git push origin main
```

**На Railway:**
1. **Зайди на [railway.app](https://railway.app)**
2. **New Project** → **Deploy from GitHub repo**
3. **Вибери** репозиторій `tg-cs-stats`
4. **Встанови змінні оточення:**
   - `TELEGRAM_BOT_TOKEN` = твій токен
   - `STEAM_API_KEY` = твій ключ  
   - `LOG_LEVEL` = `INFO`
   - `DAILY_REPORT_TIME` = `10:00`
5. **Railway автоматично деплоїть з Dockerfile!**

**💰 Вартість:** $0 (є $5 кредитів/місяць, бот витрачає ~$2-3)
**⏰ Час деплою:** 2-3 хвилини
**🔄 Автооновлення:** При кожному git push

[📋 **Детальна інструкція Railway**](RAILWAY_DEPLOY.md)

### Крок 3: Тестування

1. **Знайди бота в Telegram** за username
2. **Надішли** `/start`
3. **Встанови Steam ID:** `/steam твій_steam_id`
4. **Переглянь статистику:** `/stats`

## 📊 Основні команди

| Команда | Опис |
|---------|------|
| `/start` | Почати роботу |
| `/steam 76561198123456789` | Встановити Steam ID |
| `/stats` | Базова статистика |
| `/detailed_stats` | Детальна статистика |
| `/add_friend 76561198987654321` | Додати друга |
| `/friends_stats` | Рейтинг друзів |
| `/daily_report` | Щоденний звіт |

## 🔧 Управління ботом

```bash
# Переглянути логи
docker-compose logs -f cs2-stats-bot

# Перезапустити
docker-compose restart

# Зупинити
docker-compose down

# Оновити
./scripts/update_bot.sh
```

## ❓ Проблеми?

### Бот не відповідає
1. Перевір токен в `.env`
2. Переглянь логи: `docker-compose logs cs2-stats-bot`
3. Перезапусти: `docker-compose restart`

### Не отримує статистику
1. Перевір Steam API ключ
2. Переконайся що профіль Steam відкритий
3. Спробуй іншого гравця

### Помилка Docker
1. Перевір чи встановлено Docker
2. Перевір чи є права на запуск
3. Спробуй: `sudo docker-compose up -d`

## 💰 Вартість хостингу

| Платформа | Вартість/міс | Складність |
|-----------|--------------|------------|
| **Railway** | $5-10 | ⭐ |
| **DigitalOcean** | $5 | ⭐⭐ |
| **Heroku** | $7 | ⭐ |
| **VPS** | $3-5 | ⭐⭐⭐ |

## 🎯 Що далі?

1. **Додай друзів** командою `/add_friend`
2. **Налаштуй щоденні звіти** - вони приходять автоматично о 10:00
3. **Змагайся в рейтингу** з друзями
4. **Відстежуй прогрес** через Impact Score

## 🔗 Корисні посилання

- [Детальна інструкція деплою](DEPLOYMENT.md)
- [Інформація про щоденні звіти](DAILY_REPORTS.md)
- [Повна документація](README.md)
- [Отримати Telegram Bot Token](https://t.me/BotFather)
- [Отримати Steam API Key](https://steamcommunity.com/dev/apikey)

---

**Готово! 🎮 Твій бот працює 24/7 та відстежує статистику CS2!**

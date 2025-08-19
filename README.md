# 🎮 CS2 Stats Telegram Bot

Telegram бот для відстеження статистики Counter-Strike 2 та змагання з друзями!

## ✨ Особливості

- 📊 **Детальна статистика CS2** через Steam API
- 🧠 **Smart Impact Score** - власний алгоритм оцінки гравця
- 👥 **Система друзів** - додавай друзів та змагайся
- 🏆 **Рейтинги** - топ гравців серед твоїх друзів
- 🎯 **Порівняння** - порівнюй статистику з друзями
- ⚔️ **Статистика по зброї** - детальний аналіз
- 📅 **Щоденні звіти** - автоматичні звіти кожного ранку
- 💡 **Розумні поради** - персональні рекомендації для покращення гри

## 🚀 Швидкий старт

### 🚂 Варіант 1: Railway (рекомендовано - БЕЗКОШТОВНО)

```bash
# 1. Отримай ключі (Telegram Bot Token + Steam API Key)
# 2. Йди на railway.app та підключи цей GitHub репозиторій  
# 3. Встанови змінні оточення
# 4. Railway автоматично деплоїть з Dockerfile!
```

**Переваги Railway:**
- 💰 $5 кредитів/місяць (вистачить на бота)
- 🚀 Автоматичний деплой з GitHub
- 🔄 Не спить - працює 24/7
- 📊 Простий моніторинг

[**📋 Детальна інструкція Railway →**](RAILWAY_DEPLOY.md)

### 🐳 Варіант 2: Docker на своєму сервері

```bash
# 1. Клонуй репозиторій
git clone https://github.com/your-username/tg-cs-stats.git
cd tg-cs-stats

# 2. Запусти скрипт автоматичного деплою
./scripts/deploy.sh
```

### 💻 Варіант 3: Локальний запуск

```bash
# 1. Встановлення
git clone https://github.com/your-username/tg-cs-stats.git
cd tg-cs-stats
pip install -r requirements.txt

# 2. Конфігурація
cp config.example.py config.py
# Відредагуй config.py та встав свої ключі

# 3. Запуск
python main.py
```

## 🎯 Команди бота

### Основні
- `/start` - початок роботи з ботом
- `/help` - список всіх команд
- `/about` - інформація про бота

### Налаштування
- `/steam <Steam_ID>` - встановити свій Steam ID
- `/steam <nickname>` - встановити через нікнейм

### Статистика
- `/stats` - базова статистика
- `/detailed_stats` - детальна статистика з Impact Score
- `/weapon_stats` - статистика по зброї

### Друзі та рейтинги
- `/add_friend <Steam_ID>` - додати друга
- `/remove_friend <Steam_ID>` - видалити друга
- `/friends_stats` - рейтинг друзів
- `/leaderboard` - топ гравців
- `/compare <Steam_ID>` - порівняти з гравцем

### Щоденні звіти
- `/daily_report` - отримати щоденний звіт зараз
- `/report_settings` - налаштування автоматичних звітів

## 🧠 Impact Score Algorithm

Наш власний алгоритм оцінки ефективності гравця:

```
Impact Score = 
  K/D Ratio × 25% +
  Win Rate × 30% +
  Headshot % × 20% +
  Assists/Match × 15% +
  MVP % × 10%
```

### Чому саме ці показники?

- **Win Rate (30%)** - найважливіше це перемагати
- **K/D Ratio (25%)** - ефективність у вбивствах
- **Headshot % (20%)** - точність та майстерність
- **Assists/Match (15%)** - командна гра
- **MVP % (10%)** - лідерські якості

## 📊 Приклад використання

```
🎮 Статистика для PlayerName

📊 Основні показники:
• K/D Ratio: 1.23
• Win Rate: 67%
• Зіграно матчів: 145
• Перемог: 97

🎯 Точність:
• Headshot %: 45%
• Загальна точність: 23%

🏆 Досягнення:
• MVP раундів: 26 (18%)
• Асистів на матч: 3.2

⚡ Impact Score: 73.5/100
```

### 📅 Приклад щоденного звіту:

```
🌅 Щоденний звіт для PlayerName
📅 15.12.2024

📊 Поточна статистика:
• K/D Ratio: 1.23
• Win Rate: 67%
• Headshot %: 45%
• Impact Score: 73.5/100

🎯 Основні показники:
• Матчів зіграно: 145
• Перемог: 97
• MVP раундів: 26 (18%)

💡 Порада дня:
🎯 Працюй над точністю - намагайся більше цілитися в голову!

🏆 Рейтинг друзів (Impact Score):
👑 PlayerName 👤
   ⚡ Impact: 73.5/100 | K/D: 1.23 | Win: 67%
2️⃣ Friend1
   ⚡ Impact: 68.2/100 | K/D: 1.15 | Win: 63%
```

## 🛠 Технічний стек

- **Python 3.11** - основна мова
- **python-telegram-bot 20.7** - Telegram Bot API
- **aiohttp** - асинхронні HTTP запити
- **SQLite** - база даних
- **Steam Web API** - отримання статистики
- **Docker & Docker Compose** - контейнеризація
- **APScheduler** - планувальник завдань
- **GitHub Actions** - CI/CD

## 📁 Структура проекту

```
tg-cs-stats/
├── main.py                 # Головний файл запуску
├── config.example.py       # Приклад конфігурації
├── requirements.txt        # Залежності
├── README.md              # Документація
├── data/                  # База даних
└── src/
    ├── models/
    │   └── user.py        # Модель користувача та БД
    ├── services/
    │   └── steam_api.py   # Сервіс Steam API
    ├── handlers/
    │   └── bot_handlers.py # Обробники команд бота
    └── utils/             # Допоміжні функції
```

## 🚀 Деплой на сервер

### 🐳 Docker Compose (рекомендовано)

```bash
# На сервері
git clone https://github.com/your-username/tg-cs-stats.git
cd tg-cs-stats

# Налаштуй змінні оточення
cp env.example .env
nano .env

# Запусти
docker-compose up -d

# Переглядай логи
docker-compose logs -f cs2-stats-bot
```

### ☁️ Хмарні платформи

| Платформа | Складність | Вартість | Посилання |
|-----------|------------|----------|-----------|
| Railway | ⭐ | $5-10/міс | [railway.app](https://railway.app) |
| DigitalOcean | ⭐⭐ | $5/міс | [digitalocean.com](https://digitalocean.com) |
| Heroku | ⭐ | $7/міс | [heroku.com](https://heroku.com) |

Детальні інструкції: [DEPLOYMENT.md](DEPLOYMENT.md)

### 🔄 Автоматичне оновлення

```bash
# Використовуй готовий скрипт
./scripts/update_bot.sh

# Або додай до crontab для автооновлення
0 3 * * 0 /path/to/tg-cs-stats/scripts/update_bot.sh
```

## 🐛 Відомі обмеження

- Steam API не надає доступ до рангу CS2
- Статистика доступна тільки для відкритих профілів
- Деякі показники можуть бути недоступні для нових акаунтів
- Rate limiting Steam API (100,000 запитів на день)

## 🚧 Roadmap (Phase 2)

- [ ] 📈 FACEIT інтеграція
- [ ] 📊 Графіки прогресу та тренди
- [ ] 🏆 Система досягнень та badges
- [ ] ⚡ Real-time сповіщення після матчів
- [ ] 📱 Веб-інтерфейс з детальною аналітикою
- [ ] 📈 Тижневі та місячні звіти
- [ ] 🎯 Персональні цілі та челенджі
- [ ] 🔔 Сповіщення про досягнення друзів

## 🤝 Contributing

1. Fork проект
2. Створи feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit зміни (`git commit -m 'Add some AmazingFeature'`)
4. Push в branch (`git push origin feature/AmazingFeature`)
5. Відкрий Pull Request

## 📄 Ліцензія

Distributed under the MIT License. See `LICENSE` for more information.

## 📞 Контакти

- Telegram: @your_username
- GitHub: [your-username](https://github.com/your-username)
- Email: your.email@example.com

---

⭐ **Поставте зірочку, якщо проект вам сподобався!**

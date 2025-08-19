# 🚀 Інструкції з запуску CS2 Stats Bot

## 📋 Передумови

1. **Python 3.8+** встановлено
2. **Telegram Bot Token** (отримай у @BotFather)
3. **Steam API Key** (отримай на https://steamcommunity.com/dev/apikey)

## 🛠 Крок 1: Встановлення залежностей

```bash
# Клонуй репозиторій
git clone https://github.com/your-username/tg-cs-stats.git
cd tg-cs-stats

# Встанови залежності
pip install -r requirements.txt
```

## 🔑 Крок 2: Налаштування

### Створи Telegram бота:
1. Напиши @BotFather в Telegram
2. Відправ `/newbot`
3. Вибери ім'я та username для бота
4. Скопіюй токен

### Отримай Steam API Key:
1. Йди на https://steamcommunity.com/dev/apikey
2. Увійди в Steam акаунт
3. Заповни форму (Domain Name можна вказати localhost)
4. Скопіюй API ключ

### Налашуй конфігурацію:
```bash
# Скопіюй файл конфігурації
cp config.example.py config.py

# Відредагуй config.py
nano config.py  # або vim/code config.py
```

Встав свої ключі в `config.py`:
```python
TELEGRAM_BOT_TOKEN = "1234567890:ABCdefGHIjklMNOpqrSTUvwxyz"
STEAM_API_KEY = "1234567890ABCDEF1234567890ABCDEF12345678"
```

## 🎮 Крок 3: Запуск

```bash
python main.py
```

Якщо все налаштовано правильно, побачиш:
```
🚀 Запускаю CS2 Stats Bot...
✅ Бот налаштовано! Доступні команди:
   /start - початок роботи
   /help - довідка
   ...
🎮 Бот запущено! Натисни Ctrl+C для зупинки
```

## 📱 Крок 4: Тестування

1. Знайди свого бота в Telegram за username
2. Надішли `/start`
3. Встанови свій Steam ID: `/steam YOUR_STEAM_ID`
4. Переглянь статистику: `/stats`

## 🔧 Налаштування для продакшену

### Використання systemd (Linux):
```bash
# Створи service файл
sudo nano /etc/systemd/system/cs2-stats-bot.service
```

Вміст файлу:
```ini
[Unit]
Description=CS2 Stats Telegram Bot
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/tg-cs-stats
ExecStart=/usr/bin/python3 main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Запуск:
```bash
sudo systemctl enable cs2-stats-bot
sudo systemctl start cs2-stats-bot
sudo systemctl status cs2-stats-bot
```

### Використання Docker:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "main.py"]
```

## 🐛 Troubleshooting

### Помилка: "Invalid token"
- Перевір правильність TELEGRAM_BOT_TOKEN
- Переконайся що токен не містить зайвих пробілів

### Помилка: "Steam API Key invalid"
- Перевір правильність STEAM_API_KEY
- Переконайся що ключ активний на steamcommunity.com/dev/apikey

### Помилка: "Permission denied" для бази даних
- Переконайся що директорія `data/` існує і доступна для запису
- Створи директорію: `mkdir -p data`

### Бот не відповідає
- Перевір що бот запущений
- Подивись логи на помилки
- Переконайся що бот не заблокований в Telegram

## 📊 Структура бази даних

База даних створюється автоматично в `data/bot_database.db`:

- **users** - користувачі бота
- **user_stats_cache** - кеш статистики для оптимізації

## 🔄 Оновлення

```bash
git pull origin main
pip install -r requirements.txt
# Перезапусти бота
```

## 💡 Поради

1. **Регулярно робити backup** бази даних
2. **Моніторити логи** для виявлення помилок
3. **Обмежити rate limit** Steam API (100k запитів/день)
4. **Використовувати reverse proxy** для production

## 📞 Підтримка

Якщо виникли проблеми:
1. Перевір цю інструкцію
2. Подивись Issues на GitHub
3. Створи новий Issue з описом проблеми
4. Напиши розробнику: @csStatisticsBot

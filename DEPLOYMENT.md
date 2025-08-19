# 🚀 Деплой CS2 Stats Bot

Інструкція з розгортання бота на віддаленому сервері через Docker.

## 📋 Передумови

### На локальній машині:
- Git
- Docker та Docker Compose

### На сервері:
- Ubuntu/Debian/CentOS
- Docker та Docker Compose
- Відкритий доступ до інтернету

## 🛠 Варіант 1: Швидкий деплой з Docker Compose

### 1. Клонування репозиторію на сервер

```bash
# Підключись до сервера
ssh user@your-server.com

# Клонуй репозиторій
git clone https://github.com/your-username/tg-cs-stats.git
cd tg-cs-stats
```

### 2. Налаштування змінних оточення

```bash
# Скопіюй шаблон
cp env.example .env

# Відредагуй файл .env
nano .env
```

Встав свої ключі в `.env`:
```env
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrSTUvwxyz
STEAM_API_KEY=1234567890ABCDEF1234567890ABCDEF12345678
LOG_LEVEL=INFO
DAILY_REPORT_TIME=10:00
DATABASE_PATH=/app/data/bot_database.db
```

### 3. Створення директорій

```bash
# Створи директорії для даних
mkdir -p data logs

# Встанови права доступу
chmod 755 data logs
```

### 4. Запуск бота

```bash
# Збери та запусти контейнер
docker-compose up -d

# Переглянь логи
docker-compose logs -f cs2-stats-bot

# Перевір статус
docker-compose ps
```

### 5. Управління ботом

```bash
# Зупинити бота
docker-compose down

# Перезапустити бота
docker-compose restart

# Оновити бота (після git pull)
docker-compose down
git pull
docker-compose up -d --build

# Переглянути логи
docker-compose logs -f cs2-stats-bot
```

## 🐳 Варіант 2: Ручна збірка Docker образу

### 1. Збірка образу

```bash
# Збери образ
docker build -t cs2-stats-bot .

# Переглянь створені образи
docker images
```

### 2. Запуск контейнера

```bash
# Запусти контейнер
docker run -d \
  --name cs2-stats-bot \
  --restart unless-stopped \
  -e TELEGRAM_BOT_TOKEN="твій_токен" \
  -e STEAM_API_KEY="твій_ключ" \
  -e LOG_LEVEL="INFO" \
  -e DAILY_REPORT_TIME="10:00" \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  cs2-stats-bot

# Переглянь логи
docker logs -f cs2-stats-bot
```

## ☁️ Варіант 3: Деплой на хмарні платформи

### Railway (рекомендовано)

1. **Створи акаунт на [Railway.app](https://railway.app)**

2. **Підключи GitHub репозиторій**

3. **Встанови змінні оточення в Railway:**
   - `TELEGRAM_BOT_TOKEN`
   - `STEAM_API_KEY`
   - `LOG_LEVEL=INFO`
   - `DAILY_REPORT_TIME=10:00`
   - `DATABASE_PATH=/app/data/bot_database.db`

4. **Railway автоматично деплоїть з Dockerfile**

### Heroku

1. **Встанови Heroku CLI**

2. **Створи додаток:**
```bash
heroku create cs2-stats-bot-your-name
```

3. **Встанови змінні оточення:**
```bash
heroku config:set TELEGRAM_BOT_TOKEN="твій_токен"
heroku config:set STEAM_API_KEY="твій_ключ"
heroku config:set LOG_LEVEL="INFO"
heroku config:set DAILY_REPORT_TIME="10:00"
```

4. **Деплой:**
```bash
git push heroku main
```

### DigitalOcean App Platform

1. **Створи новий App**
2. **Підключи GitHub**
3. **Встанови змінні оточення**
4. **Вибери план ($5/місяць)**

## 🔧 Налаштування сервера (Ubuntu/Debian)

### Встановлення Docker

```bash
# Оновлення пакетів
sudo apt update

# Встановлення залежностей
sudo apt install -y apt-transport-https ca-certificates curl gnupg lsb-release

# Додавання GPG ключа Docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Додавання репозиторію
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Встановлення Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io

# Встановлення Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Додавання користувача до групи docker
sudo usermod -aG docker $USER

# Перелогінься або виконай
newgrp docker
```

### Налаштування автозапуску

```bash
# Створи systemd сервіс
sudo nano /etc/systemd/system/cs2-stats-bot.service
```

Вміст файлу:
```ini
[Unit]
Description=CS2 Stats Bot
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/home/user/tg-cs-stats
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
```

Активація сервісу:
```bash
sudo systemctl enable cs2-stats-bot
sudo systemctl start cs2-stats-bot
sudo systemctl status cs2-stats-bot
```

## 📊 Моніторинг та логування

### Перегляд логів

```bash
# Docker Compose
docker-compose logs -f cs2-stats-bot

# Docker
docker logs -f cs2-stats-bot

# Останні 100 рядків
docker-compose logs --tail=100 cs2-stats-bot
```

### Моніторинг ресурсів

```bash
# Використання ресурсів
docker stats cs2-stats-bot

# Детальна інформація
docker inspect cs2-stats-bot
```

### Backup бази даних

```bash
# Створи backup
cp data/bot_database.db data/backup_$(date +%Y%m%d_%H%M%S).db

# Або через Docker
docker-compose exec cs2-stats-bot cp /app/data/bot_database.db /app/data/backup_$(date +%Y%m%d_%H%M%S).db
```

## 🛠 Troubleshooting

### Бот не запускається

1. **Перевір логи:**
```bash
docker-compose logs cs2-stats-bot
```

2. **Перевір змінні оточення:**
```bash
docker-compose config
```

3. **Перевір права доступу:**
```bash
ls -la data/
```

### Проблеми з базою даних

1. **Перевір чи існує директорія:**
```bash
ls -la data/
```

2. **Створи директорію якщо потрібно:**
```bash
mkdir -p data
chmod 755 data
```

### Проблеми з мережею

1. **Перевір підключення до Telegram:**
```bash
curl -X GET "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getMe"
```

2. **Перевір підключення до Steam API:**
```bash
curl "https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key=<YOUR_STEAM_KEY>&steamids=76561197960435530"
```

## 🔄 Оновлення бота

### Автоматичне оновлення

```bash
#!/bin/bash
# update_bot.sh

cd /home/user/tg-cs-stats
git pull
docker-compose down
docker-compose up -d --build

echo "Бот оновлено!"
```

### Через cron (щотижня)

```bash
# Додай до crontab
crontab -e

# Оновлення кожної неділі о 3:00
0 3 * * 0 /home/user/tg-cs-stats/update_bot.sh
```

## 💰 Вартість хостингу

| Платформа | Вартість | Особливості |
|-----------|----------|-------------|
| Railway | $5-10/місяць | Простий деплой, автоматичні оновлення |
| DigitalOcean | $5/місяць | Власний сервер, більше контролю |
| Heroku | $7/місяць | Популярний, але дорожчий |
| VPS (Hetzner) | €3-5/місяць | Найдешевший, потрібні навички |

## 🔐 Безпека

1. **Не комітьте .env файл в Git**
2. **Використовуйте сильні токени**
3. **Регулярно оновлюйте залежності**
4. **Моніторьте логи на підозрілу активність**
5. **Використовуйте HTTPS для веб-хуків (в майбутньому)**

---

**Готово! 🚀** Твій бот тепер працює в хмарі та доступний 24/7!

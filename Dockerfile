# Використовуємо офіційний Python образ
FROM python:3.11-slim

# Встановлюємо робочу директорію
WORKDIR /app

# Встановлюємо системні залежності
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Копіюємо файл залежностей
COPY requirements.txt .

# Встановлюємо Python залежності
RUN pip install --no-cache-dir -r requirements.txt

# Копіюємо код додатку
COPY . .

# Створюємо директорію для бази даних
RUN mkdir -p /app/data

# Створюємо користувача для безпеки (не root)
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app

# Встановлюємо змінні оточення для Railway
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# Railway може встановлювати PORT, але наш бот його не використовує
# Відкриваємо порт для майбутніх можливостей (webhook, веб-інтерфейс)
EXPOSE $PORT

# Команда запуску
CMD ["python", "main.py"]

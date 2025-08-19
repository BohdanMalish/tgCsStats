"""
Планувальник для автоматичних завдань
"""
import asyncio
from datetime import datetime, time
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import logging

from .daily_reports import DailyReportsService


class TaskScheduler:
    def __init__(self, daily_reports_service: DailyReportsService):
        self.daily_reports_service = daily_reports_service
        self.scheduler = AsyncIOScheduler()
        self.logger = logging.getLogger(__name__)

    def start(self, daily_report_time: str = "10:00"):
        """Запустити планувальник"""
        try:
            # Парсимо час для щоденних звітів
            hour, minute = map(int, daily_report_time.split(':'))
            
            # Додаємо завдання для щоденних звітів
            self.scheduler.add_job(
                func=self.daily_reports_service.send_daily_reports_to_all_users,
                trigger=CronTrigger(hour=hour, minute=minute),
                id='daily_reports',
                name='Щоденні звіти',
                replace_existing=True
            )
            
            # Додаємо тижневі звіти (неділя о 12:00)
            self.scheduler.add_job(
                func=self.daily_reports_service.send_weekly_summary,
                trigger=CronTrigger(day_of_week=6, hour=12, minute=0),  # Неділя
                id='weekly_reports',
                name='Тижневі звіти',
                replace_existing=True
            )
            
            # Запускаємо планувальник
            self.scheduler.start()
            self.logger.info(f"✅ Планувальник запущено. Щоденні звіти о {daily_report_time}")
            
        except Exception as e:
            self.logger.error(f"❌ Помилка запуску планувальника: {e}")

    def stop(self):
        """Зупинити планувальник"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            self.logger.info("🛑 Планувальник зупинено")

    def get_next_report_time(self) -> str:
        """Отримати час наступного звіту"""
        job = self.scheduler.get_job('daily_reports')
        if job and job.next_run_time:
            return job.next_run_time.strftime('%d.%m.%Y о %H:%M')
        return "Невідомо"

    async def send_test_report(self, telegram_id: int):
        """Відправити тестовий звіт користувачу"""
        try:
            from ..models.user import UserDatabase
            # Це потрібно буде передати через конструктор
            user = self.daily_reports_service.user_db.get_user(telegram_id)
            if user and user.steam_id:
                # Відправляємо персональний звіт
                personal_report = await self.daily_reports_service.generate_personal_daily_report(user)
                if personal_report:
                    await self.daily_reports_service.bot.send_message(
                        chat_id=telegram_id,
                        text=f"🧪 **Тестовий звіт:**\n\n{personal_report}",
                        parse_mode='Markdown'
                    )
                
                # Відправляємо звіт по друзях якщо є
                if user.friends:
                    friends_report = await self.daily_reports_service.generate_friends_daily_report(user)
                    if friends_report:
                        await self.daily_reports_service.bot.send_message(
                            chat_id=telegram_id,
                            text=f"🧪 **Тестовий звіт по друзях:**\n\n{friends_report}",
                            parse_mode='Markdown'
                        )
                
                return True
            return False
        except Exception as e:
            self.logger.error(f"Помилка відправки тестового звіту: {e}")
            return False

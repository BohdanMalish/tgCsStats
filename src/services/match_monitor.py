"""
Сервіс для автоматичного моніторингу матчів гравців
"""
import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from telegram import Bot
from telegram.error import TelegramError

from src.services.steam_api import SteamAPI
from src.services.demo_analyzer import DemoAnalyzer
from src.models.user import UserDatabase, MatchAnalysis


class MatchMonitor:
    def __init__(self, steam_api_key: str, bot_token: str, user_db: UserDatabase):
        self.steam_api = SteamAPI(steam_api_key)
        self.demo_analyzer = DemoAnalyzer(steam_api_key)
        self.bot = Bot(token=bot_token)
        self.user_db = user_db
        self.monitoring_interval = 300  # 5 хвилин
        self.last_match_cache = {}  # Кеш останніх матчів для кожного гравця
    
    async def start_monitoring(self):
        """Запустити моніторинг матчів"""
        print("🎮 Запуск моніторингу матчів...")
        
        while True:
            try:
                await self.check_all_users_matches()
                await asyncio.sleep(self.monitoring_interval)
            except Exception as e:
                print(f"❌ Помилка моніторингу: {e}")
                await asyncio.sleep(60)  # Чекаємо 1 хвилину при помилці
    
    async def check_all_users_matches(self):
        """Перевірити матчі всіх користувачів з увімкненим моніторингом"""
        users = self.user_db.get_users_with_monitoring()
        
        for user in users:
            if user.steam_id:
                try:
                    await self.check_user_last_match(user)
                except Exception as e:
                    print(f"❌ Помилка перевірки матчу для {user.steam_id}: {e}")
    
    async def check_user_last_match(self, user):
        """Перевірити останній матч конкретного гравця"""
        try:
            # Отримуємо інформацію про останню активність
            recent_activity = await self.steam_api.get_recent_activity(user.steam_id)
            
            if not recent_activity:
                return
            
            # Перевіряємо чи є новий матч
            current_match_id = recent_activity.get('last_match_id')
            last_known_match = self.last_match_cache.get(user.steam_id)
            
            if current_match_id and current_match_id != last_known_match:
                # Новий матч знайдено!
                print(f"🎯 Новий матч для {user.steam_id}: {current_match_id}")
                
                # Оновлюємо кеш
                self.last_match_cache[user.steam_id] = current_match_id
                
                # Аналізуємо матч
                await self.analyze_and_notify_match(user, current_match_id, recent_activity)
            
        except Exception as e:
            print(f"❌ Помилка перевірки матчу для {user.steam_id}: {e}")
    
    async def analyze_and_notify_match(self, user, match_id: str, recent_activity: Dict[str, Any]):
        """Аналізувати матч та надіслати повідомлення"""
        try:
            # Отримуємо детальну статистику останнього матчу
            last_match_stats = await self.steam_api.get_player_stats(user.steam_id, "last_match")
            
            if not last_match_stats:
                print(f"❌ Не вдалося отримати статистику матчу {match_id}")
                return
            
            # Створюємо повідомлення про матч
            match_message = self.create_match_notification(user, match_id, last_match_stats, recent_activity)
            
            # Надсилаємо повідомлення користувачу
            await self.send_match_notification(user.telegram_id, match_message)
            
            # Аналізуємо демо якщо можливо
            await self.analyze_match_demo(user, match_id)
            
        except Exception as e:
            print(f"❌ Помилка аналізу матчу {match_id}: {e}")
    
    def create_match_notification(self, user, match_id: str, stats: Dict[str, Any], recent_activity: Dict[str, Any]) -> str:
        """Створити повідомлення про матч"""
        try:
            # Основна статистика
            kills = stats.get('kills', 0)
            deaths = stats.get('deaths', 0)
            assists = stats.get('assists', 0)
            mvps = stats.get('mvps', 0)
            damage = stats.get('damage', 0)
            
            # Розраховуємо показники
            kd_ratio = round(kills / max(deaths, 1), 2)
            headshot_percent = stats.get('headshot_percent', 0)
            
            # Інформація про матч
            map_name = recent_activity.get('last_match_map', 'Невідомо')
            match_result = recent_activity.get('last_match_result', 'Невідомо')
            match_duration = recent_activity.get('last_match_duration', 'Невідомо')
            
            # Створюємо повідомлення
            message = f"""🎮 **Матч завершено!**

📊 **Результат:** {match_result}
🗺️ **Карта:** {map_name}
⏱️ **Тривалість:** {match_duration}

📈 **Ваша статистика:**
• K/D: **{kills}/{deaths}** ({kd_ratio})
• Асисти: **{assists}**
• MVP: **{mvps}**
• Урон: **{damage:,}**
• Headshot %: **{headshot_percent}%**

🎯 **Match ID:** `{match_id}`

💡 Використайте `/demo_analysis {match_id}` для детального аналізу демо!"""
            
            return message
            
        except Exception as e:
            print(f"❌ Помилка створення повідомлення: {e}")
            return f"🎮 Матч завершено! Match ID: {match_id}"
    
    async def send_match_notification(self, telegram_id: int, message: str):
        """Надіслати повідомлення про матч"""
        try:
            await self.bot.send_message(
                chat_id=telegram_id,
                text=message,
                parse_mode='Markdown'
            )
            print(f"✅ Повідомлення надіслано користувачу {telegram_id}")
        except TelegramError as e:
            print(f"❌ Помилка надсилання повідомлення: {e}")
    
    async def analyze_match_demo(self, user, match_id: str):
        """Аналізувати демо матчу"""
        try:
            print(f"🎬 Початок аналізу демо матчу {match_id}...")
            
            # Завантажуємо демо
            demo_path = await self.demo_analyzer.download_demo(user.steam_id, match_id)
            
            if not demo_path:
                print(f"❌ Не вдалося завантажити демо для матчу {match_id}")
                return
            
            # Аналізуємо демо
            analysis_result = await self.demo_analyzer.analyze_demo(demo_path, user.steam_id, match_id)
            
            if analysis_result:
                # Зберігаємо аналіз в базу даних
                match_analysis = MatchAnalysis(
                    steam_id=user.steam_id,
                    match_id=match_id,
                    match_date=datetime.now(),
                    demo_path=demo_path
                )
                match_analysis.analyzed = True
                match_analysis.analysis_data = analysis_result
                
                self.user_db.save_match_analysis(match_analysis)
                
                # Створюємо детальний звіт
                detailed_report = await self.demo_analyzer.get_analysis_summary(analysis_result)
                
                # Надсилаємо детальний звіт
                await self.bot.send_message(
                    chat_id=user.telegram_id,
                    text=f"📊 **Детальний аналіз матчу {match_id}:**\n\n{detailed_report}",
                    parse_mode='Markdown'
                )
                
                # Видаляємо демо-файл
                await self.demo_analyzer.cleanup_demo(demo_path)
                
                print(f"✅ Аналіз демо матчу {match_id} завершено")
            else:
                print(f"❌ Помилка аналізу демо матчу {match_id}")
                
        except Exception as e:
            print(f"❌ Помилка аналізу демо: {e}")
    
    async def get_user_match_history(self, steam_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Отримати історію матчів гравця"""
        try:
            # Отримуємо збережені аналізи матчів
            match_analyses = self.user_db.get_recent_matches(steam_id, limit)
            
            history = []
            for analysis in match_analyses:
                history.append({
                    'match_id': analysis.match_id,
                    'match_date': analysis.match_date,
                    'analyzed': analysis.analyzed,
                    'analysis_data': analysis.analysis_data
                })
            
            return history
            
        except Exception as e:
            print(f"❌ Помилка отримання історії матчів: {e}")
            return []
    
    async def get_user_match_stats(self, steam_id: str) -> Dict[str, Any]:
        """Отримати агреговану статистику всіх проаналізованих матчів"""
        try:
            # Отримуємо всі аналізи матчів
            match_analyses = self.user_db.get_recent_matches(steam_id, 1000)  # Всі матчі
            
            if not match_analyses:
                return {'message': 'Немає проаналізованих матчів'}
            
            # Агрегуємо статистику
            total_matches = len(match_analyses)
            total_kills = 0
            total_deaths = 0
            total_assists = 0
            total_mvps = 0
            total_headshots = 0
            total_damage = 0
            
            for analysis in match_analyses:
                if analysis.analysis_data:
                    player_stats = analysis.analysis_data.get('player_stats', {})
                    total_kills += player_stats.get('kills', 0)
                    total_deaths += player_stats.get('deaths', 0)
                    total_assists += player_stats.get('assists', 0)
                    total_mvps += player_stats.get('mvps', 0)
                    total_headshots += player_stats.get('headshots', 0)
                    total_damage += player_stats.get('damage_dealt', 0)
            
            # Розраховуємо середні показники
            avg_kd = round(total_kills / max(total_deaths, 1), 2)
            avg_headshot_percent = round((total_headshots / max(total_kills, 1)) * 100, 1)
            avg_damage_per_match = round(total_damage / total_matches, 0)
            
            return {
                'total_matches': total_matches,
                'total_kills': total_kills,
                'total_deaths': total_deaths,
                'total_assists': total_assists,
                'total_mvps': total_mvps,
                'total_headshots': total_headshots,
                'total_damage': total_damage,
                'avg_kd_ratio': avg_kd,
                'avg_headshot_percent': avg_headshot_percent,
                'avg_damage_per_match': avg_damage_per_match,
                'avg_mvps_per_match': round(total_mvps / total_matches, 1)
            }
            
        except Exception as e:
            print(f"❌ Помилка отримання статистики матчів: {e}")
            return {'error': str(e)}

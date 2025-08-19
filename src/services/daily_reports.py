"""
Сервіс для автоматичних щоденних звітів
"""
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging

from ..models.user import UserDatabase, User
from ..services.steam_api import SteamAPI


class DailyReportsService:
    def __init__(self, user_db: UserDatabase, steam_api: SteamAPI, bot):
        self.user_db = user_db
        self.steam_api = steam_api
        self.bot = bot
        self.logger = logging.getLogger(__name__)

    async def generate_personal_daily_report(self, user: User) -> Optional[str]:
        """Генерувати персональний щоденний звіт для користувача"""
        try:
            if not user.steam_id:
                return None

            # Отримуємо поточну статистику
            current_stats = await self.steam_api.get_player_stats(user.steam_id)
            if not current_stats:
                return None

            parsed_stats = self.steam_api.parse_cs2_stats(current_stats)
            impact_score = self.steam_api.calculate_impact_score(parsed_stats)

            # Отримуємо ім'я гравця
            players = await self.steam_api.get_player_summaries([user.steam_id])
            player_name = players[0].get('personaname', 'Гравець') if players else 'Гравець'

            # TODO: В майбутньому можна додати порівняння з вчорашньою статистикою
            # Поки що показуємо поточний стан
            
            report = f"""
🌅 **Щоденний звіт для {player_name}**
📅 {datetime.now().strftime('%d.%m.%Y')}

📊 **Поточна статистика:**
• K/D Ratio: **{parsed_stats['kd_ratio']}**
• Win Rate: **{parsed_stats['win_rate']}%**
• Headshot %: **{parsed_stats['headshot_percent']}%**
• Impact Score: **{impact_score}/100**

🎯 **Основні показники:**
• Матчів зіграно: **{parsed_stats['matches_played']}**
• Перемог: **{parsed_stats['wins']}**
• MVP раундів: **{parsed_stats['mvps']}** ({parsed_stats['mvp_percent']}%)

💡 **Порада дня:**
{self._get_daily_tip(parsed_stats)}

🏆 Використай `/friends_stats` щоб подивитися як справляються друзі!
"""
            return report.strip()

        except Exception as e:
            self.logger.error(f"Помилка генерації персонального звіту для {user.telegram_id}: {e}")
            return None

    async def generate_friends_daily_report(self, user: User) -> Optional[str]:
        """Генерувати щоденний звіт по друзях"""
        try:
            if not user.steam_id or not user.friends:
                return None

            # Отримуємо статистику для всіх друзів + користувача
            all_steam_ids = [user.steam_id] + user.friends
            friends_data = []

            for steam_id in all_steam_ids:
                raw_stats = await self.steam_api.get_player_stats(steam_id)
                if raw_stats:
                    stats = self.steam_api.parse_cs2_stats(raw_stats)
                    impact_score = self.steam_api.calculate_impact_score(stats)
                    
                    # Отримуємо ім'я
                    players = await self.steam_api.get_player_summaries([steam_id])
                    name = players[0].get('personaname', 'Невідомо') if players else 'Невідомо'
                    
                    friends_data.append({
                        'steam_id': steam_id,
                        'name': name,
                        'impact_score': impact_score,
                        'kd_ratio': stats['kd_ratio'],
                        'win_rate': stats['win_rate'],
                        'is_me': steam_id == user.steam_id
                    })

            if not friends_data:
                return None

            # Сортуємо за Impact Score
            friends_data.sort(key=lambda x: x['impact_score'], reverse=True)

            # Знаходимо позицію користувача
            user_position = next((i+1 for i, friend in enumerate(friends_data) if friend['is_me']), 0)
            
            report = f"""
🏆 **Щоденний рейтинг друзів**
📅 {datetime.now().strftime('%d.%m.%Y')}

📊 **Топ-{min(5, len(friends_data))} гравців:**
"""

            # Показуємо топ-5 або всіх якщо менше
            for i, friend in enumerate(friends_data[:5], 1):
                emoji = "👑" if i == 1 else f"{i}️⃣"
                me_indicator = " 👤" if friend['is_me'] else ""
                
                report += f"\n{emoji} **{friend['name']}**{me_indicator}"
                report += f"\n   ⚡ Impact: {friend['impact_score']}/100 | K/D: {friend['kd_ratio']} | Win: {friend['win_rate']}%"

            # Додаємо інформацію про позицію користувача
            if user_position > 5:
                user_data = next(friend for friend in friends_data if friend['is_me'])
                report += f"\n\n📍 **Твоя позиція: #{user_position}**"
                report += f"\n⚡ Impact: {user_data['impact_score']}/100"

            # Додаємо статистику змін
            report += f"\n\n📈 **Загальна статистика групи:**"
            report += f"\n👥 Активних гравців: **{len(friends_data)}**"
            
            avg_impact = sum(f['impact_score'] for f in friends_data) / len(friends_data)
            report += f"\n📊 Середній Impact Score: **{avg_impact:.1f}/100**"

            # Визначаємо лідера дня
            leader = friends_data[0]
            if not leader['is_me']:
                report += f"\n\n🎯 **Лідер дня:** {leader['name']} ({leader['impact_score']}/100)"
            else:
                report += f"\n\n🎉 **Ти лідер групи!** Так тримати!"

            return report.strip()

        except Exception as e:
            self.logger.error(f"Помилка генерації звіту по друзях для {user.telegram_id}: {e}")
            return None

    def _get_daily_tip(self, stats: Dict[str, Any]) -> str:
        """Отримати пораду дня на основі статистики"""
        tips = []
        
        # Поради на основі статистики
        if stats['headshot_percent'] < 30:
            tips.append("🎯 Працюй над точністю - намагайся більше цілитися в голову!")
        
        if stats['win_rate'] < 50:
            tips.append("🤝 Грай більше з командою - комунікація це ключ до перемоги!")
        
        if stats['kd_ratio'] < 1.0:
            tips.append("⚔️ Будь більш обережним - краще вижити і допомогти команді!")
        
        if stats['assists_per_match'] < 2:
            tips.append("🤝 Допомагай товаришам - асисти теж важливі для команди!")
        
        if stats['mvp_percent'] < 10:
            tips.append("🏆 Намагайся бути більш активним в ключових раундах!")

        # Загальні поради
        general_tips = [
            "🎮 Розминайся перед грою - 10 хвилин на aim_botz творять дива!",
            "📺 Дивись професійні матчі - можна багато чому навчитися!",
            "🎧 Використовуй хороші навушники - звук в CS2 дуже важливий!",
            "💪 Роби перерви - свіжий розум грає краще!",
            "📊 Аналізуй свої демки - знаходь помилки та виправляй їх!",
            "🎯 Грай на одній чутливості миші - м'язова пам'ять важлива!",
            "🗺️ Вивчай нові позиції на картах - непередбачуваність дає перевагу!"
        ]
        
        # Якщо є специфічні поради - використовуємо їх, інакше загальні
        if tips:
            return tips[0]
        else:
            import random
            return random.choice(general_tips)

    async def send_daily_reports_to_all_users(self):
        """Відправити щоденні звіти всім активним користувачам"""
        users = self.user_db.get_all_users_with_steam()
        self.logger.info(f"Відправляю щоденні звіти для {len(users)} користувачів")
        
        reports_sent = 0
        errors = 0
        
        for user in users:
            try:
                # Генеруємо персональний звіт
                personal_report = await self.generate_personal_daily_report(user)
                if personal_report:
                    await self.bot.send_message(
                        chat_id=user.telegram_id,
                        text=personal_report,
                        parse_mode='Markdown'
                    )
                    reports_sent += 1
                    
                    # Невелика затримка між повідомленнями
                    await asyncio.sleep(0.5)
                
                # Генеруємо звіт по друзях (якщо є друзі)
                if user.friends:
                    friends_report = await self.generate_friends_daily_report(user)
                    if friends_report:
                        await self.bot.send_message(
                            chat_id=user.telegram_id,
                            text=friends_report,
                            parse_mode='Markdown'
                        )
                        
                        # Затримка між повідомленнями
                        await asyncio.sleep(0.5)
                
            except Exception as e:
                self.logger.error(f"Помилка відправки звіту користувачу {user.telegram_id}: {e}")
                errors += 1
                continue
        
        self.logger.info(f"Щоденні звіти відправлено: {reports_sent}, помилок: {errors}")
        return reports_sent, errors

    async def send_weekly_summary(self):
        """Відправити тижневий підсумок (майбутня функція)"""
        # TODO: Реалізувати тижневі звіти з порівнянням статистики
        pass

    async def get_leaderboard_changes(self) -> Dict[str, Any]:
        """Отримати зміни в рейтингу (майбутня функція)"""
        # TODO: Реалізувати відстеження змін позицій в рейтингу
        pass

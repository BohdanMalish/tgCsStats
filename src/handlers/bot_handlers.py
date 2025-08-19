"""
Обробники команд для Telegram бота
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import re
from typing import Optional

from ..models.user import UserDatabase, User
from ..services.steam_api import SteamAPI
from ..services.daily_reports import DailyReportsService



class BotHandlers:
    def __init__(self, user_db: UserDatabase, steam_api: SteamAPI, daily_reports_service: DailyReportsService = None, app_domain: str = None, steam_api_key: str = None):
        self.user_db = user_db
        self.steam_api = steam_api
        self.daily_reports_service = daily_reports_service
        self.app_domain = app_domain or "tgcsstats-production.up.railway.app"
        self.steam_api_key = steam_api_key or "YOUR_STEAM_API_KEY"

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обробник команди /start"""
        user_id = update.effective_user.id
        username = update.effective_user.username
        
        # Створюємо або оновлюємо користувача
        user = self.user_db.get_user(user_id)
        if not user:
            user = User(telegram_id=user_id, username=username)
            self.user_db.create_user(user)
            
            welcome_text = """
🎮 Вітаю в CS2 Stats Bot!

Я допоможу тобі відстежувати статистику в Counter-Strike 2 та змагатися з друзями!

🚀 Для початку роботи:
1. Додай свій Steam ID командою /steam YOUR_STEAM_ID
2. Додай друзів командою /add_friend FRIEND_STEAM_ID
3. Переглядай статистику командою /stats

📊 Доступні команди:
/help - список всіх команд
/steam - встановити свій Steam ID
/stats - моя статистика
/detailed_stats - детальна статистика
/add_friend - додати друга
/friends_stats - рейтинг друзів
/leaderboard - топ гравців

🎯 Що я вмію:
• Показувати детальну статистику CS2
• Рахувати Impact Score (власний рейтинг)
• Порівнювати з друзями
• Відстежувати прогрес

Почнемо! 🚀
"""
        else:
            welcome_text = f"""
🎮 **З поверненням, {username or 'Гравець'}!**

Радий тебе бачити знову! 

📊 Використовуй /help щоб побачити всі команди
🎯 Або /stats щоб подивитися свою статистику
"""

        await update.message.reply_text(welcome_text)

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обробник команди /help"""
        help_text = """
📋 **Список команд CS2 Stats Bot:**

🔧 **Налаштування:**
/steam - авторизація через Steam (рекомендується)
/steam_login - авторизуватися через Steam OAuth
/steam_manual `<Steam_ID>` - встановити Steam ID вручну (обмежено)

👥 **Друзі:**
/add_friend `<Steam_ID>` - додати друга
/remove_friend `<Steam_ID>` - видалити друга
/friends - список моїх друзів

📊 **Статистика:**
/stats - Steam статистика (за весь час)
/stats `week` - статистика за тиждень
/stats `month` - статистика за місяць
/stats `last_match` - статистика останнього матчу
/stats `last_20_matches` - статистика за останні 20 матчів
/detailed_stats - детальна статистика з новою інформацією
/compare `<Steam_ID>` - порівняти з гравцем

⏰ **Фільтрація по часу:**
/recent_activity `<дні>` - активність за останні N днів
/time_stats - порівняння статистики за різні періоди
/last_matches `<кількість>` - статистика за останні N матчів

🏆 **FACEIT:**
/faceit_stats - FACEIT статистика
/faceit_matches - останні 20 матчів FACEIT

🏆 **Рейтинги:**
/friends_stats - рейтинг моїх друзів
/leaderboard - топ гравців серед всіх користувачів

📅 **Щоденні звіти:**
/daily_report - отримати щоденний звіт зараз
/report_settings - налаштування звітів

🎬 **Аналіз демо:**
/demo_analysis `<MATCH_ID>` - аналізувати демо матчу
/demo_history - історія аналізованих матчів
/demo_stats - статистика всіх аналізованих матчів

🔄 **Автоматичний моніторинг:**
/enable_monitoring - увімкнути автоматичний моніторинг матчів
/disable_monitoring - вимкнути автоматичний моніторинг
/monitoring_status - статус моніторингу

ℹ️ **Інформація:**
/about - про бота та Impact Score
/help - ця довідка

💡 **Приклади використання:**
`/steam 76561198123456789`
`/steam nickname`
`/stats week` - статистика за тиждень
`/stats last_match` - останній матч
`/stats last_20_matches` - останні 20 матчів
`/last_matches 10` - останні 10 матчів
`/recent_activity 7` - активність за 7 днів
`/add_friend 76561198987654321`
`/compare 76561198987654321`
`/demo_analysis 12345` - аналіз демо матчу
`/enable_monitoring` - увімкнути моніторинг

🎯 **Impact Score** - це наш власний алгоритм оцінки гравця, що враховує:
• K/D Ratio (25%)
• Win Rate (30%)
• Headshot % (20%)
• Assists per Match (15%)
• MVP % (10%)

⚠️ **Примітка:** Фільтрація по часу (week/month) показує загальну статистику, оскільки Steam API не підтримує точну фільтрацію по часу.
"""
        
        await update.message.reply_text(help_text)

    async def steam_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обробник команди /steam - перенаправляє на Steam OAuth"""
        await update.message.reply_text(
            "🔐 **Авторизація через Steam**\n\n"
            "Для отримання детальної статистики потрібно авторизуватися через Steam.\n\n"
            "📋 **Переваги авторизації:**\n"
            "• Доступ до приватної статистики\n"
            "• Детальна інформація про матчі\n"
            "• Більше даних ніж без авторизації\n"
            "• Автоматичне оновлення статистики\n\n"
            "🔧 **Команди:**\n"
            "/steam_login - авторизуватися через Steam\n"
            "/steam_manual - встановити Steam ID вручну (обмежена функціональність)\n\n"
            "💡 **Рекомендуємо:** Використовувати /steam_login для повної функціональності!"
        )

    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обробник команди /stats"""
        user_id = update.effective_user.id
        user = self.user_db.get_user(user_id)
        
        if not user or not user.steam_id:
            await update.message.reply_text(
                "❌ Спочатку встанови свій Steam ID командою `/steam`",
                parse_mode='Markdown'
            )
            return
        
        # Перевіряємо чи є параметр часу
        time_period = "all"
        if context.args:
            period_arg = context.args[0].lower()
            if period_arg in ["week", "month", "last_match", "last_20_matches"]:
                time_period = period_arg
        
        await update.message.reply_text(f"📊 Завантажую статистику ({time_period})...")
        
        try:
            raw_stats = await self.steam_api.get_player_stats(user.steam_id, time_period)
            if not raw_stats:
                await update.message.reply_text("❌ Не вдалося отримати статистику!")
                return
            
            stats = self.steam_api.parse_cs2_stats(raw_stats)
            players = await self.steam_api.get_player_summaries([user.steam_id])
            player_name = players[0].get('personaname', 'Невідомо') if players else 'Невідомо'
            impact_score = self.steam_api.calculate_impact_score(stats)
            
            # Формуємо текст статистики
            period_text = {
                "all": "за весь час",
                "week": "за тиждень",
                "month": "за місяць",
                "last_match": "останній матч",
                "last_20_matches": "останні 20 матчів"
            }.get(time_period, "за весь час")
            
            stats_text = f"""
🎮 **Статистика для {player_name}** ({period_text})

📊 **Основні показники:**
• K/D Ratio: **{stats['kd_ratio']}** ({stats['kills']} / {stats['deaths']})
• Win Rate: **{stats['win_rate']}%** ({stats['wins']}/{stats['matches_played']})
• Headshot %: **{stats['headshot_percent']}%**
• Точність: **{stats['accuracy_percent']}%**

🏆 **Досягнення:**
• MVP: **{stats['mvps']}** ({stats['mvp_percent']}%)
• Урон за матч: **{stats['damage_per_match']:,}**
• Асисти за матч: **{stats['assists_per_match']}**

⚡ **Impact Score: {impact_score}/100**
"""
            
            # Додаємо примітку про фільтр якщо потрібно
            if time_period in ["week", "month"] and raw_stats.get('filter_note'):
                stats_text += f"\n⚠️ *{raw_stats['filter_note']}*"
            
            # Додаємо примітку про останні 20 матчів
            if time_period == "last_20_matches" and raw_stats.get('note'):
                stats_text += f"\n📝 *{raw_stats['note']}*"
                stats_text += f"\n📊 Розраховано на основі {raw_stats.get('total_matches', 0)} загальних матчів"
            
            await update.message.reply_text(stats_text, parse_mode='Markdown')
            
        except Exception as e:
            await update.message.reply_text(f"❌ Помилка: {str(e)}")

    async def detailed_stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обробник команди /detailed_stats"""
        user_id = update.effective_user.id
        user = self.user_db.get_user(user_id)
        
        if not user or not user.steam_id:
            await update.message.reply_text(
                "❌ Спочатку встанови свій Steam ID командою `/steam`",
                parse_mode='Markdown'
            )
            return
        
        await update.message.reply_text("📊 Завантажую детальну статистику...")
        
        try:
            raw_stats = await self.steam_api.get_player_stats(user.steam_id)
            if not raw_stats:
                await update.message.reply_text("❌ Не вдалося отримати статистику!")
                return
            
            stats = self.steam_api.parse_cs2_stats(raw_stats)
            players = await self.steam_api.get_player_summaries([user.steam_id])
            player_name = players[0].get('personaname', 'Невідомо') if players else 'Невідомо'
            impact_score = self.steam_api.calculate_impact_score(stats)
            
            # Детальна статистика
            detailed_text = f"""
🎮 **Детальна статистика для {player_name}**

📊 **Основне:**
• K/D Ratio: **{stats['kd_ratio']}** ({stats['kills']} / {stats['deaths']})
• Win Rate: **{stats['win_rate']}%** ({stats['wins']}/{stats['matches_played']})
• Асисти: **{stats['assists']}** ({stats['assists_per_match']}/матч)

🎯 **Точність і стрільба:**
• Headshot %: **{stats['headshot_percent']}%** ({stats['headshot_kills']}/{stats['kills']})
• Загальна точність: **{stats['accuracy_percent']}%**
• Пострілів: **{stats['shots_fired']:,}** | Влучень: **{stats['shots_hit']:,}**

🏆 **Досягнення:**
• MVP раундів: **{stats['mvps']}** ({stats['mvp_percent']}%)
• Урон за матч: **{stats['damage_per_match']:,}**
• Загальний урон: **{stats['damage_dealt']:,}**

⚔️ **Додатково:**
• Раундів зіграно: **{stats['rounds_played']:,}**
• Ножових вбивств: **{stats['knife_kills']}**
• Бомб встановлено: **{stats['planted_bombs']}**
• Бомб розміновано: **{stats['defused_bombs']}**

🔥 **Нова детальна інформація:**
• Домінації: **{stats['dominations']}** | Помсти: **{stats['revenges']}**
• Вбивств зброєю ворога: **{stats['enemy_weapon_kills']}**
• Вбивств осліплених: **{stats['blinded_kills']}**
• Ножових дуелей: **{stats['knife_fight_kills']}**
• Вбивств зум-снайперів: **{stats['zoomed_sniper_kills']}**
• Зброї подаровано: **{stats['weapons_donated']}**
• Contribution Score: **{stats['contribution_score']:,}**

⚡ **Impact Score: {impact_score}/100**
"""
            
            # Додаємо статистику по зброї якщо є
            if stats['weapon_stats']:
                detailed_text += "\n🔫 **Топ зброя:**\n"
                for i, weapon in enumerate(stats['weapon_stats'], 1):
                    detailed_text += f"{i}. **{weapon['name']}**: {weapon['kills']} вбивств"
                    if weapon['accuracy'] > 0:
                        detailed_text += f" ({weapon['accuracy']}% точність)"
                    detailed_text += "\n"
            
            # Додаємо статистику по картах
            if stats.get('map_stats'):
                detailed_text += "\n🗺️ **Топ карти:**\n"
                for i, map_stat in enumerate(stats['map_stats'][:3], 1):
                    detailed_text += f"{i}. **{map_stat['name']}**: {map_stat['wins']}W/{map_stat['rounds']}R ({map_stat['win_rate']}%)\n"
            
            # Додаємо статистику по режимах гри
            if stats.get('game_mode_stats'):
                detailed_text += "\n🎮 **Режими гри:**\n"
                for mode_name, mode_data in stats['game_mode_stats'].items():
                    if mode_name == 'gun_game':
                        detailed_text += f"• **Gun Game**: {mode_data['rounds_won']}W/{mode_data['rounds_played']}R ({mode_data['round_win_rate']}%)\n"
                    elif mode_name == 'progressive':
                        detailed_text += f"• **Progressive**: {mode_data['matches_won']} перемог\n"
                    elif mode_name == 'tr_bomb':
                        detailed_text += f"• **TR Bomb**: {mode_data['matches_won']} перемог\n"
            
            # Додаємо інформацію про останній матч
            if stats.get('last_match') and stats['last_match'].get('kills', 0) > 0:
                last_match = stats['last_match']
                detailed_text += f"\n🎯 **Останній матч:**\n"
                detailed_text += f"• K/D: **{last_match['kills']}/{last_match['deaths']}**\n"
                detailed_text += f"• MVP: **{last_match['mvps']}**\n"
                detailed_text += f"• Урон: **{last_match['damage']:,}**\n"
                detailed_text += f"• Contribution: **{last_match['contribution_score']}**\n"
                
                if last_match.get('favorite_weapon'):
                    weapon = last_match['favorite_weapon']
                    detailed_text += f"• Улюблена зброя: **{weapon['kills']}** вбивств ({weapon['accuracy']}% точність)\n"
            
            await update.message.reply_text(detailed_text, parse_mode='Markdown')
            
        except Exception as e:
            await update.message.reply_text(f"❌ Помилка: {str(e)}")

    async def add_friend_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обробник команди /add_friend"""
        user_id = update.effective_user.id
        user = self.user_db.get_user(user_id)
        
        if not user:
            await update.message.reply_text("❌ Спочатку зареєструйся командою `/start`", parse_mode='Markdown')
            return
        
        if not context.args:
            await update.message.reply_text(
                "❌ Вкажи Steam ID друга!\n\n"
                "📝 **Приклад:**\n"
                "`/add_friend 76561198123456789`",
                parse_mode='Markdown'
            )
            return
        
        friend_input = context.args[0]
        friend_steam_id = None
        
        # Перевіряємо чи це Steam ID або vanity URL
        if friend_input.isdigit() and len(friend_input) == 17:
            friend_steam_id = friend_input
        else:
            friend_steam_id = await self.steam_api.get_steam_id_from_vanity_url(friend_input)
        
        if not friend_steam_id:
            await update.message.reply_text("❌ Не вдалося знайти друга за вказаним ID/ніком!")
            return
        
        # Перевіряємо чи не додає себе
        if friend_steam_id == user.steam_id:
            await update.message.reply_text("😅 Ти не можеш додати себе в друзі!")
            return
        
        # Перевіряємо чи вже є в друзях
        if friend_steam_id in user.friends:
            await update.message.reply_text("👥 Цей гравець вже в твоїх друзях!")
            return
        
        # Отримуємо інформацію про друга
        players = await self.steam_api.get_player_summaries([friend_steam_id])
        if not players:
            await update.message.reply_text("❌ Не вдалося отримати інформацію про гравця!")
            return
        
        friend_name = players[0].get('personaname', 'Невідомо')
        
        # Додаємо друга
        success = self.user_db.add_friend(user_id, friend_steam_id)
        if success:
            await update.message.reply_text(
                f"✅ **Друг доданий!**\n\n"
                f"👤 **{friend_name}**\n"
                f"🆔 `{friend_steam_id}`\n\n"
                f"🎯 Тепер ти можеш:\n"
                f"• Порівнювати статистику `/compare {friend_steam_id}`\n"
                f"• Дивитися рейтинг друзів `/friends_stats`",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text("❌ Помилка додавання друга!")

    async def friends_stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обробник команди /friends_stats"""
        user_id = update.effective_user.id
        user = self.user_db.get_user(user_id)
        
        if not user or not user.steam_id:
            await update.message.reply_text(
                "❌ Спочатку встанови свій Steam ID командою `/steam`",
                parse_mode='Markdown'
            )
            return
        
        if not user.friends:
            await update.message.reply_text(
                "👥 У тебе ще немає друзів!\n\n"
                "Додай друзів командою:\n"
                "`/add_friend STEAM_ID`",
                parse_mode='Markdown'
            )
            return
        
        await update.message.reply_text("📊 Завантажую статистику друзів...")
        
        try:
            # Включаємо себе в рейтинг
            all_steam_ids = [user.steam_id] + user.friends
            
            # Отримуємо статистику для всіх
            friends_stats = []
            for steam_id in all_steam_ids:
                raw_stats = await self.steam_api.get_player_stats(steam_id)
                if raw_stats:
                    stats = self.steam_api.parse_cs2_stats(raw_stats)
                    impact_score = self.steam_api.calculate_impact_score(stats)
                    
                    # Отримуємо ім'я гравця
                    players = await self.steam_api.get_player_summaries([steam_id])
                    name = players[0].get('personaname', 'Невідомо') if players else 'Невідомо'
                    
                    friends_stats.append({
                        'steam_id': steam_id,
                        'name': name,
                        'stats': stats,
                        'impact_score': impact_score,
                        'is_me': steam_id == user.steam_id
                    })
            
            if not friends_stats:
                await update.message.reply_text("❌ Не вдалося отримати статистику друзів!")
                return
            
            # Сортуємо за Impact Score
            friends_stats.sort(key=lambda x: x['impact_score'], reverse=True)
            
            # Формуємо повідомлення
            leaderboard_text = "🏆 **Рейтинг друзів (Impact Score):**\n\n"
            
            for i, friend in enumerate(friends_stats, 1):
                emoji = "👑" if i == 1 else f"{i}️⃣"
                me_indicator = " 👤" if friend['is_me'] else ""
                
                leaderboard_text += f"{emoji} **{friend['name']}**{me_indicator}\n"
                leaderboard_text += f"   ⚡ Impact Score: **{friend['impact_score']}/100**\n"
                leaderboard_text += f"   📊 K/D: {friend['stats']['kd_ratio']} | Win: {friend['stats']['win_rate']}%\n\n"
            
            leaderboard_text += "💡 Використай `/compare STEAM_ID` для детального порівняння!"
            
            await update.message.reply_text(leaderboard_text, parse_mode='Markdown')
            
        except Exception as e:
            await update.message.reply_text(f"❌ Помилка: {str(e)}")

    async def compare_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обробник команди /compare"""
        user_id = update.effective_user.id
        user = self.user_db.get_user(user_id)
        
        if not user or not user.steam_id:
            await update.message.reply_text(
                "❌ Спочатку встанови свій Steam ID командою `/steam`",
                parse_mode='Markdown'
            )
            return
        
        if not context.args:
            await update.message.reply_text(
                "❌ Вкажи Steam ID для порівняння!\n\n"
                "📝 **Приклад:**\n"
                "`/compare 76561198123456789`",
                parse_mode='Markdown'
            )
            return
        
        target_input = context.args[0]
        target_steam_id = None
        
        # Перевіряємо чи це Steam ID або vanity URL
        if target_input.isdigit() and len(target_input) == 17:
            target_steam_id = target_input
        else:
            target_steam_id = await self.steam_api.get_steam_id_from_vanity_url(target_input)
        
        if not target_steam_id:
            await update.message.reply_text("❌ Не вдалося знайти гравця!")
            return
        
        await update.message.reply_text("📊 Порівнюю статистику...")
        
        try:
            # Отримуємо статистику обох гравців
            my_raw_stats = await self.steam_api.get_player_stats(user.steam_id)
            target_raw_stats = await self.steam_api.get_player_stats(target_steam_id)
            
            if not my_raw_stats or not target_raw_stats:
                await update.message.reply_text("❌ Не вдалося отримати статистику одного з гравців!")
                return
            
            my_stats = self.steam_api.parse_cs2_stats(my_raw_stats)
            target_stats = self.steam_api.parse_cs2_stats(target_raw_stats)
            
            my_impact = self.steam_api.calculate_impact_score(my_stats)
            target_impact = self.steam_api.calculate_impact_score(target_stats)
            
            # Отримуємо імена
            players = await self.steam_api.get_player_summaries([user.steam_id, target_steam_id])
            my_name = "Ти"
            target_name = "Суперник"
            
            for player in players:
                if player['steamid'] == user.steam_id:
                    my_name = player.get('personaname', 'Ти')
                elif player['steamid'] == target_steam_id:
                    target_name = player.get('personaname', 'Суперник')
            
            # Формуємо порівняння
            def compare_stat(my_val, target_val, higher_better=True):
                if my_val == target_val:
                    return "🟡"
                elif (my_val > target_val) == higher_better:
                    return "🟢"
                else:
                    return "🔴"
            
            compare_text = f"""
⚔️ **Порівняння статистики**

👤 **{my_name}** vs **{target_name}**

📊 **Impact Score:**
{compare_stat(my_impact, target_impact)} {my_name}: **{my_impact}/100**
{compare_stat(target_impact, my_impact)} {target_name}: **{target_impact}/100**

🎯 **Основні показники:**
{compare_stat(my_stats['kd_ratio'], target_stats['kd_ratio'])} K/D: **{my_stats['kd_ratio']}** vs **{target_stats['kd_ratio']}**
{compare_stat(my_stats['win_rate'], target_stats['win_rate'])} Win Rate: **{my_stats['win_rate']}%** vs **{target_stats['win_rate']}%**
{compare_stat(my_stats['headshot_percent'], target_stats['headshot_percent'])} Headshot %: **{my_stats['headshot_percent']}%** vs **{target_stats['headshot_percent']}%**

🏆 **Досягнення:**
{compare_stat(my_stats['mvp_percent'], target_stats['mvp_percent'])} MVP %: **{my_stats['mvp_percent']}%** vs **{target_stats['mvp_percent']}%**
{compare_stat(my_stats['assists_per_match'], target_stats['assists_per_match'])} Assists/Match: **{my_stats['assists_per_match']}** vs **{target_stats['assists_per_match']}**

📈 **Досвід:**
🎮 Матчів: **{my_stats['matches_played']}** vs **{target_stats['matches_played']}**
⏱️ Раундів: **{my_stats['rounds_played']:,}** vs **{target_stats['rounds_played']:,}**

🟢 - краще | 🔴 - гірше | 🟡 - однаково
"""
            
            await update.message.reply_text(compare_text, parse_mode='Markdown')
            
        except Exception as e:
            await update.message.reply_text(f"❌ Помилка: {str(e)}")

    async def remove_friend_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обробник команди /remove_friend"""
        user_id = update.effective_user.id
        user = self.user_db.get_user(user_id)
        
        if not user:
            await update.message.reply_text("❌ Спочатку зареєструйся командою `/start`", parse_mode='Markdown')
            return
        
        if not context.args:
            await update.message.reply_text(
                "❌ Вкажи Steam ID друга для видалення!\n\n"
                "📝 **Приклад:**\n"
                "`/remove_friend 76561198123456789`",
                parse_mode='Markdown'
            )
            return
        
        friend_input = context.args[0]
        friend_steam_id = None
        
        # Перевіряємо чи це Steam ID або vanity URL
        if friend_input.isdigit() and len(friend_input) == 17:
            friend_steam_id = friend_input
        else:
            friend_steam_id = await self.steam_api.get_steam_id_from_vanity_url(friend_input)
        
        if not friend_steam_id or friend_steam_id not in user.friends:
            await update.message.reply_text("❌ Цього гравця немає в твоїх друзях!")
            return
        
        # Отримуємо ім'я друга перед видаленням
        players = await self.steam_api.get_player_summaries([friend_steam_id])
        friend_name = players[0].get('personaname', 'Невідомо') if players else 'Невідомо'
        
        # Видаляємо друга
        success = self.user_db.remove_friend(user_id, friend_steam_id)
        if success:
            await update.message.reply_text(
                f"✅ **Друг видалений!**\n\n"
                f"👤 **{friend_name}** більше не в твоїх друзях\n"
                f"🆔 `{friend_steam_id}`",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text("❌ Помилка видалення друга!")

    async def daily_report_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обробник команди /daily_report"""
        user_id = update.effective_user.id
        user = self.user_db.get_user(user_id)
        
        if not user or not user.steam_id:
            await update.message.reply_text(
                "❌ Спочатку встанови свій Steam ID командою `/steam`",
                parse_mode='Markdown'
            )
            return
        
        if not self.daily_reports_service:
            await update.message.reply_text("❌ Сервіс щоденних звітів недоступний!")
            return
        
        await update.message.reply_text("📊 Генерую щоденний звіт...")
        
        try:
            # Генеруємо персональний звіт
            personal_report = await self.daily_reports_service.generate_personal_daily_report(user)
            if personal_report:
                await update.message.reply_text(personal_report, parse_mode='Markdown')
            else:
                await update.message.reply_text("❌ Не вдалося згенерувати персональний звіт!")
                return
            
            # Генеруємо звіт по друзях якщо є
            if user.friends:
                friends_report = await self.daily_reports_service.generate_friends_daily_report(user)
                if friends_report:
                    await update.message.reply_text(friends_report, parse_mode='Markdown')
            else:
                await update.message.reply_text(
                    "👥 У тебе ще немає друзів для звіту!\n"
                    "Додай друзів командою `/add_friend` щоб бачити рейтинг групи.",
                    parse_mode='Markdown'
                )
                
        except Exception as e:
            await update.message.reply_text(f"❌ Помилка генерації звіту: {str(e)}")

    async def report_settings_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обробник команди /report_settings"""
        user_id = update.effective_user.id
        user = self.user_db.get_user(user_id)
        
        if not user:
            await update.message.reply_text("❌ Спочатку зареєструйся командою `/start`", parse_mode='Markdown')
            return
        
        # TODO: В майбутньому можна додати налаштування часу звітів, вимкнення/увімкнення тощо
        settings_text = """
📅 **Налаштування щоденних звітів**

🕙 **Час відправки:** 10:00 щоранку
📊 **Персональний звіт:** ✅ Увімкнено
🏆 **Звіт по друзях:** ✅ Увімкнено (якщо є друзі)

📋 **Що включає персональний звіт:**
• Поточна статистика (K/D, Win Rate, HS%)
• Impact Score
• Порада дня на основі твоєї гри

📋 **Що включає звіт по друзях:**
• Рейтинг всіх друзів за Impact Score
• Твоя позиція в групі
• Статистика групи
• Лідер дня

💡 **Корисно знати:**
• Звіти відправляються автоматично щоранку
• Можеш отримати звіт зараз командою `/daily_report`
• Додавай друзів щоб змагатися в групі!

🔮 **Скоро буде доступно:**
• Налаштування часу відправки
• Вимкнення окремих типів звітів
• Тижневі підсумки
• Сповіщення про досягнення друзів
"""
        
        await update.message.reply_text(settings_text, parse_mode='Markdown')

    async def about_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обробник команди /about"""
        about_text = """
🤖 *CS2 Stats Bot v1.0*

Цей бот допомагає відстежувати статистику Counter-Strike 2 та змагатися з друзями!

🧠 *Impact Score Algorithm:*
Наш власний алгоритм оцінки гравця:
• *K/D Ratio* (25%) - ефективність у вбивствах
• *Win Rate* (30%) - відсоток перемог  
• *Headshot %* (20%) - точність стрільби
• *Assists/Match* (15%) - командна гра
• *MVP %* (10%) - лідерські якості

🔧 *Технології:*
• Python + python-telegram-bot
• Steam Web API
• SQLite база даних
• Асинхронна обробка

👨‍💻 *Розробник:* @Bodyamalish
📊 *Версія:* 1.0 MVP
🔄 *Оновлення:* Автоматичні

💡 *Пропозиції та баги:* @Bodyamalish
⭐ *GitHub:* github.com/BohdanMalish/tgCsStats
"""
        
        await update.message.reply_text(about_text, parse_mode='Markdown')



    async def steam_login_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обробник команди /steam_login - авторизація через Steam"""
        user_id = update.effective_user.id
        
        # Генеруємо URL для Steam OAuth
        try:
            from ..services.steam_oauth import SteamOAuth
            
            steam_oauth = SteamOAuth(
                api_key=self.steam_api_key,  # Використовуємо API ключ з конструктора
                app_domain=self.app_domain  # Використовуємо домен з конструктора
            )
            
            # Генеруємо return URL
            return_url = f"https://{self.app_domain}/steam/callback?user_id={user_id}"
            login_url = steam_oauth.generate_login_url(return_url)
            
            login_text = f"""
🔐 **Авторизація через Steam**

Для отримання детальної статистики потрібно авторизуватися через Steam.

📋 **Кроки:**
1. Натисни кнопку "Увійти через Steam" нижче
2. Увійди в свій Steam акаунт
3. Дозволь доступ до статистики
4. Повернися в бота

✅ **Що ти отримаєш:**
• Доступ до приватної статистики
• Детальна інформація про матчі
• Більше даних ніж без авторизації
• Автоматичне оновлення статистики

🔗 **Посилання для авторизації:**
{login_url}

⚠️ **Важливо:** Це безпечно, ми не зберігаємо твій пароль!
"""
            
            # Створюємо inline кнопку
            keyboard = [[InlineKeyboardButton("🔐 Увійти через Steam", url=login_url)]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(login_text, parse_mode='Markdown', reply_markup=reply_markup)
            
        except Exception as e:
            await update.message.reply_text(f"❌ Помилка налаштування Steam OAuth: {str(e)}")

    async def steam_manual_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обробник команди /steam_manual для ручного встановлення Steam ID"""
        user_id = update.effective_user.id
        
        if not context.args:
            await update.message.reply_text(
                "❌ Потрібно вказати Steam ID або нікнейм!\n\n"
                "📝 *Приклади:*\n"
                "`/steam_manual 76561198123456789`\n"
                "`/steam_manual nickname`\n\n"
                "🔍 *Як знайти свій Steam ID:*\n"
                "1. Відкрий свій профіль Steam\n"
                "2. Скопіюй числа з URL або використай нікнейм\n\n"
                "⚠️ *Обмеження:* Без авторизації доступна тільки публічна статистика!",
                parse_mode='Markdown'
            )
            return

        steam_input = context.args[0]
        steam_id = None
        
        # Перевіряємо чи це вже Steam ID (17 цифр)
        if steam_input.isdigit() and len(steam_input) == 17:
            steam_id = steam_input
        else:
            # Пробуємо отримати Steam ID з vanity URL
            steam_id = await self.steam_api.get_steam_id_from_vanity_url(steam_input)
        
        if not steam_id:
            await update.message.reply_text(
                "❌ Не вдалося знайти Steam ID!\n\n"
                "🔍 Перевір:\n"
                "• Правильність написання нікнейму\n"
                "• Чи відкритий твій профіль Steam\n"
                "• Чи правильний 17-значний Steam ID\n\n"
                "💡 *Рекомендуємо:* Використай /steam_login для повної функціональності!"
            )
            return
        
        # Валідуємо Steam ID
        if not await self.steam_api.validate_steam_id(steam_id):
            await update.message.reply_text(
                "❌ Steam ID недійсний або профіль недоступний!\n\n"
                "🔒 Можливі причини:\n"
                "• Профіль приватний\n"
                "• Steam ID неправильний\n"
                "• Тимчасові проблеми з Steam API\n\n"
                "💡 *Рекомендуємо:* Використай /steam_login для доступу до приватних профілів!"
            )
            return
        
        # Отримуємо інформацію про гравця
        players = await self.steam_api.get_player_summaries([steam_id])
        if not players:
            await update.message.reply_text("❌ Не вдалося отримати інформацію про профіль!")
            return
        
        player = players[0]
        
        # Перевіряємо чи існує користувач, якщо ні - створюємо
        user = self.user_db.get_user(user_id)
        if not user:
            user = User(telegram_id=user_id, username=update.effective_user.username)
            self.user_db.create_user(user)
        
        # Зберігаємо Steam ID
        success = self.user_db.update_steam_id(user_id, steam_id)
        if success:
            await update.message.reply_text(
                f"✅ Steam ID успішно встановлено!\n\n"
                f"👤 Профіль: {player.get('personaname', 'Невідомо')}\n"
                f"🆔 Steam ID: {steam_id}\n\n"
                f"🎯 Тепер ти можеш:\n"
                f"• Переглядати публічну статистику /stats\n"
                f"• Додавати друзів /add_friend\n"
                f"• Змагатися в рейтингу /leaderboard\n\n"
                f"⚠️ **Обмеження:** Доступна тільки публічна статистика!\n"
                f"💡 **Для повної функціональності:** Використай /steam_login"
            )
        else:
            await update.message.reply_text("❌ Помилка збереження Steam ID. Спробуй пізніше.")

    async def faceit_stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обробник команди /faceit_stats - статистика FACEIT"""
        user_id = update.effective_user.id
        user = self.user_db.get_user(user_id)
        
        if not user or not user.steam_id:
            await update.message.reply_text(
                "❌ Спочатку встанови свій Steam ID!\n\n"
                "🔧 Використай команди:\n"
                "/steam_login - авторизуватися через Steam\n"
                "/steam_manual YOUR_STEAM_ID - встановити вручну"
            )
            return
        
        await update.message.reply_text("🏆 Завантажую FACEIT статистику...")
        
        try:
            # Імпортуємо FACEIT API
            from ..services.faceit_api import FaceitAPI
            
            # TODO: Отримати FACEIT API ключ з конфігурації
            faceit_api = FaceitAPI(api_key="YOUR_FACEIT_API_KEY")
            
            # Отримуємо гравця за Steam ID
            player = await faceit_api.get_player_by_steam_id(user.steam_id)
            
            if not player:
                await update.message.reply_text(
                    "❌ FACEIT профіль не знайдено!\n\n"
                    "💡 Можливі причини:\n"
                    "• Гравець не зареєстрований на FACEIT\n"
                    "• Steam ID не пов'язаний з FACEIT\n"
                    "• Профіль приватний\n\n"
                    "🔗 Зареєструйся на: faceit.com"
                )
                return
            
            # Отримуємо статистику
            stats_data = await faceit_api.get_player_stats(player['player_id'])
            if not stats_data:
                await update.message.reply_text("❌ Не вдалося отримати FACEIT статистику!")
                return
            
            # Парсимо статистику
            stats = faceit_api.parse_player_stats(stats_data)
            
            # Формуємо повідомлення
            stats_text = f"""
🏆 FACEIT статистика для {player.get('nickname', 'Невідомо')}

📊 Основні показники:
• Матчів зіграно: {stats['matches_played']}
• Перемог: {stats['wins']} ({stats['win_rate']}%)
• K/D Ratio: {stats['kd_ratio']}
• Headshot %: {stats['headshot_percent']}%

🎯 Середні показники:
• Вбивств за матч: {stats['average_kills']}
• Смертей за матч: {stats['average_deaths']}
• Асистів за матч: {stats['average_assists']}
• Headshot за матч: {stats['average_hs']}

🔥 Серії:
• Поточна серія перемог: {stats['current_win_streak']}
• Найдовша серія перемог: {stats['longest_win_streak']}
• Поточна серія поразок: {stats['current_lose_streak']}

💡 Команди:
/faceit_matches - останні 20 матчів
/faceit_compare STEAM_ID - порівняти з гравцем
"""
            await update.message.reply_text(stats_text)
            
        except Exception as e:
            await update.message.reply_text(f"❌ Помилка FACEIT API: {str(e)}")

    async def faceit_matches_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обробник команди /faceit_matches - останні матчі FACEIT"""
        user_id = update.effective_user.id
        user = self.user_db.get_user(user_id)
        
        if not user or not user.steam_id:
            await update.message.reply_text(
                "❌ Спочатку встанови свій Steam ID!\n\n"
                "🔧 Використай команди:\n"
                "/steam_login - авторизуватися через Steam\n"
                "/steam_manual YOUR_STEAM_ID - встановити вручну"
            )
            return
        
        await update.message.reply_text("🎮 Завантажую останні FACEIT матчі...")
        
        try:
            from ..services.faceit_api import FaceitAPI
            faceit_api = FaceitAPI(api_key="YOUR_FACEIT_API_KEY")
            
            # Отримуємо гравця
            player = await faceit_api.get_player_by_steam_id(user.steam_id)
            if not player:
                await update.message.reply_text("❌ FACEIT профіль не знайдено!")
                return
            
            # Отримуємо останні матчі
            matches = await faceit_api.get_recent_matches(player['player_id'], limit=20)
            if not matches:
                await update.message.reply_text("❌ Не вдалося отримати матчі!")
                return
            
            # Формуємо список матчів
            matches_text = f"""
🎮 Останні 20 FACEIT матчів для {player.get('nickname', 'Невідомо')}

"""
            
            for i, match in enumerate(matches[:10], 1):  # Показуємо перші 10
                parsed_match = faceit_api.parse_match(match)
                result_emoji = "✅" if parsed_match['result'] == 'Victory' else "❌"
                
                matches_text += f"""
{i}. {result_emoji} {parsed_match['map']} - {parsed_match['score']}
   K/D: {parsed_match['kills']}/{parsed_match['deaths']} ({parsed_match['kd_ratio']})
   HS: {parsed_match['headshots']} | MVP: {parsed_match['mvp']}
   ELO: {parsed_match['elo']} ({parsed_match['elo_change']:+d})
"""
            
            if len(matches) > 10:
                matches_text += f"\n... та ще {len(matches) - 10} матчів"
            
            await update.message.reply_text(matches_text)
            
        except Exception as e:
            await update.message.reply_text(f"❌ Помилка отримання матчів: {str(e)}")

    async def recent_activity_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обробник команди /recent_activity"""
        user_id = update.effective_user.id
        user = self.user_db.get_user(user_id)
        
        if not user or not user.steam_id:
            await update.message.reply_text(
                "❌ Спочатку встанови свій Steam ID командою `/steam`",
                parse_mode='Markdown'
            )
            return
        
        # Перевіряємо кількість днів
        days = 7
        if context.args:
            try:
                days = int(context.args[0])
                if days < 1 or days > 365:
                    days = 7
            except ValueError:
                days = 7
        
        await update.message.reply_text(f"📊 Аналізую активність за останні {days} днів...")
        
        try:
            activity = await self.steam_api.get_recent_activity(user.steam_id, days)
            if not activity:
                await update.message.reply_text("❌ Не вдалося отримати інформацію про активність!")
                return
            
            activity_text = f"""
📈 **Активність гравця {activity['player_name']}**

🕒 **Останній онлайн:**
• Дата: **{activity['last_online']}**
• Днів тому: **{activity['days_since_online']}**
• Статус: {'🟢 Активний' if activity['is_recently_active'] else '🔴 Неактивний'}

🎯 **Останній матч:**
"""
            
            # Додаємо статистику останнього матчу якщо є
            last_match_stats = activity['last_match_stats']
            if last_match_stats.get('stats'):
                stats_dict = {}
                for stat in last_match_stats['stats']:
                    stats_dict[stat['name']] = stat['value']
                
                kills = stats_dict.get('last_match_kills', 0)
                deaths = stats_dict.get('last_match_deaths', 0)
                mvps = stats_dict.get('last_match_mvps', 0)
                damage = stats_dict.get('last_match_damage', 0)
                
                if kills > 0 or deaths > 0:
                    activity_text += f"• K/D: **{kills}/{deaths}**\n"
                    activity_text += f"• MVP: **{mvps}**\n"
                    activity_text += f"• Урон: **{damage:,}**\n"
                else:
                    activity_text += "• Немає даних про останній матч\n"
            else:
                activity_text += "• Немає даних про останній матч\n"
            
            activity_text += f"\n💡 Використай `/stats week` для тижневої статистики"
            
            await update.message.reply_text(activity_text, parse_mode='Markdown')
            
        except Exception as e:
            await update.message.reply_text(f"❌ Помилка: {str(e)}")

    async def time_stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обробник команди /time_stats для порівняння статистики за різні періоди"""
        user_id = update.effective_user.id
        user = self.user_db.get_user(user_id)
        
        if not user or not user.steam_id:
            await update.message.reply_text(
                "❌ Спочатку встанови свій Steam ID командою `/steam`",
                parse_mode='Markdown'
            )
            return
        
        await update.message.reply_text("📊 Порівнюю статистику за різні періоди...")
        
        try:
            # Отримуємо статистику за різні періоди
            all_stats = await self.steam_api.get_player_stats(user.steam_id, "all")
            last_match_stats = await self.steam_api.get_player_stats(user.steam_id, "last_match")
            
            if not all_stats:
                await update.message.reply_text("❌ Не вдалося отримати статистику!")
                return
            
            # Парсимо статистику
            all_parsed = self.steam_api.parse_cs2_stats(all_stats)
            last_match_parsed = self.steam_api.parse_cs2_stats(last_match_stats) if last_match_stats else None
            
            players = await self.steam_api.get_player_summaries([user.steam_id])
            player_name = players[0].get('personaname', 'Невідомо') if players else 'Невідомо'
            
            comparison_text = f"""
📊 **Порівняння статистики для {player_name}**

🎯 **За весь час:**
• K/D: **{all_parsed['kd_ratio']}** | Win Rate: **{all_parsed['win_rate']}%**
• Headshot %: **{all_parsed['headshot_percent']}%** | Точність: **{all_parsed['accuracy_percent']}%**
• Impact Score: **{self.steam_api.calculate_impact_score(all_parsed)}/100**
"""
            
            if last_match_parsed and last_match_parsed.get('kills', 0) > 0:
                comparison_text += f"""
🎮 **Останній матч:**
• K/D: **{last_match_parsed['kd_ratio']}** | Win Rate: **{last_match_parsed['win_rate']}%**
• Headshot %: **{last_match_parsed['headshot_percent']}%** | Точність: **{last_match_parsed['accuracy_percent']}%**
• Impact Score: **{self.steam_api.calculate_impact_score(last_match_parsed)}/100**
"""
            
            comparison_text += f"""
💡 **Команди для фільтрації:**
• `/stats` - загальна статистика
• `/stats last_match` - останній матч
• `/recent_activity 7` - активність за 7 днів
"""
            
            await update.message.reply_text(comparison_text, parse_mode='Markdown')
            
        except Exception as e:
            await update.message.reply_text(f"❌ Помилка: {str(e)}")

    async def last_matches_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обробник команди /last_matches для статистики за останні N матчів"""
        user_id = update.effective_user.id
        user = self.user_db.get_user(user_id)
        
        if not user or not user.steam_id:
            await update.message.reply_text(
                "❌ Спочатку встанови свій Steam ID командою `/steam`",
                parse_mode='Markdown'
            )
            return
        
        # Перевіряємо кількість матчів
        matches_count = 20
        if context.args:
            try:
                matches_count = int(context.args[0])
                if matches_count < 1 or matches_count > 100:
                    matches_count = 20
            except ValueError:
                matches_count = 20
        
        await update.message.reply_text(f"📊 Аналізую статистику за останні {matches_count} матчів...")
        
        try:
            recent_stats = await self.steam_api.get_recent_matches_stats(user.steam_id, matches_count)
            if not recent_stats:
                await update.message.reply_text("❌ Не вдалося отримати статистику!")
                return
            
            stats = self.steam_api.parse_cs2_stats(recent_stats)
            players = await self.steam_api.get_player_summaries([user.steam_id])
            player_name = players[0].get('personaname', 'Невідомо') if players else 'Невідомо'
            impact_score = self.steam_api.calculate_impact_score(stats)
            
            matches_text = f"""
🎮 **Статистика за останні {matches_count} матчів**
👤 **Гравець:** {player_name}

📊 **Основні показники:**
• K/D Ratio: **{stats['kd_ratio']}** ({stats['kills']} / {stats['deaths']})
• Win Rate: **{stats['win_rate']}%** ({stats['wins']}/{stats['matches_played']})
• Headshot %: **{stats['headshot_percent']}%**
• Точність: **{stats['accuracy_percent']}%**

🏆 **Досягнення:**
• MVP: **{stats['mvps']}** ({stats['mvp_percent']}%)
• Урон за матч: **{stats['damage_per_match']:,}**
• Асисти за матч: **{stats['assists_per_match']}**

🔥 **Додатково:**
• Домінації: **{stats['dominations']}** | Помсти: **{stats['revenges']}**
• Вбивств зброєю ворога: **{stats['enemy_weapon_kills']}**
• Вбивств осліплених: **{stats['blinded_kills']}**
• Ножових дуелей: **{stats['knife_fight_kills']}**
• Зброї подаровано: **{stats['weapons_donated']}**

⚡ **Impact Score: {impact_score}/100**

📝 *{recent_stats.get('note', 'Приблизна статистика')}*
📊 Розраховано на основі {recent_stats.get('total_matches', 0)} загальних матчів
"""
            
            await update.message.reply_text(matches_text, parse_mode='Markdown')
            
        except Exception as e:
            await update.message.reply_text(f"❌ Помилка: {str(e)}")

    async def demo_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обробник команди /demo для роботи з демо-файлами"""
        user_id = update.effective_user.id
        user = self.user_db.get_user(user_id)
        
        if not user or not user.steam_id:
            await update.message.reply_text(
                "❌ Спочатку встанови свій Steam ID командою `/steam`",
                parse_mode='Markdown'
            )
            return
        
        await update.message.reply_text("📊 Аналізую доступність демо-файлів...")
        
        try:
            demo_analysis = await self.steam_api.get_demo_analysis(user.steam_id)
            if not demo_analysis:
                await update.message.reply_text("❌ Не вдалося отримати інформацію про демо!")
                return
            
            demo_text = f"""
🎬 **Демо-файли для {demo_analysis['player_name']}**

📋 **Доступність:**
• Steam Client: ✅ Доступно
• API доступ: ❌ Недоступно
• Останній онлайн: {demo_analysis['last_online']}

🔗 **Способи завантаження:**

1️⃣ **Steam Client:**
• Відкрий Steam
• Перейди в CS2
• Відкрий Watch → Your Matches
• Завантаж потрібний матч

2️⃣ **Steam Community:**
• Переглянь матчі в профілі
• Знайди потрібний матч
• Завантаж демо

💡 **Рекомендації:**
• Демо зберігаються локально в Steam
• Використай CSGO Demo Manager для аналізу
• HLTV надає додаткові інструменти
• Демо доступні тільки для твоїх матчів

⚠️ **Обмеження:**
• Steam API не надає прямий доступ до демо
• Демо доступні тільки через Steam Client
• Потрібно бути учасником матчу
"""
            
            await update.message.reply_text(demo_text, parse_mode='Markdown')
            
        except Exception as e:
            await update.message.reply_text(f"❌ Помилка: {str(e)}")

    async def match_details_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обробник команди /match_details для деталей останнього матчу"""
        user_id = update.effective_user.id
        user = self.user_db.get_user(user_id)
        
        if not user or not user.steam_id:
            await update.message.reply_text(
                "❌ Спочатку встанови свій Steam ID командою `/steam`",
                parse_mode='Markdown'
            )
            return
        
        await update.message.reply_text("📊 Аналізую деталі останнього матчу...")
        
        try:
            match_details = await self.steam_api.get_match_details(user.steam_id)
            if not match_details:
                await update.message.reply_text("❌ Не вдалося отримати деталі матчу!")
                return
            
            stats = match_details['stats']
            
            # Розраховуємо додаткові показники
            kd_ratio = round(stats['kills'] / stats['deaths'], 2) if stats['deaths'] > 0 else stats['kills']
            result = "Перемога" if stats['total_wins'] > 0 else "Поразка"
            
            match_text = f"""
🎮 **Деталі останнього матчу**
👤 **Гравець:** {match_details['player_name']}

📊 **Результат:**
• Результат: **{result}**
• K/D: **{stats['kills']}/{stats['deaths']}** ({kd_ratio})
• MVP: **{stats['mvps']}**
• Урон: **{stats['damage']:,}**
• Раунди: **{stats['rounds']}**
• Contribution: **{stats['contribution_score']}**

🎯 **Рахунок:**
• T сторона: **{stats['t_wins']}** раундів
• CT сторона: **{stats['ct_wins']}** раундів
• Загалом: **{stats['total_wins']}** раундів

🎬 **Демо-файл:**
• Доступний: {'✅' if match_details['demo_info']['available'] else '❌'}
• Примітка: {match_details['demo_info']['note']}

💡 **Для завантаження демо:**
• Відкрий Steam → CS2 → Watch → Your Matches
• Знайди цей матч і завантаж демо
• Демо зберігається локально в Steam
"""
            
            await update.message.reply_text(match_text, parse_mode='Markdown')
            
        except Exception as e:
            await update.message.reply_text(f"❌ Помилка: {str(e)}")

    async def demo_help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обробник команди /demo_help для довідки по демо"""
        help_text = """
🎬 **Довідка по демо-файлам**

📋 **Що таке демо-файли:**
• Записи матчів CS2
• Можна переглядати з будь-якого кута
• Аналізувати свої помилки
• Вивчати тактики суперників

🔧 **Як завантажити демо:**

1️⃣ **Через Steam Client:**
• Відкрий Steam
• Запусти CS2
• Перейди в Watch → Your Matches
• Знайди потрібний матч
• Натисни Download

2️⃣ **Через Steam Community:**
• Відкрий свій профіль Steam
• Перейди в Game Stats → CS2
• Знайди матчі
• Завантаж демо

📁 **Де зберігаються демо:**
```
Windows: C:\Program Files (x86)\Steam\steamapps\common\Counter-Strike Global Offensive\csgo\replays
macOS: ~/Library/Application Support/Steam/steamapps/common/Counter-Strike Global Offensive/csgo/replays
Linux: ~/.steam/steam/steamapps/common/Counter-Strike Global Offensive/csgo/replays
```

🛠️ **Інструменти для аналізу:**
• **CSGO Demo Manager** - найпопулярніший
• **HLTV** - професійний аналіз
• **Steam Watch** - вбудований плеєр
• **GOTV** - для турнірних матчів

💡 **Поради:**
• Демо доступні тільки для твоїх матчів
• Зберігай важливі демо
• Аналізуй свої помилки
• Вивчай тактики кращих гравців

⚠️ **Обмеження:**
• Steam API не надає прямий доступ
• Потрібен Steam Client
• Демо займають місце на диску
"""
        
        await update.message.reply_text(help_text, parse_mode='Markdown')



    def extract_steam_id(self, text: str) -> Optional[str]:
        """Витягти Steam ID з тексту"""
        # Регулярний вираз для 17-значного Steam ID
        steam_id_pattern = r'\b7656119[0-9]{10}\b'
        match = re.search(steam_id_pattern, text)
        return match.group() if match else None

    async def demo_analysis_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обробник команди /demo_analysis для аналізу демо"""
        user_id = update.effective_user.id
        user = self.user_db.get_user(user_id)
        
        if not user or not user.steam_id:
            await update.message.reply_text(
                "❌ Спочатку встанови свій Steam ID командою `/steam`",
                parse_mode='Markdown'
            )
            return
        
        # Перевіряємо чи є match_id
        if not context.args:
            await update.message.reply_text(
                "❌ Вкажи ID матчу для аналізу!\n\n"
                "📝 **Приклад:**\n"
                "`/demo_analysis match_12345`\n\n"
                "💡 **Як отримати ID матчу:**\n"
                "• З Steam Client після матчу\n"
                "• З профілю Steam в розділі матчів",
                parse_mode='Markdown'
            )
            return
        
        match_id = context.args[0]
        
        await update.message.reply_text(f"🎮 Аналізую демо матчу {match_id}...")
        
        try:
            # Імпортуємо DemoAnalyzer
            from src.services.demo_analyzer import DemoAnalyzer
            demo_analyzer = DemoAnalyzer(self.steam_api.api_key)
            
            # Завантажуємо демо
            demo_path = await demo_analyzer.download_demo(user.steam_id, match_id)
            if not demo_path:
                await update.message.reply_text("❌ Не вдалося завантажити демо-файл!")
                return
            
            # Аналізуємо демо
            analysis_result = await demo_analyzer.analyze_demo(demo_path, user.steam_id, match_id)
            if not analysis_result:
                await update.message.reply_text("❌ Помилка аналізу демо!")
                return
            
            # Зберігаємо аналіз в базі даних
            from src.models.user import MatchAnalysis
            match_analysis = MatchAnalysis(
                steam_id=user.steam_id,
                match_id=match_id,
                match_date=datetime.now(),
                demo_path=demo_path
            )
            match_analysis.analyzed = True
            match_analysis.analysis_data = analysis_result
            
            self.user_db.save_match_analysis(match_analysis)
            
            # Створюємо звіт
            summary = await demo_analyzer.get_analysis_summary(analysis_result)
            
            # Видаляємо демо-файл
            await demo_analyzer.cleanup_demo(demo_path)
            
            await update.message.reply_text(summary, parse_mode='Markdown')
            
        except Exception as e:
            await update.message.reply_text(f"❌ Помилка: {str(e)}")

    async def demo_history_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обробник команди /demo_history для історії аналізованих матчів"""
        user_id = update.effective_user.id
        user = self.user_db.get_user(user_id)
        
        if not user or not user.steam_id:
            await update.message.reply_text(
                "❌ Спочатку встанови свій Steam ID командою `/steam`",
                parse_mode='Markdown'
            )
            return
        
        # Перевіряємо кількість матчів для показу
        limit = 10
        if context.args:
            try:
                limit = int(context.args[0])
                if limit < 1 or limit > 50:
                    limit = 10
            except ValueError:
                limit = 10
        
        await update.message.reply_text(f"📊 Завантажую історію аналізованих матчів...")
        
        try:
            # Отримуємо останні аналізовані матчі
            recent_matches = self.user_db.get_recent_matches(user.steam_id, limit)
            
            if not recent_matches:
                await update.message.reply_text(
                    "📝 **Історія аналізованих матчів порожня**\n\n"
                    "💡 **Щоб додати матч:**\n"
                    "`/demo_analysis match_id` - аналізувати демо матчу\n\n"
                    "🎮 **Приклад:**\n"
                    "`/demo_analysis match_12345`",
                    parse_mode='Markdown'
                )
                return
            
            # Створюємо список матчів
            history_text = f"📊 **Історія аналізованих матчів** ({len(recent_matches)})\n\n"
            
            for i, match in enumerate(recent_matches, 1):
                match_date = match.match_date.strftime('%d.%m.%Y %H:%M')
                analyzed_status = "✅" if match.analyzed else "⏳"
                
                history_text += f"{i}. {analyzed_status} **{match.match_id}**\n"
                history_text += f"   📅 {match_date}\n"
                
                if match.analyzed and match.analysis_data:
                    analysis = match.analysis_data
                    if 'match_info' in analysis:
                        map_name = analysis['match_info'].get('map', 'Невідомо')
                        win_rate = analysis['match_info'].get('win_rate', 0)
                        history_text += f"   🗺️ {map_name} | Win Rate: {win_rate}%\n"
                    
                    if 'player_stats' in analysis:
                        stats = analysis['player_stats']
                        kd = stats.get('kd_ratio', 0)
                        kills = stats.get('kills', 0)
                        deaths = stats.get('deaths', 0)
                        history_text += f"   🎯 K/D: {kd} ({kills}/{deaths})\n"
                
                history_text += "\n"
            
            history_text += f"💡 Використай `/demo_analysis match_id` для аналізу нового матчу"
            
            await update.message.reply_text(history_text, parse_mode='Markdown')
            
        except Exception as e:
            await update.message.reply_text(f"❌ Помилка: {str(e)}")

    async def demo_stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обробник команди /demo_stats для статистики з аналізованих матчів"""
        user_id = update.effective_user.id
        user = self.user_db.get_user(user_id)
        
        if not user or not user.steam_id:
            await update.message.reply_text(
                "❌ Спочатку встанови свій Steam ID командою `/steam`",
                parse_mode='Markdown'
            )
            return
        
        await update.message.reply_text("📊 Аналізую статистику з демо...")
        
        try:
            # Отримуємо всі аналізовані матчі
            all_matches = self.user_db.get_recent_matches(user.steam_id, 100)
            analyzed_matches = [m for m in all_matches if m.analyzed and m.analysis_data]
            
            if not analyzed_matches:
                await update.message.reply_text(
                    "📝 **Немає аналізованих матчів**\n\n"
                    "💡 Спочатку проаналізуй кілька матчів:\n"
                    "`/demo_analysis match_id`",
                    parse_mode='Markdown'
                )
                return
            
            # Розраховуємо загальну статистику
            total_kills = 0
            total_deaths = 0
            total_mvps = 0
            total_headshots = 0
            total_damage = 0
            total_rounds = 0
            total_wins = 0
            weapon_stats = {}
            map_stats = {}
            
            for match in analyzed_matches:
                analysis = match.analysis_data
                
                if 'player_stats' in analysis:
                    stats = analysis['player_stats']
                    total_kills += stats.get('kills', 0)
                    total_deaths += stats.get('deaths', 0)
                    total_mvps += stats.get('mvps', 0)
                    total_headshots += stats.get('headshots', 0)
                    total_damage += stats.get('damage_dealt', 0)
                
                if 'match_info' in analysis:
                    match_info = analysis['match_info']
                    total_rounds += match_info.get('rounds_played', 0)
                    total_wins += match_info.get('rounds_won', 0)
                    
                    map_name = match_info.get('map', 'Невідомо')
                    if map_name not in map_stats:
                        map_stats[map_name] = {'rounds': 0, 'wins': 0}
                    map_stats[map_name]['rounds'] += match_info.get('rounds_played', 0)
                    map_stats[map_name]['wins'] += match_info.get('rounds_won', 0)
                
                if 'weapon_stats' in analysis:
                    for weapon, stats in analysis['weapon_stats'].items():
                        if weapon not in weapon_stats:
                            weapon_stats[weapon] = {'kills': 0, 'accuracy': 0, 'count': 0}
                        weapon_stats[weapon]['kills'] += stats.get('kills', 0)
                        weapon_stats[weapon]['accuracy'] += stats.get('accuracy', 0)
                        weapon_stats[weapon]['count'] += 1
            
            # Розраховуємо середні показники
            matches_count = len(analyzed_matches)
            avg_kd = round(total_kills / max(total_deaths, 1), 2)
            avg_headshot = round((total_headshots / max(total_kills, 1)) * 100, 1)
            avg_damage = round(total_damage / matches_count, 0)
            win_rate = round((total_wins / max(total_rounds, 1)) * 100, 1)
            
            # Створюємо звіт
            stats_text = f"""
📊 **Статистика з {matches_count} аналізованих матчів**

🎯 **Загальні показники:**
• Матчів аналізовано: **{matches_count}**
• Загальний K/D: **{avg_kd}** ({total_kills}/{total_deaths})
• Headshot %: **{avg_headshot}%**
• MVP: **{total_mvps}**
• Урон за матч: **{avg_damage:,}**
• Win Rate: **{win_rate}%**

🗺️ **Топ картини:**
"""
            
            # Сортуємо картини за кількістю раундів
            sorted_maps = sorted(map_stats.items(), key=lambda x: x[1]['rounds'], reverse=True)
            for i, (map_name, stats) in enumerate(sorted_maps[:3], 1):
                map_win_rate = round((stats['wins'] / max(stats['rounds'], 1)) * 100, 1)
                stats_text += f"{i}. **{map_name}**: {stats['rounds']} раундів ({map_win_rate}%)\n"
            
            stats_text += "\n🔫 **Топ зброя:**\n"
            
            # Сортуємо зброю за кількістю вбивств
            sorted_weapons = sorted(weapon_stats.items(), key=lambda x: x[1]['kills'], reverse=True)
            for i, (weapon, stats) in enumerate(sorted_weapons[:3], 1):
                avg_accuracy = round(stats['accuracy'] / max(stats['count'], 1), 1)
                stats_text += f"{i}. **{weapon}**: {stats['kills']} вбивств ({avg_accuracy}% точність)\n"
            
            stats_text += f"\n💡 Використай `/demo_history` для перегляду всіх матчів"
            
            await update.message.reply_text(stats_text, parse_mode='Markdown')
            
        except Exception as e:
            await update.message.reply_text(f"❌ Помилка: {str(e)}")

    async def enable_monitoring_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обробник команди /enable_monitoring для увімкнення автоматичного моніторингу"""
        user_id = update.effective_user.id
        user = self.user_db.get_user(user_id)
        
        if not user or not user.steam_id:
            await update.message.reply_text("❌ Спочатку увійдіть через Steam: /steam_login")
            return
        
        # Оновлюємо статус моніторингу в базі даних
        user.monitoring_enabled = True
        self.user_db.update_user(user)
        
        await update.message.reply_text(
            "✅ **Автоматичний моніторинг увімкнено!**\n\n"
            "🎮 Тепер ви будете отримувати повідомлення після кожного завершеного матчу\n"
            "📊 Кожен матч буде автоматично проаналізовано\n"
            "🗑️ Демо-файли будуть видалені після аналізу\n\n"
            "💡 Використайте `/disable_monitoring` для вимкнення"
        )
    
    async def disable_monitoring_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обробник команди /disable_monitoring для вимкнення автоматичного моніторингу"""
        user_id = update.effective_user.id
        user = self.user_db.get_user(user_id)
        
        if not user or not user.steam_id:
            await update.message.reply_text("❌ Спочатку увійдіть через Steam: /steam_login")
            return
        
        # Оновлюємо статус моніторингу в базі даних
        user.monitoring_enabled = False
        self.user_db.update_user(user)
        
        await update.message.reply_text(
            "❌ **Автоматичний моніторинг вимкнено!**\n\n"
            "🎮 Ви більше не будете отримувати автоматичні повідомлення\n"
            "💡 Використайте `/enable_monitoring` для повторного увімкнення"
        )
    
    async def monitoring_status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обробник команди /monitoring_status для перевірки статусу моніторингу"""
        user_id = update.effective_user.id
        user = self.user_db.get_user(user_id)
        
        if not user or not user.steam_id:
            await update.message.reply_text("❌ Спочатку увійдіть через Steam: /steam_login")
            return
        
        status = "✅ Увімкнено" if getattr(user, 'monitoring_enabled', False) else "❌ Вимкнено"
        
        await update.message.reply_text(
            f"📊 **Статус автоматичного моніторингу:** {status}\n\n"
            f"🎮 Steam ID: `{user.steam_id}`\n"
            f"⏰ Перевірка кожні 5 хвилин\n"
            f"📱 Повідомлення: {'Так' if getattr(user, 'monitoring_enabled', False) else 'Ні'}\n"
            f"🎬 Аналіз демо: {'Так' if getattr(user, 'monitoring_enabled', False) else 'Ні'}\n\n"
            f"💡 Команди:\n"
            f"• `/enable_monitoring` - увімкнути\n"
            f"• `/disable_monitoring` - вимкнути"
        )

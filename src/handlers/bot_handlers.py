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
from ..services.steam_scraper import SteamScraper


class BotHandlers:
    def __init__(self, user_db: UserDatabase, steam_api: SteamAPI, daily_reports_service: DailyReportsService = None):
        self.user_db = user_db
        self.steam_api = steam_api
        self.daily_reports_service = daily_reports_service

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
/steam `<Steam_ID>` - встановити свій Steam ID
/steam `<vanity_url>` - встановити через нік (напр: /steam nickname)

👥 **Друзі:**
/add_friend `<Steam_ID>` - додати друга
/remove_friend `<Steam_ID>` - видалити друга
/friends - список моїх друзів

📊 **Статистика:**
/stats - загальна статистика
/week_stats - тижнева статистика
/month_stats - місячна статистика
/detailed_stats - детальна статистика з Impact Score
/weapon_stats - статистика по зброї
/compare `<Steam_ID>` - порівняти з гравцем

🏆 **Рейтинги:**
/friends_stats - рейтинг моїх друзів
/leaderboard - топ гравців серед всіх користувачів

📅 **Щоденні звіти:**
/daily_report - отримати щоденний звіт зараз
/report_settings - налаштування звітів

ℹ️ **Інформація:**
/about - про бота та Impact Score
/help - ця довідка

💡 **Приклади використання:**
`/steam 76561198123456789`
`/steam nickname`
`/add_friend 76561198987654321`
`/compare 76561198987654321`

🎯 **Impact Score** - це наш власний алгоритм оцінки гравця, що враховує:
• K/D Ratio (25%)
• Win Rate (30%)
• Headshot % (20%)
• Assists per Match (15%)
• MVP % (10%)
"""
        
        await update.message.reply_text(help_text)

    async def steam_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обробник команди /steam для встановлення Steam ID"""
        user_id = update.effective_user.id
        
        if not context.args:
            await update.message.reply_text(
                "❌ Потрібно вказати Steam ID або нікнейм!\n\n"
                "📝 **Приклади:**\n"
                "`/steam 76561198123456789`\n"
                "`/steam nickname`\n\n"
                "🔍 **Як знайти свій Steam ID:**\n"
                "1. Відкрий свій профіль Steam\n"
                "2. Скопіюй числа з URL або використай нікнейм",
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
                "• Чи правильний 17-значний Steam ID"
            )
            return
        
        # Валідуємо Steam ID
        if not await self.steam_api.validate_steam_id(steam_id):
            await update.message.reply_text(
                "❌ Steam ID недійсний або профіль недоступний!\n\n"
                "🔒 Можливі причини:\n"
                "• Профіль приватний\n"
                "• Steam ID неправильний\n"
                "• Тимчасові проблеми з Steam API"
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
                f"• Переглядати статистику /stats\n"
                f"• Додавати друзів /add_friend\n"
                f"• Змагатися в рейтингу /leaderboard"
            )
        else:
            await update.message.reply_text("❌ Помилка збереження Steam ID. Спробуй пізніше.")

    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обробник команди /stats (загальна статистика)"""
        await self._get_stats(update, context, "all")
    
    async def week_stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обробник команди /week_stats (тижнева статистика)"""
        await self._get_stats(update, context, "week")
    
    async def month_stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обробник команди /month_stats (місячна статистика)"""
        await self._get_stats(update, context, "month")
    
    async def _get_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE, time_period: str = "all"):
        """Загальний метод для отримання статистики"""
        user_id = update.effective_user.id
        user = self.user_db.get_user(user_id)
        
        if not user or not user.steam_id:
            await update.message.reply_text(
                "❌ Спочатку встанови свій Steam ID!\n\n"
                "🔧 Використай команду:\n"
                "/steam YOUR_STEAM_ID"
            )
            return
        
        # Визначаємо назву періоду
        period_names = {
            "all": "загальна",
            "week": "тижнева", 
            "month": "місячна"
        }
        period_name = period_names.get(time_period, "загальна")
        
        # Показуємо індикатор завантаження
        await update.message.reply_text(f"📊 Завантажую {period_name} статистику...")
        
        try:
            # Отримуємо статистику
            raw_stats = await self.steam_api.get_player_stats(user.steam_id, time_period)
            if not raw_stats:
                await update.message.reply_text(
                    "❌ Не вдалося отримати статистику!\n\n"
                    "🔒 Можливі причини:\n"
                    "• Профіль Steam приватний\n"
                    "• Ще не грав у CS2\n"
                    "• Тимчасові проблеми з Steam API"
                )
                return
            
            # Парсимо статистику
            stats = self.steam_api.parse_cs2_stats(raw_stats)
            if not stats:
                await update.message.reply_text("❌ Не вдалося обробити статистику!")
                return
            
            # Отримуємо інформацію про гравця
            players = await self.steam_api.get_player_summaries([user.steam_id])
            player_name = players[0].get('personaname', 'Невідомо') if players else 'Невідомо'
            
            # Розраховуємо Impact Score
            impact_score = self.steam_api.calculate_impact_score(stats)
            
            # Перевіряємо на дивні дані
            data_warning = ""
            if stats['win_rate'] > 100 or stats['mvp_percent'] > 100:
                data_warning = "\n⚠️ Увага: Деякі дані можуть бути неточними через обмеження Steam API"
            
            # Формуємо повідомлення
            period_emoji = {"all": "🎮", "week": "📅", "month": "📊"}
            emoji = period_emoji.get(time_period, "🎮")
            
            stats_text = f"""
{emoji} {period_name.capitalize()} статистика для {player_name}

📊 Основні показники:
• K/D Ratio: {stats['kd_ratio']}
• Win Rate: {stats['win_rate']}%
• Зіграно матчів: {stats['matches_played']}
• Перемог: {stats['wins']}

🎯 Точність:
• Headshot %: {stats['headshot_percent']}%
• Загальна точність: {stats['accuracy_percent']}%

🏆 Досягнення:
• MVP раундів: {stats['mvps']} ({stats['mvp_percent']}%)
• Асистів на матч: {stats['assists_per_match']}

⚡ Impact Score: {impact_score}/100

💡 Інші періоди:
/stats - загальна статистика
/week_stats - тижнева статистика  
/month_stats - місячна статистика

⚠️ Увага: Steam API не підтримує фільтрацію по часу.
Всі команди показують загальну статистику за весь час гри.
Для отримання актуальної статистики використовуй /daily_report.{data_warning}
"""
            
            await update.message.reply_text(stats_text)
            
        except Exception as e:
            await update.message.reply_text(f"❌ Помилка отримання статистики: {str(e)}")

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
• Пострілів: **{stats['shots_fired']}** | Влучень: **{stats['shots_hit']}**

🏆 **Досягнення:**
• MVP раундів: **{stats['mvps']}** ({stats['mvp_percent']}%)
• Урон за матч: **{stats['damage_per_match']}**
• Загальний урон: **{stats['damage_dealt']:,}**

⚔️ **Додатково:**
• Раундів зіграно: **{stats['rounds_played']:,}**
• Ножових вбивств: **{stats['knife_kills']}**
• Бомб встановлено: **{stats['planted_bombs']}**
• Бомб розміновано: **{stats['defused_bombs']}**

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
🤖 **CS2 Stats Bot v1.0**

Цей бот допомагає відстежувати статистику Counter-Strike 2 та змагатися з друзями!

🧠 **Impact Score Algorithm:**
Наш власний алгоритм оцінки гравця:
• **K/D Ratio** (25%) - ефективність у вбивствах
• **Win Rate** (30%) - відсоток перемог  
• **Headshot %** (20%) - точність стрільби
• **Assists/Match** (15%) - командна гра
• **MVP %** (10%) - лідерські якості

🔧 **Технології:**
• Python + python-telegram-bot
• Steam Web API
• SQLite база даних
• Асинхронна обробка

👨‍💻 **Розробник:** @your_username
📊 **Версія:** 1.0 MVP
🔄 **Оновлення:** Автоматичні

💡 **Пропозиції та баги:** @your_username
⭐ **GitHub:** github.com/your_repo
"""
        
        await update.message.reply_text(about_text, parse_mode='Markdown')

    async def debug_stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обробник команди /debug_stats - показати всі доступні статистики"""
        user_id = update.effective_user.id
        user = self.user_db.get_user(user_id)
        
        if not user or not user.steam_id:
            await update.message.reply_text(
                "❌ Спочатку встанови свій Steam ID!\n\n"
                "🔧 Використай команду:\n"
                "/steam YOUR_STEAM_ID"
            )
            return
        
        await update.message.reply_text("🔍 Завантажую всі доступні статистики...")
        
        try:
            # Отримуємо сирі статистики
            raw_stats = await self.steam_api.get_player_stats(user.steam_id)
            if not raw_stats:
                await update.message.reply_text("❌ Не вдалося отримати статистику!")
                return
            
            # Парсимо щоб отримати всі доступні поля
            self.steam_api.parse_cs2_stats(raw_stats)
            
            if hasattr(self.steam_api, 'all_available_stats'):
                stats = self.steam_api.all_available_stats
                
                # Формуємо список всіх статистик
                stats_list = []
                for key, value in sorted(stats.items()):
                    stats_list.append(f"• {key}: {value}")
                
                debug_text = f"""
🔍 Всі доступні статистики Steam API:

📊 Загальна інформація:
{chr(10).join(stats_list[:20])}

📈 Всього полів: {len(stats)}

ℹ️ Це всі дані, які надає Steam API для CS2.
Вони не фільтруються по часу і показують загальну статистику за весь час гри.
"""
                
                # Розбиваємо на частини якщо повідомлення занадто довге
                if len(debug_text) > 4000:
                    parts = [debug_text[i:i+4000] for i in range(0, len(debug_text), 4000)]
                    for i, part in enumerate(parts):
                        await update.message.reply_text(f"Частина {i+1}/{len(parts)}:\n{part}")
                else:
                    await update.message.reply_text(debug_text)
            else:
                await update.message.reply_text("❌ Не вдалося отримати список статистик!")
                
        except Exception as e:
            await update.message.reply_text(f"❌ Помилка: {str(e)}")

    async def web_stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обробник команди /web_stats - статистика через веб-парсинг"""
        user_id = update.effective_user.id
        user = self.user_db.get_user(user_id)
        
        if not user or not user.steam_id:
            await update.message.reply_text(
                "❌ Спочатку встанови свій Steam ID!\n\n"
                "🔧 Використай команду:\n"
                "/steam YOUR_STEAM_ID"
            )
            return
        
        await update.message.reply_text("🌐 Завантажую статистику через веб-парсинг...")
        
        try:
            # Імпортуємо scraper
            from ..services.steam_scraper import SteamScraper
            scraper = SteamScraper()
            
            # Отримуємо статистику через веб-парсинг
            web_stats = await scraper.get_profile_stats(user.steam_id)
            
            print(f"🔍 Результат веб-парсингу: {web_stats}")
            
            if web_stats and len(web_stats) > 0:
                # Формуємо повідомлення
                stats_text = f"""
🌐 Статистика через веб-парсинг для {user.steam_id}

📊 Основні показники:
• Kills: {web_stats.get('kills', 'N/A')}
• Deaths: {web_stats.get('deaths', 'N/A')}
• Wins: {web_stats.get('wins', 'N/A')}
• Matches: {web_stats.get('matches', 'N/A')}
• MVPs: {web_stats.get('mvps', 'N/A')}
• Headshots: {web_stats.get('headshots', 'N/A')}
• Damage: {web_stats.get('damage', 'N/A')}

🔫 Зброя:
• AK47: {web_stats.get('ak47_kills', 'N/A')}
• M4A1: {web_stats.get('m4a1_kills', 'N/A')}
• AWP: {web_stats.get('awp_kills', 'N/A')}

ℹ️ Це дані отримані через парсинг веб-сторінки Steam.
Може містити більше деталей ніж API.
"""
                await update.message.reply_text(stats_text)
            else:
                await update.message.reply_text("❌ Не вдалося отримати статистику через веб-парсинг!")
                
        except Exception as e:
            await update.message.reply_text(f"❌ Помилка веб-парсингу: {str(e)}")

    def extract_steam_id(self, text: str) -> Optional[str]:
        """Витягти Steam ID з тексту"""
        # Регулярний вираз для 17-значного Steam ID
        steam_id_pattern = r'\b7656119[0-9]{10}\b'
        match = re.search(steam_id_pattern, text)
        return match.group() if match else None

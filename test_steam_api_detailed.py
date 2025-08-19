#!/usr/bin/env python3
"""
Тестовий скрипт для детального аналізу Steam API
"""
import asyncio
import json
import aiohttp
from src.services.steam_api import SteamAPI
from src.services.steam_oauth import SteamOAuth

# Конфігурація
STEAM_API_KEY = "6629403219DD2ADCA0D3F552F03F92A8"
STEAM_ID = "76561198329975115"  # Makiavellli
APP_DOMAIN = "tgcsstats-production.up.railway.app"

async def test_steam_api_detailed():
    """Тестуємо детальну роботу з Steam API"""
    print("🔍 Тестуємо детальну роботу з Steam API")
    print("=" * 50)
    
    steam_api = SteamAPI(STEAM_API_KEY)
    steam_oauth = SteamOAuth(STEAM_API_KEY, APP_DOMAIN)
    
    # 1. Отримуємо базову інформацію про гравця
    print("\n1️⃣ Базова інформація про гравця:")
    print("-" * 30)
    players = await steam_api.get_player_summaries([STEAM_ID])
    if players:
        player = players[0]
        print(f"👤 Ім'я: {player.get('personaname', 'Невідомо')}")
        print(f"🆔 Steam ID: {player.get('steamid', 'Невідомо')}")
        print(f"🌐 Профіль: {player.get('profileurl', 'Невідомо')}")
        print(f"📊 Статус: {player.get('personastate', 'Невідомо')}")
        print(f"🕒 Останній онлайн: {player.get('lastlogoff', 'Невідомо')}")
        print(f"🔒 Приватність: {player.get('communityvisibilitystate', 'Невідомо')}")
        print(f"✅ VAC бан: {player.get('vacbanned', False)}")
        print(f"🎮 Ігри: {player.get('gameextrainfo', 'Не в грі')}")
    else:
        print("❌ Не вдалося отримати інформацію про гравця")
    
    # 2. Отримуємо сиру статистику
    print("\n2️⃣ Сира статистика з Steam API:")
    print("-" * 30)
    raw_stats = await steam_api.get_player_stats(STEAM_ID)
    if raw_stats:
        print(f"✅ Статистика отримана")
        print(f"📊 Кількість статистик: {len(raw_stats.get('stats', []))}")
        print(f"🏆 Кількість досягнень: {len(raw_stats.get('achievements', []))}")
        
        # Показуємо всі доступні статистики
        print("\n📈 Всі доступні статистики:")
        stats = raw_stats.get('stats', [])
        
        # Групуємо статистики по категоріях
        categories = {
            'Основні': ['total_kills', 'total_deaths', 'total_wins', 'total_matches_played', 'total_mvps'],
            'Точність': ['total_shots_fired', 'total_shots_hit', 'total_kills_headshot'],
            'Зброя': ['total_kills_ak47', 'total_kills_m4a1', 'total_kills_awp', 'total_kills_deagle'],
            'Карти': ['total_wins_map_de_dust2', 'total_wins_map_de_inferno', 'total_wins_map_de_nuke'],
            'Додаткові': ['total_damage_done', 'total_money_earned', 'total_planted_bombs', 'total_defused_bombs']
        }
        
        for category, keys in categories.items():
            print(f"\n  📊 {category}:")
            for stat in stats:
                if any(key in stat['name'] for key in keys):
                    print(f"    • {stat['name']}: {stat['value']}")
        
        # Показуємо всі досягнення
        print("\n🏅 Всі досягнення:")
        achievements = raw_stats.get('achievements', [])
        for achievement in achievements:
            status = "✅" if achievement['achieved'] else "❌"
            name = achievement.get('name', 'Невідомо')
            description = achievement.get('description', 'Немає опису')
            print(f"  {status} {name}: {description}")
            
    else:
        print("❌ Не вдалося отримати статистику")
    
    # 3. Парсимо статистику
    print("\n3️⃣ Парсена статистика:")
    print("-" * 30)
    if raw_stats:
        parsed_stats = steam_api.parse_cs2_stats(raw_stats)
        print("📊 Основні показники:")
        for key, value in parsed_stats.items():
            if key != 'weapon_stats':
                print(f"  • {key}: {value}")
        
        print("\n🔫 Статистика по зброї:")
        weapon_stats = parsed_stats.get('weapon_stats', [])
        for weapon in weapon_stats:
            print(f"  • {weapon['name']}: {weapon['kills']} вбивств ({weapon['accuracy']}% точність)")
    
    # 4. Тестуємо приватну статистику через OAuth
    print("\n4️⃣ Спроба отримати приватну статистику:")
    print("-" * 30)
    private_stats = await steam_oauth.get_private_stats(STEAM_ID)
    if private_stats:
        print("✅ Приватна статистика доступна!")
        print(f"📊 Кількість статистик: {len(private_stats.get('stats', []))}")
        
        # Порівнюємо з публічною статистикою
        if raw_stats:
            public_count = len(raw_stats.get('stats', []))
            private_count = len(private_stats.get('stats', []))
            print(f"📈 Публічних статистик: {public_count}")
            print(f"🔒 Приватних статистик: {private_count}")
            print(f"📊 Різниця: {private_count - public_count} додаткових статистик")
    else:
        print("❌ Приватна статистика недоступна")
    
    # 5. Тестуємо різні API endpoints
    print("\n5️⃣ Тестуємо різні API endpoints:")
    print("-" * 30)
    
    # Steam API endpoints для тестування
    endpoints = [
        {
            'name': 'GetPlayerSummaries',
            'url': f'http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/',
            'params': {'key': STEAM_API_KEY, 'steamids': STEAM_ID}
        },
        {
            'name': 'GetUserStatsForGame',
            'url': f'http://api.steampowered.com/ISteamUserStats/GetUserStatsForGame/v0002/',
            'params': {'key': STEAM_API_KEY, 'steamid': STEAM_ID, 'appid': 730}
        },
        {
            'name': 'GetOwnedGames',
            'url': f'http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/',
            'params': {'key': STEAM_API_KEY, 'steamid': STEAM_ID, 'include_appinfo': 1, 'include_played_free_games': 1}
        },
        {
            'name': 'GetRecentlyPlayedGames',
            'url': f'http://api.steampowered.com/IPlayerService/GetRecentlyPlayedGames/v0001/',
            'params': {'key': STEAM_API_KEY, 'steamid': STEAM_ID, 'count': 10}
        }
    ]
    
    async with aiohttp.ClientSession() as session:
        for endpoint in endpoints:
            try:
                async with session.get(endpoint['url'], params=endpoint['params']) as response:
                    if response.status == 200:
                        data = await response.json()
                        print(f"✅ {endpoint['name']}: Успішно")
                        if 'response' in data:
                            response_data = data['response']
                            if isinstance(response_data, dict):
                                for key, value in response_data.items():
                                    if isinstance(value, list):
                                        print(f"    • {key}: {len(value)} елементів")
                                    else:
                                        print(f"    • {key}: {value}")
                    else:
                        print(f"❌ {endpoint['name']}: Помилка {response.status}")
            except Exception as e:
                print(f"❌ {endpoint['name']}: Помилка - {e}")

if __name__ == "__main__":
    asyncio.run(test_steam_api_detailed())

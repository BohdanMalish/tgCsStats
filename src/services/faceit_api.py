"""
Сервіс для роботи з FACEIT API
"""
import aiohttp
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class FaceitAPI:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://open.faceit.com/data/v4"
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Accept': 'application/json'
        }

    async def get_player_by_nickname(self, nickname: str) -> Optional[Dict[str, Any]]:
        """Отримати інформацію про гравця за нікнеймом"""
        try:
            url = f"{self.base_url}/players"
            params = {'nickname': nickname}
            
            async with aiohttp.ClientSession(headers=self.headers) as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        return await response.json()
                    elif response.status == 404:
                        logger.warning(f"FACEIT гравець не знайдений: {nickname}")
                        return None
                    else:
                        logger.error(f"FACEIT API помилка: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Помилка отримання FACEIT гравця: {e}")
            return None

    async def get_player_by_steam_id(self, steam_id: str) -> Optional[Dict[str, Any]]:
        """Отримати інформацію про гравця за Steam ID"""
        try:
            url = f"{self.base_url}/players"
            params = {'game': 'cs2', 'game_player_id': steam_id}
            
            async with aiohttp.ClientSession(headers=self.headers) as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        return await response.json()
                    elif response.status == 404:
                        logger.warning(f"FACEIT гравець не знайдений за Steam ID: {steam_id}")
                        return None
                    else:
                        logger.error(f"FACEIT API помилка: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Помилка отримання FACEIT гравця за Steam ID: {e}")
            return None

    async def get_player_stats(self, player_id: str) -> Optional[Dict[str, Any]]:
        """Отримати статистику гравця"""
        try:
            url = f"{self.base_url}/players/{player_id}/stats/cs2"
            
            async with aiohttp.ClientSession(headers=self.headers) as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.error(f"FACEIT API помилка статистики: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Помилка отримання FACEIT статистики: {e}")
            return None

    async def get_recent_matches(self, player_id: str, limit: int = 20) -> Optional[List[Dict[str, Any]]]:
        """Отримати останні матчі гравця"""
        try:
            url = f"{self.base_url}/players/{player_id}/history"
            params = {
                'game': 'cs2',
                'offset': 0,
                'limit': limit
            }
            
            async with aiohttp.ClientSession(headers=self.headers) as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('items', [])
                    else:
                        logger.error(f"FACEIT API помилка матчів: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Помилка отримання FACEIT матчів: {e}")
            return None

    async def get_match_details(self, match_id: str) -> Optional[Dict[str, Any]]:
        """Отримати деталі конкретного матчу"""
        try:
            url = f"{self.base_url}/matches/{match_id}"
            
            async with aiohttp.ClientSession(headers=self.headers) as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.error(f"FACEIT API помилка матчу: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Помилка отримання FACEIT матчу: {e}")
            return None

    def parse_player_stats(self, stats_data: Dict[str, Any]) -> Dict[str, Any]:
        """Парсинг статистики FACEIT гравця"""
        try:
            lifetime = stats_data.get('lifetime', {})
            
            return {
                'matches_played': lifetime.get('Matches', 0),
                'wins': lifetime.get('Wins', 0),
                'win_rate': round((lifetime.get('Wins', 0) / max(lifetime.get('Matches', 1), 1)) * 100, 1),
                'kills': lifetime.get('Kills', 0),
                'deaths': lifetime.get('Deaths', 0),
                'kd_ratio': round(lifetime.get('K/D Ratio', 0), 2),
                'headshots': lifetime.get('Headshots', 0),
                'headshot_percent': round((lifetime.get('Headshots', 0) / max(lifetime.get('Kills', 1), 1)) * 100, 1),
                'mvps': lifetime.get('MVPs', 0),
                'average_kills': round(lifetime.get('Average Kills', 0), 1),
                'average_deaths': round(lifetime.get('Average Deaths', 0), 1),
                'average_assists': round(lifetime.get('Average Assists', 0), 1),
                'average_hs': round(lifetime.get('Average Headshots', 0), 1),
                'current_win_streak': lifetime.get('Current Win Streak', 0),
                'longest_win_streak': lifetime.get('Longest Win Streak', 0),
                'current_lose_streak': lifetime.get('Current Lose Streak', 0),
                'longest_lose_streak': lifetime.get('Longest Lose Streak', 0)
            }
        except Exception as e:
            logger.error(f"Помилка парсингу FACEIT статистики: {e}")
            return {}

    def parse_match(self, match_data: Dict[str, Any]) -> Dict[str, Any]:
        """Парсинг матчу FACEIT"""
        try:
            return {
                'match_id': match_data.get('match_id', ''),
                'map': match_data.get('i1', 'Unknown'),
                'result': match_data.get('i18', 'Unknown'),
                'score': match_data.get('i19', '0-0'),
                'kills': match_data.get('Kills', 0),
                'deaths': match_data.get('Deaths', 0),
                'assists': match_data.get('Assists', 0),
                'mvp': match_data.get('MVPs', 0),
                'headshots': match_data.get('Headshots', 0),
                'kd_ratio': round(match_data.get('K/D Ratio', 0), 2),
                'date': match_data.get('Date', ''),
                'elo': match_data.get('Elo', 0),
                'elo_change': match_data.get('Elo Change', 0)
            }
        except Exception as e:
            logger.error(f"Помилка парсингу FACEIT матчу: {e}")
            return {}

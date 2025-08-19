"""
Сервіс для роботи з Steam API
"""
import aiohttp
import asyncio
from typing import Optional, Dict, Any, List
import json
from datetime import datetime, timedelta


class SteamAPI:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "http://api.steampowered.com"
        self.cs2_app_id = 730
        
    async def get_steam_id_from_vanity_url(self, vanity_url: str) -> Optional[str]:
        """Отримати Steam ID з vanity URL (наприклад, /id/nickname)"""
        url = f"{self.base_url}/ISteamUser/ResolveVanityURL/v0001/"
        params = {
            'key': self.api_key,
            'vanityurl': vanity_url,
            'url_type': 1
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data['response']['success'] == 1:
                            return data['response']['steamid']
            return None
        except Exception as e:
            print(f"Помилка отримання Steam ID: {e}")
            return None

    async def get_player_summaries(self, steam_ids: List[str]) -> Dict[str, Any]:
        """Отримати базову інформацію про гравців"""
        url = f"{self.base_url}/ISteamUser/GetPlayerSummaries/v0002/"
        params = {
            'key': self.api_key,
            'steamids': ','.join(steam_ids)
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data['response']['players']
            return []
        except Exception as e:
            print(f"Помилка отримання інформації про гравців: {e}")
            return []

    async def get_player_stats(self, steam_id: str, time_period: str = "all") -> Optional[Dict[str, Any]]:
        """
        Отримати статистику гравця для CS2
        
        Args:
            steam_id: Steam ID гравця
            time_period: Період статистики ("all", "week", "month")
        """
        url = f"{self.base_url}/ISteamUserStats/GetUserStatsForGame/v0002/"
        params = {
            'appid': self.cs2_app_id,
            'key': self.api_key,
            'steamid': steam_id
        }
        
        # Додаємо параметри часу якщо потрібно
        if time_period == "week":
            # Steam API не підтримує фільтрацію по часу, тому будемо використовувати загальну статистику
            # але додамо індикатор що це "тижнева" статистика
            params['time_period'] = 'week'
        elif time_period == "month":
            params['time_period'] = 'month'
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        stats = data['playerstats']
                        # Додаємо інформацію про період
                        stats['time_period'] = time_period
                        return stats
            return None
        except Exception as e:
            print(f"Помилка отримання статистики гравця {steam_id}: {e}")
            return None

    def parse_cs2_stats(self, raw_stats: Dict[str, Any]) -> Dict[str, Any]:
        """Парсинг сирих статистик CS2 у зручний формат"""
        if not raw_stats or 'stats' not in raw_stats:
            return {}
            
        stats_dict = {}
        for stat in raw_stats['stats']:
            stats_dict[stat['name']] = stat['value']
        
        # Розрахунок основних показників
        kills = stats_dict.get('total_kills', 0)
        deaths = stats_dict.get('total_deaths', 1)  # уникаємо ділення на нуль
        headshot_kills = stats_dict.get('total_kills_headshot', 0)
        shots_fired = stats_dict.get('total_shots_fired', 1)
        shots_hit = stats_dict.get('total_shots_hit', 0)
        wins = stats_dict.get('total_wins', 0)
        matches = stats_dict.get('total_matches_played', 1)
        mvps = stats_dict.get('total_mvps', 0)
        
        parsed = {
            # Базові статистики
            'kills': kills,
            'deaths': deaths,
            'assists': stats_dict.get('total_kills_assist', 0),
            'headshot_kills': headshot_kills,
            'shots_fired': shots_fired,
            'shots_hit': shots_hit,
            'damage_dealt': stats_dict.get('total_damage_done', 0),
            'money_earned': stats_dict.get('total_money_earned', 0),
            'wins': wins,
            'matches_played': matches,
            'mvps': mvps,
            
            # Розраховані показники
            'kd_ratio': round(kills / deaths, 2),
            'win_rate': round((wins / matches) * 100, 1),
            'headshot_percent': round((headshot_kills / kills) * 100, 1) if kills > 0 else 0,
            'accuracy_percent': round((shots_hit / shots_fired) * 100, 1) if shots_fired > 0 else 0,
            'assists_per_match': round(stats_dict.get('total_kills_assist', 0) / matches, 1),
            'mvp_percent': round((mvps / matches) * 100, 1) if matches > 0 else 0,
            'damage_per_match': round(stats_dict.get('total_damage_done', 0) / matches, 0) if matches > 0 else 0,
            
            # Додаткові статистики
            'rounds_played': stats_dict.get('total_rounds_played', 0),
            'time_played': stats_dict.get('total_time_played', 0),
            'knife_kills': stats_dict.get('total_kills_knife', 0),
            'planted_bombs': stats_dict.get('total_planted_bombs', 0),
            'defused_bombs': stats_dict.get('total_defused_bombs', 0),
            
            # Статистика по зброї (топ-3)
            'weapon_stats': self._extract_weapon_stats(stats_dict)
        }
        
        return parsed

    def _extract_weapon_stats(self, stats_dict: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Витягти статистику по зброї"""
        weapons = {}
        
        # Популярна зброя в CS2
        weapon_names = [
            'ak47', 'm4a1', 'awp', 'glock', 'usp_silencer', 
            'famas', 'galil', 'mp9', 'mac10', 'p90'
        ]
        
        for weapon in weapon_names:
            kills_key = f'total_kills_{weapon}'
            shots_key = f'total_shots_{weapon}'
            hits_key = f'total_hits_{weapon}'
            
            if kills_key in stats_dict and stats_dict[kills_key] > 0:
                weapons[weapon] = {
                    'name': weapon.upper(),
                    'kills': stats_dict[kills_key],
                    'shots': stats_dict.get(shots_key, 0),
                    'hits': stats_dict.get(hits_key, 0),
                    'accuracy': round((stats_dict.get(hits_key, 0) / stats_dict.get(shots_key, 1)) * 100, 1)
                }
        
        # Сортуємо за кількістю вбивств і повертаємо топ-3
        sorted_weapons = sorted(weapons.values(), key=lambda x: x['kills'], reverse=True)
        return sorted_weapons[:3]

    def calculate_impact_score(self, stats: Dict[str, Any], weights: Dict[str, float] = None) -> float:
        """Розрахунок Impact Score на основі статистики"""
        if not weights:
            weights = {
                "kd_ratio": 0.25,
                "win_rate": 0.30,
                "headshot_percent": 0.20,
                "assists_per_match": 0.15,
                "mvp_percent": 0.10
            }
        
        # Нормалізація значень для розрахунку
        kd_score = min(stats.get('kd_ratio', 0) / 2.0, 1.0)  # макс 2.0 K/D = 1.0 score
        win_rate_score = stats.get('win_rate', 0) / 100.0  # відсоток в десяткові
        hs_score = min(stats.get('headshot_percent', 0) / 70.0, 1.0)  # макс 70% HS = 1.0 score
        assists_score = min(stats.get('assists_per_match', 0) / 5.0, 1.0)  # макс 5 асистів = 1.0 score
        mvp_score = min(stats.get('mvp_percent', 0) / 30.0, 1.0)  # макс 30% MVP = 1.0 score
        
        impact_score = (
            kd_score * weights["kd_ratio"] +
            win_rate_score * weights["win_rate"] +
            hs_score * weights["headshot_percent"] +
            assists_score * weights["assists_per_match"] +
            mvp_score * weights["mvp_percent"]
        )
        
        return round(impact_score * 100, 1)  # повертаємо в відсотках (0-100)

    async def get_player_rank_info(self, steam_id: str) -> Optional[Dict[str, Any]]:
        """Спроба отримати інформацію про ранг гравця (може не працювати через обмеження API)"""
        # На жаль, Steam API не надає прямий доступ до рангу CS2
        # Це можна реалізувати через парсинг профілю або інші методи
        return {
            'rank': 'Недоступно',
            'rank_image': None,
            'competitive_wins': 0
        }

    async def validate_steam_id(self, steam_id: str) -> bool:
        """Перевірити, чи валідний Steam ID"""
        try:
            # Steam ID має бути 17-значним числом
            if len(steam_id) != 17 or not steam_id.isdigit():
                return False
                
            # Перевіряємо через API
            players = await self.get_player_summaries([steam_id])
            return len(players) > 0
        except:
            return False

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
            time_period: Період статистики ("all", "week", "month", "last_match")
        """
        url = f"{self.base_url}/ISteamUserStats/GetUserStatsForGame/v0002/"
        params = {
            'appid': self.cs2_app_id,
            'key': self.api_key,
            'steamid': steam_id
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        stats = data['playerstats']
                        
                        # Якщо потрібна фільтрація по часу, застосовуємо її
                        if time_period != "all":
                            stats = self._filter_stats_by_time(stats, time_period)
                        
                        # Додаємо інформацію про період
                        stats['time_period'] = time_period
                        return stats
            return None
        except Exception as e:
            print(f"Помилка отримання статистики гравця {steam_id}: {e}")
            return None

    def _filter_stats_by_time(self, stats: Dict[str, Any], time_period: str) -> Dict[str, Any]:
        """
        Фільтрує статистику по часу
        
        Args:
            stats: Сира статистика з Steam API
            time_period: Період фільтрації
        """
        if time_period == "last_match":
            return self._extract_last_match_stats_only(stats)
        elif time_period == "week":
            return self._extract_recent_stats(stats, days=7)
        elif time_period == "month":
            return self._extract_recent_stats(stats, days=30)
        else:
            return stats

    def _extract_last_match_stats_only(self, stats: Dict[str, Any]) -> Dict[str, Any]:
        """Витягує тільки статистику останнього матчу"""
        filtered_stats = {'stats': [], 'achievements': stats.get('achievements', [])}
        
        # Витягуємо тільки статистики останнього матчу
        last_match_stats = [
            'last_match_kills', 'last_match_deaths', 'last_match_mvps',
            'last_match_damage', 'last_match_money_spent', 'last_match_rounds',
            'last_match_contribution_score', 'last_match_t_wins', 'last_match_ct_wins',
            'last_match_wins', 'last_match_favweapon_id', 'last_match_favweapon_shots',
            'last_match_favweapon_hits', 'last_match_favweapon_kills'
        ]
        
        for stat in stats.get('stats', []):
            if stat['name'] in last_match_stats:
                filtered_stats['stats'].append(stat)
        
        return filtered_stats

    def _extract_recent_stats(self, stats: Dict[str, Any], days: int) -> Dict[str, Any]:
        """
        Витягує статистику за останні N днів
        Примітка: Steam API не надає точну фільтрацію по часу,
        тому ми використовуємо приблизні методи
        """
        # Для тижневої/місячної статистики можемо використовувати
        # статистики, які оновлюються частіше (наприклад, останній матч)
        # або показувати загальну статистику з індикатором періоду
        
        filtered_stats = {
            'stats': stats.get('stats', []),
            'achievements': stats.get('achievements', []),
            'filter_note': f"Показує загальну статистику (фільтр {days} днів не підтримується Steam API)"
        }
        
        return filtered_stats

    async def get_recent_activity(self, steam_id: str, days: int = 7) -> Optional[Dict[str, Any]]:
        """
        Отримати нещодавню активність гравця
        
        Args:
            steam_id: Steam ID гравця
            days: Кількість днів для аналізу
        """
        try:
            # Отримуємо загальну статистику
            all_stats = await self.get_player_stats(steam_id, "all")
            if not all_stats:
                return None
            
            # Витягуємо статистику останнього матчу як індикатор нещодавньої активності
            last_match_stats = self._extract_last_match_stats_only(all_stats)
            
            # Отримуємо інформацію про гравця
            players = await self.get_player_summaries([steam_id])
            if not players:
                return None
            
            player = players[0]
            last_logoff = player.get('lastlogoff', 0)
            
            # Розраховуємо час останньої активності
            from datetime import datetime
            last_online = datetime.fromtimestamp(last_logoff)
            now = datetime.now()
            days_since_online = (now - last_online).days
            
            return {
                'player_name': player.get('personaname', 'Невідомо'),
                'last_online': last_online.strftime('%Y-%m-%d %H:%M:%S'),
                'days_since_online': days_since_online,
                'last_match_stats': last_match_stats,
                'is_recently_active': days_since_online <= days
            }
            
        except Exception as e:
            print(f"Помилка отримання нещодавньої активності: {e}")
            return None

    def parse_cs2_stats(self, raw_stats: Dict[str, Any]) -> Dict[str, Any]:
        """Парсинг сирих статистик CS2 у зручний формат"""
        if not raw_stats or 'stats' not in raw_stats:
            return {}
            
        stats_dict = {}
        for stat in raw_stats['stats']:
            stats_dict[stat['name']] = stat['value']
        
        # Додаємо всі доступні статистики для дебагу
        self.all_available_stats = stats_dict
        
        # Розрахунок основних показників
        kills = stats_dict.get('total_kills', 0)
        deaths = stats_dict.get('total_deaths', 0)
        headshot_kills = stats_dict.get('total_kills_headshot', 0)
        shots_fired = stats_dict.get('total_shots_fired', 0)
        shots_hit = stats_dict.get('total_shots_hit', 0)
        wins = stats_dict.get('total_wins', 0)
        matches = stats_dict.get('total_matches_played', 0)
        mvps = stats_dict.get('total_mvps', 0)
        
        # Захист від ділення на нуль
        if deaths == 0:
            deaths = 1
        if matches == 0:
            matches = 1
        if shots_fired == 0:
            shots_fired = 1
        if kills == 0:
            kills = 1
        
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
            
            # Розраховані показники з обмеженнями
            'kd_ratio': round(kills / deaths, 2),
            'win_rate': min(round((wins / matches) * 100, 1), 100.0),  # максимум 100%
            'headshot_percent': min(round((headshot_kills / kills) * 100, 1), 100.0),  # максимум 100%
            'accuracy_percent': min(round((shots_hit / shots_fired) * 100, 1), 100.0),  # максимум 100%
            'assists_per_match': round(stats_dict.get('total_kills_assist', 0) / matches, 1),
            'mvp_percent': min(round((mvps / matches) * 100, 1), 100.0),  # максимум 100%
            'damage_per_match': round(stats_dict.get('total_damage_done', 0) / matches, 0) if matches > 0 else 0,
            
            # Додаткові статистики
            'rounds_played': stats_dict.get('total_rounds_played', 0),
            'time_played': stats_dict.get('total_time_played', 0),
            'knife_kills': stats_dict.get('total_kills_knife', 0),
            'planted_bombs': stats_dict.get('total_planted_bombs', 0),
            'defused_bombs': stats_dict.get('total_defused_bombs', 0),
            
            # НОВІ ДЕТАЛЬНІ СТАТИСТИКИ
            'dominations': stats_dict.get('total_dominations', 0),
            'revenges': stats_dict.get('total_revenges', 0),
            'enemy_weapon_kills': stats_dict.get('total_kills_enemy_weapon', 0),
            'blinded_kills': stats_dict.get('total_kills_enemy_blinded', 0),
            'knife_fight_kills': stats_dict.get('total_kills_knife_fight', 0),
            'zoomed_sniper_kills': stats_dict.get('total_kills_against_zoomed_sniper', 0),
            'weapons_donated': stats_dict.get('total_weapons_donated', 0),
            'contribution_score': stats_dict.get('total_contribution_score', 0),
            
            # Статистика по картах
            'map_stats': self._extract_map_stats(stats_dict),
            
            # Статистика по зброї (розширена)
            'weapon_stats': self._extract_weapon_stats(stats_dict),
            
            # Статистика по режимах гри
            'game_mode_stats': self._extract_game_mode_stats(stats_dict),
            
            # Останній матч
            'last_match': self._extract_last_match_stats(stats_dict)
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
        
        # Обмежуємо до 100 балів
        final_score = min(round(impact_score * 100, 1), 100.0)
        return final_score

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

    def _extract_map_stats(self, stats_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Витягти статистику по картах"""
        maps = {}
        
        # Популярні карти CS2
        map_names = [
            'de_dust2', 'de_inferno', 'de_nuke', 'de_train', 'de_mirage',
            'de_overpass', 'de_vertigo', 'de_cache', 'de_cbble', 'de_office'
        ]
        
        for map_name in map_names:
            wins_key = f'total_wins_map_{map_name}'
            rounds_key = f'total_rounds_map_{map_name}'
            
            wins = stats_dict.get(wins_key, 0)
            rounds = stats_dict.get(rounds_key, 0)
            
            if rounds > 0:
                win_rate = round((wins / rounds) * 100, 1) if rounds > 0 else 0
                maps[map_name] = {
                    'name': map_name,
                    'wins': wins,
                    'rounds': rounds,
                    'win_rate': win_rate
                }
        
        # Сортуємо за кількістю раундів
        sorted_maps = sorted(maps.values(), key=lambda x: x['rounds'], reverse=True)
        return sorted_maps[:5]  # Топ-5 карт

    def _extract_game_mode_stats(self, stats_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Витягти статистику по режимах гри"""
        modes = {}
        
        # Gun Game
        gg_wins = stats_dict.get('total_gun_game_rounds_won', 0)
        gg_rounds = stats_dict.get('total_gun_game_rounds_played', 0)
        gg_matches_won = stats_dict.get('total_gg_matches_won', 0)
        gg_matches_played = stats_dict.get('total_gg_matches_played', 0)
        
        if gg_rounds > 0:
            modes['gun_game'] = {
                'name': 'Gun Game',
                'rounds_won': gg_wins,
                'rounds_played': gg_rounds,
                'round_win_rate': round((gg_wins / gg_rounds) * 100, 1),
                'matches_won': gg_matches_won,
                'matches_played': gg_matches_played,
                'match_win_rate': round((gg_matches_won / gg_matches_played) * 100, 1) if gg_matches_played > 0 else 0
            }
        
        # Progressive
        prog_matches_won = stats_dict.get('total_progressive_matches_won', 0)
        if prog_matches_won > 0:
            modes['progressive'] = {
                'name': 'Progressive',
                'matches_won': prog_matches_won
            }
        
        # TR Bomb
        tr_matches_won = stats_dict.get('total_trbomb_matches_won', 0)
        if tr_matches_won > 0:
            modes['tr_bomb'] = {
                'name': 'TR Bomb',
                'matches_won': tr_matches_won
            }
        
        return modes

    def _extract_last_match_stats(self, stats_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Витягти статистику останнього матчу"""
        last_match = {}
        
        # Основні показники останнього матчу
        last_match['kills'] = stats_dict.get('last_match_kills', 0)
        last_match['deaths'] = stats_dict.get('last_match_deaths', 0)
        last_match['mvps'] = stats_dict.get('last_match_mvps', 0)
        last_match['damage'] = stats_dict.get('last_match_damage', 0)
        last_match['money_spent'] = stats_dict.get('last_match_money_spent', 0)
        last_match['rounds'] = stats_dict.get('last_match_rounds', 0)
        last_match['contribution_score'] = stats_dict.get('last_match_contribution_score', 0)
        
        # Результат матчу
        t_wins = stats_dict.get('last_match_t_wins', 0)
        ct_wins = stats_dict.get('last_match_ct_wins', 0)
        total_wins = stats_dict.get('last_match_wins', 0)
        
        if t_wins > 0 or ct_wins > 0:
            last_match['t_wins'] = t_wins
            last_match['ct_wins'] = ct_wins
            last_match['total_wins'] = total_wins
            last_match['result'] = 'Перемога' if total_wins > 0 else 'Поразка'
        
        # Улюблена зброя останнього матчу
        fav_weapon_id = stats_dict.get('last_match_favweapon_id', 0)
        fav_weapon_shots = stats_dict.get('last_match_favweapon_shots', 0)
        fav_weapon_hits = stats_dict.get('last_match_favweapon_hits', 0)
        fav_weapon_kills = stats_dict.get('last_match_favweapon_kills', 0)
        
        if fav_weapon_id > 0:
            last_match['favorite_weapon'] = {
                'id': fav_weapon_id,
                'shots': fav_weapon_shots,
                'hits': fav_weapon_hits,
                'kills': fav_weapon_kills,
                'accuracy': round((fav_weapon_hits / fav_weapon_shots) * 100, 1) if fav_weapon_shots > 0 else 0
            }
        
        return last_match

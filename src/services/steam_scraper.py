"""
Простий сервіс для парсингу Steam профілів
"""
import aiohttp
import re
from typing import Optional, Dict, Any


class SteamScraper:
    def __init__(self):
        self.base_url = "https://steamcommunity.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

    async def get_profile_stats(self, steam_id: str) -> Optional[Dict[str, Any]]:
        """Отримати статистику з профілю Steam"""
        try:
            url = f"{self.base_url}/profiles/{steam_id}/stats/CS2"
            
            async with aiohttp.ClientSession(headers=self.headers) as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        html = await response.text()
                        return self._parse_profile_html(html)
                    else:
                        print(f"Помилка отримання профілю: {response.status}")
                        return None
        except Exception as e:
            print(f"Помилка парсингу профілю: {e}")
            return None

    def _parse_profile_html(self, html: str) -> Dict[str, Any]:
        """Простий парсинг HTML профілю Steam"""
        stats = {}
        
        try:
            # Шукаємо основні статистики через регулярні вирази
            stats.update(self._extract_basic_stats(html))
            stats.update(self._extract_weapon_stats(html))
            
        except Exception as e:
            print(f"Помилка парсингу HTML: {e}")
        
        return stats

    def _extract_basic_stats(self, html: str) -> Dict[str, Any]:
        """Витягти основні статистики"""
        stats = {}
        
        # Прості регулярні вирази для пошуку статистик
        patterns = {
            'kills': r'Kills["\s]*:["\s]*([0-9,]+)',
            'deaths': r'Deaths["\s]*:["\s]*([0-9,]+)',
            'wins': r'Wins["\s]*:["\s]*([0-9,]+)',
            'matches': r'Matches["\s]*:["\s]*([0-9,]+)',
            'mvps': r'MVPs["\s]*:["\s]*([0-9,]+)',
            'headshots': r'Headshots["\s]*:["\s]*([0-9,]+)',
            'damage': r'Damage["\s]*:["\s]*([0-9,]+)',
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, html, re.IGNORECASE)
            if match:
                value = match.group(1).replace(',', '')
                stats[key] = int(value) if value.isdigit() else 0
        
        return stats

    def _extract_weapon_stats(self, html: str) -> Dict[str, Any]:
        """Витягти статистику по зброї"""
        weapon_stats = {}
        
        # Шукаємо статистику популярної зброї
        weapons = ['ak47', 'm4a1', 'awp', 'glock', 'usp']
        
        for weapon in weapons:
            pattern = f'{weapon}["\s]*:["\s]*([0-9,]+)'
            match = re.search(pattern, html, re.IGNORECASE)
            if match:
                value = match.group(1).replace(',', '')
                weapon_stats[f'{weapon}_kills'] = int(value) if value.isdigit() else 0
        
        return weapon_stats

    async def get_recent_activity(self, steam_id: str) -> Optional[Dict[str, Any]]:
        """Отримати останню активність"""
        try:
            url = f"{self.base_url}/profiles/{steam_id}"
            
            async with aiohttp.ClientSession(headers=self.headers) as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        html = await response.text()
                        return self._parse_activity_html(html)
                    return None
        except Exception as e:
            print(f"Помилка отримання активності: {e}")
            return None

    def _parse_activity_html(self, html: str) -> Dict[str, Any]:
        """Парсинг активності"""
        activity = {}
        
        # Шукаємо останню активність
        last_online_match = re.search(r'Last Online["\s]*:["\s]*([^"]+)', html)
        if last_online_match:
            activity['last_online'] = last_online_match.group(1).strip()
        
        return activity

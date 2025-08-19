"""
Steam OAuth авторизація
"""
import aiohttp
import hashlib
import hmac
import time
from typing import Optional, Dict, Any
from urllib.parse import urlencode


class SteamOAuth:
    def __init__(self, api_key: str, app_domain: str):
        self.api_key = api_key
        self.app_domain = app_domain
        self.steam_login_url = "https://steamcommunity.com/openid/login"
        self.steam_api_url = "https://api.steampowered.com"
        
    def generate_login_url(self, return_url: str) -> str:
        """Генерує URL для Steam OAuth"""
        params = {
            'openid.ns': 'http://specs.openid.net/auth/2.0',
            'openid.mode': 'checkid_setup',
            'openid.return_to': return_url,
            'openid.realm': f'https://{self.app_domain}',
            'openid.identity': 'http://specs.openid.net/auth/2.0/identifier_select',
            'openid.claimed_id': 'http://specs.openid.net/auth/2.0/identifier_select'
        }
        
        return f"{self.steam_login_url}?{urlencode(params)}"
    
    async def verify_steam_response(self, query_params: Dict[str, str]) -> Optional[str]:
        """Перевіряє відповідь від Steam і повертає Steam ID"""
        try:
            # Додаємо необхідні параметри
            params = {
                'openid.ns': 'http://specs.openid.net/auth/2.0',
                'openid.mode': 'check_authentication',
                'openid.sig': query_params.get('openid.sig', ''),
                'openid.signed': query_params.get('openid.signed', ''),
            }
            
            # Додаємо всі підписані параметри
            signed_params = query_params.get('openid.signed', '').split(',')
            for param in signed_params:
                param_name = f'openid.{param}'
                if param_name in query_params:
                    params[param_name] = query_params[param_name]
            
            # Відправляємо запит на перевірку
            async with aiohttp.ClientSession() as session:
                async with session.post(self.steam_login_url, data=params) as response:
                    if response.status == 200:
                        text = await response.text()
                        if 'is_valid:true' in text:
                            # Витягуємо Steam ID
                            steam_id = query_params.get('openid.claimed_id', '')
                            if steam_id:
                                # Steam ID в форматі: https://steamcommunity.com/openid/id/76561198123456789
                                steam_id = steam_id.split('/')[-1]
                                return steam_id
            return None
        except Exception as e:
            print(f"Помилка перевірки Steam відповіді: {e}")
            return None
    
    async def get_user_info(self, steam_id: str) -> Optional[Dict[str, Any]]:
        """Отримати інформацію про користувача"""
        try:
            url = f"{self.steam_api_url}/ISteamUser/GetPlayerSummaries/v0002/"
            params = {
                'key': self.api_key,
                'steamids': steam_id
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        players = data.get('response', {}).get('players', [])
                        if players:
                            return players[0]
            return None
        except Exception as e:
            print(f"Помилка отримання інформації користувача: {e}")
            return None
    
    async def get_private_stats(self, steam_id: str) -> Optional[Dict[str, Any]]:
        """Отримати приватну статистику (якщо доступна)"""
        try:
            url = f"{self.steam_api_url}/ISteamUserStats/GetUserStatsForGame/v0002/"
            params = {
                'key': self.api_key,
                'steamid': steam_id,
                'appid': 730  # CS2 app ID
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('playerstats', {})
            return None
        except Exception as e:
            print(f"Помилка отримання приватної статистики: {e}")
            return None

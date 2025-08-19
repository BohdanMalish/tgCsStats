"""
CS2 Game State Integration (GSI) сервіс
"""
import json
import asyncio
from typing import Optional, Dict, Any, Callable
from aiohttp import web
import logging

logger = logging.getLogger(__name__)


class CS2GSI:
    def __init__(self, port: int = 3000):
        self.port = port
        self.app = web.Application()
        self.app.router.add_post('/cs2', self.handle_gsi_data)
        self.latest_data = {}
        self.callbacks = []
        
    async def start_server(self):
        """Запустити GSI сервер"""
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', self.port)
        await site.start()
        logger.info(f"CS2 GSI сервер запущено на порту {self.port}")
        
    async def handle_gsi_data(self, request):
        """Обробка даних від CS2"""
        try:
            data = await request.json()
            self.latest_data = data
            
            # Викликаємо всі зареєстровані callback'и
            for callback in self.callbacks:
                try:
                    await callback(data)
                except Exception as e:
                    logger.error(f"Помилка в GSI callback: {e}")
            
            return web.Response(text="OK")
        except Exception as e:
            logger.error(f"Помилка обробки GSI даних: {e}")
            return web.Response(text="ERROR", status=500)
    
    def add_callback(self, callback: Callable):
        """Додати callback для обробки GSI даних"""
        self.callbacks.append(callback)
    
    def get_latest_data(self) -> Dict[str, Any]:
        """Отримати останні дані від CS2"""
        return self.latest_data.copy()
    
    def get_player_stats(self) -> Dict[str, Any]:
        """Отримати статистику гравця з GSI"""
        data = self.latest_data
        
        if not data or 'player' not in data:
            return {}
        
        player = data['player']
        match_stats = data.get('match_stats', {})
        
        stats = {
            'kills': match_stats.get('kills', 0),
            'deaths': match_stats.get('deaths', 0),
            'assists': match_stats.get('assists', 0),
            'mvps': match_stats.get('mvps', 0),
            'score': match_stats.get('score', 0),
            'damage': match_stats.get('damage', 0),
            'money': player.get('money', 0),
            'health': player.get('state', {}).get('health', 100),
            'armor': player.get('state', {}).get('armor', 0),
            'weapons': player.get('weapons', {}),
            'position': player.get('position', {}),
            'map': data.get('map', {}).get('name', 'Unknown'),
            'round': data.get('round', {}).get('phase', 'Unknown'),
            'match_info': {
                'mode': data.get('map', {}).get('mode', 'Unknown'),
                'round_wins': data.get('round_wins', {}),
                'round_total': data.get('round_total', 0)
            }
        }
        
        return stats
    
    def get_match_info(self) -> Dict[str, Any]:
        """Отримати інформацію про поточний матч"""
        data = self.latest_data
        
        if not data:
            return {}
        
        return {
            'map': data.get('map', {}).get('name', 'Unknown'),
            'mode': data.get('map', {}).get('mode', 'Unknown'),
            'round': data.get('round', {}).get('phase', 'Unknown'),
            'round_number': data.get('round', {}).get('current', 0),
            'round_wins': data.get('round_wins', {}),
            'round_total': data.get('round_total', 0),
            'players': data.get('players', {}),
            'timestamp': data.get('timestamp', 0)
        }
    
    def is_in_game(self) -> bool:
        """Перевірити чи гравець в грі"""
        data = self.latest_data
        return bool(data and 'player' in data and data['player'].get('steamid'))
    
    def get_weapon_stats(self) -> Dict[str, Any]:
        """Отримати статистику по зброї"""
        data = self.latest_data
        
        if not data or 'player' not in data:
            return {}
        
        weapons = data['player'].get('weapons', {})
        weapon_stats = {}
        
        for weapon_id, weapon_data in weapons.items():
            if weapon_data.get('state') == 'active':
                weapon_stats['current_weapon'] = {
                    'name': weapon_data.get('name', 'Unknown'),
                    'ammo': weapon_data.get('ammo_clip', 0),
                    'ammo_reserve': weapon_data.get('ammo_reserve', 0),
                    'type': weapon_data.get('type', 'Unknown')
                }
                break
        
        return weapon_stats

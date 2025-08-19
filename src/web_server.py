"""
Веб-сервер для обробки Steam OAuth callback
"""
from aiohttp import web
import logging
from urllib.parse import parse_qs, urlparse
from typing import Dict, Any

logger = logging.getLogger(__name__)


class WebServer:
    def __init__(self, bot_handlers, port: int = 3000):
        self.bot_handlers = bot_handlers
        self.port = port
        self.app = web.Application()
        self.app.router.add_get('/steam/callback', self.handle_steam_callback)
        self.app.router.add_get('/', self.handle_root)
        
    async def start_server(self):
        """Запустити веб-сервер"""
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', self.port)
        await site.start()
        logger.info(f"Веб-сервер запущено на порту {self.port}")
        
    async def handle_root(self, request):
        """Обробка головної сторінки"""
        return web.Response(text="CS2 Stats Bot - Steam OAuth Callback Server")
        
    async def handle_steam_callback(self, request):
        """Обробка Steam OAuth callback"""
        try:
            # Отримуємо параметри з URL
            query_string = request.query_string
            query_params = parse_qs(query_string)
            
            # Витягуємо user_id
            user_id = query_params.get('user_id', [None])[0]
            if not user_id:
                return web.Response(text="❌ Помилка: user_id не знайдено", status=400)
            
            # Конвертуємо в int
            try:
                user_id = int(user_id)
            except ValueError:
                return web.Response(text="❌ Помилка: невірний user_id", status=400)
            
            # Витягуємо Steam параметри
            steam_params = {}
            for key, value in query_params.items():
                if key.startswith('openid.'):
                    steam_params[key] = value[0] if value else ''
            
            # Перевіряємо Steam відповідь
            from .services.steam_oauth import SteamOAuth
            steam_oauth = SteamOAuth(
                api_key="YOUR_STEAM_API_KEY",  # TODO: Отримати з конфігурації
                app_domain="your-app.railway.app"  # TODO: Отримати з конфігурації
            )
            
            steam_id = await steam_oauth.verify_steam_response(steam_params)
            
            if steam_id:
                # Зберігаємо Steam ID в базі даних
                success = self.bot_handlers.user_db.update_steam_id(user_id, steam_id)
                
                if success:
                    # Отримуємо інформацію про гравця
                    user_info = await steam_oauth.get_user_info(steam_id)
                    player_name = user_info.get('personaname', 'Невідомо') if user_info else 'Невідомо'
                    
                    html_response = f"""
<!DOCTYPE html>
<html>
<head>
    <title>CS2 Stats Bot - Успішна авторизація</title>
    <meta charset="utf-8">
    <style>
        body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; }}
        .success {{ color: #28a745; font-size: 24px; margin-bottom: 20px; }}
        .info {{ color: #666; margin-bottom: 30px; }}
        .button {{ background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; }}
    </style>
</head>
<body>
    <div class="success">✅ Успішна авторизація!</div>
    <div class="info">
        <p>Steam ID: {steam_id}</p>
        <p>Гравець: {player_name}</p>
    </div>
    <p>Тепер ти можеш використовувати всі команди бота!</p>
    <a href="https://t.me/your_bot_username" class="button">Повернутися до бота</a>
</body>
</html>
"""
                    return web.Response(text=html_response, content_type='text/html')
                else:
                    return web.Response(text="❌ Помилка збереження Steam ID", status=500)
            else:
                return web.Response(text="❌ Помилка перевірки Steam авторизації", status=400)
                
        except Exception as e:
            logger.error(f"Помилка обробки Steam callback: {e}")
            return web.Response(text=f"❌ Помилка: {str(e)}", status=500)

#!/usr/bin/env python3
"""
Тестовий скрипт для перевірки конфігурації Steam OAuth
"""

def test_config():
    """Тестуємо конфігурацію"""
    print("🧪 Тестування конфігурації Steam OAuth...")
    
    # Імпортуємо основні модулі
    try:
        from src.services.steam_oauth import SteamOAuth
        print("✅ SteamOAuth імпортовано успішно")
    except Exception as e:
        print(f"❌ Помилка імпорту SteamOAuth: {e}")
        return False
    
    try:
        from src.handlers.bot_handlers import BotHandlers
        print("✅ BotHandlers імпортовано успішно")
    except Exception as e:
        print(f"❌ Помилка імпорту BotHandlers: {e}")
        return False
    
    try:
        from src.web_server import WebServer
        print("✅ WebServer імпортовано успішно")
    except Exception as e:
        print(f"❌ Помилка імпорту WebServer: {e}")
        return False
    
    # Тестуємо створення об'єктів
    try:
        # Хардкодовані значення з main.py
        STEAM_API_KEY = "6629403219DD2ADCA0D3F552F03F92A8"
        APP_DOMAIN = "tgcsstats-production.up.railway.app"
        
        # Тестуємо SteamOAuth
        steam_oauth = SteamOAuth(STEAM_API_KEY, APP_DOMAIN)
        print("✅ SteamOAuth створено успішно")
        
        # Тестуємо генерацію URL
        return_url = f"https://{APP_DOMAIN}/steam/callback?user_id=123456"
        login_url = steam_oauth.generate_login_url(return_url)
        print(f"✅ Login URL згенеровано: {login_url[:50]}...")
        
    except Exception as e:
        print(f"❌ Помилка створення SteamOAuth: {e}")
        return False
    
    print("\n🎉 Всі тести пройшли успішно!")
    print("📋 Конфігурація:")
    print(f"   STEAM_API_KEY: {STEAM_API_KEY[:10]}...")
    print(f"   APP_DOMAIN: {APP_DOMAIN}")
    print(f"   Login URL: {login_url[:50]}...")
    
    return True

if __name__ == "__main__":
    test_config()

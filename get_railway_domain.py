#!/usr/bin/env python3
"""
Скрипт для визначення Railway домену
"""

import os

def get_railway_domain():
    """Визначає Railway домен на основі змінних оточення"""
    
    # Отримуємо змінні Railway
    project_name = os.getenv("RAILWAY_PROJECT_NAME", "")
    environment_name = os.getenv("RAILWAY_ENVIRONMENT_NAME", "")
    service_name = os.getenv("RAILWAY_SERVICE_NAME", "")
    
    print(f"🔍 Railway змінні:")
    print(f"   RAILWAY_PROJECT_NAME: {project_name}")
    print(f"   RAILWAY_ENVIRONMENT_NAME: {environment_name}")
    print(f"   RAILWAY_SERVICE_NAME: {service_name}")
    
    # Формуємо домен
    if project_name and environment_name:
        domain = f"{project_name}-{environment_name}.up.railway.app"
        print(f"✅ Згенерований домен: {domain}")
        return domain
    else:
        print("❌ Не вдалося визначити Railway домен")
        return None

def main():
    """Головна функція"""
    print("🚂 Визначення Railway домену...")
    
    domain = get_railway_domain()
    
    if domain:
        print(f"\n📋 Для використання в коді:")
        print(f'APP_DOMAIN = "{domain}"')
        
        print(f"\n🔗 Callback URL:")
        print(f"https://{domain}/steam/callback")
    else:
        print("\n❌ Потрібно встановити змінну APP_DOMAIN вручну")

if __name__ == "__main__":
    main()

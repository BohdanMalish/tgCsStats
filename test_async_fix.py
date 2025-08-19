#!/usr/bin/env python3
"""
Тестовий скрипт для перевірки асинхронного запуску
"""

def test_async_imports():
    """Тестуємо імпорт асинхронних модулів"""
    print("🧪 Тестування асинхронних імпортів...")
    
    try:
        import asyncio
        print("✅ asyncio імпортовано успішно")
    except Exception as e:
        print(f"❌ Помилка імпорту asyncio: {e}")
        return False
    
    try:
        import threading
        print("✅ threading імпортовано успішно")
    except Exception as e:
        print(f"❌ Помилка імпорту threading: {e}")
        return False
    
    try:
        from aiohttp import web
        print("✅ aiohttp.web імпортовано успішно")
    except Exception as e:
        print(f"❌ Помилка імпорту aiohttp.web: {e}")
        return False
    
    return True

def test_event_loop():
    """Тестуємо створення event loop"""
    print("\n🧪 Тестування event loop...")
    
    try:
        import asyncio
        
        # Тестуємо створення нового event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        print("✅ Event loop створено успішно")
        
        # Тестуємо закриття
        loop.close()
        print("✅ Event loop закрито успішно")
        
        return True
    except Exception as e:
        print(f"❌ Помилка event loop: {e}")
        return False

def test_threading():
    """Тестуємо threading"""
    print("\n🧪 Тестування threading...")
    
    try:
        import threading
        import time
        
        def test_function():
            time.sleep(0.1)
            return "test"
        
        # Тестуємо створення потоку
        thread = threading.Thread(target=test_function, daemon=True)
        thread.start()
        thread.join(timeout=1)
        
        print("✅ Threading працює успішно")
        return True
    except Exception as e:
        print(f"❌ Помилка threading: {e}")
        return False

def main():
    """Головна функція тестування"""
    print("🔧 Тестування асинхронного запуску...")
    
    # Тестуємо імпорти
    if not test_async_imports():
        return False
    
    # Тестуємо event loop
    if not test_event_loop():
        return False
    
    # Тестуємо threading
    if not test_threading():
        return False
    
    print("\n🎉 Всі тести пройшли успішно!")
    print("✅ Асинхронний запуск готовий до роботи")
    
    return True

if __name__ == "__main__":
    main()

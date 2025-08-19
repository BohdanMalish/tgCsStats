"""
Модель користувача для бази даних
"""
import sqlite3
from typing import List, Optional, Dict, Any
from datetime import datetime


class User:
    def __init__(self, telegram_id: int, steam_id: str = None, username: str = None):
        self.telegram_id = telegram_id
        self.steam_id = steam_id
        self.username = username
        self.created_at = datetime.now()
        self.friends: List[str] = []  # список Steam ID друзів

    def to_dict(self) -> Dict[str, Any]:
        return {
            'telegram_id': self.telegram_id,
            'steam_id': self.steam_id,
            'username': self.username,
            'created_at': self.created_at.isoformat(),
            'friends': ','.join(self.friends) if self.friends else ''
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        user = cls(
            telegram_id=data['telegram_id'],
            steam_id=data.get('steam_id'),
            username=data.get('username')
        )
        if data.get('created_at'):
            user.created_at = datetime.fromisoformat(data['created_at'])
        if data.get('friends'):
            user.friends = data['friends'].split(',') if data['friends'] else []
        return user


class UserDatabase:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Ініціалізація бази даних"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    telegram_id INTEGER PRIMARY KEY,
                    steam_id TEXT,
                    username TEXT,
                    created_at TEXT,
                    friends TEXT
                )
            ''')
            
            # Таблиця для кешування статистики
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_stats_cache (
                    steam_id TEXT PRIMARY KEY,
                    stats_data TEXT,
                    updated_at TEXT
                )
            ''')
            
            conn.commit()

    def create_user(self, user: User) -> bool:
        """Створити нового користувача"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                data = user.to_dict()
                cursor.execute('''
                    INSERT OR REPLACE INTO users 
                    (telegram_id, steam_id, username, created_at, friends)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    data['telegram_id'],
                    data['steam_id'],
                    data['username'],
                    data['created_at'],
                    data['friends']
                ))
                conn.commit()
                return True
        except Exception as e:
            print(f"Помилка створення користувача: {e}")
            return False

    def get_user(self, telegram_id: int) -> Optional[User]:
        """Отримати користувача за Telegram ID"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT telegram_id, steam_id, username, created_at, friends
                    FROM users WHERE telegram_id = ?
                ''', (telegram_id,))
                
                row = cursor.fetchone()
                if row:
                    data = {
                        'telegram_id': row[0],
                        'steam_id': row[1],
                        'username': row[2],
                        'created_at': row[3],
                        'friends': row[4]
                    }
                    return User.from_dict(data)
                return None
        except Exception as e:
            print(f"Помилка отримання користувача: {e}")
            return None

    def update_steam_id(self, telegram_id: int, steam_id: str) -> bool:
        """Оновити Steam ID користувача"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE users SET steam_id = ? WHERE telegram_id = ?
                ''', (steam_id, telegram_id))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Помилка оновлення Steam ID: {e}")
            return False

    def add_friend(self, telegram_id: int, friend_steam_id: str) -> bool:
        """Додати друга до списку користувача"""
        user = self.get_user(telegram_id)
        if not user:
            return False
            
        if friend_steam_id not in user.friends:
            user.friends.append(friend_steam_id)
            return self.create_user(user)
        return True

    def remove_friend(self, telegram_id: int, friend_steam_id: str) -> bool:
        """Видалити друга зі списку користувача"""
        user = self.get_user(telegram_id)
        if not user:
            return False
            
        if friend_steam_id in user.friends:
            user.friends.remove(friend_steam_id)
            return self.create_user(user)
        return True

    def get_all_users_with_steam(self) -> List[User]:
        """Отримати всіх користувачів, які мають Steam ID"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT telegram_id, steam_id, username, created_at, friends
                    FROM users WHERE steam_id IS NOT NULL AND steam_id != ''
                ''')
                
                users = []
                for row in cursor.fetchall():
                    data = {
                        'telegram_id': row[0],
                        'steam_id': row[1],
                        'username': row[2],
                        'created_at': row[3],
                        'friends': row[4]
                    }
                    users.append(User.from_dict(data))
                return users
        except Exception as e:
            print(f"Помилка отримання користувачів: {e}")
            return []

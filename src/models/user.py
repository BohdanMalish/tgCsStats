"""
Модель користувача для бази даних
"""
import sqlite3
import json
from datetime import datetime
from typing import Optional, Dict, Any, List


class User:
    def __init__(self, telegram_id: int, steam_id: str = None, username: str = None, monitoring_enabled: bool = False):
        self.telegram_id = telegram_id
        self.steam_id = steam_id
        self.username = username
        self.monitoring_enabled = monitoring_enabled
        self.created_at = datetime.now()
        self.friends = []
    
    def to_dict(self):
        return {
            'telegram_id': self.telegram_id,
            'steam_id': self.steam_id,
            'username': self.username,
            'monitoring_enabled': self.monitoring_enabled,
            'created_at': self.created_at.isoformat(),
            'friends': self.friends
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        user = cls(
            telegram_id=data['telegram_id'],
            steam_id=data.get('steam_id'),
            username=data.get('username'),
            monitoring_enabled=data.get('monitoring_enabled', False)
        )
        user.created_at = datetime.fromisoformat(data['created_at'])
        user.friends = data.get('friends', [])
        return user


class MatchAnalysis:
    """Модель для збереження аналізу матчу з демо"""
    def __init__(self, steam_id: str, match_id: str, match_date: datetime, demo_path: str = None):
        self.steam_id = steam_id
        self.match_id = match_id
        self.match_date = match_date
        self.demo_path = demo_path
        self.analyzed = False
        self.analysis_data = {}
        self.created_at = datetime.now()
    
    def to_dict(self):
        return {
            'steam_id': self.steam_id,
            'match_id': self.match_id,
            'match_date': self.match_date.isoformat(),
            'demo_path': self.demo_path,
            'analyzed': self.analyzed,
            'analysis_data': json.dumps(self.analysis_data),
            'created_at': self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        match = cls(
            steam_id=data['steam_id'],
            match_id=data['match_id'],
            match_date=datetime.fromisoformat(data['match_date']),
            demo_path=data.get('demo_path')
        )
        match.analyzed = data.get('analyzed', False)
        match.analysis_data = json.loads(data.get('analysis_data', '{}'))
        match.created_at = datetime.fromisoformat(data['created_at'])
        return match


class UserDatabase:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Ініціалізація бази даних"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Таблиця користувачів
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    telegram_id INTEGER PRIMARY KEY,
                    steam_id TEXT,
                    username TEXT,
                    monitoring_enabled BOOLEAN DEFAULT FALSE,
                    created_at TEXT,
                    friends TEXT
                )
            ''')
            
            # Додаємо колонку monitoring_enabled якщо її немає
            try:
                cursor.execute('ALTER TABLE users ADD COLUMN monitoring_enabled BOOLEAN DEFAULT FALSE')
            except sqlite3.OperationalError:
                # Колонка вже існує
                pass
            
            # Таблиця аналізу матчів
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS match_analysis (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    steam_id TEXT NOT NULL,
                    match_id TEXT NOT NULL,
                    match_date TEXT NOT NULL,
                    demo_path TEXT,
                    analyzed BOOLEAN DEFAULT FALSE,
                    analysis_data TEXT,
                    created_at TEXT,
                    UNIQUE(steam_id, match_id)
                )
            ''')
            
            # Таблиця детальної статистики
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS detailed_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    steam_id TEXT NOT NULL,
                    match_id TEXT,
                    stat_type TEXT NOT NULL,
                    stat_name TEXT NOT NULL,
                    stat_value REAL,
                    stat_data TEXT,
                    created_at TEXT,
                    UNIQUE(steam_id, match_id, stat_type, stat_name)
                )
            ''')
            
            conn.commit()
    
    def create_user(self, user: User) -> bool:
        """Створити нового користувача"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO users (telegram_id, steam_id, username, monitoring_enabled, created_at, friends)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    user.telegram_id,
                    user.steam_id,
                    user.username,
                    user.monitoring_enabled,
                    user.created_at.isoformat(),
                    json.dumps(user.friends)
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
                    SELECT telegram_id, steam_id, username, monitoring_enabled, created_at, friends
                    FROM users WHERE telegram_id = ?
                ''', (telegram_id,))
                
                row = cursor.fetchone()
                if row:
                    user = User(
                        telegram_id=row[0],
                        steam_id=row[1],
                        username=row[2],
                        monitoring_enabled=bool(row[3])
                    )
                    user.created_at = datetime.fromisoformat(row[4])
                    user.friends = json.loads(row[5]) if row[5] else []
                    return user
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
    
    def update_user(self, user: User) -> bool:
        """Оновити користувача"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE users SET steam_id = ?, username = ?, monitoring_enabled = ?, friends = ?
                    WHERE telegram_id = ?
                ''', (
                    user.steam_id,
                    user.username,
                    user.monitoring_enabled,
                    json.dumps(user.friends),
                    user.telegram_id
                ))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Помилка оновлення користувача: {e}")
            return False
    
    def add_friend(self, telegram_id: int, friend_steam_id: str) -> bool:
        """Додати друга"""
        try:
            user = self.get_user(telegram_id)
            if not user:
                return False
            
            if friend_steam_id not in user.friends:
                user.friends.append(friend_steam_id)
                
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute('''
                        UPDATE users SET friends = ? WHERE telegram_id = ?
                    ''', (json.dumps(user.friends), telegram_id))
                    conn.commit()
                    return True
            return True
        except Exception as e:
            print(f"Помилка додавання друга: {e}")
            return False
    
    def remove_friend(self, telegram_id: int, friend_steam_id: str) -> bool:
        """Видалити друга"""
        try:
            user = self.get_user(telegram_id)
            if not user:
                return False
            
            if friend_steam_id in user.friends:
                user.friends.remove(friend_steam_id)
                
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute('''
                        UPDATE users SET friends = ? WHERE telegram_id = ?
                    ''', (json.dumps(user.friends), telegram_id))
                    conn.commit()
                    return True
            return True
        except Exception as e:
            print(f"Помилка видалення друга: {e}")
            return False
    
    def get_friends(self, telegram_id: int) -> List[str]:
        """Отримати список друзів"""
        user = self.get_user(telegram_id)
        return user.friends if user else []
    
    def get_all_users(self) -> List[User]:
        """Отримати всіх користувачів"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT telegram_id, steam_id, username, monitoring_enabled, created_at, friends
                    FROM users
                ''')
                
                users = []
                for row in cursor.fetchall():
                    user = User(
                        telegram_id=row[0],
                        steam_id=row[1],
                        username=row[2],
                        monitoring_enabled=bool(row[3])
                    )
                    user.created_at = datetime.fromisoformat(row[4])
                    user.friends = json.loads(row[5]) if row[5] else []
                    users.append(user)
                
                return users
        except Exception as e:
            print(f"Помилка отримання всіх користувачів: {e}")
            return []
    
    def get_users_with_monitoring(self) -> List[User]:
        """Отримати користувачів з увімкненим моніторингом"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT telegram_id, steam_id, username, monitoring_enabled, created_at, friends
                    FROM users WHERE monitoring_enabled = TRUE AND steam_id IS NOT NULL
                ''')
                
                users = []
                for row in cursor.fetchall():
                    user = User(
                        telegram_id=row[0],
                        steam_id=row[1],
                        username=row[2],
                        monitoring_enabled=bool(row[3])
                    )
                    user.created_at = datetime.fromisoformat(row[4])
                    user.friends = json.loads(row[5]) if row[5] else []
                    users.append(user)
                
                return users
        except Exception as e:
            print(f"Помилка отримання користувачів з моніторингом: {e}")
            return []
    
    # Методи для роботи з аналізом матчів
    def save_match_analysis(self, match: MatchAnalysis) -> bool:
        """Зберегти аналіз матчу"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO match_analysis 
                    (steam_id, match_id, match_date, demo_path, analyzed, analysis_data, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    match.steam_id,
                    match.match_id,
                    match.match_date.isoformat(),
                    match.demo_path,
                    match.analyzed,
                    json.dumps(match.analysis_data),
                    match.created_at.isoformat()
                ))
                conn.commit()
                return True
        except Exception as e:
            print(f"Помилка збереження аналізу матчу: {e}")
            return False
    
    def get_match_analysis(self, steam_id: str, match_id: str) -> Optional[MatchAnalysis]:
        """Отримати аналіз матчу"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT steam_id, match_id, match_date, demo_path, analyzed, analysis_data, created_at
                    FROM match_analysis WHERE steam_id = ? AND match_id = ?
                ''', (steam_id, match_id))
                
                row = cursor.fetchone()
                if row:
                    return MatchAnalysis(
                        steam_id=row[0],
                        match_id=row[1],
                        match_date=datetime.fromisoformat(row[2]),
                        demo_path=row[3]
                    )
                return None
        except Exception as e:
            print(f"Помилка отримання аналізу матчу: {e}")
            return None
    
    def get_recent_matches(self, steam_id: str, limit: int = 20) -> List[MatchAnalysis]:
        """Отримати останні матчі"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT steam_id, match_id, match_date, demo_path, analyzed, analysis_data, created_at
                    FROM match_analysis 
                    WHERE steam_id = ? 
                    ORDER BY match_date DESC 
                    LIMIT ?
                ''', (steam_id, limit))
                
                matches = []
                for row in cursor.fetchall():
                    match = MatchAnalysis(
                        steam_id=row[0],
                        match_id=row[1],
                        match_date=datetime.fromisoformat(row[2]),
                        demo_path=row[3]
                    )
                    match.analyzed = row[4]
                    match.analysis_data = json.loads(row[5])
                    match.created_at = datetime.fromisoformat(row[6])
                    matches.append(match)
                
                return matches
        except Exception as e:
            print(f"Помилка отримання останніх матчів: {e}")
            return []
    
    def save_detailed_stat(self, steam_id: str, stat_type: str, stat_name: str, stat_value: float, 
                          match_id: str = None, stat_data: Dict = None) -> bool:
        """Зберегти детальну статистику"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO detailed_stats 
                    (steam_id, match_id, stat_type, stat_name, stat_value, stat_data, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    steam_id,
                    match_id,
                    stat_type,
                    stat_name,
                    stat_value,
                    json.dumps(stat_data) if stat_data else None,
                    datetime.now().isoformat()
                ))
                conn.commit()
                return True
        except Exception as e:
            print(f"Помилка збереження детальної статистики: {e}")
            return False
    
    def get_detailed_stats(self, steam_id: str, stat_type: str = None, match_id: str = None) -> List[Dict]:
        """Отримати детальну статистику"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                query = '''
                    SELECT steam_id, match_id, stat_type, stat_name, stat_value, stat_data, created_at
                    FROM detailed_stats WHERE steam_id = ?
                '''
                params = [steam_id]
                
                if stat_type:
                    query += ' AND stat_type = ?'
                    params.append(stat_type)
                
                if match_id:
                    query += ' AND match_id = ?'
                    params.append(match_id)
                
                query += ' ORDER BY created_at DESC'
                
                cursor.execute(query, params)
                
                stats = []
                for row in cursor.fetchall():
                    stat = {
                        'steam_id': row[0],
                        'match_id': row[1],
                        'stat_type': row[2],
                        'stat_name': row[3],
                        'stat_value': row[4],
                        'stat_data': json.loads(row[5]) if row[5] else None,
                        'created_at': datetime.fromisoformat(row[6])
                    }
                    stats.append(stat)
                
                return stats
        except Exception as e:
            print(f"Помилка отримання детальної статистики: {e}")
            return []

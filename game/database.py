import sqlite3
import json
from typing import Optional, List, Dict


class Database:
    def __init__(self, db_name="game_data.db"):
        self.conn = sqlite3.connect(db_name)
        self.create_tables()
    
    def create_tables(self):
        cursor = self.conn.cursor()
        
        # Таблица пользователей с расширенными полями
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                -- Статистика игры
                high_score INTEGER DEFAULT 0,
                total_kills INTEGER DEFAULT 0,
                total_play_time INTEGER DEFAULT 0,
                games_played INTEGER DEFAULT 0,
                
                -- Настройки игрока
                current_skin TEXT DEFAULT 'Солдат',
                skin_level INTEGER DEFAULT 1,
                skin_upgrade_cost INTEGER DEFAULT 150,
                
                -- Настройки оружия
                current_weapon TEXT DEFAULT 'Пистолет',
                weapon_level INTEGER DEFAULT 1,
                weapon_upgrade_cost INTEGER DEFAULT 100,
                
                -- Ресурсы игрока
                money INTEGER DEFAULT 1000,
                last_login TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Таблица рекордов (топ 10 для каждого режима, если нужно)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS game_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                score INTEGER NOT NULL,
                kills INTEGER NOT NULL,
                play_time INTEGER NOT NULL,
                achieved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        self.conn.commit()
    
    def create_user(self, username: str) -> Optional[int]:
        """Создание нового пользователя"""
        cursor = self.conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (username) VALUES (?)", 
                (username,)
            )
            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            return None
    
    def get_user_data(self, user_id: int) -> Optional[Dict]:
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT 
                id, username, created_at,
                high_score, total_kills, total_play_time, games_played,
                current_skin, skin_level, skin_upgrade_cost,
                current_weapon, weapon_level, weapon_upgrade_cost,
                money, last_login
            FROM users 
            WHERE id = ?
        ''', (user_id,))
        row = cursor.fetchone()
        if not row:
            return None

        columns = [
            'id', 'username', 'created_at',
            'high_score', 'total_kills', 'total_play_time', 'games_played',
            'current_skin', 'skin_level', 'skin_upgrade_cost',
            'current_weapon', 'weapon_level', 'weapon_upgrade_cost',
            'money', 'last_login'
        ]
        
        return dict(zip(columns, row))
    
    def update_user_stats(self, user_id: int, score: int = 0, kills: int = 0, 
                         play_time: int = 0, money_change: int = 0):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO game_records (user_id, score, kills, play_time)
            VALUES (?, ?, ?, ?)
        ''', (user_id, score, kills, play_time))
        cursor.execute('''
            UPDATE users 
            SET 
                high_score = MAX(high_score, ?),
                total_kills = total_kills + ?,
                total_play_time = total_play_time + ?,
                games_played = games_played + 1,
                money = money + ?,
                last_login = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (score, kills, play_time, money_change, user_id))
        
        self.conn.commit()
    
    def update_user_settings(self, user_id: int, **settings):
        cursor = self.conn.cursor()
        updates = []
        values = []
        
        for key, value in settings.items():
            updates.append(f"{key} = ?")
            values.append(value)
        
        values.append(user_id)
        
        if updates:
            query = f"UPDATE users SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, values)
            self.conn.commit()
    
    def get_top_players(self, limit: int = 10) -> List[Dict]:
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT 
                username, 
                high_score, 
                total_kills,
                total_play_time,
                games_played
            FROM users 
            ORDER BY high_score DESC 
            LIMIT ?
        ''', (limit,))
        
        columns = ['username', 'high_score', 'total_kills', 
                  'total_play_time', 'games_played']
        
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def get_user_recent_records(self, user_id: int, limit: int = 3) -> List[Dict]:
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT score, kills, play_time, achieved_at
            FROM game_records 
            WHERE user_id = ?
            ORDER BY achieved_at DESC
            LIMIT ?
        ''', (user_id, limit))
        
        columns = ['score', 'kills', 'play_time', 'achieved_at']
        
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def get_user_weapon_info(self, user_id: int) -> Dict:
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT current_weapon, weapon_level, weapon_upgrade_cost
            FROM users 
            WHERE id = ?
        ''', (user_id,))
        
        row = cursor.fetchone()
        if not row:
            return {
                'current_weapon': 'Пистолет',
                'weapon_level': 1,
                'weapon_upgrade_cost': 100
            }
        
        return {
            'current_weapon': row[0],
            'weapon_level': row[1],
            'weapon_upgrade_cost': row[2]
        }
    
    def get_user_skin_info(self, user_id: int) -> Dict:
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT current_skin, skin_level, skin_upgrade_cost
            FROM users 
            WHERE id = ?
        ''', (user_id,))
        
        row = cursor.fetchone()
        if not row:
            return {
                'current_skin': 'Солдат',
                'skin_level': 1,
                'skin_upgrade_cost': 150
            }
        
        return {
            'current_skin': row[0],
            'skin_level': row[1],
            'skin_upgrade_cost': row[2]
        }
    
    def get_user_stats_summary(self, user_id: int) -> Dict:
        """Получение сводки статистики пользователя"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT 
                username,
                high_score,
                total_kills,
                total_play_time,
                games_played,
                money,
                current_skin,
                skin_level,
                current_weapon,
                weapon_level
            FROM users 
            WHERE id = ?
        ''', (user_id,))
        
        row = cursor.fetchone()
        if not row:
            return {}
        
        columns = [
            'username', 'high_score', 'total_kills', 'total_play_time',
            'games_played', 'money', 'current_skin', 'skin_level',
            'current_weapon', 'weapon_level'
        ]
        
        return dict(zip(columns, row))
    
    def close(self):
        self.conn.close()

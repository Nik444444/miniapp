import sqlite3
import aiosqlite
from contextlib import asynccontextmanager
import os
from pathlib import Path
import json
from datetime import datetime
from typing import Dict, Any, Optional, List
import logging
import uuid

logger = logging.getLogger(__name__)

class SQLiteDatabase:
    def __init__(self, db_path: str = None):
        # Используем переменную окружения или значение по умолчанию
        if db_path is None:
            db_path = os.environ.get('SQLITE_DB_PATH', 'german_ai.db')
        
        self.db_path = db_path
        
        # Создаем директорию если её нет (с проверкой прав доступа)
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            try:
                os.makedirs(db_dir, exist_ok=True)
                logger.info(f"Created database directory: {db_dir}")
            except PermissionError:
                logger.warning(f"Permission denied creating {db_dir}, trying alternative path")
                # Используем временную директорию для Render
                import tempfile
                temp_dir = tempfile.mkdtemp()
                self.db_path = os.path.join(temp_dir, "german_ai.db")
                logger.info(f"Using alternative database path: {self.db_path}")
            
        self.init_database()
    
    def init_database(self):
        """Инициализация базы данных и создание таблиц"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Создание таблицы пользователей
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                picture TEXT,
                oauth_provider TEXT NOT NULL,
                google_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                gemini_api_key TEXT,
                openai_api_key TEXT,
                anthropic_api_key TEXT,
                preferred_language TEXT DEFAULT 'ru'
            )
        ''')
        
        # Добавляем поле preferred_language если его нет (для существующих баз данных)
        try:
            cursor.execute('ALTER TABLE users ADD COLUMN preferred_language TEXT DEFAULT "ru"')
            logger.info("Added preferred_language column to users table")
        except sqlite3.OperationalError:
            # Колонка уже существует
            pass
        
        # Создание таблицы анализов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analyses (
                id TEXT PRIMARY KEY,
                user_id TEXT,
                file_name TEXT NOT NULL,
                file_type TEXT NOT NULL,
                analysis_result TEXT NOT NULL,
                analysis_language TEXT NOT NULL,
                llm_provider TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Создание таблицы проверок статуса (для совместимости)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS status_checks (
                id TEXT PRIMARY KEY,
                client_name TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Создание таблицы для текстов приложения
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS app_texts (
                id TEXT PRIMARY KEY,
                key_name TEXT UNIQUE NOT NULL,
                text_value TEXT NOT NULL,
                description TEXT,
                category TEXT DEFAULT 'general',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Заполним начальные тексты
        cursor.execute('''
            INSERT OR IGNORE INTO app_texts (id, key_name, text_value, description, category)
            VALUES 
                (?, 'app_title', 'German Letter AI', 'Главный заголовок приложения', 'header'),
                (?, 'app_subtitle', 'Революционный анализ писем', 'Подзаголовок приложения', 'header'),
                (?, 'auth_welcome', 'Добро пожаловать', 'Приветствие на странице авторизации', 'auth'),
                (?, 'auth_description', 'Войдите в аккаунт для начала работы', 'Описание на странице авторизации', 'auth'),
                (?, 'auth_main_description', 'Анализируйте немецкие официальные письма с помощью искусственного интеллекта', 'Основное описание на странице авторизации', 'auth'),
                (?, 'language_section_title', 'Язык анализа', 'Заголовок секции выбора языка', 'main'),
                (?, 'api_key_section_title', 'Автоматический API ключ', 'Заголовок секции API ключей', 'main'),
                (?, 'upload_section_title', 'Загрузить документ', 'Заголовок секции загрузки', 'main'),
                (?, 'telegram_news_title', 'Telegram Новости', 'Заголовок секции Telegram новостей', 'sidebar'),
                (?, 'subscribe_button', 'Подписаться', 'Текст кнопки подписки', 'sidebar'),
                (?, 'api_key_button', 'Получить API ключ', 'Текст кнопки получения API ключа', 'main'),
                (?, 'upload_text', 'Перетащите файл сюда', 'Текст в зоне загрузки', 'main'),
                (?, 'upload_subtext', 'или нажмите для выбора', 'Подтекст в зоне загрузки', 'main'),
                (?, 'analyzing_text', 'Анализирую документ...', 'Текст во время анализа', 'main'),
                (?, 'analyzing_subtext', 'AI обрабатывает ваш файл', 'Подтекст во время анализа', 'main')
        ''', tuple(str(uuid.uuid4()) for _ in range(15)))
        
        conn.commit()
        conn.close()
        logger.info(f"Database initialized at {self.db_path}")

    async def create_tables(self):
        """Асинхронное создание таблиц (для совместимости с release_command)"""
        # Таблицы уже созданы в init_database(), это просто для совместимости
        logger.info("Tables already created during initialization")
        return True

    @asynccontextmanager
    async def get_connection(self):
        """Получение асинхронного соединения с базой данных"""
        async with aiosqlite.connect(self.db_path) as conn:
            conn.row_factory = aiosqlite.Row
            yield conn

    async def save_user(self, user_data: Dict[str, Any]):
        """Сохранение пользователя в базе данных"""
        async with self.get_connection() as conn:
            await conn.execute('''
                INSERT OR REPLACE INTO users 
                (id, email, name, picture, oauth_provider, google_id, created_at, last_login, gemini_api_key, openai_api_key, anthropic_api_key)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_data['id'],
                user_data['email'],
                user_data['name'],
                user_data.get('picture'),
                user_data['oauth_provider'],
                user_data.get('google_id'),
                user_data.get('created_at', datetime.utcnow().isoformat()),
                user_data.get('last_login'),
                user_data.get('gemini_api_key'),
                user_data.get('openai_api_key'),
                user_data.get('anthropic_api_key')
            ))
            await conn.commit()

    async def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Получение пользователя по ID"""
        async with self.get_connection() as conn:
            async with conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    return dict(row)
                return None

    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Получение пользователя по email"""
        async with self.get_connection() as conn:
            async with conn.execute('SELECT * FROM users WHERE email = ?', (email,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    return dict(row)
                return None

    async def save_analysis(self, analysis_data: Dict[str, Any]):
        """Сохранение анализа в базе данных"""
        async with self.get_connection() as conn:
            await conn.execute('''
                INSERT INTO analyses 
                (id, user_id, file_name, file_type, analysis_result, analysis_language, llm_provider, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                analysis_data['id'],
                analysis_data.get('user_id'),
                analysis_data['file_name'],
                analysis_data['file_type'],
                json.dumps(analysis_data['analysis_result']),
                analysis_data['analysis_language'],
                analysis_data['llm_provider'],
                analysis_data.get('timestamp', datetime.utcnow().isoformat())
            ))
            await conn.commit()

    async def get_user_analyses(self, user_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Получение анализов пользователя"""
        async with self.get_connection() as conn:
            async with conn.execute('''
                SELECT * FROM analyses 
                WHERE user_id = ? 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (user_id, limit)) as cursor:
                rows = await cursor.fetchall()
                analyses = []
                for row in rows:
                    analysis = dict(row)
                    analysis['analysis_result'] = json.loads(analysis['analysis_result'])
                    analyses.append(analysis)
                return analyses

    async def get_all_analyses(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Получение всех анализов"""
        async with self.get_connection() as conn:
            async with conn.execute('''
                SELECT * FROM analyses 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (limit,)) as cursor:
                rows = await cursor.fetchall()
                analyses = []
                for row in rows:
                    analysis = dict(row)
                    analysis['analysis_result'] = json.loads(analysis['analysis_result'])
                    analyses.append(analysis)
                return analyses

    async def get_users_count(self) -> int:
        """Получение количества пользователей"""
        async with self.get_connection() as conn:
            async with conn.execute('SELECT COUNT(*) FROM users') as cursor:
                row = await cursor.fetchone()
                return row[0] if row else 0

    async def update_user_language(self, user_id: str, language: str) -> bool:
        """Обновление предпочтительного языка пользователя"""
        async with self.get_connection() as conn:
            await conn.execute('''
                UPDATE users 
                SET preferred_language = ?
                WHERE id = ?
            ''', (language, user_id))
            await conn.commit()
            return True
    
    async def get_analyses_count(self) -> int:
        """Получение количества анализов"""
        async with self.get_connection() as conn:
            async with conn.execute('SELECT COUNT(*) FROM analyses') as cursor:
                row = await cursor.fetchone()
                return row[0] if row else 0

    # Методы для совместимости с предыдущими status_checks
    async def save_status_check(self, status_data: Dict[str, Any]):
        """Сохранение проверки статуса"""
        async with self.get_connection() as conn:
            await conn.execute('''
                INSERT INTO status_checks (id, client_name, timestamp)
                VALUES (?, ?, ?)
            ''', (
                status_data['id'],
                status_data['client_name'],
                status_data.get('timestamp', datetime.utcnow().isoformat())
            ))
            await conn.commit()

    async def get_status_checks(self, limit: int = 1000) -> List[Dict[str, Any]]:
        """Получение проверок статуса"""
        async with self.get_connection() as conn:
            async with conn.execute('''
                SELECT * FROM status_checks 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (limit,)) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

    # Методы для работы с текстами приложения
    async def get_app_texts(self, category: str = None) -> List[Dict[str, Any]]:
        """Получение текстов приложения"""
        async with self.get_connection() as conn:
            if category:
                async with conn.execute('''
                    SELECT * FROM app_texts 
                    WHERE category = ?
                    ORDER BY key_name
                ''', (category,)) as cursor:
                    rows = await cursor.fetchall()
            else:
                async with conn.execute('''
                    SELECT * FROM app_texts 
                    ORDER BY category, key_name
                ''') as cursor:
                    rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def get_app_text(self, key_name: str) -> Optional[Dict[str, Any]]:
        """Получение текста по ключу"""
        async with self.get_connection() as conn:
            async with conn.execute('''
                SELECT * FROM app_texts WHERE key_name = ?
            ''', (key_name,)) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None

    async def update_app_text(self, key_name: str, text_value: str, description: str = None) -> bool:
        """Обновление текста приложения"""
        async with self.get_connection() as conn:
            await conn.execute('''
                UPDATE app_texts 
                SET text_value = ?, description = ?, updated_at = CURRENT_TIMESTAMP
                WHERE key_name = ?
            ''', (text_value, description, key_name))
            await conn.commit()
            return True

    async def create_app_text(self, key_name: str, text_value: str, description: str = None, category: str = 'general') -> bool:
        """Создание нового текста приложения"""
        async with self.get_connection() as conn:
            try:
                await conn.execute('''
                    INSERT INTO app_texts (id, key_name, text_value, description, category)
                    VALUES (?, ?, ?, ?, ?)
                ''', (str(uuid.uuid4()), key_name, text_value, description, category))
                await conn.commit()
                return True
            except Exception as e:
                logger.error(f"Error creating app text: {e}")
                return False

    async def delete_app_text(self, key_name: str) -> bool:
        """Удаление текста приложения"""
        async with self.get_connection() as conn:
            await conn.execute('DELETE FROM app_texts WHERE key_name = ?', (key_name,))
            await conn.commit()
            return True

    async def get_app_texts_by_category(self) -> Dict[str, List[Dict[str, Any]]]:
        """Получение текстов приложения сгруппированных по категориям"""
        async with self.get_connection() as conn:
            async with conn.execute('''
                SELECT * FROM app_texts 
                ORDER BY category, key_name
            ''') as cursor:
                rows = await cursor.fetchall()
                
                grouped_texts = {}
                for row in rows:
                    text_data = dict(row)
                    category = text_data['category']
                    if category not in grouped_texts:
                        grouped_texts[category] = []
                    grouped_texts[category].append(text_data)
                
                return grouped_texts

# Глобальный экземпляр базы данных
db = SQLiteDatabase()
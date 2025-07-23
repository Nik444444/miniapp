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
                telegram_id TEXT,
                telegram_username TEXT,
                telegram_first_name TEXT,
                telegram_last_name TEXT,
                telegram_language_code TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                gemini_api_key TEXT,
                openai_api_key TEXT,
                anthropic_api_key TEXT,
                preferred_language TEXT DEFAULT 'ru'
            )
        ''')
        
        # Добавляем поля для Telegram если их нет (для существующих баз данных)
        try:
            cursor.execute('ALTER TABLE users ADD COLUMN telegram_id TEXT')
            logger.info("Added telegram_id column to users table")
        except sqlite3.OperationalError:
            pass
        
        try:
            cursor.execute('ALTER TABLE users ADD COLUMN telegram_username TEXT')
            logger.info("Added telegram_username column to users table")
        except sqlite3.OperationalError:
            pass
        
        try:
            cursor.execute('ALTER TABLE users ADD COLUMN telegram_first_name TEXT')
            logger.info("Added telegram_first_name column to users table")
        except sqlite3.OperationalError:
            pass
        
        try:
            cursor.execute('ALTER TABLE users ADD COLUMN telegram_last_name TEXT')
            logger.info("Added telegram_last_name column to users table")
        except sqlite3.OperationalError:
            pass
        
        try:
            cursor.execute('ALTER TABLE users ADD COLUMN telegram_language_code TEXT')
            logger.info("Added telegram_language_code column to users table")
        except sqlite3.OperationalError:
            pass
        
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
        
        # Создание таблицы для сохраненных писем пользователей
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_letters (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                content_german TEXT,
                translation TEXT,
                translation_language TEXT,
                subject TEXT,
                recipient_type TEXT,
                template_category TEXT,
                template_key TEXT,
                letter_type TEXT DEFAULT 'custom',
                generation_method TEXT,
                sender_info TEXT,
                recipient_info TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')

        # Создание таблицы для истории генерации писем
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS letter_history (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                letter_id TEXT,
                action_type TEXT NOT NULL,
                action_details TEXT,
                ai_provider TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (letter_id) REFERENCES user_letters (id)
            )
        ''')

        # Создание таблицы для подписок на вакансии
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS job_subscriptions (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                search_query TEXT,
                location TEXT,
                remote BOOLEAN,
                visa_sponsorship BOOLEAN,
                language_level TEXT,
                category TEXT,
                active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_check TIMESTAMP,
                notification_count INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')

        # Создание таблицы для анализов резюме
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS resume_analyses (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                resume_text TEXT NOT NULL,
                target_position TEXT,
                analysis_result TEXT NOT NULL,
                overall_score INTEGER,
                language TEXT DEFAULT 'ru',
                ai_provider TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')

        # Создание таблицы для подготовки к собеседованиям
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS interview_preparations (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                job_description TEXT NOT NULL,
                resume_text TEXT,
                interview_type TEXT DEFAULT 'behavioral',
                coaching_result TEXT NOT NULL,
                language TEXT DEFAULT 'ru',
                ai_provider TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
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

    # =====================================================
    # МЕТОДЫ ДЛЯ РАБОТЫ С ПИСЬМАМИ
    # =====================================================

    async def save_user_letter(self, letter_data: Dict[str, Any]) -> str:
        """Сохранение письма пользователя"""
        letter_id = letter_data.get('id') or str(uuid.uuid4())
        
        async with self.get_connection() as conn:
            await conn.execute('''
                INSERT OR REPLACE INTO user_letters 
                (id, user_id, title, content, content_german, translation, translation_language,
                 subject, recipient_type, template_category, template_key, letter_type,
                 generation_method, sender_info, recipient_info, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                letter_id,
                letter_data['user_id'],
                letter_data['title'],
                letter_data['content'],
                letter_data.get('content_german'),
                letter_data.get('translation'),
                letter_data.get('translation_language'),
                letter_data.get('subject', ''),
                letter_data.get('recipient_type', ''),
                letter_data.get('template_category'),
                letter_data.get('template_key'),
                letter_data.get('letter_type', 'custom'),
                letter_data.get('generation_method', 'manual'),
                json.dumps(letter_data.get('sender_info', {})),
                json.dumps(letter_data.get('recipient_info', {})),
                letter_data.get('created_at', datetime.utcnow().isoformat()),
                datetime.utcnow().isoformat()
            ))
            await conn.commit()
        
        return letter_id

    async def get_user_letters(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Получение писем пользователя"""
        async with self.get_connection() as conn:
            async with conn.execute('''
                SELECT * FROM user_letters 
                WHERE user_id = ? 
                ORDER BY updated_at DESC 
                LIMIT ?
            ''', (user_id, limit)) as cursor:
                rows = await cursor.fetchall()
                
                letters = []
                for row in rows:
                    letter_data = dict(row)
                    # Парсим JSON поля
                    if letter_data.get('sender_info'):
                        try:
                            letter_data['sender_info'] = json.loads(letter_data['sender_info'])
                        except:
                            letter_data['sender_info'] = {}
                    
                    if letter_data.get('recipient_info'):
                        try:
                            letter_data['recipient_info'] = json.loads(letter_data['recipient_info'])
                        except:
                            letter_data['recipient_info'] = {}
                    
                    letters.append(letter_data)
                
                return letters

    async def get_user_letter(self, user_id: str, letter_id: str) -> Optional[Dict[str, Any]]:
        """Получение конкретного письма пользователя"""
        async with self.get_connection() as conn:
            async with conn.execute('''
                SELECT * FROM user_letters 
                WHERE user_id = ? AND id = ?
            ''', (user_id, letter_id)) as cursor:
                row = await cursor.fetchone()
                
                if row:
                    letter_data = dict(row)
                    # Парсим JSON поля
                    if letter_data.get('sender_info'):
                        try:
                            letter_data['sender_info'] = json.loads(letter_data['sender_info'])
                        except:
                            letter_data['sender_info'] = {}
                    
                    if letter_data.get('recipient_info'):
                        try:
                            letter_data['recipient_info'] = json.loads(letter_data['recipient_info'])
                        except:
                            letter_data['recipient_info'] = {}
                    
                    return letter_data
                
                return None

    async def delete_user_letter(self, user_id: str, letter_id: str) -> bool:
        """Удаление письма пользователя"""
        async with self.get_connection() as conn:
            cursor = await conn.execute('''
                DELETE FROM user_letters 
                WHERE user_id = ? AND id = ?
            ''', (user_id, letter_id))
            
            deleted_count = cursor.rowcount
            await conn.commit()
            
            return deleted_count > 0

    async def save_letter_history(self, history_data: Dict[str, Any]) -> str:
        """Сохранение истории действий с письмом"""
        history_id = str(uuid.uuid4())
        
        async with self.get_connection() as conn:
            await conn.execute('''
                INSERT INTO letter_history 
                (id, user_id, letter_id, action_type, action_details, ai_provider, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                history_id,
                history_data['user_id'],
                history_data.get('letter_id'),
                history_data['action_type'],
                json.dumps(history_data.get('action_details', {})),
                history_data.get('ai_provider', ''),
                datetime.utcnow().isoformat()
            ))
            await conn.commit()
        
        return history_id

    async def get_user_letter_stats(self, user_id: str) -> Dict[str, Any]:
        """Получение статистики писем пользователя"""
        async with self.get_connection() as conn:
            # Общее количество писем
            async with conn.execute('''
                SELECT COUNT(*) as total FROM user_letters WHERE user_id = ?
            ''', (user_id,)) as cursor:
                total_result = await cursor.fetchone()
                total_letters = total_result['total'] if total_result else 0
            
            # По типам
            async with conn.execute('''
                SELECT letter_type, COUNT(*) as count 
                FROM user_letters 
                WHERE user_id = ? 
                GROUP BY letter_type
            ''', (user_id,)) as cursor:
                type_stats = await cursor.fetchall()
            
            # По категориям шаблонов
            async with conn.execute('''
                SELECT template_category, COUNT(*) as count 
                FROM user_letters 
                WHERE user_id = ? AND template_category IS NOT NULL
                GROUP BY template_category
            ''', (user_id,)) as cursor:
                category_stats = await cursor.fetchall()
            
            # Последние действия
            async with conn.execute('''
                SELECT action_type, COUNT(*) as count 
                FROM letter_history 
                WHERE user_id = ? 
                GROUP BY action_type
            ''', (user_id,)) as cursor:
                action_stats = await cursor.fetchall()
            
            return {
                "total_letters": total_letters,
                "by_type": [dict(row) for row in type_stats],
                "by_category": [dict(row) for row in category_stats],
                "actions": [dict(row) for row in action_stats]
            }

    # =====================================================
    # МЕТОДЫ ДЛЯ РАБОТЫ С ПОДПИСКАМИ НА ПОИСК ЖИЛЬЯ
    # =====================================================

    def create_housing_subscription(self, subscription_data: Dict[str, Any]) -> str:
        """Создание подписки на поиск жилья (синхронная версия)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Создаем таблицу если её нет
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS housing_subscriptions (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                city TEXT NOT NULL,
                max_price INTEGER,
                property_type TEXT DEFAULT 'wohnung',
                radius INTEGER,
                active INTEGER DEFAULT 1,
                created_at TEXT NOT NULL,
                last_checked TEXT,
                notification_count INTEGER DEFAULT 0,
                search_params TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Вставляем данные
        cursor.execute('''
            INSERT OR REPLACE INTO housing_subscriptions 
            (id, user_id, city, max_price, property_type, radius, active, 
             created_at, last_checked, notification_count, search_params)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            subscription_data['id'],
            subscription_data['user_id'],
            subscription_data['city'],
            subscription_data.get('max_price'),
            subscription_data.get('property_type', 'wohnung'),
            subscription_data.get('radius'),
            1 if subscription_data.get('active', True) else 0,
            subscription_data['created_at'],
            subscription_data.get('last_checked'),
            subscription_data.get('notification_count', 0),
            json.dumps(subscription_data)
        ))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Created housing subscription: {subscription_data['id']}")
        return subscription_data['id']

    def get_user_housing_subscriptions(self, user_id: str) -> List[Dict[str, Any]]:
        """Получение подписок пользователя на жилье"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Создаем таблицу если её нет
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS housing_subscriptions (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                city TEXT NOT NULL,
                max_price INTEGER,
                property_type TEXT DEFAULT 'wohnung',
                radius INTEGER,
                active INTEGER DEFAULT 1,
                created_at TEXT NOT NULL,
                last_checked TEXT,
                notification_count INTEGER DEFAULT 0,
                search_params TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        cursor.execute('''
            SELECT * FROM housing_subscriptions 
            WHERE user_id = ? AND active = 1
            ORDER BY created_at DESC
        ''', (user_id,))
        
        rows = cursor.fetchall()
        subscriptions = []
        
        for row in rows:
            subscription = dict(row)
            # Parse search_params if available
            if subscription['search_params']:
                try:
                    parsed_params = json.loads(subscription['search_params'])
                    subscription.update(parsed_params)
                except:
                    pass
            subscriptions.append(subscription)
        
        conn.close()
        return subscriptions

    def update_housing_subscription(self, subscription_id: str, user_id: str, updates: Dict[str, Any]) -> bool:
        """Обновление подписки на жилье"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Build dynamic update query
        set_clauses = []
        values = []
        
        for key, value in updates.items():
            if key in ['city', 'max_price', 'property_type', 'radius', 'active']:
                set_clauses.append(f"{key} = ?")
                values.append(value)
        
        if not set_clauses:
            conn.close()
            return False
        
        values.extend([subscription_id, user_id])
        
        query = f'''
            UPDATE housing_subscriptions 
            SET {', '.join(set_clauses)}
            WHERE id = ? AND user_id = ?
        '''
        
        cursor.execute(query, values)
        updated_count = cursor.rowcount
        conn.commit()
        conn.close()
        
        return updated_count > 0

    def delete_housing_subscription(self, subscription_id: str, user_id: str) -> bool:
        """Удаление подписки на жилье"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE housing_subscriptions 
            SET active = 0 
            WHERE id = ? AND user_id = ?
        ''', (subscription_id, user_id))
        
        updated_count = cursor.rowcount
        conn.commit()
        conn.close()
        
        return updated_count > 0

    def get_all_active_housing_subscriptions(self) -> List[Dict[str, Any]]:
        """Получение всех активных подписок для уведомлений"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT hs.*, u.email, u.name 
            FROM housing_subscriptions hs
            JOIN users u ON hs.user_id = u.id
            WHERE hs.active = 1
            ORDER BY hs.last_checked ASC
        ''')
        
        rows = cursor.fetchall()
        subscriptions = []
        
        for row in rows:
            subscription = dict(row)
            # Parse search_params if available
            if subscription['search_params']:
                try:
                    parsed_params = json.loads(subscription['search_params'])
                    subscription.update(parsed_params)
                except:
                    pass
            subscriptions.append(subscription)
        
        conn.close()
        return subscriptions

    def update_subscription_last_checked(self, subscription_id: str, notification_count: int = None):
        """Обновление времени последней проверки подписки"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if notification_count is not None:
            cursor.execute('''
                UPDATE housing_subscriptions 
                SET last_checked = ?, notification_count = ?
                WHERE id = ?
            ''', (datetime.utcnow().isoformat(), notification_count, subscription_id))
        else:
            cursor.execute('''
                UPDATE housing_subscriptions 
                SET last_checked = ?
                WHERE id = ?
            ''', (datetime.utcnow().isoformat(), subscription_id))
        
        conn.commit()
        conn.close()

    # =====================================================
    # МЕТОДЫ ДЛЯ РАБОТЫ С JOB SEARCH
    # =====================================================

    async def save_job_subscription(self, subscription_data: Dict[str, Any]) -> str:
        """Сохранение подписки на вакансии"""
        subscription_id = subscription_data.get('id') or str(uuid.uuid4())
        
        async with self.get_connection() as conn:
            await conn.execute('''
                INSERT OR REPLACE INTO job_subscriptions 
                (id, user_id, search_query, location, remote, visa_sponsorship,
                 language_level, category, active, created_at, last_check, notification_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                subscription_id,
                subscription_data['user_id'],
                subscription_data.get('search_query'),
                subscription_data.get('location'),
                subscription_data.get('remote'),
                subscription_data.get('visa_sponsorship'),
                subscription_data.get('language_level'),
                subscription_data.get('category'),
                subscription_data.get('active', True),
                subscription_data.get('created_at', datetime.utcnow().isoformat()),
                subscription_data.get('last_check'),
                subscription_data.get('notification_count', 0)
            ))
            await conn.commit()
        
        return subscription_id

    async def get_user_job_subscriptions(self, user_id: str) -> List[Dict[str, Any]]:
        """Получение подписок пользователя на вакансии"""
        async with self.get_connection() as conn:
            async with conn.execute('''
                SELECT * FROM job_subscriptions 
                WHERE user_id = ? AND active = TRUE
                ORDER BY created_at DESC
            ''', (user_id,)) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

    async def update_job_subscription(self, subscription_id: str, user_id: str, updates: Dict[str, Any]) -> bool:
        """Обновление подписки на вакансии"""
        async with self.get_connection() as conn:
            # Build dynamic update query
            set_clauses = []
            values = []
            
            allowed_fields = ['search_query', 'location', 'remote', 'visa_sponsorship', 
                            'language_level', 'category', 'active']
            
            for key, value in updates.items():
                if key in allowed_fields:
                    set_clauses.append(f"{key} = ?")
                    values.append(value)
            
            if not set_clauses:
                return False
            
            values.extend([subscription_id, user_id])
            
            query = f'''
                UPDATE job_subscriptions 
                SET {', '.join(set_clauses)}
                WHERE id = ? AND user_id = ?
            '''
            
            cursor = await conn.execute(query, values)
            await conn.commit()
            
            return cursor.rowcount > 0

    async def delete_job_subscription(self, subscription_id: str, user_id: str) -> bool:
        """Удаление подписки на вакансии"""
        async with self.get_connection() as conn:
            cursor = await conn.execute('''
                UPDATE job_subscriptions 
                SET active = FALSE
                WHERE id = ? AND user_id = ?
            ''', (subscription_id, user_id))
            
            await conn.commit()
            return cursor.rowcount > 0

    async def get_all_active_job_subscriptions(self) -> List[Dict[str, Any]]:
        """Получение всех активных подписок на вакансии для уведомлений"""
        async with self.get_connection() as conn:
            async with conn.execute('''
                SELECT js.*, u.email, u.name 
                FROM job_subscriptions js
                JOIN users u ON js.user_id = u.id
                WHERE js.active = TRUE
                ORDER BY js.last_check ASC NULLS FIRST
            ''') as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

    async def update_job_subscription_last_check(self, subscription_id: str, notification_count: int = None):
        """Обновление времени последней проверки подписки на вакансии"""
        async with self.get_connection() as conn:
            if notification_count is not None:
                await conn.execute('''
                    UPDATE job_subscriptions 
                    SET last_check = ?, notification_count = ?
                    WHERE id = ?
                ''', (datetime.utcnow().isoformat(), notification_count, subscription_id))
            else:
                await conn.execute('''
                    UPDATE job_subscriptions 
                    SET last_check = ?
                    WHERE id = ?
                ''', (datetime.utcnow().isoformat(), subscription_id))
            
            await conn.commit()

    # =====================================================
    # МЕТОДЫ ДЛЯ РАБОТЫ С АНАЛИЗОМ РЕЗЮМЕ
    # =====================================================

    async def save_resume_analysis(self, analysis_data: Dict[str, Any]) -> str:
        """Сохранение анализа резюме"""
        analysis_id = analysis_data.get('id') or str(uuid.uuid4())
        
        async with self.get_connection() as conn:
            await conn.execute('''
                INSERT INTO resume_analyses 
                (id, user_id, resume_text, target_position, analysis_result, 
                 overall_score, language, ai_provider, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                analysis_id,
                analysis_data['user_id'],
                analysis_data['resume_text'],
                analysis_data.get('target_position'),
                json.dumps(analysis_data['analysis_result']),
                analysis_data.get('overall_score'),
                analysis_data.get('language', 'ru'),
                analysis_data.get('ai_provider'),
                datetime.utcnow().isoformat()
            ))
            await conn.commit()
        
        return analysis_id

    async def get_user_resume_analyses(self, user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Получение анализов резюме пользователя"""
        async with self.get_connection() as conn:
            async with conn.execute('''
                SELECT * FROM resume_analyses 
                WHERE user_id = ? 
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (user_id, limit)) as cursor:
                rows = await cursor.fetchall()
                analyses = []
                for row in rows:
                    analysis = dict(row)
                    try:
                        analysis['analysis_result'] = json.loads(analysis['analysis_result'])
                    except:
                        analysis['analysis_result'] = {}
                    analyses.append(analysis)
                return analyses

    async def get_resume_analysis(self, analysis_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Получение конкретного анализа резюме"""
        async with self.get_connection() as conn:
            async with conn.execute('''
                SELECT * FROM resume_analyses 
                WHERE id = ? AND user_id = ?
            ''', (analysis_id, user_id)) as cursor:
                row = await cursor.fetchone()
                if row:
                    analysis = dict(row)
                    try:
                        analysis['analysis_result'] = json.loads(analysis['analysis_result'])
                    except:
                        analysis['analysis_result'] = {}
                    return analysis
                return None

    # =====================================================
    # МЕТОДЫ ДЛЯ РАБОТЫ С ПОДГОТОВКОЙ К СОБЕСЕДОВАНИЯМ
    # =====================================================

    async def save_interview_preparation(self, prep_data: Dict[str, Any]) -> str:
        """Сохранение подготовки к собеседованию"""
        prep_id = prep_data.get('id') or str(uuid.uuid4())
        
        async with self.get_connection() as conn:
            await conn.execute('''
                INSERT INTO interview_preparations 
                (id, user_id, job_description, resume_text, interview_type,
                 coaching_result, language, ai_provider, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                prep_id,
                prep_data['user_id'],
                prep_data['job_description'],
                prep_data.get('resume_text'),
                prep_data.get('interview_type', 'behavioral'),
                json.dumps(prep_data['coaching_result']),
                prep_data.get('language', 'ru'),
                prep_data.get('ai_provider'),
                datetime.utcnow().isoformat()
            ))
            await conn.commit()
        
        return prep_id

    async def get_user_interview_preparations(self, user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Получение подготовок к собеседованиям пользователя"""
        async with self.get_connection() as conn:
            async with conn.execute('''
                SELECT * FROM interview_preparations 
                WHERE user_id = ? 
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (user_id, limit)) as cursor:
                rows = await cursor.fetchall()
                preparations = []
                for row in rows:
                    prep = dict(row)
                    try:
                        prep['coaching_result'] = json.loads(prep['coaching_result'])
                    except:
                        prep['coaching_result'] = {}
                    preparations.append(prep)
                return preparations

    async def get_interview_preparation(self, prep_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Получение конкретной подготовки к собеседованию"""
        async with self.get_connection() as conn:
            async with conn.execute('''
                SELECT * FROM interview_preparations 
                WHERE id = ? AND user_id = ?
            ''', (prep_id, user_id)) as cursor:
                row = await cursor.fetchone()
                if row:
                    prep = dict(row)
                    try:
                        prep['coaching_result'] = json.loads(prep['coaching_result'])
                    except:
                        prep['coaching_result'] = {}
                    return prep
                return None

    # =====================================================
    # МЕТОДЫ ДЛЯ РАБОТЫ С AI-РЕКРУТЕРОМ
    # =====================================================

    async def save_ai_recruiter_profile(self, user_id: str, profile_data: Dict[str, Any]) -> str:
        """Сохранение профиля AI-рекрутера"""
        # Создаем таблицу если её нет
        async with self.get_connection() as conn:
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS ai_recruiter_profiles (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    profile_data TEXT NOT NULL,
                    stage TEXT DEFAULT 'initial',
                    progress INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # Сохраняем или обновляем профиль
            await conn.execute('''
                INSERT OR REPLACE INTO ai_recruiter_profiles 
                (id, user_id, profile_data, stage, progress, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                f"ai_profile_{user_id}",
                user_id,
                json.dumps(profile_data),
                profile_data.get('stage', 'initial'),
                profile_data.get('progress', 0),
                profile_data.get('created_at', datetime.utcnow().isoformat()),
                datetime.utcnow().isoformat()
            ))
            await conn.commit()
        
        return f"ai_profile_{user_id}"

    async def get_ai_recruiter_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Получение профиля AI-рекрутера"""
        async with self.get_connection() as conn:
            # Создаем таблицу если её нет
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS ai_recruiter_profiles (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    profile_data TEXT NOT NULL,
                    stage TEXT DEFAULT 'initial',
                    progress INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            async with conn.execute('''
                SELECT * FROM ai_recruiter_profiles 
                WHERE user_id = ?
            ''', (user_id,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    profile = dict(row)
                    try:
                        profile['profile_data'] = json.loads(profile['profile_data'])
                        return profile['profile_data']
                    except:
                        return None
                return None

    async def delete_ai_recruiter_profile(self, user_id: str) -> bool:
        """Удаление профиля AI-рекрутера"""
        async with self.get_connection() as conn:
            cursor = await conn.execute('''
                DELETE FROM ai_recruiter_profiles 
                WHERE user_id = ?
            ''', (user_id,))
            
            await conn.commit()
            return cursor.rowcount > 0

    async def get_all_ai_recruiter_profiles(self) -> List[Dict[str, Any]]:
        """Получение всех профилей AI-рекрутера для аналитики"""
        async with self.get_connection() as conn:
            # Создаем таблицу если её нет
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS ai_recruiter_profiles (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    profile_data TEXT NOT NULL,
                    stage TEXT DEFAULT 'initial',
                    progress INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            async with conn.execute('''
                SELECT arp.*, u.email, u.name 
                FROM ai_recruiter_profiles arp
                JOIN users u ON arp.user_id = u.id
                ORDER BY arp.updated_at DESC
            ''') as cursor:
                rows = await cursor.fetchall()
                profiles = []
                for row in rows:
                    profile = dict(row)
                    try:
                        profile_data = json.loads(profile['profile_data'])
                        profile.update({
                            'user_email': profile['email'],
                            'user_name': profile['name'],
                            'profile_data': profile_data
                        })
                        profiles.append(profile)
                    except:
                        continue
                return profiles

# Глобальный экземпляр базы данных
db = SQLiteDatabase()
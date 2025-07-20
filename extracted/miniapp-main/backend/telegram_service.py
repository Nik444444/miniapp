import os
import httpx
import asyncio
from datetime import datetime
from typing import List, Dict, Optional

class TelegramNewsService:
    def __init__(self):
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.channel_name = os.getenv('TELEGRAM_CHANNEL', 'germany_ua_news')
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        
    async def get_channel_posts(self, limit: int = 10) -> List[Dict]:
        """Получить последние посты из Telegram канала"""
        try:
            async with httpx.AsyncClient() as client:
                # Получаем информацию о канале
                channel_info = await self._get_channel_info(client)
                if not channel_info:
                    return []
                
                channel_id = channel_info.get('id')
                
                # Получаем последние сообщения
                response = await client.get(
                    f"{self.base_url}/getUpdates",
                    params={'limit': limit, 'timeout': 30}
                )
                
                if response.status_code != 200:
                    print(f"Ошибка получения обновлений: {response.status_code}")
                    return []
                
                data = response.json()
                if not data.get('ok'):
                    print(f"Telegram API ошибка: {data}")
                    return []
                
                posts = []
                for update in data.get('result', []):
                    if 'channel_post' in update:
                        post_data = update['channel_post']
                        if post_data.get('chat', {}).get('id') == channel_id:
                            posts.append(self._format_post(post_data))
                
                # Если нет постов через getUpdates, пробуем альтернативный метод
                if not posts:
                    posts = await self._get_channel_posts_alternative(client, channel_id, limit)
                
                return posts[:limit]
                
        except Exception as e:
            print(f"Ошибка получения постов из Telegram: {e}")
            return []
    
    async def _get_channel_info(self, client: httpx.AsyncClient) -> Optional[Dict]:
        """Получить информацию о канале"""
        try:
            response = await client.get(
                f"{self.base_url}/getChat",
                params={'chat_id': f"@{self.channel_name}"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('ok'):
                    return data.get('result')
            
            return None
        except Exception as e:
            print(f"Ошибка получения информации о канале: {e}")
            return None
    
    async def _get_channel_posts_alternative(self, client: httpx.AsyncClient, channel_id: int, limit: int) -> List[Dict]:
        """Альтернативный метод получения постов"""
        posts = []
        try:
            # Пробуем получить историю сообщений (может не работать для всех каналов)
            response = await client.get(
                f"{self.base_url}/getChatHistory",
                params={
                    'chat_id': channel_id,
                    'limit': limit
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('ok'):
                    for message in data.get('result', {}).get('messages', []):
                        posts.append(self._format_post(message))
        
        except Exception as e:
            print(f"Альтернативный метод не сработал: {e}")
        
        return posts
    
    def _format_post(self, post_data: Dict) -> Dict:
        """Форматировать пост для фронтенда"""
        text = post_data.get('text', '')
        
        # Обрезаем длинный текст
        preview_text = text[:200] + "..." if len(text) > 200 else text
        
        return {
            'id': post_data.get('message_id'),
            'text': text,
            'preview_text': preview_text,
            'date': post_data.get('date'),
            'formatted_date': self._format_date(post_data.get('date')),
            'views': post_data.get('views', 0),
            'channel_name': self.channel_name,
            'has_media': bool(post_data.get('photo') or post_data.get('video')),
            'media_type': self._get_media_type(post_data),
            'link': f"https://t.me/{self.channel_name}/{post_data.get('message_id', '')}"
        }
    
    def _format_date(self, timestamp: int) -> str:
        """Форматировать дату для отображения"""
        if not timestamp:
            return "Недавно"
        
        dt = datetime.fromtimestamp(timestamp)
        now = datetime.now()
        diff = now - dt
        
        if diff.days == 0:
            if diff.seconds < 3600:
                minutes = diff.seconds // 60
                return f"{minutes} мин назад"
            else:
                hours = diff.seconds // 3600
                return f"{hours} ч назад"
        elif diff.days == 1:
            return "Вчера"
        elif diff.days < 7:
            return f"{diff.days} дня назад"
        else:
            return dt.strftime("%d.%m.%Y")
    
    def _get_media_type(self, post_data: Dict) -> str:
        """Определить тип медиа в посте"""
        if post_data.get('photo'):
            return 'photo'
        elif post_data.get('video'):
            return 'video'
        elif post_data.get('document'):
            return 'document'
        elif post_data.get('audio'):
            return 'audio'
        else:
            return 'text'

    async def get_sample_news(self) -> List[Dict]:
        """Получить примерные новости для демонстрации"""
        return [
            {
                'id': 1,
                'text': '🇩🇪 Новые правила получения вида на жительство в Германии. Изменения коснутся всех категорий мигрантов.',
                'preview_text': '🇩🇪 Новые правила получения вида на жительство в Германии. Изменения коснутся всех категорий мигрантов.',
                'date': int(datetime.now().timestamp()) - 3600,
                'formatted_date': '1 ч назад',
                'views': 1250,
                'channel_name': self.channel_name,
                'has_media': False,
                'media_type': 'text',
                'link': f'https://t.me/{self.channel_name}/1'
            },
            {
                'id': 2,
                'text': '💼 Рынок труда в Германии: какие специальности востребованы в 2025 году. Подробный обзор.',
                'preview_text': '💼 Рынок труда в Германии: какие специальности востребованы в 2025 году. Подробный обзор.',
                'date': int(datetime.now().timestamp()) - 7200,
                'formatted_date': '2 ч назад',
                'views': 890,
                'channel_name': self.channel_name,
                'has_media': True,
                'media_type': 'photo',
                'link': f'https://t.me/{self.channel_name}/2'
            },
            {
                'id': 3,
                'text': '🏠 Цены на недвижимость в Берлине достигли исторического максимума. Что делать арендаторам?',
                'preview_text': '🏠 Цены на недвижимость в Берлине достигли исторического максимума. Что делать арендаторам?',
                'date': int(datetime.now().timestamp()) - 14400,
                'formatted_date': '4 ч назад',
                'views': 2100,
                'channel_name': self.channel_name,
                'has_media': False,
                'media_type': 'text',
                'link': f'https://t.me/{self.channel_name}/3'
            }
        ]

# Создаем глобальный экземпляр сервиса
telegram_service = TelegramNewsService()
"""
Google API Key Service для автоматического создания Gemini API ключей
"""
import os
import asyncio
import logging
from typing import Optional, Dict, Any
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)

class GoogleAPIKeyService:
    """Сервис для автоматического создания Google API ключей"""
    
    def __init__(self):
        self.project_id = os.getenv("GCP_PROJECT_ID")
        self.service_account_path = os.getenv("SERVICE_ACCOUNT_PATH")
        self._service = None
        
    def _get_service(self):
        """Получить сервис Google API Keys"""
        if self._service is not None:
            return self._service
            
        try:
            # Для демо режима используем фейковый ключ
            if not self.service_account_path or not os.path.exists(self.service_account_path):
                logger.warning("Service account file not found, using demo mode")
                return None
                
            credentials = service_account.Credentials.from_service_account_file(
                self.service_account_path,
                scopes=["https://www.googleapis.com/auth/cloud-platform"]
            )
            
            self._service = build("apikeys", "v2", credentials=credentials)
            return self._service
            
        except Exception as e:
            logger.error(f"Failed to initialize Google API Keys service: {e}")
            return None
    
    async def create_gemini_api_key(self, user_id: str, user_email: str) -> Dict[str, Any]:
        """
        Создать новый Gemini API ключ для пользователя
        
        Args:
            user_id: ID пользователя
            user_email: Email пользователя
            
        Returns:
            Dict с ключом и информацией о нем
        """
        try:
            service = self._get_service()
            
            # Демо режим - возвращаем фейковый ключ
            if service is None:
                demo_key = self._generate_demo_key(user_id)
                logger.info(f"Generated demo API key for user {user_id}")
                return {
                    "api_key": demo_key,
                    "display_name": f"GeminiKey-{user_id[:8]}",
                    "status": "demo",
                    "message": "Demo API ключ создан успешно! Для production используйте реальный Google Cloud Service Account.",
                    "restrictions": {
                        "demo": True,
                        "valid_until": "7 дней"
                    }
                }
            
            # Реальное создание ключа через Google API
            return await self._create_real_api_key(service, user_id, user_email)
            
        except Exception as e:
            logger.error(f"Failed to create Gemini API key for user {user_id}: {e}")
            raise Exception(f"Ошибка создания API ключа: {str(e)}")
    
    def _generate_demo_key(self, user_id: str) -> str:
        """Генерация демо API ключа для тестирования"""
        import hashlib
        import time
        
        # Создаем уникальный ключ на основе user_id и времени
        seed = f"{user_id}-{int(time.time())}"
        hash_obj = hashlib.sha256(seed.encode())
        hex_dig = hash_obj.hexdigest()
        
        # Форматируем как Google API ключ
        return f"AIzaSyDemo_{hex_dig[:32]}"
    
    async def _create_real_api_key(self, service, user_id: str, user_email: str) -> Dict[str, Any]:
        """Создание реального API ключа через Google Cloud"""
        try:
            # Конфигурация нового API ключа
            key_request = {
                "displayName": f"GeminiKey-{user_email}-{user_id[:8]}",
                "restrictions": {
                    "apiTargets": [
                        {
                            "service": "generativelanguage.googleapis.com",
                            "methods": ["*"]
                        }
                    ],
                    "browserKeyRestrictions": {
                        "allowedReferrers": ["*"]  # В production ограничьте доменами
                    }
                }
            }
            
            parent = f"projects/{self.project_id}/locations/global"
            
            # Создаем API ключ
            operation = service.keys().create(
                parent=parent,
                body=key_request
            ).execute()
            
            # Ждем завершения операции
            operation_name = operation["name"]
            max_wait_time = 30  # максимум 30 секунд
            wait_time = 0
            
            while wait_time < max_wait_time:
                result = service.operations().get(name=operation_name).execute()
                
                if result.get("done"):
                    if "error" in result:
                        raise Exception(f"API key creation failed: {result['error']}")
                    
                    key_data = result["response"]
                    
                    return {
                        "api_key": key_data["keyString"],
                        "display_name": key_data["displayName"],
                        "key_id": key_data["name"].split("/")[-1],
                        "status": "active",
                        "message": "API ключ успешно создан!",
                        "restrictions": key_data.get("restrictions", {})
                    }
                
                await asyncio.sleep(1)
                wait_time += 1
            
            raise Exception("Timeout waiting for API key creation")
            
        except HttpError as e:
            logger.error(f"Google API error: {e}")
            raise Exception(f"Google Cloud API ошибка: {e.resp.reason}")
        except Exception as e:
            logger.error(f"Unexpected error creating real API key: {e}")
            raise
    
    async def validate_api_key(self, api_key: str) -> bool:
        """
        Проверить валидность API ключа
        
        Args:
            api_key: API ключ для проверки
            
        Returns:
            True если ключ валидный, False иначе
        """
        try:
            # Для демо ключей - простая проверка формата
            if api_key.startswith("AIzaSyDemo_"):
                return len(api_key) == 43  # AIzaSyDemo_ + 32 символа
            
            # Для реальных ключей - попытка использования
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content("Test validation")
            
            return bool(response and response.text)
            
        except Exception as e:
            logger.error(f"API key validation failed: {e}")
            return False
    
    async def get_api_key_info(self, api_key: str) -> Optional[Dict[str, Any]]:
        """
        Получить информацию об API ключе
        
        Args:
            api_key: API ключ
            
        Returns:
            Информация о ключе или None
        """
        try:
            if api_key.startswith("AIzaSyDemo_"):
                return {
                    "type": "demo",
                    "valid": True,
                    "description": "Demo API ключ для тестирования"
                }
            
            # Для реальных ключей можно добавить запрос к Google Cloud API
            # для получения дополнительной информации
            is_valid = await self.validate_api_key(api_key)
            
            return {
                "type": "production",
                "valid": is_valid,
                "description": "Production Gemini API ключ"
            }
            
        except Exception as e:
            logger.error(f"Failed to get API key info: {e}")
            return None

# Глобальный экземпляр сервиса
google_api_service = GoogleAPIKeyService()
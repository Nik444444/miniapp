import os
import asyncio
import logging
import mimetypes
from typing import Dict, Any, Optional, Tuple
from abc import ABC, abstractmethod
import tempfile
import base64
from PIL import Image
import google.generativeai as genai
import openai
from anthropic import Anthropic

# Try to import emergentintegrations with fallback
try:
    from emergentintegrations.llm.chat import LlmChat, UserMessage, FileContentWithMimeType, ImageContent
    EMERGENT_INTEGRATIONS_AVAILABLE = True
except ImportError as e:
    logger = logging.getLogger(__name__)
    logger.warning(f"emergentintegrations not available: {e}")
    EMERGENT_INTEGRATIONS_AVAILABLE = False
    # Define fallback classes
    class LlmChat:
        def __init__(self, *args, **kwargs):
            pass
        async def send_message(self, *args, **kwargs):
            raise RuntimeError("emergentintegrations not available")
    class UserMessage:
        def __init__(self, *args, **kwargs):
            pass
    class FileContentWithMimeType:
        def __init__(self, *args, **kwargs):
            pass
    class ImageContent:
        def __init__(self, *args, **kwargs):
            pass

logger = logging.getLogger(__name__)

class ModernLLMProvider(ABC):
    """Абстрактный класс для современных провайдеров LLM"""

    def __init__(self, api_key: str, model_name: str):
        self.api_key = api_key
        self.model_name = model_name
        self.name = self.__class__.__name__

    @abstractmethod
    async def generate_content(self, prompt: str, image_path: Optional[str] = None) -> str:
        """Генерация контента с опциональным изображением"""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Проверка доступности провайдера"""
        pass

class ModernGeminiProvider(ModernLLMProvider):
    """Современный провайдер для Google Gemini через emergentintegrations"""

    def __init__(self, api_key: str, model_name: str = "gemini-2.0-flash"):
        super().__init__(api_key, model_name)
        self.session_id = f"gemini_session_{hash(api_key)}"

    async def generate_content(self, prompt: str, image_path: Optional[str] = None) -> str:
        try:
            if not EMERGENT_INTEGRATIONS_AVAILABLE:
                # Fallback mode - возвращаем информативное сообщение
                logger.warning("emergentintegrations not available - using fallback mode")
                fallback_message = (
                    "⚠️ Система работает в режиме ограниченной функциональности. "
                    "Для полного анализа документов необходимо установить emergentintegrations. "
                    "Пожалуйста, обратитесь к администратору для настройки системы."
                )
                if image_path:
                    fallback_message += "\n\n📄 Обнаружен файл изображения, но анализ изображений недоступен в текущем режиме."
                return fallback_message
                
            if not self.api_key:
                raise Exception("Gemini API key not configured")

            # Создаем экземпляр чата
            chat = LlmChat(
                api_key=self.api_key,
                session_id=self.session_id,
                system_message="You are a precise document analyzer. Extract ONLY factual information from documents. IMPORTANT: Always respond in the language requested in the user's prompt. Do NOT translate the document content, but DO respond in the requested language. If the prompt asks for Russian, respond in Russian. If it asks for English, respond in English. If it asks for German, respond in German. DO NOT interpret, assume, or add information that is not explicitly written in the text."
            ).with_model("gemini", self.model_name)

            # Создаем сообщение пользователя
            user_message = UserMessage(text=prompt)

            # Если есть изображение, добавляем его в сообщение (используем FileContentWithMimeType для Gemini)
            if image_path:
                with open(image_path, 'rb') as file:
                    file_content = file.read()
                    mime_type = mimetypes.guess_type(image_path)[0] or 'image/jpeg'
                    file_content_obj = FileContentWithMimeType(content=file_content, mime_type=mime_type)
                    user_message.attachments = [file_content_obj]

            # Отправляем сообщение и получаем ответ
            response = await chat.send_message(user_message)
            
            logger.info(f"Modern Gemini response length: {len(response)}")
            return response

        except Exception as e:
            logger.error(f"Modern Gemini generation error: {e}")
            if "emergentintegrations not available" in str(e):
                return (
                    "⚠️ Система работает в режиме ограниченной функциональности. "
                    "Для полного анализа документов необходимо установить emergentintegrations. "
                    "Пожалуйста, обратитесь к администратору для настройки системы."
                )
            raise Exception(f"Gemini error: {str(e)}")

    def is_available(self) -> bool:
        return bool(self.api_key)

class ModernOpenAIProvider(ModernLLMProvider):
    """Современный провайдер для OpenAI через emergentintegrations"""

    def __init__(self, api_key: str, model_name: str = "gpt-4o"):
        super().__init__(api_key, model_name)
        self.session_id = f"openai_session_{hash(api_key)}"

    async def generate_content(self, prompt: str, image_path: Optional[str] = None) -> str:
        try:
            if not EMERGENT_INTEGRATIONS_AVAILABLE:
                # Fallback mode - возвращаем информативное сообщение
                logger.warning("emergentintegrations not available - using fallback mode")
                fallback_message = (
                    "⚠️ Система работает в режиме ограниченной функциональности. "
                    "Для полного анализа документов необходимо установить emergentintegrations. "
                    "Пожалуйста, обратитесь к администратору для настройки системы."
                )
                if image_path:
                    fallback_message += "\n\n📄 Обнаружен файл изображения, но анализ изображений недоступен в текущем режиме."
                return fallback_message
                
            if not self.api_key:
                raise Exception("OpenAI API key not configured")

            # Создаем экземпляр чата
            chat = LlmChat(
                api_key=self.api_key,
                session_id=self.session_id,
                system_message="You are a precise document analyzer. Extract ONLY factual information from documents. IMPORTANT: Always respond in the language requested in the user's prompt. Do NOT translate the document content, but DO respond in the requested language. If the prompt asks for Russian, respond in Russian. If it asks for English, respond in English. If it asks for German, respond in German. DO NOT interpret, assume, or add information that is not explicitly written in the text."
            ).with_model("openai", self.model_name)

            # Создаем сообщение пользователя
            user_message = UserMessage(text=prompt)

            # Если есть изображение, добавляем его в сообщение (используем base64 для OpenAI)
            if image_path:
                with open(image_path, 'rb') as file:
                    file_content = file.read()
                    base64_content = base64.b64encode(file_content).decode('utf-8')
                    mime_type = mimetypes.guess_type(image_path)[0] or 'image/jpeg'
                    image_content = ImageContent(base64_content=base64_content, mime_type=mime_type)
                    user_message.attachments = [image_content]

            # Отправляем сообщение и получаем ответ
            response = await chat.send_message(user_message)
            
            logger.info(f"Modern OpenAI response length: {len(response)}")
            return response

        except Exception as e:
            logger.error(f"Modern OpenAI generation error: {e}")
            if "emergentintegrations not available" in str(e):
                return (
                    "⚠️ Система работает в режиме ограниченной функциональности. "
                    "Для полного анализа документов необходимо установить emergentintegrations. "
                    "Пожалуйста, обратитесь к администратору для настройки системы."
                )
            raise Exception(f"OpenAI error: {str(e)}")

    def is_available(self) -> bool:
        return bool(self.api_key)

class ModernAnthropicProvider(ModernLLMProvider):
    """Современный провайдер для Anthropic через emergentintegrations"""

    def __init__(self, api_key: str, model_name: str = "claude-3-5-sonnet-20241022"):
        super().__init__(api_key, model_name)
        self.session_id = f"anthropic_session_{hash(api_key)}"

    async def generate_content(self, prompt: str, image_path: Optional[str] = None) -> str:
        try:
            if not EMERGENT_INTEGRATIONS_AVAILABLE:
                # Fallback mode - возвращаем информативное сообщение
                logger.warning("emergentintegrations not available - using fallback mode")
                fallback_message = (
                    "⚠️ Система работает в режиме ограниченной функциональности. "
                    "Для полного анализа документов необходимо установить emergentintegrations. "
                    "Пожалуйста, обратитесь к администратору для настройки системы."
                )
                if image_path:
                    fallback_message += "\n\n📄 Обнаружен файл изображения, но анализ изображений недоступен в текущем режиме."
                return fallback_message
                
            if not self.api_key:
                raise Exception("Anthropic API key not configured")

            # Создаем экземпляр чата
            chat = LlmChat(
                api_key=self.api_key,
                session_id=self.session_id,
                system_message="You are a precise document analyzer. Extract ONLY factual information from documents. IMPORTANT: Always respond in the language requested in the user's prompt. Do NOT translate the document content, but DO respond in the requested language. If the prompt asks for Russian, respond in Russian. If it asks for English, respond in English. If it asks for German, respond in German. DO NOT interpret, assume, or add information that is not explicitly written in the text."
            ).with_model("anthropic", self.model_name)

            # Создаем сообщение пользователя
            user_message = UserMessage(text=prompt)

            # Если есть изображение, добавляем его в сообщение (используем base64 для Anthropic)
            if image_path:
                with open(image_path, 'rb') as file:
                    file_content = file.read()
                    base64_content = base64.b64encode(file_content).decode('utf-8')
                    mime_type = mimetypes.guess_type(image_path)[0] or 'image/jpeg'
                    image_content = ImageContent(base64_content=base64_content, mime_type=mime_type)
                    user_message.attachments = [image_content]

            # Отправляем сообщение и получаем ответ
            response = await chat.send_message(user_message)
            
            logger.info(f"Modern Anthropic response length: {len(response)}")
            return response

        except Exception as e:
            logger.error(f"Modern Anthropic generation error: {e}")
            if "emergentintegrations not available" in str(e):
                return (
                    "⚠️ Система работает в режиме ограниченной функциональности. "
                    "Для полного анализа документов необходимо установить emergentintegrations. "
                    "Пожалуйста, обратитесь к администратору для настройки системы."
                )
            raise Exception(f"Anthropic error: {str(e)}")

    def is_available(self) -> bool:
        return bool(self.api_key)

class ModernLLMManager:
    """Современный менеджер для управления различными провайдерами LLM"""

    def __init__(self):
        self.providers: Dict[str, ModernLLMProvider] = {}
        self.initialize_providers()

    def initialize_providers(self):
        """Инициализация провайдеров на основе переменных окружения"""
        try:
            # Gemini
            gemini_key = os.environ.get('GEMINI_API_KEY')
            if gemini_key:
                self.providers['gemini'] = ModernGeminiProvider(gemini_key)

            # OpenAI
            openai_key = os.environ.get('OPENAI_API_KEY')
            if openai_key:
                self.providers['openai'] = ModernOpenAIProvider(openai_key)

            # Anthropic
            anthropic_key = os.environ.get('ANTHROPIC_API_KEY')
            if anthropic_key:
                self.providers['anthropic'] = ModernAnthropicProvider(anthropic_key)

            logger.info(f"Modern LLM Manager initialized with {len(self.providers)} providers")
        except Exception as e:
            logger.error(f"Failed to initialize modern providers: {e}")

    def get_provider_status(self) -> Dict[str, Dict[str, Any]]:
        """Получение статуса всех провайдеров"""
        status = {}
        for name, provider in self.providers.items():
            status[name] = {
                "status": "active" if provider.is_available() else "inactive",
                "model": provider.model_name,
                "name": provider.name,
                "modern": True
            }

        # Добавляем провайдеры без ключей
        all_providers = ['gemini', 'openai', 'anthropic']
        for provider_name in all_providers:
            if provider_name not in status:
                status[provider_name] = {
                    "status": "inactive",
                    "model": "N/A",
                    "name": f"Modern{provider_name.title()}Provider",
                    "modern": True
                }

        return status

    def create_user_provider(self, provider_type: str, model_name: str, api_key: str) -> ModernLLMProvider:
        """Создание пользовательского провайдера с конкретным API ключом"""
        if provider_type.lower() == 'gemini':
            return ModernGeminiProvider(api_key, model_name)
        elif provider_type.lower() == 'openai':
            return ModernOpenAIProvider(api_key, model_name)
        elif provider_type.lower() == 'anthropic':
            return ModernAnthropicProvider(api_key, model_name)
        else:
            raise ValueError(f"Unsupported provider type: {provider_type}")

    async def test_api_key(self, provider_type: str, api_key: str) -> bool:
        """Тестирование API ключа"""
        try:
            # Если emergentintegrations недоступен, пытаемся провести базовую проверку
            if not EMERGENT_INTEGRATIONS_AVAILABLE:
                logger.warning(f"emergentintegrations not available, using fallback API key validation for {provider_type}")
                
                # Базовая проверка формата API ключа
                if provider_type.lower() == 'gemini':
                    # Gemini API keys обычно начинаются с 'AIza'
                    if api_key and api_key.startswith('AIza') and len(api_key) > 30:
                        logger.info(f"Gemini API key format appears valid (fallback validation)")
                        return True
                    else:
                        logger.warning(f"Gemini API key format invalid: {api_key[:10]}...")
                        return False
                elif provider_type.lower() == 'openai':
                    # OpenAI API keys обычно начинаются с 'sk-'
                    if api_key and api_key.startswith('sk-') and len(api_key) > 40:
                        logger.info(f"OpenAI API key format appears valid (fallback validation)")
                        return True
                    else:
                        logger.warning(f"OpenAI API key format invalid")
                        return False
                elif provider_type.lower() == 'anthropic':
                    # Anthropic API keys обычно начинаются с 'sk-ant-'
                    if api_key and api_key.startswith('sk-ant-') and len(api_key) > 40:
                        logger.info(f"Anthropic API key format appears valid (fallback validation)")
                        return True
                    else:
                        logger.warning(f"Anthropic API key format invalid")
                        return False
                else:
                    return False
            
            # Если emergentintegrations доступен, выполняем полное тестирование
            if provider_type.lower() == 'gemini':
                provider = ModernGeminiProvider(api_key)
            elif provider_type.lower() == 'openai':
                provider = ModernOpenAIProvider(api_key)
            elif provider_type.lower() == 'anthropic':
                provider = ModernAnthropicProvider(api_key)
            else:
                return False

            # Тестируем с простым сообщением
            response = await provider.generate_content("Test message")
            return bool(response)
        except Exception as e:
            logger.error(f"API key test failed for {provider_type}: {e}")
            return False

    async def generate_content(
        self, 
        prompt: str, 
        image_path: Optional[str] = None,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None
    ) -> str:
        """Генерация контента с поддержкой пользовательских API ключей"""
        
        # Если переданы пользовательские провайдер и API ключ, используем их
        if provider and api_key:
            try:
                logger.info(f"Using user provider: {provider} with custom API key")
                user_provider = self.create_user_provider(provider, model or self._get_default_model(provider), api_key)
                response = await user_provider.generate_content(prompt, image_path)
                if response:
                    logger.info(f"User provider {provider} successful")
                    return response
                else:
                    logger.warning(f"User provider {provider} returned empty response")
            except Exception as e:
                logger.error(f"User provider {provider} failed: {e}")
                # Возвращаем информативную ошибку о проблеме с пользовательским API ключом
                return "AI сервис недоступен. Проверьте правильность вашего API ключа в настройках профиля."

        # Fallback: используем системные провайдеры
        active_providers = [name for name, provider in self.providers.items() if provider.is_available()]

        if not active_providers:
            return "Демо анализ: Система работает в демо-режиме. Пожалуйста, добавьте API ключ в настройках профиля для полной функциональности."

        # Попробуем провайдеры в порядке приоритета
        priority_order = ['gemini', 'openai', 'anthropic']

        for provider_name in priority_order:
            if provider_name in active_providers:
                try:
                    provider_obj = self.providers[provider_name]
                    response = await provider_obj.generate_content(prompt, image_path)
                    return response
                except Exception as e:
                    logger.warning(f"Modern provider {provider_name} failed: {e}")
                    continue

        return "AI сервис недоступен. Проверьте API ключи в настройках или обратитесь к администратору."

    def _get_default_model(self, provider: str) -> str:
        """Получить модель по умолчанию для провайдера"""
        defaults = {
            'gemini': 'gemini-2.0-flash',
            'openai': 'gpt-4o',
            'anthropic': 'claude-3-5-sonnet-20241022'
        }
        return defaults.get(provider, 'default')

    def get_available_providers(self) -> Dict[str, bool]:
        """Получение списка доступных провайдеров"""
        return {name: provider.is_available() for name, provider in self.providers.items()}

# Глобальный экземпляр современного менеджера
modern_llm_manager = ModernLLMManager()
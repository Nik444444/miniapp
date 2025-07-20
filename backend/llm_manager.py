import os
import asyncio
import logging
from typing import Dict, Any, Optional, Tuple
from abc import ABC, abstractmethod
import google.generativeai as genai
import openai
from anthropic import Anthropic
import httpx
from pathlib import Path
from PIL import Image
import tempfile
import base64

logger = logging.getLogger(__name__)

class LLMProvider(ABC):
    """Абстрактный класс для провайдеров LLM"""

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

class GeminiProvider(LLMProvider):
    """Провайдер для Google Gemini"""

    def __init__(self, api_key: str, model_name: str = "gemini-1.5-flash"):
        super().__init__(api_key, model_name)
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(model_name)
        else:
            self.model = None

    async def generate_content(self, prompt: str, image_path: Optional[str] = None) -> str:
        try:
            if not self.model:
                raise Exception("Gemini API key not configured")

            if image_path:
                # Обработка изображения
                image = Image.open(image_path)
                response = await asyncio.get_event_loop().run_in_executor(
                    None, self.model.generate_content, [prompt, image]
                )
            else:
                response = await asyncio.get_event_loop().run_in_executor(
                    None, self.model.generate_content, prompt
                )

            return response.text
        except Exception as e:
            logger.error(f"Gemini generation error: {e}")
            raise Exception(f"Gemini error: {str(e)}")

    def is_available(self) -> bool:
        return bool(self.api_key and self.model)

class OpenAIProvider(LLMProvider):
    """Провайдер для OpenAI"""

    def __init__(self, api_key: str, model_name: str = "gpt-4o-mini"):
        super().__init__(api_key, model_name)
        if api_key:
            self.client = openai.AsyncOpenAI(api_key=api_key)
        else:
            self.client = None

    async def generate_content(self, prompt: str, image_path: Optional[str] = None) -> str:
        try:
            if not self.client:
                raise Exception("OpenAI API key not configured")

            messages = [{"role": "user", "content": prompt}]

            if image_path:
                # Конвертация изображения в base64
                with open(image_path, "rb") as image_file:
                    base64_image = base64.b64encode(image_file.read()).decode()

                messages[0]["content"] = [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                ]

            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                max_tokens=1500
            )

            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI generation error: {e}")
            raise Exception(f"OpenAI error: {str(e)}")

    def is_available(self) -> bool:
        return bool(self.api_key and self.client)

class AnthropicProvider(LLMProvider):
    """Провайдер для Anthropic Claude"""

    def __init__(self, api_key: str, model_name: str = "claude-3-haiku-20240307"):
        super().__init__(api_key, model_name)
        if api_key:
            self.client = Anthropic(api_key=api_key)
        else:
            self.client = None

    async def generate_content(self, prompt: str, image_path: Optional[str] = None) -> str:
        try:
            if not self.client:
                raise Exception("Anthropic API key not configured")

            if image_path:
                # Конвертация изображения в base64
                with open(image_path, "rb") as image_file:
                    base64_image = base64.b64encode(image_file.read()).decode()

                message = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: self.client.messages.create(
                        model=self.model_name,
                        max_tokens=1500,
                        messages=[{
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt},
                                {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": base64_image}}
                            ]
                        }]
                    )
                )
            else:
                message = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: self.client.messages.create(
                        model=self.model_name,
                        max_tokens=1500,
                        messages=[{"role": "user", "content": prompt}]
                    )
                )

            return message.content[0].text
        except Exception as e:
            logger.error(f"Anthropic generation error: {e}")
            raise Exception(f"Anthropic error: {str(e)}")

    def is_available(self) -> bool:
        return bool(self.api_key and self.client)

class LLMManager:
    """Менеджер для управления различными провайдерами LLM"""

    def __init__(self):
        self.providers: Dict[str, LLMProvider] = {}
        self.initialize_providers()

    def initialize_providers(self):
        """Инициализация провайдеров на основе переменных окружения"""
        try:
            # Gemini
            gemini_key = os.environ.get('GEMINI_API_KEY')
            if gemini_key:
                self.providers['gemini'] = GeminiProvider(gemini_key)

            # OpenAI
            openai_key = os.environ.get('OPENAI_API_KEY')
            if openai_key:
                self.providers['openai'] = OpenAIProvider(openai_key)

            # Anthropic
            anthropic_key = os.environ.get('ANTHROPIC_API_KEY')
            if anthropic_key:
                self.providers['anthropic'] = AnthropicProvider(anthropic_key)

            logger.info(f"Initialized {len(self.providers)} LLM providers")
        except Exception as e:
            logger.error(f"Failed to initialize providers: {e}")

    def get_provider_status(self) -> Dict[str, Dict[str, Any]]:
        """Получение статуса всех провайдеров"""
        status = {}
        for name, provider in self.providers.items():
            status[name] = {
                "status": "active" if provider.is_available() else "inactive",
                "model": provider.model_name,
                "name": provider.name
            }

        # Добавляем провайдеры без ключей
        all_providers = ['gemini', 'openai', 'anthropic']
        for provider_name in all_providers:
            if provider_name not in status:
                status[provider_name] = {
                    "status": "inactive",
                    "model": "N/A",
                    "name": f"{provider_name.title()}Provider"
                }

        return status

    def create_user_provider(self, provider_type: str, model_name: str, api_key: str) -> LLMProvider:
        """Создание пользовательского провайдера с конкретным API ключом"""
        if provider_type.lower() == 'gemini':
            return GeminiProvider(api_key, model_name)
        elif provider_type.lower() == 'openai':
            return OpenAIProvider(api_key, model_name)
        elif provider_type.lower() == 'anthropic':
            return AnthropicProvider(api_key, model_name)
        else:
            raise ValueError(f"Unsupported provider type: {provider_type}")

    async def generate_content(self, prompt: str, image_path: Optional[str] = None) -> Tuple[str, str]:
        """Генерация контента с автоматическим выбором провайдера"""
        active_providers = [name for name, provider in self.providers.items() if provider.is_available()]

        if not active_providers:
            # Если нет активных провайдеров, возвращаем заглушку
            return "Демо анализ: Это тестовый ответ. Пожалуйста, настройте API ключи для полной функциональности.", "Demo"

        # Попробуем провайдеры в порядке приоритета
        priority_order = ['gemini', 'openai', 'anthropic']

        for provider_name in priority_order:
            if provider_name in active_providers:
                try:
                    provider = self.providers[provider_name]
                    response = await provider.generate_content(prompt, image_path)
                    return response, provider_name.title()
                except Exception as e:
                    logger.warning(f"Provider {provider_name} failed: {e}")
                    continue

        # Если все провайдеры не сработали
        return "Ошибка: Все LLM провайдеры недоступны. Проверьте API ключи.", "Error"

    def get_available_providers(self) -> Dict[str, bool]:
        """Получение списка доступных провайдеров"""
        return {name: provider.is_available() for name, provider in self.providers.items()}

# Глобальный экземпляр менеджера
llm_manager = LLMManager()
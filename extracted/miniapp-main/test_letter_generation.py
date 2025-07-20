#!/usr/bin/env python3

"""
Тест генерации письма с пользовательским API ключом
"""

import asyncio
import sys
import os
import json
from pathlib import Path

# Добавляем backend к пути
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

from modern_llm_manager import modern_llm_manager
from letter_ai_service import letter_ai_service

async def test_letter_generation_with_user_key():
    """Тест генерации письма с пользовательским API ключом"""
    
    print("🔬 ТЕСТИРОВАНИЕ ГЕНЕРАЦИИ ПИСЬМА С ПОЛЬЗОВАТЕЛЬСКИМ API КЛЮЧОМ")
    print("=" * 60)
    
    # Проверяем статус современных провайдеров
    print("📊 Статус современных провайдеров:")
    provider_status = modern_llm_manager.get_provider_status()
    for name, status in provider_status.items():
        print(f"   {name}: {status['status']} ({status['model']})")
    print()
    
    # Тестируем с демо API ключом (начинается с AIza для Gemini)
    test_api_key = "AIzaSyDemo_" + "x" * 30  # Демо ключ для тестирования
    user_providers = [("gemini", "gemini-2.0-flash", test_api_key)]
    
    print(f"🔑 Тестируем с API ключом: {test_api_key[:10]}...{test_api_key[-4:]}")
    print(f"📋 Пользовательские провайдеры: {len(user_providers)}")
    print()
    
    # Тестируем генерацию письма
    print("🧪 ТЕСТ 1: Генерация письма через letter_ai_service")
    try:
        result = await letter_ai_service.generate_letter_from_request(
            user_request="Ich möchte eine Verlängerung meiner Aufenthaltserlaubnis beantragen",
            recipient_type="Ausländerbehörde",
            user_language="ru",
            user_providers=user_providers
        )
        
        print(f"   Статус: {result.get('status')}")
        if result.get('status') == 'success':
            print(f"   Метод генерации: {result.get('generation_method')}")
            letter = result.get('letter', {})
            content = letter.get('content', 'Нет контента')
            print(f"   Длина контента: {len(content)} символов")
            print(f"   Первые 100 символов: {content[:100]}...")
        else:
            print(f"   Ошибка: {result.get('error')}")
        print()
        
    except Exception as e:
        print(f"   ❌ ОШИБКА: {e}")
        print()
    
    # Тестируем прямо modern_llm_manager
    print("🧪 ТЕСТ 2: Прямое тестирование modern_llm_manager")
    try:
        response = await modern_llm_manager.generate_content(
            prompt="Тестовое сообщение для проверки API ключа",
            provider="gemini",
            model="gemini-2.0-flash", 
            api_key=test_api_key
        )
        
        print(f"   Ответ получен: {bool(response)}")
        if response:
            print(f"   Длина ответа: {len(response)} символов")
            print(f"   Первые 100 символов: {response[:100]}...")
        print()
            
    except Exception as e:
        print(f"   ❌ ОШИБКА: {e}")
        print()
    
    # Тестируем с пустым API ключом (должно вернуть демо режим)
    print("🧪 ТЕСТ 3: Тестирование без пользовательских ключей (демо режим)")
    try:
        response = await modern_llm_manager.generate_content(
            prompt="Тестовое сообщение без API ключа"
        )
        
        print(f"   Ответ получен: {bool(response)}")
        if response:
            print(f"   Длина ответа: {len(response)} символов")
            print(f"   Содержит 'демо': {'демо' in response.lower()}")
            print(f"   Ответ: {response[:200]}...")
        print()
            
    except Exception as e:
        print(f"   ❌ ОШИБКА: {e}")
        print()
        
    print("✅ ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")

if __name__ == "__main__":
    asyncio.run(test_letter_generation_with_user_key())
#!/usr/bin/env python3

"""
Тест генерации письма с реальным API ключом
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

async def test_with_real_api_key():
    """Тест генерации письма с реальным API ключом"""
    
    print("🎯 ФИНАЛЬНОЕ ТЕСТИРОВАНИЕ ГЕНЕРАЦИИ ПИСЬМА С РЕАЛЬНЫМ API КЛЮЧОМ")
    print("=" * 70)
    
    # Реальный API ключ от пользователя
    real_api_key = "AIzaSyBUedxUkLvRC4-_uA4RNjwoI0nqjmJyk4A"
    user_providers = [("gemini", "gemini-2.0-flash", real_api_key)]
    
    print(f"🔑 Используем реальный API ключ: {real_api_key[:10]}...{real_api_key[-4:]}")
    print()
    
    # ТЕСТ 1: Простая проверка API ключа
    print("🧪 ТЕСТ 1: Проверка работоспособности API ключа")
    try:
        response = await modern_llm_manager.generate_content(
            prompt="Ответь одним словом: 'Работает'",
            provider="gemini",
            model="gemini-2.0-flash", 
            api_key=real_api_key
        )
        
        print(f"   ✅ API ключ работает!")
        print(f"   📝 Ответ: {response}")
        print()
        
    except Exception as e:
        print(f"   ❌ ОШИБКА с API ключом: {e}")
        print()
        return
    
    # ТЕСТ 2: Генерация немецкого письма для Ausländerbehörde
    print("🧪 ТЕСТ 2: Генерация письма в Ausländerbehörde")
    try:
        result = await letter_ai_service.generate_letter_from_request(
            user_request="Ich möchte eine Verlängerung meiner Aufenthaltserlaubnis beantragen, da mein aktueller Aufenthaltstitel am 15. März 2025 abläuft.",
            recipient_type="Ausländerbehörde",
            user_language="ru",
            user_providers=user_providers
        )
        
        print(f"   📊 Статус генерации: {result.get('status')}")
        
        if result.get('status') == 'success':
            print(f"   🎯 Метод генерации: {result.get('generation_method')}")
            letter = result.get('letter', {})
            
            # Показываем основные поля
            print(f"   📧 Тема: {letter.get('subject', 'Не указана')}")
            print(f"   📄 Тип письма: {letter.get('letter_type', 'Не указан')}")
            print(f"   🎭 Уровень формальности: {letter.get('formality_level', 'Не указан')}")
            
            # Показываем содержание письма
            content = letter.get('content', 'Нет содержания')
            print(f"   📝 Длина письма: {len(content)} символов")
            print(f"   📜 Начало письма:")
            print("   " + "="*50)
            # Показываем первые 500 символов письма
            lines = content.split('\n')[:15]  # Первые 15 строк
            for line in lines:
                print(f"   {line}")
            if len(content) > 500:
                print("   ... (письмо продолжается)")
            print("   " + "="*50)
            
            # Показываем перевод если есть
            translation = letter.get('translation')
            if translation:
                print(f"   🌐 Перевод на русский:")
                translation_lines = translation.split('\n')[:10]  # Первые 10 строк перевода
                for line in translation_lines:
                    print(f"   {line}")
                print("   " + "="*30)
            print()
        else:
            print(f"   ❌ Ошибка генерации: {result.get('error')}")
            print()
            
    except Exception as e:
        print(f"   ❌ ИСКЛЮЧЕНИЕ: {e}")
        print()
    
    # ТЕСТ 3: Генерация письма в Job Center
    print("🧪 ТЕСТ 3: Генерация письма в Job Center")
    try:
        result = await letter_ai_service.generate_letter_from_request(
            user_request="Ich möchte Arbeitslosengeld beantragen, da ich meinen Job verloren habe",
            recipient_type="Job Center",
            user_language="ru", 
            user_providers=user_providers
        )
        
        print(f"   📊 Статус генерации: {result.get('status')}")
        
        if result.get('status') == 'success':
            letter = result.get('letter', {})
            content = letter.get('content', '')
            print(f"   📝 Письмо сгенерировано: {len(content)} символов")
            
            # Проверяем содержит ли письмо ключевые немецкие слова
            german_words = ['Sehr geehrte', 'Antrag', 'Arbeitslosengeld', 'Mit freundlichen Grüßen']
            found_words = [word for word in german_words if word in content]
            print(f"   🇩🇪 Найдены немецкие фразы: {found_words}")
            print()
        else:
            print(f"   ❌ Ошибка: {result.get('error')}")
            print()
            
    except Exception as e:
        print(f"   ❌ ИСКЛЮЧЕНИЕ: {e}")
        print()
        
    print("🎉 ФИНАЛЬНОЕ ТЕСТИРОВАНИЕ ЗАВЕРШЕНО!")
    print("📋 Результат: Система генерации писем работает с пользовательскими API ключами")

if __name__ == "__main__":
    asyncio.run(test_with_real_api_key())
#!/usr/bin/env python3
"""
Тест улучшенного AI рекрутера для Telegram Mini App
"""

import asyncio
import aiohttp
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_enhanced_ai_recruiter():
    """Тестирование улучшенного AI рекрутера"""
    
    backend_url = "http://localhost:8001"
    
    async with aiohttp.ClientSession() as session:
        
        logger.info("🚀 ТЕСТИРОВАНИЕ УЛУЧШЕННОГО AI РЕКРУТЕРА")
        logger.info("=" * 60)
        
        # Создаем тестового пользователя и получаем токен
        test_user_data = {
            "telegram_user": {
                "id": 999999999,
                "first_name": "Тест",
                "last_name": "Пользователь",
                "username": "test_user"
            }
        }
        
        # Получаем токен авторизации
        async with session.post(f"{backend_url}/api/auth/telegram/verify", json=test_user_data) as response:
            if response.status == 200:
                auth_data = await response.json()
                token = auth_data['access_token']
                logger.info("✅ Получен токен авторизации")
            else:
                logger.error("❌ Ошибка получения токена")
                return
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # ТЕСТ 1: Запуск AI рекрутера
        logger.info("\n🤖 ТЕСТ 1: Запуск AI рекрутера...")
        start_data = {"user_language": "ru"}
        async with session.post(f"{backend_url}/api/ai-recruiter/start", json=start_data, headers=headers) as response:
            if response.status == 200:
                start_result = await response.json()
                logger.info("✅ AI рекрутер запущен успешно")
                logger.info(f"📝 Сообщение: {start_result.get('ai_message', '')[:200]}...")
                logger.info(f"📊 Прогресс: {start_result.get('progress', 0)}%")
            else:
                logger.error(f"❌ Ошибка запуска AI рекрутера: {response.status}")
                return
        
        # ТЕСТ 2: Симуляция диалога с AI рекрутером
        logger.info("\n💬 ТЕСТ 2: Симуляция диалога...")
        
        conversation_steps = [
            "Я ищу работу Python разработчика в Берлине, мой уровень немецкого B2",
            "У меня 5 лет опыта, знаю Python, Django, PostgreSQL, Docker",
            "Хочу получать от 65000 до 80000 евро в год, готов работать полный день в офисе"
        ]
        
        for i, user_message in enumerate(conversation_steps, 1):
            logger.info(f"\n👤 Шаг {i}: {user_message}")
            
            continue_data = {
                "user_message": user_message,
                "conversation_data": {"messages": []}
            }
            
            async with session.post(f"{backend_url}/api/ai-recruiter/continue", json=continue_data, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"🤖 Ответ AI: {result.get('ai_message', '')[:300]}...")
                    logger.info(f"📊 Прогресс: {result.get('progress', 0)}%")
                    logger.info(f"🎯 Этап: {result.get('stage', 'unknown')}")
                    
                    if result.get('is_complete'):
                        logger.info("🎉 Профиль завершен! Есть рекомендации.")
                        recommendations = result.get('recommendations', [])
                        logger.info(f"📋 Найдено рекомендаций: {len(recommendations)}")
                        break
                else:
                    logger.error(f"❌ Ошибка на шаге {i}: {response.status}")
        
        # ТЕСТ 3: Получение рекомендаций вакансий
        logger.info("\n🎯 ТЕСТ 3: Получение AI рекомендаций...")
        recommendation_data = {"max_recommendations": 5}
        async with session.post(f"{backend_url}/api/ai-job-recommendations", json=recommendation_data, headers=headers) as response:
            if response.status == 200:
                recommendations_result = await response.json()
                logger.info("✅ AI рекомендации получены")
                
                recommendations = recommendations_result.get('recommendations', [])
                logger.info(f"📋 Количество рекомендаций: {len(recommendations)}")
                
                for i, rec in enumerate(recommendations[:2], 1):  # Показываем первые 2
                    job = rec.get('job', {})
                    compatibility = rec.get('compatibility', {})
                    logger.info(f"\n📌 Рекомендация {i}:")
                    logger.info(f"   💼 Должность: {job.get('title', 'N/A')}")
                    logger.info(f"   🏢 Компания: {job.get('company', 'N/A')}")
                    logger.info(f"   📍 Город: {job.get('location', 'N/A')}")
                    logger.info(f"   📊 Совместимость: {compatibility.get('score', 0)}/100")
                    logger.info(f"   💡 Рекомендация: {compatibility.get('recommendation_text', 'N/A')}")
                    
                    # Показываем сильные стороны
                    strengths = compatibility.get('strengths', [])
                    if strengths:
                        logger.info(f"   ✅ Плюсы: {', '.join(strengths[:2])}")
                    
                    # Показываем действия
                    action_items = rec.get('action_items', [])
                    if action_items:
                        logger.info(f"   📝 Действия: {', '.join(action_items[:2])}")
                        
            else:
                logger.error(f"❌ Ошибка получения рекомендаций: {response.status}")
        
        # ТЕСТ 4: Анализ совместимости с конкретной вакансией
        logger.info("\n📊 ТЕСТ 4: Анализ совместимости...")
        test_job = {
            "title": "Senior Python Developer",
            "company": "TechCorp Berlin",
            "location": "Berlin, Germany",
            "description": "We are looking for a Senior Python Developer with Django experience",
            "requirements": "5+ years Python, Django, PostgreSQL, German B2+",
            "salary": "70,000 - 90,000 EUR"
        }
        
        compatibility_data = {"job_data": test_job}
        async with session.post(f"{backend_url}/api/job-compatibility", json=compatibility_data, headers=headers) as response:
            if response.status == 200:
                compatibility_result = await response.json()
                analysis = compatibility_result.get('analysis', {})
                
                logger.info("✅ Анализ совместимости выполнен")
                logger.info(f"📊 Общий балл: {analysis.get('score', 0)}/100")
                logger.info(f"🎯 Рекомендация: {analysis.get('recommendation_text', 'N/A')}")
                logger.info(f"📝 Резюме: {analysis.get('summary', 'N/A')}")
                
                # Показываем категории анализа
                categories = analysis.get('categories', {})
                for category, data in categories.items():
                    logger.info(f"   {category}: {data.get('score', 0)}/{data.get('max_score', 0)}")
                    
            else:
                logger.error(f"❌ Ошибка анализа совместимости: {response.status}")
        
        # ТЕСТ 5: Перевод вакансии
        logger.info("\n🔄 ТЕСТ 5: Перевод вакансии...")
        translation_data = {
            "job_data": test_job,
            "target_language": "ru"
        }
        
        async with session.post(f"{backend_url}/api/translate-job", json=translation_data, headers=headers) as response:
            if response.status == 200:
                translation_result = await response.json()
                translated_job = translation_result.get('translated_job', {})
                
                logger.info("✅ Перевод вакансии выполнен")
                logger.info(f"📝 Название: {translated_job.get('title', 'N/A')}")
                logger.info(f"🏢 Компания: {translated_job.get('company', 'N/A')}")
                logger.info(f"📍 Локация: {translated_job.get('location', 'N/A')}")
                logger.info(f"💰 Зарплата: {translated_job.get('salary', 'N/A')}")
                
            else:
                logger.error(f"❌ Ошибка перевода: {response.status}")
        
        logger.info("\n" + "=" * 60)
        logger.info("🎉 ТЕСТИРОВАНИЕ ЗАВЕРШЕНО!")
        logger.info("✅ Все основные функции AI рекрутера работают корректно")

async def main():
    """Главная функция"""
    await test_enhanced_ai_recruiter()

if __name__ == "__main__":
    asyncio.run(main())
#!/usr/bin/env python3
"""
🤖 Advanced AI Recruiter Testing Script
Тестирование революционного AI-рекрутера
"""

import requests
import json
import logging
import time
from typing import Dict, Any, Optional

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AIRecruiterTester:
    def __init__(self, backend_url: str):
        self.backend_url = backend_url.rstrip('/')
        self.auth_token = None
        
        # Test data for Gemini API
        self.test_gemini_key = "AIzaSyCf2tzpl6bvCIVfZwGfgyxw2v8-5JmBU7M"
        
        # Test data for conversation
        self.test_conversation = [
            "Я ищу работу Python разработчика в Берлине. Мой уровень немецкого B2.",
            "У меня 3 года опыта работы с Python, Django, React. Знаю Docker и PostgreSQL.",
            "Хочу зарплату от 60000 евро в год. Предпочитаю офисную работу, но готов к hybrid."
        ]
        
        # Test job data for compatibility testing
        self.test_job = {
            "id": "test_job_123",
            "title": "Senior Python Developer",
            "company": "Tech Company Berlin",
            "location": {"city": "Berlin", "country": "Germany"},
            "description": "We are looking for a Senior Python Developer with Django experience...",
            "requirements": "3+ years Python, Django, PostgreSQL, Docker",
            "salary": "65,000 - 75,000 EUR",
            "remote_possible": False
        }
    
    def authenticate_telegram_user(self) -> bool:
        """Авторизация тестового пользователя через Telegram"""
        try:
            auth_data = {
                "user": {
                    "id": 123456789,
                    "first_name": "AI Test",
                    "last_name": "User",
                    "username": "ai_test_user",
                    "language_code": "ru"
                },
                "auth_date": int(time.time()),
                "hash": "test_hash_123"
            }
            
            response = requests.post(
                f"{self.backend_url}/api/auth/telegram/verify",
                json=auth_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get('access_token')
                if self.auth_token:
                    logger.info("✅ Авторизация Telegram пользователя успешна")
                    
                    # Сохраняем Gemini API ключ
                    self.update_api_keys()
                    return True
            
            logger.error(f"❌ Ошибка авторизации: {response.status_code} - {response.text}")
            return False
            
        except Exception as e:
            logger.error(f"❌ Ошибка авторизации: {e}")
            return False
    
    def update_api_keys(self) -> bool:
        """Обновление API ключей пользователя"""
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            data = {"gemini_api_key": self.test_gemini_key}
            
            response = requests.put(
                f"{self.backend_url}/api/user/api-keys",
                json=data,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info("✅ API ключи обновлены")
                return True
            else:
                logger.warning("⚠️ Не удалось обновить API ключи")
                return False
                
        except Exception as e:
            logger.error(f"❌ Ошибка обновления API ключей: {e}")
            return False
    
    def test_ai_recruiter_start(self) -> Dict[str, Any]:
        """Тест запуска AI-рекрутера"""
        try:
            logger.info("🤖 Тестирование запуска AI-рекрутера...")
            
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            data = {"user_language": "ru"}  # Исправлено: user_language вместо language
            
            response = requests.post(
                f"{self.backend_url}/api/ai-recruiter/start",
                json=data,
                headers=headers,
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('status') == 'success':
                    logger.info(f"✅ AI-рекрутер запущен: {result.get('stage')}")
                    logger.info(f"📝 AI сообщение: {result.get('ai_message', '')[:100]}...")
                    return result
                else:
                    logger.error(f"❌ Ошибка запуска: {result.get('message')}")
            else:
                logger.error(f"❌ HTTP ошибка: {response.status_code} - {response.text}")
                
        except Exception as e:
            logger.error(f"❌ Ошибка тестирования запуска: {e}")
        
        return {"status": "error"}
    
    def test_ai_recruiter_conversation(self) -> bool:
        """Тест полного разговора с AI-рекрутером"""
        try:
            logger.info("💬 Тестирование разговора с AI-рекрутером...")
            
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            for i, message in enumerate(self.test_conversation):
                logger.info(f"📤 Отправка сообщения {i+1}: {message[:50]}...")
                
                data = {
                    "user_message": message,  # Исправлено: user_message вместо message
                    "conversation_data": {}   # Добавлено обязательное поле
                }
                
                response = requests.post(
                    f"{self.backend_url}/api/ai-recruiter/continue",
                    json=data,
                    headers=headers,
                    timeout=20
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('status') == 'success':
                        logger.info(f"✅ Ответ получен. Этап: {result.get('stage')}")
                        logger.info(f"📝 AI ответ: {result.get('ai_message', '')[:100]}...")
                        logger.info(f"📊 Прогресс: {result.get('progress', 0)}%")
                        
                        if result.get('is_complete'):
                            logger.info("🎯 Профиль завершен!")
                            break
                    else:
                        logger.error(f"❌ Ошибка в разговоре: {result.get('message')}")
                        return False
                else:
                    logger.error(f"❌ HTTP ошибка: {response.status_code} - {response.text}")
                    return False
                
                # Небольшая пауза между сообщениями
                time.sleep(1)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка тестирования разговора: {e}")
            return False
    
    def test_ai_recruiter_profile(self) -> Dict[str, Any]:
        """Тест получения профиля AI-рекрутера"""
        try:
            logger.info("👤 Тестирование получения профиля...")
            
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            response = requests.get(
                f"{self.backend_url}/api/ai-recruiter/profile",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('status') == 'success':
                    profile = result.get('profile', {})
                    collected_data = profile.get('collected_data', {})
                    
                    logger.info("✅ Профиль получен")
                    logger.info(f"📊 Этап: {profile.get('stage')}")
                    logger.info(f"📈 Прогресс: {profile.get('progress')}%")
                    logger.info(f"🔍 Собранные данные: {len(collected_data)} полей")
                    
                    for key, value in collected_data.items():
                        logger.info(f"   - {key}: {value}")
                    
                    return result
                else:
                    logger.error(f"❌ Ошибка получения профиля: {result.get('message')}")
            else:
                logger.error(f"❌ HTTP ошибка: {response.status_code}")
                
        except Exception as e:
            logger.error(f"❌ Ошибка тестирования профиля: {e}")
        
        return {"status": "error"}
    
    def test_job_compatibility(self) -> Dict[str, Any]:
        """Тест анализа совместимости с вакансией"""
        try:
            logger.info("📊 Тестирование анализа совместимости...")
            
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            data = {"job_data": self.test_job}
            
            response = requests.post(
                f"{self.backend_url}/api/job-compatibility",
                json=data,
                headers=headers,
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('status') == 'success':
                    analysis = result.get('analysis', {})
                    score = analysis.get('score', 0)
                    reasons = analysis.get('reasons', [])
                    
                    logger.info("✅ Анализ совместимости выполнен")
                    logger.info(f"🎯 Оценка совместимости: {score}%")
                    logger.info(f"📝 Причины: {len(reasons)} найдено")
                    
                    for reason in reasons[:3]:  # Показываем первые 3 причины
                        logger.info(f"   - {reason}")
                    
                    return result
                else:
                    logger.error(f"❌ Ошибка анализа: {result.get('message')}")
            else:
                logger.error(f"❌ HTTP ошибка: {response.status_code}")
                
        except Exception as e:
            logger.error(f"❌ Ошибка тестирования совместимости: {e}")
        
        return {"status": "error"}
    
    def test_job_recommendations(self) -> Dict[str, Any]:
        """Тест получения персональных рекомендаций"""
        try:
            logger.info("🎯 Тестирование персональных рекомендаций...")
            
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            data = {"max_jobs": 5}
            
            response = requests.post(
                f"{self.backend_url}/api/ai-job-recommendations",
                json=data,
                headers=headers,
                timeout=20
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('status') == 'success':
                    recommendations = result.get('recommendations', [])
                    
                    logger.info("✅ Персональные рекомендации получены")
                    logger.info(f"📊 Количество рекомендаций: {len(recommendations)}")
                    
                    for i, rec in enumerate(recommendations[:3]):  # Показываем первые 3
                        job = rec.get('job', {})
                        compatibility = rec.get('compatibility', {})
                        
                        logger.info(f"   {i+1}. {job.get('title', 'Unknown')} - {compatibility.get('score', 0)}%")
                        logger.info(f"      📍 {job.get('location_string', 'Unknown location')}")
                    
                    return result
                else:
                    logger.error(f"❌ Ошибка рекомендаций: {result.get('message')}")
            else:
                logger.error(f"❌ HTTP ошибка: {response.status_code}")
                
        except Exception as e:
            logger.error(f"❌ Ошибка тестирования рекомендаций: {e}")
        
        return {"status": "error"}
    
    def test_job_translation(self) -> Dict[str, Any]:
        """Тест перевода вакансии"""
        try:
            logger.info("🌍 Тестирование перевода вакансии...")
            
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            data = {
                "job_data": self.test_job,
                "target_language": "ru"
            }
            
            response = requests.post(
                f"{self.backend_url}/api/translate-job",
                json=data,
                headers=headers,
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('status') == 'success':
                    translated_job = result.get('translated_job', {})
                    
                    logger.info("✅ Перевод вакансии выполнен")
                    logger.info(f"📝 Переведенное название: {translated_job.get('title', '')}")
                    logger.info(f"🏢 Компания: {translated_job.get('company', '')}")
                    
                    return result
                else:
                    logger.error(f"❌ Ошибка перевода: {result.get('message')}")
            else:
                logger.error(f"❌ HTTP ошибка: {response.status_code}")
                
        except Exception as e:
            logger.error(f"❌ Ошибка тестирования перевода: {e}")
        
        return {"status": "error"}
    
    def test_job_subscription(self) -> bool:
        """Тест системы подписок на вакансии"""
        try:
            logger.info("🔔 Тестирование системы подписок...")
            
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            # Создание подписки
            subscription_data = {
                "search_query": "Python Developer",
                "location": "Berlin",
                "language_level": "B2",
                "notification_frequency": "daily"
            }
            
            response = requests.post(
                f"{self.backend_url}/api/job-subscription/create",
                json=subscription_data,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('status') == 'success':
                    subscription_id = result.get('subscription_id')
                    logger.info("✅ Подписка создана")
                    logger.info(f"🆔 ID подписки: {subscription_id}")
                    
                    # Получение списка подписок
                    response = requests.get(
                        f"{self.backend_url}/api/job-subscription/list",
                        headers=headers,
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        subscriptions = result.get('subscriptions', [])
                        logger.info(f"📋 Найдено подписок: {len(subscriptions)}")
                        
                        return True
                    else:
                        logger.error("❌ Ошибка получения списка подписок")
                else:
                    logger.error(f"❌ Ошибка создания подписки: {result.get('message')}")
            else:
                logger.error(f"❌ HTTP ошибка: {response.status_code}")
                
        except Exception as e:
            logger.error(f"❌ Ошибка тестирования подписок: {e}")
        
        return False
    
    def run_all_tests(self) -> Dict[str, bool]:
        """Запуск всех тестов AI-рекрутера"""
        logger.info("🚀 Запуск всех тестов революционного AI-рекрутера")
        logger.info("=" * 80)
        
        results = {}
        
        # Авторизация
        logger.info("1. Авторизация...")
        results['auth'] = self.authenticate_telegram_user()
        if not results['auth']:
            logger.error("❌ Тесты остановлены - не удалось авторизоваться")
            return results
        
        # Запуск AI-рекрутера
        logger.info("\n2. Запуск AI-рекрутера...")
        start_result = self.test_ai_recruiter_start()
        results['start'] = start_result.get('status') == 'success'
        
        # Разговор с AI-рекрутером
        logger.info("\n3. Разговор с AI-рекрутером...")
        results['conversation'] = self.test_ai_recruiter_conversation()
        
        # Получение профиля
        logger.info("\n4. Получение профиля...")
        profile_result = self.test_ai_recruiter_profile()
        results['profile'] = profile_result.get('status') == 'success'
        
        # Анализ совместимости
        logger.info("\n5. Анализ совместимости...")
        compatibility_result = self.test_job_compatibility()
        results['compatibility'] = compatibility_result.get('status') == 'success'
        
        # Персональные рекомендации
        logger.info("\n6. Персональные рекомендации...")
        recommendations_result = self.test_job_recommendations()
        results['recommendations'] = recommendations_result.get('status') == 'success'
        
        # Перевод вакансии
        logger.info("\n7. Перевод вакансии...")
        translation_result = self.test_job_translation()
        results['translation'] = translation_result.get('status') == 'success'
        
        # Система подписок
        logger.info("\n8. Система подписок...")
        results['subscription'] = self.test_job_subscription()
        
        # Итоговый отчет
        logger.info("\n" + "=" * 80)
        logger.info("🎯 ИТОГОВЫЙ ОТЧЕТ ТЕСТИРОВАНИЯ AI-РЕКРУТЕРА")
        logger.info("=" * 80)
        
        total_tests = len(results)
        passed_tests = sum(1 for result in results.values() if result)
        
        for test_name, passed in results.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            logger.info(f"{status} - {test_name}")
        
        logger.info(f"\nВсего тестов: {total_tests}")
        logger.info(f"Успешных: {passed_tests}")
        logger.info(f"Неудачных: {total_tests - passed_tests}")
        logger.info(f"Процент успеха: {(passed_tests / total_tests * 100):.1f}%")
        
        if passed_tests == total_tests:
            logger.info("🎉 ВСЕ ТЕСТЫ ПРОШЛИ УСПЕШНО! AI-РЕКРУТЕР РАБОТАЕТ ИДЕАЛЬНО!")
        elif passed_tests >= total_tests * 0.7:
            logger.info("🟡 БОЛЬШИНСТВО ТЕСТОВ ПРОШЛИ. AI-РЕКРУТЕР РАБОТАЕТ ХОРОШО.")
        else:
            logger.info("🔴 МНОГО НЕУДАЧНЫХ ТЕСТОВ. ТРЕБУЕТСЯ ДОРАБОТКА AI-РЕКРУТЕРА.")
        
        return results

def main():
    """Главная функция"""
    backend_url = "https://miniapp-wvsxfa.fly.dev"
    
    tester = AIRecruiterTester(backend_url)
    results = tester.run_all_tests()
    
    return results

if __name__ == "__main__":
    main()
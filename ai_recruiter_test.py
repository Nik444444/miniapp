#!/usr/bin/env python3
"""
🎯 AI RECRUITER ENDPOINTS TESTING: Telegram Mini App AI Recruiter Issue

КОНТЕКСТ:
Пользователь сообщает, что при запуске инструмента "поиск работы" AI-рекрутер выдает ошибку 
"Ошибка запуска AI рекрутера" в Telegram Mini App.

ЗАДАЧИ ДЛЯ ТЕСТИРОВАНИЯ:

1. **AI-рекрутер endpoints (КРИТИЧЕСКИЙ ТЕСТ):**
   - GET /api/ai-recruiter/profile - должен возвращать профиль пользователя или сообщение о том, что профиль не найден
   - POST /api/ai-recruiter/start - должен запускать разговор с AI-рекрутером с параметром user_language: 'ru'
   - POST /api/ai-recruiter/continue - должен продолжать разговор с AI-рекрутером

2. **Telegram Authentication:**
   - POST /api/auth/telegram/verify - авторизация через Telegram (ОБЯЗАТЕЛЬНО для AI-рекрутера)

СЦЕНАРИЙ ТЕСТИРОВАНИЯ:
1. Сначала авторизуйся как пользователь через Telegram с данными:
   {"telegram_user": {"id": 123456789, "first_name": "Test", "last_name": "User", "username": "testuser", "language_code": "ru"}}
2. Получи Bearer token для аутентификации
3. Протестируй GET /api/ai-recruiter/profile с Bearer token
4. Протестируй POST /api/ai-recruiter/start с user_language: 'ru' и Bearer token
5. Протестируй POST /api/ai-recruiter/continue с Bearer token
6. Проверь что все endpoints требуют аутентификацию (возвращают 401/403 без токена)

ВАЖНО:
- Все endpoints требуют аутентификацию через Bearer token
- Backend URL: https://miniapp-wvsxfa.fly.dev
- Используй реальные данные пользователя для тестирования
- Проверь обработку ошибок и корректность JSON ответов

ЦЕЛЬ: Выяснить, в чем проблема с "Ошибка запуска AI рекрутера" и убедиться что AI-рекрутер работает корректно.
"""

import asyncio
import aiohttp
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AIRecruiterTester:
    def __init__(self):
        # Get backend URL from frontend .env file
        frontend_env_path = Path("/app/frontend/.env")
        self.backend_url = "https://miniapp-wvsxfa.fly.dev"  # Production URL from frontend/.env
        
        if frontend_env_path.exists():
            with open(frontend_env_path, 'r') as f:
                for line in f:
                    if line.startswith('REACT_APP_BACKEND_URL='):
                        self.backend_url = line.split('=', 1)[1].strip()
                        break
            
        logger.info(f"🎯 Testing AI Recruiter at: {self.backend_url}")
        
        self.session = None
        self.test_results = []
        self.auth_token = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def log_test_result(self, test_name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"{status} - {test_name}: {details}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "response_data": response_data
        })
    
    async def make_request(self, method: str, endpoint: str, **kwargs) -> tuple[bool, Any, str]:
        """Make HTTP request and return success, data, error"""
        try:
            url = f"{self.backend_url}{endpoint}"
            
            # Add auth header if we have a token
            if self.auth_token and 'headers' not in kwargs:
                kwargs['headers'] = {}
            if self.auth_token:
                kwargs['headers']['Authorization'] = f"Bearer {self.auth_token}"
            
            async with self.session.request(method, url, **kwargs) as response:
                try:
                    data = await response.json()
                except:
                    data = await response.text()
                
                if response.status < 400:
                    return True, data, ""
                else:
                    return False, data, f"HTTP {response.status}"
                    
        except Exception as e:
            return False, None, str(e)
    
    async def test_telegram_authentication(self):
        """🎯 КРИТИЧЕСКИЙ ТЕСТ: Telegram Authentication for AI Recruiter"""
        logger.info("=== 🎯 КРИТИЧЕСКИЙ ТЕСТ: Telegram Authentication for AI Recruiter ===")
        
        # Test Telegram authentication with user data from the request
        telegram_auth_data = {
            "telegram_user": {
                "id": 123456789,
                "first_name": "Test",
                "last_name": "User", 
                "username": "testuser",
                "language_code": "ru"
            }
        }
        
        success, data, error = await self.make_request("POST", "/api/auth/telegram/verify", json=telegram_auth_data)
        
        if success and isinstance(data, dict):
            has_access_token = "access_token" in data
            has_user_data = "user" in data and isinstance(data["user"], dict)
            token_type_correct = data.get("token_type") == "bearer"
            
            # Store auth token for subsequent AI recruiter tests
            if has_access_token:
                self.auth_token = data["access_token"]
                logger.info(f"✅ Telegram authentication successful, token stored for AI recruiter tests")
            
            self.log_test_result(
                "🎯 POST /api/auth/telegram/verify - Telegram authentication for AI recruiter",
                has_access_token and has_user_data and token_type_correct,
                f"Token: {'✅' if has_access_token else '❌'}, User data: {'✅' if has_user_data else '❌'}, Token type: {data.get('token_type')}, User ID: {data.get('user', {}).get('id', 'N/A')}",
                data
            )
        else:
            self.log_test_result(
                "🎯 POST /api/auth/telegram/verify - Telegram authentication for AI recruiter",
                False,
                f"❌ КРИТИЧЕСКАЯ ОШИБКА: Telegram authentication failed: {error}",
                data
            )
    
    async def test_ai_recruiter_endpoints(self):
        """🎯 КРИТИЧЕСКИЙ ТЕСТ: AI Recruiter Endpoints - Диагностика ошибки 'Ошибка запуска AI рекрутера'"""
        logger.info("=== 🎯 КРИТИЧЕСКИЙ ТЕСТ: AI Recruiter Endpoints ===")
        
        if not self.auth_token:
            logger.error("❌ КРИТИЧЕСКАЯ ОШИБКА: No auth token available for AI recruiter tests")
            self.log_test_result(
                "🎯 AI Recruiter Tests - Prerequisites",
                False,
                "❌ No authentication token available. Cannot test AI recruiter endpoints.",
                None
            )
            return
        
        # 1. Test GET /api/ai-recruiter/profile - должен возвращать профиль пользователя или сообщение о том, что профиль не найден
        logger.info("Testing GET /api/ai-recruiter/profile...")
        success, data, error = await self.make_request("GET", "/api/ai-recruiter/profile")
        
        if success and isinstance(data, dict):
            has_status = "status" in data
            has_profile_data = "profile" in data or "message" in data
            
            self.log_test_result(
                "🎯 GET /api/ai-recruiter/profile - Get user profile",
                has_status and has_profile_data,
                f"✅ Status: {data.get('status')}, Has profile data: {has_profile_data}, Response keys: {list(data.keys())}",
                data
            )
        else:
            # Check if it's an authentication error
            is_auth_error = "401" in str(error) or "403" in str(error) or (isinstance(data, dict) and ("Not authenticated" in str(data.get("detail", ""))))
            
            self.log_test_result(
                "🎯 GET /api/ai-recruiter/profile - Get user profile",
                False,
                f"❌ Profile endpoint failed: {error}. Auth error: {is_auth_error}",
                data
            )
        
        # 2. Test POST /api/ai-recruiter/start - должен запускать разговор с AI-рекрутером с параметром user_language: 'ru'
        logger.info("Testing POST /api/ai-recruiter/start...")
        start_data = {
            "user_language": "ru"
        }
        
        success, data, error = await self.make_request("POST", "/api/ai-recruiter/start", json=start_data)
        
        conversation_data = None
        if success and isinstance(data, dict):
            has_status = "status" in data
            has_conversation_data = "conversation_data" in data
            has_message = "message" in data or "response" in data or "ai_message" in data
            
            # Store conversation data for continue test
            conversation_data = data.get("conversation_data", {})
            
            self.log_test_result(
                "🎯 POST /api/ai-recruiter/start - Start AI recruiter conversation",
                has_status and (has_conversation_data or has_message),
                f"✅ Status: {data.get('status')}, Has conversation data: {has_conversation_data}, Has message: {has_message}, Response keys: {list(data.keys())}",
                data
            )
        else:
            # Check if it's an authentication error
            is_auth_error = "401" in str(error) or "403" in str(error) or (isinstance(data, dict) and ("Not authenticated" in str(data.get("detail", ""))))
            
            self.log_test_result(
                "🎯 POST /api/ai-recruiter/start - Start AI recruiter conversation",
                False,
                f"❌ КРИТИЧЕСКАЯ ОШИБКА: AI recruiter start failed: {error}. Auth error: {is_auth_error}. This could be the source of 'Ошибка запуска AI рекрутера'",
                data
            )
        
        # 3. Test POST /api/ai-recruiter/continue - должен продолжать разговор с AI-рекрутером
        logger.info("Testing POST /api/ai-recruiter/continue...")
        
        # Use conversation data from start if available, otherwise use empty dict
        if not conversation_data:
            conversation_data = {"conversation_id": "test_conversation", "messages": []}
            logger.warning("⚠️ Using fallback conversation data for continue test")
        
        continue_data = {
            "user_message": "Я ищу работу разработчика в Берлине",
            "conversation_data": conversation_data
        }
        
        success, data, error = await self.make_request("POST", "/api/ai-recruiter/continue", json=continue_data)
        
        if success and isinstance(data, dict):
            has_status = "status" in data
            has_response = "response" in data or "ai_message" in data or "message" in data
            has_updated_conversation = "conversation_data" in data
            
            self.log_test_result(
                "🎯 POST /api/ai-recruiter/continue - Continue AI recruiter conversation",
                has_status and has_response,
                f"✅ Status: {data.get('status')}, Has response: {has_response}, Has updated conversation: {has_updated_conversation}, Response keys: {list(data.keys())}",
                data
            )
        else:
            # Check if it's an authentication error
            is_auth_error = "401" in str(error) or "403" in str(error) or (isinstance(data, dict) and ("Not authenticated" in str(data.get("detail", ""))))
            
            self.log_test_result(
                "🎯 POST /api/ai-recruiter/continue - Continue AI recruiter conversation",
                False,
                f"❌ AI recruiter continue failed: {error}. Auth error: {is_auth_error}",
                data
            )
    
    async def test_ai_recruiter_authentication_requirements(self):
        """🎯 КРИТИЧЕСКИЙ ТЕСТ: AI Recruiter Authentication Requirements"""
        logger.info("=== 🎯 КРИТИЧЕСКИЙ ТЕСТ: AI Recruiter Authentication Requirements ===")
        
        # Temporarily remove auth token to test authentication requirements
        original_token = self.auth_token
        self.auth_token = None
        
        # Test all AI recruiter endpoints without authentication
        ai_recruiter_endpoints = [
            ("GET", "/api/ai-recruiter/profile", "Get AI recruiter profile"),
            ("POST", "/api/ai-recruiter/start", "Start AI recruiter conversation"),
            ("POST", "/api/ai-recruiter/continue", "Continue AI recruiter conversation")
        ]
        
        for method, endpoint, description in ai_recruiter_endpoints:
            if method == "POST" and "start" in endpoint:
                test_data = {"user_language": "ru"}
                success, data, error = await self.make_request(method, endpoint, json=test_data)
            elif method == "POST" and "continue" in endpoint:
                test_data = {
                    "user_message": "test message",
                    "conversation_data": {"conversation_id": "test"}
                }
                success, data, error = await self.make_request(method, endpoint, json=test_data)
            else:
                success, data, error = await self.make_request(method, endpoint)
            
            # Should fail with 401 or 403 (authentication required)
            is_auth_required = not success and ("401" in str(error) or "403" in str(error) or (isinstance(data, dict) and ("Not authenticated" in str(data.get("detail", "")))))
            
            self.log_test_result(
                f"🎯 {method} {endpoint} - {description} (no auth)",
                is_auth_required,
                f"✅ Correctly requires authentication" if is_auth_required else f"❌ SECURITY ISSUE: Endpoint allows unauthorized access: {error}",
                data
            )
        
        # Restore auth token
        self.auth_token = original_token
    
    async def run_all_tests(self):
        """Run all AI recruiter tests"""
        logger.info("🎯 STARTING AI RECRUITER ENDPOINTS TESTING")
        logger.info("=" * 80)
        
        # Test sequence
        await self.test_telegram_authentication()
        await self.test_ai_recruiter_authentication_requirements()
        await self.test_ai_recruiter_endpoints()
        
        # Summary
        logger.info("=" * 80)
        logger.info("🎯 AI RECRUITER TESTING SUMMARY")
        logger.info("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        logger.info(f"📊 Total tests: {total_tests}")
        logger.info(f"✅ Passed: {passed_tests}")
        logger.info(f"❌ Failed: {failed_tests}")
        logger.info(f"📈 Success rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Critical findings
        logger.info("\n🔍 CRITICAL FINDINGS:")
        
        auth_test = next((r for r in self.test_results if "Telegram authentication for AI recruiter" in r["test"]), None)
        if auth_test and not auth_test["success"]:
            logger.error("❌ КРИТИЧЕСКАЯ ПРОБЛЕМА: Telegram authentication не работает - это может быть причиной 'Ошибка запуска AI рекрутера'")
        
        start_test = next((r for r in self.test_results if "Start AI recruiter conversation" in r["test"] and "no auth" not in r["test"]), None)
        if start_test and not start_test["success"]:
            logger.error("❌ КРИТИЧЕСКАЯ ПРОБЛЕМА: AI recruiter start endpoint не работает - это источник 'Ошибка запуска AI рекрутера'")
        
        profile_test = next((r for r in self.test_results if "Get user profile" in r["test"] and "no auth" not in r["test"]), None)
        if profile_test and not profile_test["success"]:
            logger.warning("⚠️ AI recruiter profile endpoint не работает")
        
        continue_test = next((r for r in self.test_results if "Continue AI recruiter conversation" in r["test"] and "no auth" not in r["test"]), None)
        if continue_test and not continue_test["success"]:
            logger.warning("⚠️ AI recruiter continue endpoint не работает")
        
        # Recommendations
        logger.info("\n💡 РЕКОМЕНДАЦИИ:")
        if failed_tests > 0:
            logger.info("1. Проверьте логи backend сервера для детальной диагностики ошибок")
            logger.info("2. Убедитесь что все AI recruiter endpoints правильно настроены в server.py")
            logger.info("3. Проверьте что advanced_ai_recruiter модуль корректно импортирован и инициализирован")
            logger.info("4. Убедитесь что аутентификация работает корректно")
        else:
            logger.info("✅ Все AI recruiter endpoints работают корректно!")
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": (passed_tests/total_tests)*100,
            "test_results": self.test_results
        }

async def main():
    """Main test runner"""
    async with AIRecruiterTester() as tester:
        results = await tester.run_all_tests()
        return results

if __name__ == "__main__":
    asyncio.run(main())
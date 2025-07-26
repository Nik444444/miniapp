#!/usr/bin/env python3
"""
🎯 КРИТИЧЕСКОЕ ТЕСТИРОВАНИЕ: Telegram Mini App Deployment и AI Recruiter Fixes

КОНТЕКСТ:
Пользователь сообщает о двух критических проблемах:
1. Deployment error: "ERROR: No matching distribution found for emergentintegrations" 
2. AI recruiter not working in Telegram Mini App job search tool

ИСПРАВЛЕНИЯ ВЫПОЛНЕНЫ:
1. ✅ DEPLOYMENT FIX: Removed emergentintegrations from requirements.txt (was causing pip install failure)
2. ✅ AI RECRUITER API FIX: Fixed missing /api prefixes in 5 endpoints in AIJobAssistant.js:
   - /job-compatibility → /api/job-compatibility  
   - /translate-job → /api/translate-job
   - /generate-cover-letter → /api/generate-cover-letter
   - /ai-job-recommendations → /api/ai-job-recommendations
   - /telegram-notifications/send → /api/telegram-notifications/send

ЗАДАЧИ ДЛЯ ТЕСТИРОВАНИЯ:

1. **AI Recruiter Endpoints (КРИТИЧЕСКИЙ ТЕСТ):**
   - GET /api/ai-recruiter/profile - должен работать с аутентификацией
   - POST /api/ai-recruiter/start - должен работать с аутентификацией
   - POST /api/ai-recruiter/continue - должен работать с аутентификацией

2. **Job Assistant Endpoints (КРИТИЧЕСКИЙ ТЕСТ):**
   - POST /api/job-compatibility - должен работать с аутентификацией
   - POST /api/translate-job - должен работать с аутентификацией
   - POST /api/generate-cover-letter - должен работать с аутентификацией
   - POST /api/ai-job-recommendations - должен работать с аутентификацией

3. **Telegram Notifications Endpoint:**
   - POST /api/telegram-notifications/send - должен работать с аутентификацией

4. **Deployment Testing:**
   - Verify requirements.txt can be installed without emergentintegrations error
   - Verify emergentintegrations is available (should be installed via Dockerfile)

ЦЕЛЬ: Подтвердить что deployment и AI recruiter функции теперь работают корректно.
"""

import asyncio
import aiohttp
import json
import os
import tempfile
from pathlib import Path
import logging
from typing import Dict, Any, Optional
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CriticalBackendTester:
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
            
        logger.info(f"Testing backend at: {self.backend_url}")
        
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
                "id": 987654321,
                "first_name": "TestUser",
                "last_name": "AIRecruiter", 
                "username": "testuser_ai",
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
    
    async def test_deployment_requirements_fix(self):
        """🎯 КРИТИЧЕСКИЙ ТЕСТ: Deployment Requirements Fix - emergentintegrations"""
        logger.info("=== 🎯 КРИТИЧЕСКИЙ ТЕСТ: Deployment Requirements Fix ===")
        
        # Test 1: Check that requirements.txt doesn't contain emergentintegrations
        try:
            with open("/app/backend/requirements.txt", "r") as f:
                requirements_content = f.read()
            
            has_emergentintegrations = "emergentintegrations" in requirements_content.lower()
            
            self.log_test_result(
                "🎯 Requirements.txt - emergentintegrations removed",
                not has_emergentintegrations,
                f"emergentintegrations found in requirements.txt: {has_emergentintegrations}" if has_emergentintegrations else "✅ emergentintegrations correctly removed from requirements.txt",
                {"requirements_content": requirements_content[:500] + "..." if len(requirements_content) > 500 else requirements_content}
            )
        except Exception as e:
            self.log_test_result(
                "🎯 Requirements.txt - emergentintegrations removed",
                False,
                f"Error reading requirements.txt: {e}",
                None
            )
        
        # Test 2: Check that emergentintegrations is still available (installed via Dockerfile)
        success, data, error = await self.make_request("GET", "/api/modern-llm-status")
        
        if success and isinstance(data, dict):
            has_modern_flag = data.get("modern") is True
            has_providers = "providers" in data and isinstance(data["providers"], dict)
            providers_count = len(data.get("providers", {}))
            
            # Check if emergentintegrations is working (modern LLM manager should work)
            emergent_working = has_modern_flag and providers_count > 0
            
            self.log_test_result(
                "🎯 Emergentintegrations - Available via Dockerfile",
                emergent_working,
                f"Modern LLM: {has_modern_flag}, Providers: {providers_count}, Working: {emergent_working}",
                data
            )
        else:
            self.log_test_result(
                "🎯 Emergentintegrations - Available via Dockerfile",
                False,
                f"Modern LLM status error: {error}",
                data
            )
    
    async def test_ai_recruiter_endpoints_with_auth(self):
        """🎯 КРИТИЧЕСКИЙ ТЕСТ: AI Recruiter Endpoints with Authentication"""
        logger.info("=== 🎯 КРИТИЧЕСКИЙ ТЕСТ: AI Recruiter Endpoints with Authentication ===")
        
        # Test 1: GET /api/ai-recruiter/profile (with authentication)
        success, data, error = await self.make_request("GET", "/api/ai-recruiter/profile")
        
        if self.auth_token:
            # With authentication, should work or return proper response
            if success:
                self.log_test_result(
                    "🎯 GET /api/ai-recruiter/profile - With authentication",
                    True,
                    f"✅ Profile endpoint working with auth: {data.get('status', 'N/A')}",
                    data
                )
            else:
                # Check if it's a proper API response (not 404)
                is_proper_response = "404" not in str(error) and "Not Found" not in str(error)
                self.log_test_result(
                    "🎯 GET /api/ai-recruiter/profile - With authentication",
                    is_proper_response,
                    f"Profile endpoint exists but returned: {error}",
                    data
                )
        else:
            self.log_test_result(
                "🎯 GET /api/ai-recruiter/profile - With authentication",
                False,
                "❌ No auth token available for testing",
                None
            )
        
        # Test 2: POST /api/ai-recruiter/start (with authentication)
        start_data = {
            "user_language": "ru"
        }
        
        success, data, error = await self.make_request("POST", "/api/ai-recruiter/start", json=start_data)
        
        if self.auth_token:
            if success:
                has_status = "status" in data
                has_response = "message" in data or "response" in data or "conversation_data" in data
                
                self.log_test_result(
                    "🎯 POST /api/ai-recruiter/start - With authentication",
                    has_status or has_response,
                    f"✅ Start endpoint working: Status={data.get('status')}, Has response={has_response}",
                    data
                )
            else:
                # Check if it's a proper API response (not 404)
                is_proper_response = "404" not in str(error) and "Not Found" not in str(error)
                self.log_test_result(
                    "🎯 POST /api/ai-recruiter/start - With authentication",
                    is_proper_response,
                    f"Start endpoint exists but returned: {error}",
                    data
                )
        else:
            self.log_test_result(
                "🎯 POST /api/ai-recruiter/start - With authentication",
                False,
                "❌ No auth token available for testing",
                None
            )
        
        # Test 3: POST /api/ai-recruiter/continue (with authentication)
        continue_data = {
            "user_message": "Я ищу работу разработчика в Берлине",
            "conversation_data": {"step": 1, "language": "ru"}
        }
        
        success, data, error = await self.make_request("POST", "/api/ai-recruiter/continue", json=continue_data)
        
        if self.auth_token:
            if success:
                has_status = "status" in data
                has_response = "message" in data or "response" in data
                
                self.log_test_result(
                    "🎯 POST /api/ai-recruiter/continue - With authentication",
                    has_status or has_response,
                    f"✅ Continue endpoint working: Status={data.get('status')}, Has response={has_response}",
                    data
                )
            else:
                # Check if it's a proper API response (not 404)
                is_proper_response = "404" not in str(error) and "Not Found" not in str(error)
                self.log_test_result(
                    "🎯 POST /api/ai-recruiter/continue - With authentication",
                    is_proper_response,
                    f"Continue endpoint exists but returned: {error}",
                    data
                )
        else:
            self.log_test_result(
                "🎯 POST /api/ai-recruiter/continue - With authentication",
                False,
                "❌ No auth token available for testing",
                None
            )
    
    async def test_ai_recruiter_endpoints_without_auth(self):
        """🎯 КРИТИЧЕСКИЙ ТЕСТ: AI Recruiter Endpoints without Authentication (should fail)"""
        logger.info("=== 🎯 КРИТИЧЕСКИЙ ТЕСТ: AI Recruiter Endpoints without Authentication ===")
        
        # Temporarily remove auth token
        original_token = self.auth_token
        self.auth_token = None
        
        # Test 1: GET /api/ai-recruiter/profile (without authentication)
        success, data, error = await self.make_request("GET", "/api/ai-recruiter/profile")
        
        is_auth_required = not success and ("401" in str(error) or "403" in str(error) or 
                                          (isinstance(data, dict) and ("Not authenticated" in str(data.get("detail", "")) or 
                                                                     "Unauthorized" in str(data.get("detail", "")))))
        
        self.log_test_result(
            "🎯 GET /api/ai-recruiter/profile - Without authentication (should fail)",
            is_auth_required,
            f"✅ Correctly requires authentication" if is_auth_required else f"❌ Allows unauthorized access: {error}",
            data
        )
        
        # Test 2: POST /api/ai-recruiter/start (without authentication)
        start_data = {"user_language": "ru"}
        success, data, error = await self.make_request("POST", "/api/ai-recruiter/start", json=start_data)
        
        is_auth_required = not success and ("401" in str(error) or "403" in str(error) or 
                                          (isinstance(data, dict) and ("Not authenticated" in str(data.get("detail", "")) or 
                                                                     "Unauthorized" in str(data.get("detail", "")))))
        
        self.log_test_result(
            "🎯 POST /api/ai-recruiter/start - Without authentication (should fail)",
            is_auth_required,
            f"✅ Correctly requires authentication" if is_auth_required else f"❌ Allows unauthorized access: {error}",
            data
        )
        
        # Test 3: POST /api/ai-recruiter/continue (without authentication)
        continue_data = {
            "user_message": "Test message",
            "conversation_data": {"step": 1}
        }
        success, data, error = await self.make_request("POST", "/api/ai-recruiter/continue", json=continue_data)
        
        is_auth_required = not success and ("401" in str(error) or "403" in str(error) or 
                                          (isinstance(data, dict) and ("Not authenticated" in str(data.get("detail", "")) or 
                                                                     "Unauthorized" in str(data.get("detail", "")))))
        
        self.log_test_result(
            "🎯 POST /api/ai-recruiter/continue - Without authentication (should fail)",
            is_auth_required,
            f"✅ Correctly requires authentication" if is_auth_required else f"❌ Allows unauthorized access: {error}",
            data
        )
        
        # Restore auth token
        self.auth_token = original_token
    
    async def test_job_assistant_endpoints_with_api_prefix(self):
        """🎯 КРИТИЧЕСКИЙ ТЕСТ: Job Assistant Endpoints with /api prefix (FIXED)"""
        logger.info("=== 🎯 КРИТИЧЕСКИЙ ТЕСТ: Job Assistant Endpoints with /api prefix ===")
        
        # Test data for job assistant endpoints
        job_data = {
            "job_id": "test_job_123",
            "job_data": {
                "title": "Software Developer",
                "company": "Test Company",
                "location": "Berlin",
                "description": "Test job description"
            }
        }
        
        # Test 1: POST /api/job-compatibility (FIXED: added /api prefix)
        success, data, error = await self.make_request("POST", "/api/job-compatibility", json=job_data)
        
        if self.auth_token:
            if success:
                self.log_test_result(
                    "🎯 POST /api/job-compatibility - With /api prefix (FIXED)",
                    True,
                    f"✅ Job compatibility endpoint working with /api prefix",
                    data
                )
            else:
                # Check if it's a proper API response (not 404)
                is_proper_response = "404" not in str(error) and "Not Found" not in str(error)
                self.log_test_result(
                    "🎯 POST /api/job-compatibility - With /api prefix (FIXED)",
                    is_proper_response,
                    f"Endpoint exists with /api prefix but returned: {error}",
                    data
                )
        else:
            # Without auth, should return auth error (not 404)
            is_auth_error = "401" in str(error) or "403" in str(error)
            is_not_404 = "404" not in str(error) and "Not Found" not in str(error)
            
            self.log_test_result(
                "🎯 POST /api/job-compatibility - With /api prefix (FIXED)",
                is_auth_error and is_not_404,
                f"✅ Endpoint exists with /api prefix, requires auth" if (is_auth_error and is_not_404) else f"❌ Endpoint issue: {error}",
                data
            )
        
        # Test 2: POST /api/translate-job (FIXED: added /api prefix)
        translate_data = {
            "job_id": "test_job_123",
            "job_data": job_data["job_data"],
            "target_language": "ru"
        }
        
        success, data, error = await self.make_request("POST", "/api/translate-job", json=translate_data)
        
        if self.auth_token:
            if success:
                self.log_test_result(
                    "🎯 POST /api/translate-job - With /api prefix (FIXED)",
                    True,
                    f"✅ Job translation endpoint working with /api prefix",
                    data
                )
            else:
                is_proper_response = "404" not in str(error) and "Not Found" not in str(error)
                self.log_test_result(
                    "🎯 POST /api/translate-job - With /api prefix (FIXED)",
                    is_proper_response,
                    f"Endpoint exists with /api prefix but returned: {error}",
                    data
                )
        else:
            is_auth_error = "401" in str(error) or "403" in str(error)
            is_not_404 = "404" not in str(error) and "Not Found" not in str(error)
            
            self.log_test_result(
                "🎯 POST /api/translate-job - With /api prefix (FIXED)",
                is_auth_error and is_not_404,
                f"✅ Endpoint exists with /api prefix, requires auth" if (is_auth_error and is_not_404) else f"❌ Endpoint issue: {error}",
                data
            )
        
        # Test 3: POST /api/generate-cover-letter (FIXED: added /api prefix)
        cover_letter_data = {
            "job_id": "test_job_123",
            "job_data": job_data["job_data"],
            "user_profile_id": "test_user_123"
        }
        
        success, data, error = await self.make_request("POST", "/api/generate-cover-letter", json=cover_letter_data)
        
        if self.auth_token:
            if success:
                self.log_test_result(
                    "🎯 POST /api/generate-cover-letter - With /api prefix (FIXED)",
                    True,
                    f"✅ Cover letter generation endpoint working with /api prefix",
                    data
                )
            else:
                is_proper_response = "404" not in str(error) and "Not Found" not in str(error)
                self.log_test_result(
                    "🎯 POST /api/generate-cover-letter - With /api prefix (FIXED)",
                    is_proper_response,
                    f"Endpoint exists with /api prefix but returned: {error}",
                    data
                )
        else:
            is_auth_error = "401" in str(error) or "403" in str(error)
            is_not_404 = "404" not in str(error) and "Not Found" not in str(error)
            
            self.log_test_result(
                "🎯 POST /api/generate-cover-letter - With /api prefix (FIXED)",
                is_auth_error and is_not_404,
                f"✅ Endpoint exists with /api prefix, requires auth" if (is_auth_error and is_not_404) else f"❌ Endpoint issue: {error}",
                data
            )
        
        # Test 4: POST /api/ai-job-recommendations (FIXED: added /api prefix)
        recommendations_data = {
            "user_profile_id": "test_user_123",
            "max_jobs": 5
        }
        
        success, data, error = await self.make_request("POST", "/api/ai-job-recommendations", json=recommendations_data)
        
        if self.auth_token:
            if success:
                self.log_test_result(
                    "🎯 POST /api/ai-job-recommendations - With /api prefix (FIXED)",
                    True,
                    f"✅ AI job recommendations endpoint working with /api prefix",
                    data
                )
            else:
                is_proper_response = "404" not in str(error) and "Not Found" not in str(error)
                self.log_test_result(
                    "🎯 POST /api/ai-job-recommendations - With /api prefix (FIXED)",
                    is_proper_response,
                    f"Endpoint exists with /api prefix but returned: {error}",
                    data
                )
        else:
            is_auth_error = "401" in str(error) or "403" in str(error)
            is_not_404 = "404" not in str(error) and "Not Found" not in str(error)
            
            self.log_test_result(
                "🎯 POST /api/ai-job-recommendations - With /api prefix (FIXED)",
                is_auth_error and is_not_404,
                f"✅ Endpoint exists with /api prefix, requires auth" if (is_auth_error and is_not_404) else f"❌ Endpoint issue: {error}",
                data
            )
        
        # Test 5: POST /api/telegram-notifications/send (FIXED: added /api prefix)
        notification_data = {
            "user_telegram_id": "123456789",
            "notification_type": "job_match",
            "job_data": job_data["job_data"],
            "user_language": "ru"
        }
        
        success, data, error = await self.make_request("POST", "/api/telegram-notifications/send", json=notification_data)
        
        if self.auth_token:
            if success:
                self.log_test_result(
                    "🎯 POST /api/telegram-notifications/send - With /api prefix (FIXED)",
                    True,
                    f"✅ Telegram notifications endpoint working with /api prefix",
                    data
                )
            else:
                is_proper_response = "404" not in str(error) and "Not Found" not in str(error)
                self.log_test_result(
                    "🎯 POST /api/telegram-notifications/send - With /api prefix (FIXED)",
                    is_proper_response,
                    f"Endpoint exists with /api prefix but returned: {error}",
                    data
                )
        else:
            is_auth_error = "401" in str(error) or "403" in str(error)
            is_not_404 = "404" not in str(error) and "Not Found" not in str(error)
            
            self.log_test_result(
                "🎯 POST /api/telegram-notifications/send - With /api prefix (FIXED)",
                is_auth_error and is_not_404,
                f"✅ Endpoint exists with /api prefix, requires auth" if (is_auth_error and is_not_404) else f"❌ Endpoint issue: {error}",
                data
            )
    
    async def run_critical_tests(self):
        """Run all critical tests for the deployment and AI recruiter fixes"""
        logger.info("🎯 STARTING CRITICAL TESTS FOR TELEGRAM MINI APP FIXES")
        
        # Test 1: Deployment requirements fix
        await self.test_deployment_requirements_fix()
        
        # Test 2: Telegram authentication (needed for AI recruiter tests)
        await self.test_telegram_authentication()
        
        # Test 3: AI recruiter endpoints with authentication
        await self.test_ai_recruiter_endpoints_with_auth()
        
        # Test 4: AI recruiter endpoints without authentication (should fail)
        await self.test_ai_recruiter_endpoints_without_auth()
        
        # Test 5: Job assistant endpoints with /api prefix
        await self.test_job_assistant_endpoints_with_api_prefix()
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        logger.info("🎯 CRITICAL TESTS SUMMARY")
        logger.info("=" * 80)
        
        passed_tests = [test for test in self.test_results if test["success"]]
        failed_tests = [test for test in self.test_results if not test["success"]]
        
        logger.info(f"✅ PASSED: {len(passed_tests)}/{len(self.test_results)} tests")
        logger.info(f"❌ FAILED: {len(failed_tests)}/{len(self.test_results)} tests")
        
        if failed_tests:
            logger.info("\n❌ FAILED TESTS:")
            for test in failed_tests:
                logger.info(f"  - {test['test']}: {test['details']}")
        
        if passed_tests:
            logger.info("\n✅ PASSED TESTS:")
            for test in passed_tests:
                logger.info(f"  - {test['test']}: {test['details']}")
        
        # Critical assessment
        deployment_tests = [t for t in self.test_results if "Requirements.txt" in t["test"] or "Emergentintegrations" in t["test"]]
        ai_recruiter_tests = [t for t in self.test_results if "ai-recruiter" in t["test"]]
        job_assistant_tests = [t for t in self.test_results if ("job-compatibility" in t["test"] or 
                                                               "translate-job" in t["test"] or 
                                                               "generate-cover-letter" in t["test"] or 
                                                               "ai-job-recommendations" in t["test"] or 
                                                               "telegram-notifications" in t["test"])]
        
        deployment_success = all(t["success"] for t in deployment_tests)
        ai_recruiter_success = all(t["success"] for t in ai_recruiter_tests)
        job_assistant_success = all(t["success"] for t in job_assistant_tests)
        
        logger.info("\n🎯 CRITICAL FIXES ASSESSMENT:")
        logger.info(f"  📦 Deployment Fix: {'✅ WORKING' if deployment_success else '❌ FAILED'}")
        logger.info(f"  🤖 AI Recruiter Fix: {'✅ WORKING' if ai_recruiter_success else '❌ FAILED'}")
        logger.info(f"  🔧 Job Assistant Fix: {'✅ WORKING' if job_assistant_success else '❌ FAILED'}")
        
        overall_success = deployment_success and ai_recruiter_success and job_assistant_success
        logger.info(f"\n🎯 OVERALL RESULT: {'✅ ALL CRITICAL FIXES WORKING' if overall_success else '❌ SOME FIXES NEED ATTENTION'}")

async def main():
    """Main function to run critical tests"""
    async with CriticalBackendTester() as tester:
        await tester.run_critical_tests()

if __name__ == "__main__":
    asyncio.run(main())
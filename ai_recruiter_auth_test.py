#!/usr/bin/env python3
"""
🎯 AI RECRUITER AUTHENTICATION TESTING: Telegram Mini App

КОНТЕКСТ:
Test AI recruiter endpoints authentication requirements specifically for the review request.
This test focuses on verifying that all AI recruiter endpoints properly require authentication
and return 403/401 errors when accessed without proper authorization.

КРИТИЧЕСКИЕ ТЕСТЫ:
1. GET /api/ai-recruiter/profile - должен возвращать 403/401 без авторизации
2. POST /api/ai-recruiter/start - должен возвращать 403/401 без авторизации  
3. POST /api/ai-recruiter/continue - должен возвращать 403/401 без авторизации

ВАЖНО:
- Endpoints должны быть с префиксом /api (критично для Kubernetes ingress)
- Без префикса /api должны возвращать 404
- Все endpoints должны требовать авторизацию

Backend URL: https://miniapp-wvsxfa.fly.dev
"""

import asyncio
import aiohttp
import json
import logging
from pathlib import Path
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AIRecruiterAuthTester:
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
            
        logger.info(f"Testing AI recruiter endpoints at: {self.backend_url}")
        
        self.session = None
        self.test_results = []
        
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
    
    async def test_ai_recruiter_profile_auth(self):
        """Test GET /api/ai-recruiter/profile authentication requirement"""
        logger.info("=== Testing GET /api/ai-recruiter/profile Authentication ===")
        
        success, data, error = await self.make_request("GET", "/api/ai-recruiter/profile")
        
        # Should fail with 401 or 403 (authentication required)
        is_auth_required = not success and ("401" in str(error) or "403" in str(error) or (isinstance(data, dict) and ("Not authenticated" in str(data.get("detail", "")) or "401" in str(data) or "403" in str(data))))
        
        self.log_test_result(
            "GET /api/ai-recruiter/profile - Authentication required",
            is_auth_required,
            f"Correctly requires authentication (401/403)" if is_auth_required else f"Unexpected response: {error}",
            data
        )
        
        return is_auth_required
    
    async def test_ai_recruiter_start_auth(self):
        """Test POST /api/ai-recruiter/start authentication requirement"""
        logger.info("=== Testing POST /api/ai-recruiter/start Authentication ===")
        
        start_data = {
            "user_language": "ru"
        }
        
        success, data, error = await self.make_request("POST", "/api/ai-recruiter/start", json=start_data)
        
        # Should fail with 401 or 403 (authentication required)
        is_auth_required = not success and ("401" in str(error) or "403" in str(error) or (isinstance(data, dict) and ("Not authenticated" in str(data.get("detail", "")) or "401" in str(data) or "403" in str(data))))
        
        self.log_test_result(
            "POST /api/ai-recruiter/start - Authentication required",
            is_auth_required,
            f"Correctly requires authentication (401/403)" if is_auth_required else f"Unexpected response: {error}",
            data
        )
        
        return is_auth_required
    
    async def test_ai_recruiter_continue_auth(self):
        """Test POST /api/ai-recruiter/continue authentication requirement"""
        logger.info("=== Testing POST /api/ai-recruiter/continue Authentication ===")
        
        continue_data = {
            "user_message": "Я ищу работу разработчика в Берлине",
            "conversation_data": {"test": "data"}
        }
        
        success, data, error = await self.make_request("POST", "/api/ai-recruiter/continue", json=continue_data)
        
        # Should fail with 401 or 403 (authentication required)
        is_auth_required = not success and ("401" in str(error) or "403" in str(error) or (isinstance(data, dict) and ("Not authenticated" in str(data.get("detail", "")) or "401" in str(data) or "403" in str(data))))
        
        self.log_test_result(
            "POST /api/ai-recruiter/continue - Authentication required",
            is_auth_required,
            f"Correctly requires authentication (401/403)" if is_auth_required else f"Unexpected response: {error}",
            data
        )
        
        return is_auth_required
    
    async def test_api_prefix_requirement(self):
        """Test that endpoints require /api prefix (critical for Kubernetes ingress)"""
        logger.info("=== Testing /api Prefix Requirement ===")
        
        # Test that endpoints without /api prefix return 404
        success_no_prefix, data_no_prefix, error_no_prefix = await self.make_request("GET", "/ai-recruiter/profile")
        
        # Should fail with 404 (not found) because correct endpoint is /api/ai-recruiter/profile
        is_404_without_prefix = not success_no_prefix and ("404" in str(error_no_prefix) or (isinstance(data_no_prefix, dict) and "404" in str(data_no_prefix)))
        
        self.log_test_result(
            "GET /ai-recruiter/profile (without /api prefix) - Should return 404",
            is_404_without_prefix,
            f"Correctly returns 404 without /api prefix" if is_404_without_prefix else f"Unexpected response: {error_no_prefix}",
            data_no_prefix
        )
        
        return is_404_without_prefix
    
    async def run_all_tests(self):
        """Run all AI recruiter authentication tests"""
        logger.info("🎯 STARTING AI RECRUITER AUTHENTICATION TESTS")
        logger.info("=" * 60)
        
        # Run all tests
        profile_auth = await self.test_ai_recruiter_profile_auth()
        start_auth = await self.test_ai_recruiter_start_auth()
        continue_auth = await self.test_ai_recruiter_continue_auth()
        api_prefix = await self.test_api_prefix_requirement()
        
        # Summary
        logger.info("=" * 60)
        logger.info("🎯 AI RECRUITER AUTHENTICATION TEST SUMMARY")
        logger.info("=" * 60)
        
        all_passed = profile_auth and start_auth and continue_auth and api_prefix
        
        logger.info(f"✅ GET /api/ai-recruiter/profile requires auth: {profile_auth}")
        logger.info(f"✅ POST /api/ai-recruiter/start requires auth: {start_auth}")
        logger.info(f"✅ POST /api/ai-recruiter/continue requires auth: {continue_auth}")
        logger.info(f"✅ /api prefix requirement working: {api_prefix}")
        
        logger.info("=" * 60)
        if all_passed:
            logger.info("🎉 ALL TESTS PASSED - AI Recruiter endpoints correctly configured!")
            logger.info("✅ All endpoints require authentication (401/403)")
            logger.info("✅ All endpoints use /api prefix for Kubernetes ingress")
        else:
            logger.info("❌ SOME TESTS FAILED - Check authentication configuration!")
            
        logger.info("=" * 60)
        
        return all_passed

async def main():
    """Main test runner"""
    async with AIRecruiterAuthTester() as tester:
        success = await tester.run_all_tests()
        return success

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
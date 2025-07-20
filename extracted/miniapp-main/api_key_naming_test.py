#!/usr/bin/env python3
"""
Specific test for API key naming changes
Tests if backend supports new API key names (api_key_1, api_key_2, api_key_3)
vs old names (gemini_api_key, openai_api_key, anthropic_api_key)
"""

import asyncio
import aiohttp
import json
import os
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ApiKeyNamingTester:
    def __init__(self):
        # Get backend URL from frontend .env file
        frontend_env_path = Path("/app/frontend/.env")
        self.backend_url = "https://german-letterai-assistant.onrender.com"  # Use production URL
        
        if frontend_env_path.exists():
            with open(frontend_env_path, 'r') as f:
                for line in f:
                    if line.startswith('REACT_APP_BACKEND_URL='):
                        self.backend_url = line.split('=', 1)[1].strip()
                        break
        
        logger.info(f"Testing API key naming at: {self.backend_url}")
        self.session = None
        self.test_results = []
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def log_test_result(self, test_name: str, success: bool, details: str = "", response_data: any = None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"{status} - {test_name}: {details}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "response_data": response_data
        })
    
    async def make_request(self, method: str, endpoint: str, **kwargs) -> tuple[bool, any, str]:
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
    
    async def test_old_api_key_names(self):
        """Test if backend still accepts old API key names"""
        logger.info("=== Testing Old API Key Names ===")
        
        # Test with old naming convention (without auth - should fail with auth error, not validation error)
        old_api_keys = {
            "gemini_api_key": "test_gemini_key",
            "openai_api_key": "test_openai_key", 
            "anthropic_api_key": "test_anthropic_key"
        }
        
        success, data, error = await self.make_request("POST", "/api/api-keys", json=old_api_keys)
        
        # Should fail with authentication error (401/403), not validation error (422)
        is_auth_error = not success and ("401" in str(error) or "403" in str(error) or (isinstance(data, dict) and ("Not authenticated" in str(data.get("detail", "")))))
        is_validation_error = "422" in str(error) or (isinstance(data, dict) and "validation" in str(data).lower())
        
        # If it's auth error, the endpoint accepts the field names
        # If it's validation error, the endpoint doesn't recognize the field names
        accepts_old_names = is_auth_error and not is_validation_error
        
        self.log_test_result(
            "POST /api/api-keys - Old API key names (gemini_api_key, openai_api_key, anthropic_api_key)",
            accepts_old_names,
            f"Auth error: {is_auth_error}, Validation error: {is_validation_error}, Accepts old names: {accepts_old_names}",
            data
        )
        
        return accepts_old_names
    
    async def test_new_api_key_names(self):
        """Test if backend accepts new API key names"""
        logger.info("=== Testing New API Key Names ===")
        
        # Test with new naming convention (without auth - should fail with auth error, not validation error)
        new_api_keys = {
            "api_key_1": "test_api_key_1",
            "api_key_2": "test_api_key_2",
            "api_key_3": "test_api_key_3"
        }
        
        success, data, error = await self.make_request("POST", "/api/api-keys", json=new_api_keys)
        
        # Should fail with authentication error (401/403), not validation error (422)
        is_auth_error = not success and ("401" in str(error) or "403" in str(error) or (isinstance(data, dict) and ("Not authenticated" in str(data.get("detail", "")))))
        is_validation_error = "422" in str(error) or (isinstance(data, dict) and "validation" in str(data).lower())
        
        # If it's auth error, the endpoint accepts the field names
        # If it's validation error, the endpoint doesn't recognize the field names
        accepts_new_names = is_auth_error and not is_validation_error
        
        self.log_test_result(
            "POST /api/api-keys - New API key names (api_key_1, api_key_2, api_key_3)",
            accepts_new_names,
            f"Auth error: {is_auth_error}, Validation error: {is_validation_error}, Accepts new names: {accepts_new_names}",
            data
        )
        
        return accepts_new_names
    
    async def test_mixed_api_key_names(self):
        """Test if backend handles mixed old and new API key names"""
        logger.info("=== Testing Mixed API Key Names ===")
        
        # Test with mixed naming convention
        mixed_api_keys = {
            "gemini_api_key": "test_gemini_key",  # Old name
            "api_key_2": "test_api_key_2",        # New name
            "anthropic_api_key": "test_anthropic_key"  # Old name
        }
        
        success, data, error = await self.make_request("POST", "/api/api-keys", json=mixed_api_keys)
        
        # Should fail with authentication error (401/403), not validation error (422)
        is_auth_error = not success and ("401" in str(error) or "403" in str(error) or (isinstance(data, dict) and ("Not authenticated" in str(data.get("detail", "")))))
        is_validation_error = "422" in str(error) or (isinstance(data, dict) and "validation" in str(data).lower())
        
        # If it's auth error, the endpoint accepts the field names
        # If it's validation error, the endpoint doesn't recognize some field names
        handles_mixed_names = is_auth_error and not is_validation_error
        
        self.log_test_result(
            "POST /api/api-keys - Mixed API key names (old + new)",
            handles_mixed_names,
            f"Auth error: {is_auth_error}, Validation error: {is_validation_error}, Handles mixed: {handles_mixed_names}",
            data
        )
        
        return handles_mixed_names
    
    async def check_backend_model_structure(self):
        """Check what API key fields the backend model expects"""
        logger.info("=== Checking Backend Model Structure ===")
        
        # Test with completely invalid field names to see validation response
        invalid_api_keys = {
            "invalid_field_1": "test_value_1",
            "invalid_field_2": "test_value_2"
        }
        
        success, data, error = await self.make_request("POST", "/api/api-keys", json=invalid_api_keys)
        
        # Should fail with authentication error (401/403) if endpoint exists and accepts any JSON
        # Or validation error (422) if it validates field names
        is_auth_error = not success and ("401" in str(error) or "403" in str(error) or (isinstance(data, dict) and ("Not authenticated" in str(data.get("detail", "")))))
        is_validation_error = "422" in str(error) or (isinstance(data, dict) and "validation" in str(data).lower())
        
        self.log_test_result(
            "POST /api/api-keys - Invalid field names test",
            is_auth_error or is_validation_error,
            f"Auth error: {is_auth_error}, Validation error: {is_validation_error}",
            data
        )
        
        # Test with empty JSON
        success, data, error = await self.make_request("POST", "/api/api-keys", json={})
        
        is_auth_error_empty = not success and ("401" in str(error) or "403" in str(error) or (isinstance(data, dict) and ("Not authenticated" in str(data.get("detail", "")))))
        
        self.log_test_result(
            "POST /api/api-keys - Empty JSON test",
            is_auth_error_empty,
            f"Auth error with empty JSON: {is_auth_error_empty}",
            data
        )
    
    async def run_all_tests(self):
        """Run all API key naming tests"""
        logger.info("🔑 Starting API key naming tests...")
        
        try:
            old_names_supported = await self.test_old_api_key_names()
            new_names_supported = await self.test_new_api_key_names()
            mixed_names_supported = await self.test_mixed_api_key_names()
            await self.check_backend_model_structure()
            
            # Analysis
            logger.info("\n📊 API KEY NAMING ANALYSIS:")
            logger.info(f"Old names (gemini_api_key, etc.) supported: {old_names_supported}")
            logger.info(f"New names (api_key_1, etc.) supported: {new_names_supported}")
            logger.info(f"Mixed names supported: {mixed_names_supported}")
            
            if old_names_supported and not new_names_supported:
                logger.warning("⚠️  ISSUE: Backend only supports OLD API key names, but frontend may be sending NEW names!")
            elif new_names_supported and not old_names_supported:
                logger.info("✅ Backend supports NEW API key names only")
            elif old_names_supported and new_names_supported:
                logger.info("✅ Backend supports BOTH old and new API key names")
            else:
                logger.error("❌ Backend doesn't seem to support either naming convention properly")
            
        except Exception as e:
            logger.error(f"Test execution error: {e}")
            self.log_test_result("API key naming tests", False, f"Critical error: {e}")
    
    def print_summary(self):
        """Print test summary"""
        logger.info("\n" + "="*60)
        logger.info("📊 API KEY NAMING TEST SUMMARY")
        logger.info("="*60)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        logger.info(f"Total Tests: {total}")
        logger.info(f"Passed: {passed}")
        logger.info(f"Failed: {total - passed}")
        logger.info(f"Success Rate: {(passed/total*100):.1f}%" if total > 0 else "0%")
        
        logger.info("\n📋 DETAILED RESULTS:")
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            logger.info(f"{status} {result['test']}: {result['details']}")
        
        logger.info("="*60)
        
        return passed, total

async def main():
    """Main test execution"""
    async with ApiKeyNamingTester() as tester:
        await tester.run_all_tests()
        passed, total = tester.print_summary()
        
        return 0 if passed == total else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
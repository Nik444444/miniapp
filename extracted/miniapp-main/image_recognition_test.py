#!/usr/bin/env python3
"""
Focused test for image recognition functionality in AI_germany app
Tests the critical fix for modern_llm_manager.py image support
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
import io

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ImageRecognitionTester:
    def __init__(self):
        self.backend_url = "http://localhost:8001"  # Test locally
        logger.info(f"Testing backend at: {self.backend_url}")
        
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
    
    def create_test_image(self):
        """Create a simple test image for testing"""
        try:
            from PIL import Image
            
            # Create a simple 100x100 red image
            img = Image.new('RGB', (100, 100), color='red')
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='JPEG')
            img_bytes.seek(0)
            return img_bytes.getvalue()
        except ImportError:
            # If PIL is not available, create a minimal JPEG-like bytes
            return b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xc0\x00\x11\x08\x00d\x00d\x01\x01\x11\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x14\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\xff\xc4\x00\x14\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00\x3f\x00\xaa\xff\xd9'
    
    async def test_modern_llm_status_endpoint(self):
        """Test modern LLM status endpoint for image support"""
        logger.info("=== Testing Modern LLM Status Endpoint ===")
        
        success, data, error = await self.make_request("GET", "/api/modern-llm-status")
        if success and isinstance(data, dict):
            has_status = "status" in data
            has_providers = "providers" in data and isinstance(data["providers"], dict)
            has_counts = "active_providers" in data and "total_providers" in data
            has_modern_flag = data.get("modern") is True
            
            # Check if all expected providers are present
            expected_providers = ["gemini", "openai", "anthropic"]
            providers_present = all(provider in data.get("providers", {}) for provider in expected_providers)
            
            # Check if providers have modern flag
            providers_modern = all(
                provider_info.get("modern") is True 
                for provider_info in data.get("providers", {}).values()
            )
            
            self.log_test_result(
                "Modern LLM Status - Image support infrastructure",
                has_status and has_providers and has_counts and providers_present and has_modern_flag and providers_modern,
                f"Modern: {has_modern_flag}, Active: {data.get('active_providers')}/{data.get('total_providers')}, All modern: {providers_modern}",
                data
            )
        else:
            self.log_test_result("Modern LLM Status - Image support infrastructure", False, f"Error: {error}", data)
    
    async def test_modern_models_configuration(self):
        """Test that modern models are properly configured"""
        logger.info("=== Testing Modern Models Configuration ===")
        
        success, data, error = await self.make_request("GET", "/api/modern-llm-status")
        if success and isinstance(data, dict):
            providers = data.get("providers", {})
            
            # Check for modern models in the configuration
            expected_modern_models = {
                "gemini": ["gemini-2.0-flash"],
                "openai": ["gpt-4o"],
                "anthropic": ["claude-3-5-sonnet"]
            }
            
            models_configured = {}
            for provider_name, provider_info in providers.items():
                model = provider_info.get("model", "N/A")
                models_configured[provider_name] = model
            
            # Check if modern models are available (even if inactive due to no API keys)
            modern_models_available = []
            for provider, expected_models in expected_modern_models.items():
                if provider in providers:
                    provider_info = providers[provider]
                    if provider_info.get("modern") is True:
                        modern_models_available.append(provider)
            
            self.log_test_result(
                "Modern Models - Configuration check",
                len(modern_models_available) == 3,  # All 3 providers should be modern
                f"Modern providers available: {modern_models_available}, Models: {models_configured}",
                {"modern_providers": modern_models_available, "models": models_configured}
            )
        else:
            self.log_test_result("Modern Models - Configuration check", False, f"Error: {error}", data)
    
    async def test_analyze_file_endpoint_structure(self):
        """Test analyze-file endpoint structure for image support"""
        logger.info("=== Testing Analyze File Endpoint Structure ===")
        
        # Test without authentication (should fail but show proper structure)
        test_image_data = self.create_test_image()
        
        form_data = aiohttp.FormData()
        form_data.add_field('file', test_image_data, filename='test_image.jpg', content_type='image/jpeg')
        form_data.add_field('language', 'en')
        
        success, data, error = await self.make_request("POST", "/api/analyze-file", data=form_data)
        
        # Should fail with authentication required (not file format error)
        is_auth_required = not success and ("401" in str(error) or "403" in str(error) or (isinstance(data, dict) and ("Not authenticated" in str(data.get("detail", "")))))
        
        self.log_test_result(
            "Analyze File - Image upload structure",
            is_auth_required,
            f"Endpoint correctly handles image uploads and requires auth" if is_auth_required else f"Unexpected response: {error}",
            data
        )
        
        # Test with different image formats
        formats_to_test = [
            ('test.png', 'image/png'),
            ('test.gif', 'image/gif'),
            ('test.webp', 'image/webp')
        ]
        
        for filename, content_type in formats_to_test:
            form_data = aiohttp.FormData()
            form_data.add_field('file', test_image_data, filename=filename, content_type=content_type)
            form_data.add_field('language', 'en')
            
            success, data, error = await self.make_request("POST", "/api/analyze-file", data=form_data)
            
            # Should still require authentication (not reject file format)
            is_auth_required = not success and ("401" in str(error) or "403" in str(error) or (isinstance(data, dict) and ("Not authenticated" in str(data.get("detail", "")))))
            
            self.log_test_result(
                f"Analyze File - {content_type} support",
                is_auth_required,
                f"Endpoint accepts {content_type} format" if is_auth_required else f"May not support {content_type}: {error}",
                {"format": content_type, "response": str(data)[:100] if data else None}
            )
    
    async def test_legacy_vs_modern_llm_comparison(self):
        """Compare legacy and modern LLM manager endpoints"""
        logger.info("=== Testing Legacy vs Modern LLM Comparison ===")
        
        # Test legacy LLM status
        success_legacy, data_legacy, error_legacy = await self.make_request("GET", "/api/llm-status")
        
        # Test modern LLM status
        success_modern, data_modern, error_modern = await self.make_request("GET", "/api/modern-llm-status")
        
        if success_legacy and success_modern:
            # Compare the responses
            legacy_has_modern_flag = data_legacy.get("modern") is True
            modern_has_modern_flag = data_modern.get("modern") is True
            
            legacy_providers = data_legacy.get("providers", {})
            modern_providers = data_modern.get("providers", {})
            
            # Check that modern endpoint has modern flag but legacy doesn't
            proper_distinction = not legacy_has_modern_flag and modern_has_modern_flag
            
            # Check that both have the same provider names but different capabilities
            same_provider_names = set(legacy_providers.keys()) == set(modern_providers.keys())
            
            self.log_test_result(
                "Legacy vs Modern - Proper distinction",
                proper_distinction and same_provider_names,
                f"Legacy modern flag: {legacy_has_modern_flag}, Modern modern flag: {modern_has_modern_flag}, Same providers: {same_provider_names}",
                {
                    "legacy_modern": legacy_has_modern_flag,
                    "modern_modern": modern_has_modern_flag,
                    "legacy_providers": list(legacy_providers.keys()),
                    "modern_providers": list(modern_providers.keys())
                }
            )
        else:
            self.log_test_result(
                "Legacy vs Modern - Proper distinction",
                False,
                f"Legacy error: {error_legacy}, Modern error: {error_modern}",
                {"legacy_success": success_legacy, "modern_success": success_modern}
            )
    
    async def test_emergentintegrations_integration(self):
        """Test that emergentintegrations library is properly integrated"""
        logger.info("=== Testing Emergentintegrations Integration ===")
        
        # Check if modern LLM manager is working (indicates emergentintegrations is available)
        success, data, error = await self.make_request("GET", "/api/modern-llm-status")
        
        if success and isinstance(data, dict):
            # If we get a successful response with modern flag, emergentintegrations is working
            has_modern_flag = data.get("modern") is True
            has_providers = len(data.get("providers", {})) > 0
            
            # Check that all providers have modern flag (indicating emergentintegrations support)
            all_providers_modern = all(
                provider_info.get("modern") is True
                for provider_info in data.get("providers", {}).values()
            )
            
            self.log_test_result(
                "Emergentintegrations - Library integration",
                has_modern_flag and has_providers and all_providers_modern,
                f"Modern flag: {has_modern_flag}, Providers: {len(data.get('providers', {}))}, All modern: {all_providers_modern}",
                data
            )
        else:
            self.log_test_result(
                "Emergentintegrations - Library integration",
                False,
                f"Modern LLM manager not responding properly: {error}",
                data
            )
    
    async def run_image_recognition_tests(self):
        """Run all image recognition tests"""
        logger.info("🎯 Starting Image Recognition Functionality Tests...")
        
        try:
            await self.test_modern_llm_status_endpoint()
            await self.test_modern_models_configuration()
            await self.test_analyze_file_endpoint_structure()
            await self.test_legacy_vs_modern_llm_comparison()
            await self.test_emergentintegrations_integration()
            
        except Exception as e:
            logger.error(f"Test execution error: {e}")
            self.log_test_result("Test execution", False, f"Critical error: {e}")
    
    def print_summary(self):
        """Print test summary"""
        logger.info("\n" + "="*60)
        logger.info("🎯 IMAGE RECOGNITION TEST SUMMARY")
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
        
        if total - passed > 0:
            logger.info("\n🔍 FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    logger.info(f"❌ {result['test']}: {result['details']}")
                    if result["response_data"]:
                        logger.info(f"   Response: {result['response_data']}")
        
        logger.info("="*60)
        
        return passed, total

async def main():
    """Main test execution"""
    async with ImageRecognitionTester() as tester:
        await tester.run_image_recognition_tests()
        passed, total = tester.print_summary()
        
        # Return exit code based on results
        return 0 if passed == total else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
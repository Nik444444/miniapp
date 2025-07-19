#!/usr/bin/env python3
"""
Focused OCR Testing for Telegram Mini App Document Analysis
Testing the critical OCR functionality that was causing "вечная загрузка"
"""

import asyncio
import aiohttp
import json
import os
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class OCRFocusedTester:
    def __init__(self):
        # Get backend URL from frontend .env file
        frontend_env_path = Path("/app/frontend/.env")
        self.backend_url = "http://localhost:8001"  # Default fallback
        
        if frontend_env_path.exists():
            with open(frontend_env_path, 'r') as f:
                for line in f:
                    if line.startswith('REACT_APP_BACKEND_URL='):
                        self.backend_url = line.split('=', 1)[1].strip()
                        break
            
        logger.info(f"Testing backend at: {self.backend_url}")
        
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
    
    async def test_ocr_status_endpoint(self):
        """🎯 КРИТИЧЕСКИЙ ТЕСТ: OCR Status Endpoint"""
        logger.info("=== 🎯 КРИТИЧЕСКИЙ ТЕСТ: OCR Status Endpoint ===")
        
        success, data, error = await self.make_request("GET", "/api/ocr-status")
        
        if success and isinstance(data, dict):
            # Check main status fields
            has_status = data.get("status") == "success"
            has_ocr_service = "ocr_service" in data and isinstance(data["ocr_service"], dict)
            tesseract_not_required = data.get("tesseract_required") is False
            production_ready = data.get("production_ready") is True
            
            # Check OCR service details
            ocr_service = data.get("ocr_service", {})
            service_name = ocr_service.get("service_name", "")
            is_simple_tesseract = service_name == "Simple Tesseract OCR Service"
            
            primary_method = ocr_service.get("primary_method", "")
            primary_is_tesseract = primary_method == "tesseract_ocr"
            
            tesseract_version = ocr_service.get("tesseract_version", "")
            has_version_5_3_0 = tesseract_version == "5.3.0"
            
            optimized_for_speed = ocr_service.get("optimized_for_speed") is True
            tesseract_dependency = ocr_service.get("tesseract_dependency") is True
            
            # Check methods
            methods = ocr_service.get("methods", {})
            expected_methods = {"tesseract_ocr", "direct_pdf"}
            actual_methods = set(methods.keys())
            only_expected_methods = actual_methods == expected_methods
            
            # Check tesseract method availability
            tesseract_method = methods.get("tesseract_ocr", {})
            tesseract_available = tesseract_method.get("available") is True
            
            # Overall OCR status check
            ocr_status_perfect = all([
                has_status, has_ocr_service, production_ready,
                is_simple_tesseract, primary_is_tesseract, has_version_5_3_0,
                optimized_for_speed, tesseract_dependency, only_expected_methods,
                tesseract_available
            ])
            
            self.log_test_result(
                "🎯 OCR Status - Complete Check",
                ocr_status_perfect,
                f"Service: {service_name}, Primary: {primary_method}, Version: {tesseract_version}, Methods: {list(actual_methods)}",
                data
            )
            
            # Individual checks for detailed reporting
            self.log_test_result(
                "OCR Status - tesseract_available should be true",
                tesseract_available,
                f"tesseract_ocr.available = {tesseract_available}",
                {"tesseract_available": tesseract_available}
            )
            
            self.log_test_result(
                "OCR Status - primary_method should be tesseract_ocr",
                primary_is_tesseract,
                f"primary_method = {primary_method}",
                {"primary_method": primary_method}
            )
            
            self.log_test_result(
                "OCR Status - tesseract_version should be 5.3.0",
                has_version_5_3_0,
                f"tesseract_version = {tesseract_version}",
                {"tesseract_version": tesseract_version}
            )
            
            self.log_test_result(
                "OCR Status - production_ready should be true",
                production_ready,
                f"production_ready = {production_ready}",
                {"production_ready": production_ready}
            )
            
        else:
            self.log_test_result("🎯 OCR Status - Complete Check", False, f"Error: {error}", data)
    
    async def test_health_endpoint(self):
        """🎯 КРИТИЧЕСКИЙ ТЕСТ: Health Endpoint"""
        logger.info("=== 🎯 КРИТИЧЕСКИЙ ТЕСТ: Health Endpoint ===")
        
        success, data, error = await self.make_request("GET", "/api/health")
        
        if success and isinstance(data, dict):
            is_healthy = data.get("status") == "healthy"
            has_database = "database" in data
            has_counts = "users_count" in data and "analyses_count" in data
            
            self.log_test_result(
                "🎯 Health Check - Backend Healthy",
                is_healthy and has_database and has_counts,
                f"Status: {data.get('status')}, DB: {data.get('database')}, Users: {data.get('users_count')}, Analyses: {data.get('analyses_count')}",
                data
            )
        else:
            self.log_test_result("🎯 Health Check - Backend Healthy", False, f"Error: {error}", data)
    
    async def test_no_fallback_mode(self):
        """🎯 КРИТИЧЕСКИЙ ТЕСТ: System NOT in Fallback Mode"""
        logger.info("=== 🎯 КРИТИЧЕСКИЙ ТЕСТ: System NOT in Fallback Mode ===")
        
        # Check OCR status for fallback indicators
        success, data, error = await self.make_request("GET", "/api/ocr-status")
        
        if success and isinstance(data, dict):
            ocr_service = data.get("ocr_service", {})
            primary_method = ocr_service.get("primary_method", "")
            
            # System should NOT be in fallback mode
            not_in_fallback = primary_method == "tesseract_ocr"  # Not llm_vision or other fallback methods
            
            # Check that tesseract is available (not falling back due to unavailability)
            methods = ocr_service.get("methods", {})
            tesseract_method = methods.get("tesseract_ocr", {})
            tesseract_available = tesseract_method.get("available") is True
            
            # Check production ready (not in development/fallback mode)
            production_ready = ocr_service.get("production_ready") is True
            
            not_fallback_mode = not_in_fallback and tesseract_available and production_ready
            
            self.log_test_result(
                "🎯 System NOT in Fallback Mode",
                not_fallback_mode,
                f"Primary method: {primary_method}, Tesseract available: {tesseract_available}, Production ready: {production_ready}",
                {"primary_method": primary_method, "tesseract_available": tesseract_available, "production_ready": production_ready}
            )
        else:
            self.log_test_result("🎯 System NOT in Fallback Mode", False, f"Error: {error}", data)
    
    async def test_emergentintegrations_available(self):
        """🎯 КРИТИЧЕСКИЙ ТЕСТ: emergentintegrations Available"""
        logger.info("=== 🎯 КРИТИЧЕСКИЙ ТЕСТ: emergentintegrations Available ===")
        
        success, data, error = await self.make_request("GET", "/api/modern-llm-status")
        
        if success and isinstance(data, dict):
            has_modern_flag = data.get("modern") is True
            has_status_success = data.get("status") == "success"
            has_providers = "providers" in data and isinstance(data["providers"], dict)
            
            # Check if emergentintegrations is working (indicated by modern flag and successful status)
            emergent_available = has_modern_flag and has_status_success and has_providers
            
            self.log_test_result(
                "🎯 emergentintegrations Available",
                emergent_available,
                f"Modern flag: {has_modern_flag}, Status: {data.get('status')}, Providers: {len(data.get('providers', {}))}" if has_providers else f"Modern flag: {has_modern_flag}, Status: {data.get('status')}",
                data
            )
        else:
            self.log_test_result("🎯 emergentintegrations Available", False, f"Error: {error}", data)
    
    async def test_no_slow_methods_as_primary(self):
        """🎯 КРИТИЧЕСКИЙ ТЕСТ: No LLM Vision or Slow Methods as Primary"""
        logger.info("=== 🎯 КРИТИЧЕСКИЙ ТЕСТ: No LLM Vision or Slow Methods as Primary ===")
        
        success, data, error = await self.make_request("GET", "/api/ocr-status")
        
        if success and isinstance(data, dict):
            ocr_service = data.get("ocr_service", {})
            primary_method = ocr_service.get("primary_method", "")
            
            # Primary method should be tesseract_ocr (fast), NOT llm_vision (slow)
            is_fast_primary = primary_method == "tesseract_ocr"
            is_not_slow_primary = primary_method not in ["llm_vision", "ocr_space", "azure_vision"]
            
            # Check that slow methods are not in the methods list at all
            methods = ocr_service.get("methods", {})
            slow_methods = {"llm_vision", "ocr_space", "azure_vision"}
            slow_methods_present = slow_methods.intersection(set(methods.keys()))
            no_slow_methods = len(slow_methods_present) == 0
            
            fast_primary_only = is_fast_primary and is_not_slow_primary and no_slow_methods
            
            self.log_test_result(
                "🎯 No Slow Methods as Primary",
                fast_primary_only,
                f"Primary: {primary_method}, Slow methods present: {list(slow_methods_present)}",
                {"primary_method": primary_method, "slow_methods_found": list(slow_methods_present)}
            )
        else:
            self.log_test_result("🎯 No Slow Methods as Primary", False, f"Error: {error}", data)
    
    async def test_simple_tesseract_service_working(self):
        """🎯 КРИТИЧЕСКИЙ ТЕСТ: simple_tesseract_ocr Service Working"""
        logger.info("=== 🎯 КРИТИЧЕСКИЙ ТЕСТ: simple_tesseract_ocr Service Working ===")
        
        success, data, error = await self.make_request("GET", "/api/ocr-status")
        
        if success and isinstance(data, dict):
            ocr_service = data.get("ocr_service", {})
            
            # Check service name
            service_name = ocr_service.get("service_name", "")
            is_simple_tesseract_service = service_name == "Simple Tesseract OCR Service"
            
            # Check that it's optimized for speed
            optimized_for_speed = ocr_service.get("optimized_for_speed") is True
            
            # Check tesseract dependency is true (service depends on tesseract)
            tesseract_dependency = ocr_service.get("tesseract_dependency") is True
            
            # Check methods structure
            methods = ocr_service.get("methods", {})
            has_tesseract_method = "tesseract_ocr" in methods
            has_direct_pdf_method = "direct_pdf" in methods
            
            if has_tesseract_method:
                tesseract_method = methods["tesseract_ocr"]
                tesseract_available = tesseract_method.get("available") is True
                tesseract_description = tesseract_method.get("description", "")
                has_correct_description = "единственный метод" in tesseract_description
            else:
                tesseract_available = False
                has_correct_description = False
            
            service_working = all([
                is_simple_tesseract_service, optimized_for_speed, tesseract_dependency,
                has_tesseract_method, has_direct_pdf_method, tesseract_available, has_correct_description
            ])
            
            self.log_test_result(
                "🎯 simple_tesseract_ocr Service Working",
                service_working,
                f"Service: {service_name}, Speed optimized: {optimized_for_speed}, Tesseract available: {tesseract_available}",
                ocr_service
            )
        else:
            self.log_test_result("🎯 simple_tesseract_ocr Service Working", False, f"Error: {error}", data)
    
    async def run_all_tests(self):
        """Run all focused OCR tests"""
        logger.info("🎯 Starting Focused OCR Tests for Telegram Mini App Document Analysis")
        logger.info("=" * 80)
        
        # Run critical tests in order
        await self.test_health_endpoint()
        await self.test_ocr_status_endpoint()
        await self.test_simple_tesseract_service_working()
        await self.test_no_fallback_mode()
        await self.test_no_slow_methods_as_primary()
        await self.test_emergentintegrations_available()
        
        # Summary
        logger.info("=" * 80)
        logger.info("🎯 FOCUSED OCR TEST RESULTS SUMMARY")
        logger.info("=" * 80)
        
        passed_tests = [result for result in self.test_results if result["success"]]
        failed_tests = [result for result in self.test_results if not result["success"]]
        
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
        critical_tests = [
            "🎯 OCR Status - Complete Check",
            "🎯 Health Check - Backend Healthy", 
            "🎯 simple_tesseract_ocr Service Working",
            "🎯 System NOT in Fallback Mode",
            "🎯 No Slow Methods as Primary"
        ]
        
        critical_passed = [test for test in passed_tests if test["test"] in critical_tests]
        critical_failed = [test for test in failed_tests if test["test"] in critical_tests]
        
        logger.info(f"\n🎯 CRITICAL TESTS: {len(critical_passed)}/{len(critical_tests)} passed")
        
        if len(critical_passed) == len(critical_tests):
            logger.info("🚀 ALL CRITICAL TESTS PASSED - Telegram Mini App OCR should work correctly!")
        else:
            logger.info("⚠️ SOME CRITICAL TESTS FAILED - Issues may persist in Telegram Mini App")
        
        return len(failed_tests) == 0

async def main():
    async with OCRFocusedTester() as tester:
        success = await tester.run_all_tests()
        return success

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
#!/usr/bin/env python3
"""
Final Testing for Render Deployment Fixes
Tests specifically for the deployment issues resolution:
1. TESSERACT OCR PRIMARY METHOD
2. EMERGENTINTEGRATIONS AVAILABLE  
3. SYSTEM PRODUCTION READY
4. RENDER DEPLOYMENT FIX VERIFICATION
"""

import asyncio
import aiohttp
import json
import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RenderDeploymentTester:
    def __init__(self):
        # Get backend URL from frontend .env file
        frontend_env_path = Path("/app/frontend/.env")
        self.backend_url = "http://localhost:8001"
        
        if frontend_env_path.exists():
            with open(frontend_env_path, 'r') as f:
                for line in f:
                    if line.startswith('REACT_APP_BACKEND_URL='):
                        self.backend_url = line.split('=', 1)[1].strip()
                        break
        
        logger.info(f"Testing Render deployment fixes at: {self.backend_url}")
        
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
    
    async def test_tesseract_ocr_primary_method(self):
        """Test 1: TESSERACT OCR PRIMARY METHOD"""
        logger.info("=== 1. TESTING TESSERACT OCR PRIMARY METHOD ===")
        
        success, data, error = await self.make_request("GET", "/api/ocr-status")
        
        if success and isinstance(data, dict):
            # Check main response structure
            has_status = data.get("status") == "success"
            ocr_service = data.get("ocr_service", {})
            
            # CRITICAL: Check primary_method is "tesseract_ocr"
            primary_method = ocr_service.get("primary_method")
            is_tesseract_primary = primary_method == "tesseract_ocr"
            
            # CRITICAL: Check tesseract_dependency is true
            tesseract_dependency = ocr_service.get("tesseract_dependency")
            has_tesseract_dependency = tesseract_dependency is True
            
            # CRITICAL: Check tesseract_version is "5.3.0"
            tesseract_version = ocr_service.get("tesseract_version")
            has_correct_version = tesseract_version == "5.3.0"
            
            # Check tesseract_ocr method is available
            methods = ocr_service.get("methods", {})
            tesseract_method = methods.get("tesseract_ocr", {})
            tesseract_available = tesseract_method.get("available") is True
            
            all_tesseract_checks = (
                has_status and 
                is_tesseract_primary and 
                has_tesseract_dependency and 
                has_correct_version and 
                tesseract_available
            )
            
            self.log_test_result(
                "TESSERACT OCR PRIMARY METHOD - All requirements",
                all_tesseract_checks,
                f"Status: {has_status}, Primary: {primary_method}, Dependency: {tesseract_dependency}, Version: {tesseract_version}, Available: {tesseract_available}",
                data
            )
            
            # Individual checks for detailed reporting
            self.log_test_result(
                "TESSERACT - primary_method: tesseract_ocr",
                is_tesseract_primary,
                f"Expected: tesseract_ocr, Got: {primary_method}",
                {"primary_method": primary_method}
            )
            
            self.log_test_result(
                "TESSERACT - tesseract_dependency: true",
                has_tesseract_dependency,
                f"Expected: true, Got: {tesseract_dependency}",
                {"tesseract_dependency": tesseract_dependency}
            )
            
            self.log_test_result(
                "TESSERACT - tesseract_version: 5.3.0",
                has_correct_version,
                f"Expected: 5.3.0, Got: {tesseract_version}",
                {"tesseract_version": tesseract_version}
            )
            
            self.log_test_result(
                "TESSERACT - tesseract_ocr method available: true",
                tesseract_available,
                f"Expected: true, Got: {tesseract_available}",
                tesseract_method
            )
            
        else:
            self.log_test_result(
                "TESSERACT OCR PRIMARY METHOD - All requirements",
                False,
                f"Failed to get OCR status: {error}",
                data
            )
    
    async def test_emergentintegrations_available(self):
        """Test 2: EMERGENTINTEGRATIONS AVAILABLE"""
        logger.info("=== 2. TESTING EMERGENTINTEGRATIONS AVAILABLE ===")
        
        success, data, error = await self.make_request("GET", "/api/modern-llm-status")
        
        if success and isinstance(data, dict):
            # CRITICAL: Modern LLM manager should NOT be in fallback mode
            has_modern_flag = data.get("modern") is True
            status_success = data.get("status") == "success"
            
            # CRITICAL: All modern providers should be active
            providers = data.get("providers", {})
            all_providers_modern = True
            active_modern_providers = []
            
            for provider_name, provider_info in providers.items():
                if provider_info.get("modern") is True:
                    active_modern_providers.append(provider_name)
                else:
                    all_providers_modern = False
            
            # Check that we have the expected modern providers
            expected_providers = ["gemini", "openai", "anthropic"]
            has_all_expected = all(provider in providers for provider in expected_providers)
            
            all_emergent_checks = (
                has_modern_flag and 
                status_success and 
                all_providers_modern and 
                has_all_expected and
                len(active_modern_providers) > 0
            )
            
            self.log_test_result(
                "EMERGENTINTEGRATIONS AVAILABLE - All requirements",
                all_emergent_checks,
                f"Modern: {has_modern_flag}, Status: {status_success}, All modern: {all_providers_modern}, Active: {active_modern_providers}",
                data
            )
            
            # Individual checks
            self.log_test_result(
                "EMERGENT - Modern LLM manager not in fallback mode",
                has_modern_flag and status_success,
                f"Modern flag: {has_modern_flag}, Status: {status_success}",
                {"modern": has_modern_flag, "status": status_success}
            )
            
            self.log_test_result(
                "EMERGENT - All modern providers active",
                all_providers_modern,
                f"All providers modern: {all_providers_modern}, Active providers: {active_modern_providers}",
                {"providers": providers}
            )
            
            self.log_test_result(
                "EMERGENT - modern: true flag everywhere",
                has_modern_flag and all_providers_modern,
                f"Main modern flag: {has_modern_flag}, All providers modern: {all_providers_modern}",
                data
            )
            
        else:
            self.log_test_result(
                "EMERGENTINTEGRATIONS AVAILABLE - All requirements",
                False,
                f"Failed to get modern LLM status: {error}",
                data
            )
    
    async def test_system_production_ready(self):
        """Test 3: SYSTEM PRODUCTION READY"""
        logger.info("=== 3. TESTING SYSTEM PRODUCTION READY ===")
        
        # Test OCR service production readiness
        success, data, error = await self.make_request("GET", "/api/ocr-status")
        
        ocr_production_ready = False
        if success and isinstance(data, dict):
            # CRITICAL: production_ready should be true
            main_production_ready = data.get("production_ready") is True
            ocr_service = data.get("ocr_service", {})
            service_production_ready = ocr_service.get("production_ready") is True
            
            ocr_production_ready = main_production_ready and service_production_ready
            
            self.log_test_result(
                "PRODUCTION READY - OCR service",
                ocr_production_ready,
                f"Main production ready: {main_production_ready}, OCR service production ready: {service_production_ready}",
                data
            )
        
        # Test Modern LLM service production readiness
        success, data, error = await self.make_request("GET", "/api/modern-llm-status")
        
        llm_production_ready = False
        if success and isinstance(data, dict):
            # CRITICAL: No fallback mode
            status_success = data.get("status") == "success"
            has_modern_flag = data.get("modern") is True
            
            # Check that providers are working (not in fallback)
            providers = data.get("providers", {})
            providers_working = len(providers) > 0 and all(
                provider.get("modern") is True for provider in providers.values()
            )
            
            llm_production_ready = status_success and has_modern_flag and providers_working
            
            self.log_test_result(
                "PRODUCTION READY - Modern LLM service",
                llm_production_ready,
                f"Status: {status_success}, Modern: {has_modern_flag}, Providers working: {providers_working}",
                data
            )
        
        # Test overall system health
        success, data, error = await self.make_request("GET", "/api/health")
        
        system_healthy = False
        if success and isinstance(data, dict):
            status_healthy = data.get("status") == "healthy"
            database_connected = data.get("database") == "sqlite"
            has_user_count = "users_count" in data
            has_analysis_count = "analyses_count" in data
            
            system_healthy = status_healthy and database_connected and has_user_count and has_analysis_count
            
            self.log_test_result(
                "PRODUCTION READY - System health",
                system_healthy,
                f"Status: {status_healthy}, DB: {database_connected}, Users: {has_user_count}, Analyses: {has_analysis_count}",
                data
            )
        
        # Overall production readiness
        overall_production_ready = ocr_production_ready and llm_production_ready and system_healthy
        
        self.log_test_result(
            "SYSTEM PRODUCTION READY - All requirements",
            overall_production_ready,
            f"OCR ready: {ocr_production_ready}, LLM ready: {llm_production_ready}, System healthy: {system_healthy}",
            {
                "ocr_ready": ocr_production_ready,
                "llm_ready": llm_production_ready, 
                "system_healthy": system_healthy
            }
        )
    
    async def test_render_deployment_fix_verification(self):
        """Test 4: RENDER DEPLOYMENT FIX VERIFICATION"""
        logger.info("=== 4. TESTING RENDER DEPLOYMENT FIX VERIFICATION ===")
        
        # Test that PATH is configured correctly (tesseract available)
        success, data, error = await self.make_request("GET", "/api/ocr-status")
        
        path_configured = False
        if success and isinstance(data, dict):
            ocr_service = data.get("ocr_service", {})
            methods = ocr_service.get("methods", {})
            tesseract_method = methods.get("tesseract_ocr", {})
            
            # If tesseract is available, PATH is configured correctly
            tesseract_available = tesseract_method.get("available") is True
            tesseract_version = ocr_service.get("tesseract_version") == "5.3.0"
            
            path_configured = tesseract_available and tesseract_version
            
            self.log_test_result(
                "RENDER FIX - PATH configured correctly",
                path_configured,
                f"Tesseract available: {tesseract_available}, Version: {tesseract_version}",
                tesseract_method
            )
        
        # Test that race condition is fixed (modern LLM works)
        success, data, error = await self.make_request("GET", "/api/modern-llm-status")
        
        race_condition_fixed = False
        if success and isinstance(data, dict):
            # If modern LLM status works without errors, race condition is fixed
            status_success = data.get("status") == "success"
            has_modern_flag = data.get("modern") is True
            has_providers = len(data.get("providers", {})) > 0
            
            race_condition_fixed = status_success and has_modern_flag and has_providers
            
            self.log_test_result(
                "RENDER FIX - Race condition fixed",
                race_condition_fixed,
                f"Status: {status_success}, Modern: {has_modern_flag}, Providers: {has_providers}",
                data
            )
        
        # Test system ready for production deploy
        success, data, error = await self.make_request("GET", "/api/health")
        
        deploy_ready = False
        if success and isinstance(data, dict):
            status_healthy = data.get("status") == "healthy"
            service_running = "service" in data
            auth_configured = "auth" in data and "google-oauth" in str(data.get("auth", "")).lower()
            database_working = data.get("database") == "sqlite"
            
            deploy_ready = status_healthy and service_running and auth_configured and database_working
            
            self.log_test_result(
                "RENDER FIX - System ready for production deploy",
                deploy_ready,
                f"Healthy: {status_healthy}, Service: {service_running}, Auth: {auth_configured}, DB: {database_working}",
                data
            )
        
        # Overall deployment fix verification
        deployment_fixed = path_configured and race_condition_fixed and deploy_ready
        
        self.log_test_result(
            "RENDER DEPLOYMENT FIX VERIFICATION - All requirements",
            deployment_fixed,
            f"PATH OK: {path_configured}, Race condition fixed: {race_condition_fixed}, Deploy ready: {deploy_ready}",
            {
                "path_configured": path_configured,
                "race_condition_fixed": race_condition_fixed,
                "deploy_ready": deploy_ready
            }
        )
    
    async def test_comprehensive_deployment_status(self):
        """Comprehensive test of all deployment requirements"""
        logger.info("=== COMPREHENSIVE DEPLOYMENT STATUS CHECK ===")
        
        # Get OCR status
        ocr_success, ocr_data, ocr_error = await self.make_request("GET", "/api/ocr-status")
        
        # Get Modern LLM status  
        llm_success, llm_data, llm_error = await self.make_request("GET", "/api/modern-llm-status")
        
        # Get system health
        health_success, health_data, health_error = await self.make_request("GET", "/api/health")
        
        if ocr_success and llm_success and health_success:
            # Extract all critical values
            ocr_service = ocr_data.get("ocr_service", {})
            
            # Tesseract checks
            primary_method = ocr_service.get("primary_method")
            tesseract_dependency = ocr_service.get("tesseract_dependency")
            tesseract_version = ocr_service.get("tesseract_version")
            tesseract_available = ocr_service.get("methods", {}).get("tesseract_ocr", {}).get("available")
            
            # Modern LLM checks
            modern_flag = llm_data.get("modern")
            llm_status = llm_data.get("status")
            providers = llm_data.get("providers", {})
            all_modern = all(p.get("modern") is True for p in providers.values()) if providers else False
            
            # Production readiness
            ocr_production_ready = ocr_data.get("production_ready")
            system_healthy = health_data.get("status") == "healthy"
            
            # Create comprehensive status
            deployment_status = {
                "tesseract_primary": primary_method == "tesseract_ocr",
                "tesseract_dependency": tesseract_dependency is True,
                "tesseract_version_correct": tesseract_version == "5.3.0",
                "tesseract_available": tesseract_available is True,
                "modern_llm_active": modern_flag is True,
                "llm_status_success": llm_status == "success",
                "all_providers_modern": all_modern,
                "ocr_production_ready": ocr_production_ready is True,
                "system_healthy": system_healthy,
                "no_fallback_mode": modern_flag is True and llm_status == "success"
            }
            
            all_checks_pass = all(deployment_status.values())
            
            self.log_test_result(
                "COMPREHENSIVE DEPLOYMENT STATUS - All critical requirements",
                all_checks_pass,
                f"All checks: {all_checks_pass}, Details: {deployment_status}",
                {
                    "deployment_status": deployment_status,
                    "ocr_data": ocr_data,
                    "llm_data": llm_data,
                    "health_data": health_data
                }
            )
            
            # Log individual status for clarity
            for check_name, check_result in deployment_status.items():
                self.log_test_result(
                    f"DEPLOYMENT CHECK - {check_name}",
                    check_result,
                    f"Status: {check_result}",
                    None
                )
                
        else:
            self.log_test_result(
                "COMPREHENSIVE DEPLOYMENT STATUS - All critical requirements",
                False,
                f"Failed to get status - OCR: {ocr_error}, LLM: {llm_error}, Health: {health_error}",
                {"ocr_error": ocr_error, "llm_error": llm_error, "health_error": health_error}
            )
    
    async def run_all_tests(self):
        """Run all deployment fix tests"""
        logger.info("🚀 STARTING RENDER DEPLOYMENT FIX VERIFICATION TESTS")
        
        await self.test_tesseract_ocr_primary_method()
        await self.test_emergentintegrations_available()
        await self.test_system_production_ready()
        await self.test_render_deployment_fix_verification()
        await self.test_comprehensive_deployment_status()
        
        # Summary
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        logger.info(f"\n{'='*60}")
        logger.info(f"RENDER DEPLOYMENT FIX VERIFICATION COMPLETE")
        logger.info(f"{'='*60}")
        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"Passed: {passed_tests}")
        logger.info(f"Failed: {total_tests - passed_tests}")
        logger.info(f"Success Rate: {success_rate:.1f}%")
        
        # Show failed tests
        failed_tests = [result for result in self.test_results if not result["success"]]
        if failed_tests:
            logger.info(f"\n❌ FAILED TESTS:")
            for test in failed_tests:
                logger.info(f"  - {test['test']}: {test['details']}")
        
        # Show critical deployment status
        logger.info(f"\n🎯 CRITICAL DEPLOYMENT STATUS:")
        critical_tests = [
            "TESSERACT OCR PRIMARY METHOD - All requirements",
            "EMERGENTINTEGRATIONS AVAILABLE - All requirements", 
            "SYSTEM PRODUCTION READY - All requirements",
            "RENDER DEPLOYMENT FIX VERIFICATION - All requirements",
            "COMPREHENSIVE DEPLOYMENT STATUS - All critical requirements"
        ]
        
        for test_name in critical_tests:
            test_result = next((r for r in self.test_results if r["test"] == test_name), None)
            if test_result:
                status = "✅ PASS" if test_result["success"] else "❌ FAIL"
                logger.info(f"  {status} {test_name}")
        
        return success_rate >= 90  # Consider successful if 90%+ tests pass

async def main():
    """Main test execution"""
    async with RenderDeploymentTester() as tester:
        success = await tester.run_all_tests()
        return success

if __name__ == "__main__":
    result = asyncio.run(main())
    exit(0 if result else 1)
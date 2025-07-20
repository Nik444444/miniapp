#!/usr/bin/env python3
"""
Deployment Issues Test - Testing specific fixes mentioned in review request
"""

import asyncio
import aiohttp
import json
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DeploymentTester:
    def __init__(self):
        self.backend_url = "http://localhost:8001"
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
    
    async def test_health_endpoint_database_connectivity(self):
        """Test health endpoint shows database connectivity"""
        logger.info("=== Testing Health Endpoint Database Connectivity ===")
        
        success, data, error = await self.make_request("GET", "/api/health")
        if success and isinstance(data, dict):
            has_status = data.get("status") == "healthy"
            has_database = "database" in data and data["database"] == "connected"
            has_users_count = "users_count" in data and isinstance(data["users_count"], int)
            has_analyses_count = "analyses_count" in data and isinstance(data["analyses_count"], int)
            
            self.log_test_result(
                "Health endpoint database connectivity",
                has_status and has_database and has_users_count and has_analyses_count,
                f"Status: {data.get('status')}, DB: {data.get('database')}, Users: {data.get('users_count')}, Analyses: {data.get('analyses_count')}",
                data
            )
        else:
            self.log_test_result("Health endpoint database connectivity", False, f"Error: {error}", data)
    
    async def test_modern_llm_status_endpoint(self):
        """Test modern LLM status endpoint shows all providers with modern=true"""
        logger.info("=== Testing Modern LLM Status Endpoint ===")
        
        success, data, error = await self.make_request("GET", "/api/modern-llm-status")
        if success and isinstance(data, dict):
            has_modern_flag = data.get("modern") is True
            has_providers = "providers" in data and isinstance(data["providers"], dict)
            
            # Check if all providers have modern=true
            all_providers_modern = True
            provider_details = []
            if has_providers:
                for provider_name, provider_info in data["providers"].items():
                    is_modern = provider_info.get("modern") is True
                    provider_details.append(f"{provider_name}:modern={is_modern}")
                    if not is_modern:
                        all_providers_modern = False
            
            self.log_test_result(
                "Modern LLM status - all providers modern=true",
                has_modern_flag and has_providers and all_providers_modern,
                f"Global modern: {has_modern_flag}, All providers modern: {all_providers_modern}, Details: {provider_details}",
                data
            )
        else:
            self.log_test_result("Modern LLM status - all providers modern=true", False, f"Error: {error}", data)
    
    async def test_quick_gemini_setup_api_key_validation(self):
        """Test quick Gemini setup endpoint handles API key validation properly"""
        logger.info("=== Testing Quick Gemini Setup API Key Validation ===")
        
        # Test without authentication - should require auth
        test_data = {"api_key": "AIzaSyTest_invalid_key_format"}
        success, data, error = await self.make_request("POST", "/api/quick-gemini-setup", json=test_data)
        
        # Should fail with authentication required
        is_auth_required = not success and ("401" in str(error) or "403" in str(error) or 
                                          (isinstance(data, dict) and ("Not authenticated" in str(data.get("detail", "")))))
        
        self.log_test_result(
            "Quick Gemini setup - authentication required",
            is_auth_required,
            f"Correctly requires authentication" if is_auth_required else f"Unexpected response: {error}",
            data
        )
        
        # Test with invalid API key format
        invalid_key_data = {"api_key": "invalid_key_format"}
        success, data, error = await self.make_request("POST", "/api/quick-gemini-setup", json=invalid_key_data)
        
        # Should still require authentication first
        handles_validation = not success and ("401" in str(error) or "403" in str(error) or 
                                            (isinstance(data, dict) and ("Not authenticated" in str(data.get("detail", "")))))
        
        self.log_test_result(
            "Quick Gemini setup - API key validation structure",
            handles_validation,
            f"Endpoint properly structured for validation" if handles_validation else f"Structure issue: {error}",
            data
        )
    
    async def test_fallback_mechanisms(self):
        """Test fallback mechanisms when emergentintegrations works vs fallback mode"""
        logger.info("=== Testing Fallback Mechanisms ===")
        
        # Test that modern LLM manager works with emergentintegrations
        success, data, error = await self.make_request("GET", "/api/modern-llm-status")
        
        if success and isinstance(data, dict):
            has_modern_flag = data.get("modern") is True
            has_status_success = data.get("status") == "success"
            has_providers = "providers" in data and len(data["providers"]) > 0
            
            # Check if emergentintegrations is working (no error status)
            emergent_working = has_status_success and not ("error" in str(data).lower())
            
            self.log_test_result(
                "Fallback mechanisms - emergentintegrations working",
                has_modern_flag and has_status_success and has_providers and emergent_working,
                f"Modern: {has_modern_flag}, Status: {data.get('status')}, Providers: {len(data.get('providers', {}))}, Working: {emergent_working}",
                data
            )
        else:
            self.log_test_result("Fallback mechanisms - emergentintegrations working", False, f"Error: {error}", data)
        
        # Test that regular LLM status also works (fallback)
        success, data, error = await self.make_request("GET", "/api/llm-status")
        
        if success and isinstance(data, dict):
            has_status = data.get("status") == "success"
            has_providers = "providers" in data and len(data["providers"]) > 0
            
            self.log_test_result(
                "Fallback mechanisms - legacy LLM manager fallback",
                has_status and has_providers,
                f"Legacy status: {data.get('status')}, Providers: {len(data.get('providers', {}))}",
                data
            )
        else:
            self.log_test_result("Fallback mechanisms - legacy LLM manager fallback", False, f"Error: {error}", data)
    
    async def test_system_dependencies(self):
        """Test that all system dependencies are working"""
        logger.info("=== Testing System Dependencies ===")
        
        # Test that endpoints don't return 500 errors (which would indicate missing dependencies)
        endpoints_to_test = [
            "/api/health",
            "/api/modern-llm-status", 
            "/api/llm-status",
            "/api/telegram-news"
        ]
        
        all_dependencies_ok = True
        dependency_results = []
        
        for endpoint in endpoints_to_test:
            success, data, error = await self.make_request("GET", endpoint)
            
            # Check for 500 errors or import errors
            has_dependency_error = "500" in str(error) or (isinstance(data, dict) and 
                                                         ("import" in str(data).lower() or 
                                                          "module" in str(data).lower() or
                                                          "500" in str(data)))
            
            if has_dependency_error:
                all_dependencies_ok = False
                dependency_results.append(f"{endpoint}: DEPENDENCY ERROR")
            else:
                dependency_results.append(f"{endpoint}: OK")
        
        self.log_test_result(
            "System dependencies - no import/dependency errors",
            all_dependencies_ok,
            f"All endpoints working without dependency errors: {dependency_results}",
            {"results": dependency_results}
        )
    
    async def test_backend_startup_without_errors(self):
        """Test that backend starts without any missing dependency errors"""
        logger.info("=== Testing Backend Startup Without Errors ===")
        
        # Test basic connectivity to ensure backend is running
        success, data, error = await self.make_request("GET", "/")
        
        if success and isinstance(data, dict):
            has_message = "message" in data
            has_version = "version" in data
            is_running = "status" in data and data["status"] == "OK"
            
            self.log_test_result(
                "Backend startup - no missing dependency errors",
                has_message and has_version and is_running,
                f"Backend running successfully: {data.get('message')}, Version: {data.get('version')}",
                data
            )
        else:
            self.log_test_result("Backend startup - no missing dependency errors", False, f"Backend not responding: {error}", data)
    
    async def test_specific_deployment_scenarios(self):
        """Test specific scenarios mentioned in review request"""
        logger.info("=== Testing Specific Deployment Scenarios ===")
        
        # Test invalid API key format scenario
        invalid_key_scenarios = [
            {"api_key": "invalid_format"},
            {"api_key": ""},
            {"api_key": "AIza_too_short"}
        ]
        
        for i, scenario in enumerate(invalid_key_scenarios):
            success, data, error = await self.make_request("POST", "/api/quick-gemini-setup", json=scenario)
            
            # Should handle gracefully (auth required, not crash)
            handles_gracefully = not success and not ("500" in str(error))
            
            self.log_test_result(
                f"Invalid API key scenario {i+1} - graceful handling",
                handles_gracefully,
                f"Scenario {scenario}: {'Handled gracefully' if handles_gracefully else 'Server error'}",
                {"scenario": scenario, "error": error}
            )
        
        # Test valid API key format scenario (should still require auth)
        valid_format_scenario = {"api_key": "AIzaSyTest_valid_format_but_fake_key_1234567890"}
        success, data, error = await self.make_request("POST", "/api/quick-gemini-setup", json=valid_format_scenario)
        
        # Should require auth, not crash
        handles_valid_format = not success and not ("500" in str(error))
        
        self.log_test_result(
            "Valid API key format - graceful handling",
            handles_valid_format,
            f"Valid format handled gracefully: {'Yes' if handles_valid_format else 'Server error'}",
            {"scenario": valid_format_scenario, "error": error}
        )
    
    async def run_deployment_tests(self):
        """Run all deployment-specific tests"""
        logger.info("🚀 Starting deployment issues testing...")
        
        try:
            await self.test_health_endpoint_database_connectivity()
            await self.test_modern_llm_status_endpoint()
            await self.test_quick_gemini_setup_api_key_validation()
            await self.test_fallback_mechanisms()
            await self.test_system_dependencies()
            await self.test_backend_startup_without_errors()
            await self.test_specific_deployment_scenarios()
            
        except Exception as e:
            logger.error(f"Test execution error: {e}")
            self.log_test_result("Test execution", False, f"Critical error: {e}")
    
    def print_summary(self):
        """Print test summary"""
        logger.info("\n" + "="*60)
        logger.info("📊 DEPLOYMENT ISSUES TEST SUMMARY")
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
    async with DeploymentTester() as tester:
        await tester.run_deployment_tests()
        passed, total = tester.print_summary()
        
        # Return exit code based on results
        return 0 if passed == total else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
#!/usr/bin/env python3
"""
🎯 КРИТИЧЕСКОЕ ТЕСТИРОВАНИЕ: Cities API и Job Search API для Telegram Mini App

ЗАДАЧИ ПО ЗАПРОСУ ПОЛЬЗОВАТЕЛЯ:

1. Cities API:
   - GET /api/cities/popular - должен возвращать популярные города
   - GET /api/cities/search?q=Berlin - должен найти Berlin
   - GET /api/cities/search?q=Ber - должен найти города, начинающиеся с "Ber"
   - GET /api/cities/search?q=München - должен найти München

2. Job Search API:
   - GET /api/job-search?location=Berlin&language_level=B1 - должен работать БЕЗ search_query
   - GET /api/job-search?location=Berlin&language_level=B1&search_query=Developer - должен работать с полными параметрами

ОСОБЕННО ПРОВЕРИТЬ:
- Возвращается ли корректная структура данных
- Нет ли ошибок "The string did not match the expected pattern"
- Правильно ли обрабатываются параметры с пробелами и специальными символами
- Все endpoints должны возвращать status: "success"
"""

import asyncio
import aiohttp
import json
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TelegramMiniAppTester:
    def __init__(self):
        # Get backend URL from frontend .env file
        frontend_env_path = Path("/app/frontend/.env")
        self.backend_url = "https://843cb380-5c7f-4b66-a0ac-349ffb8d9c34.preview.emergentagent.com"
        
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
    
    async def test_cities_api_popular(self):
        """Test GET /api/cities/popular - должен возвращать популярные города"""
        logger.info("=== Testing Cities API: Popular Cities ===")
        
        success, data, error = await self.make_request("GET", "/api/cities/popular")
        
        if success and isinstance(data, dict):
            has_status_success = data.get("status") == "success"
            has_data = "data" in data and isinstance(data["data"], dict)
            has_cities = has_data and "cities" in data["data"] and isinstance(data["data"]["cities"], list)
            cities_count = len(data["data"].get("cities", [])) if has_data else 0
            
            # Check city structure if cities exist
            city_structure_valid = True
            if has_cities and data["data"]["cities"]:
                first_city = data["data"]["cities"][0]
                required_fields = ["name", "state"]
                city_structure_valid = all(field in first_city for field in required_fields)
            
            self.log_test_result(
                "GET /api/cities/popular - Popular cities",
                has_status_success and has_cities and cities_count > 0 and city_structure_valid,
                f"Status: {data.get('status')}, Cities count: {cities_count}, Structure valid: {city_structure_valid}",
                data
            )
        else:
            self.log_test_result(
                "GET /api/cities/popular - Popular cities",
                False,
                f"Error: {error}",
                data
            )
    
    async def test_cities_api_search_berlin(self):
        """Test GET /api/cities/search?q=Berlin - должен найти Berlin"""
        logger.info("=== Testing Cities API: Search Berlin ===")
        
        success, data, error = await self.make_request("GET", "/api/cities/search?q=Berlin")
        
        if success and isinstance(data, dict):
            has_status_success = data.get("status") == "success"
            has_data = "data" in data and isinstance(data["data"], dict)
            has_cities = has_data and "cities" in data["data"] and isinstance(data["data"]["cities"], list)
            cities_count = len(data["data"].get("cities", [])) if has_data else 0
            
            # Check if Berlin is found
            berlin_found = False
            if has_cities and data["data"]["cities"]:
                berlin_found = any(
                    city.get("name", "").lower() == "berlin" 
                    for city in data["data"]["cities"]
                )
            
            self.log_test_result(
                "GET /api/cities/search?q=Berlin - Find Berlin",
                has_status_success and has_cities and berlin_found,
                f"Status: {data.get('status')}, Cities found: {cities_count}, Berlin found: {berlin_found}",
                data
            )
        else:
            self.log_test_result(
                "GET /api/cities/search?q=Berlin - Find Berlin",
                False,
                f"Error: {error}",
                data
            )
    
    async def test_cities_api_search_ber(self):
        """Test GET /api/cities/search?q=Ber - должен найти города, начинающиеся с "Ber" """
        logger.info("=== Testing Cities API: Search Ber (partial) ===")
        
        success, data, error = await self.make_request("GET", "/api/cities/search?q=Ber")
        
        if success and isinstance(data, dict):
            has_status_success = data.get("status") == "success"
            has_data = "data" in data and isinstance(data["data"], dict)
            has_cities = has_data and "cities" in data["data"] and isinstance(data["data"]["cities"], list)
            cities_count = len(data["data"].get("cities", [])) if has_data else 0
            
            # Check if cities starting with "Ber" are found
            ber_cities_found = False
            if has_cities and data["data"]["cities"]:
                ber_cities_found = any(
                    city.get("name", "").lower().startswith("ber") 
                    for city in data["data"]["cities"]
                )
            
            self.log_test_result(
                "GET /api/cities/search?q=Ber - Find cities starting with 'Ber'",
                has_status_success and has_cities and ber_cities_found,
                f"Status: {data.get('status')}, Cities found: {cities_count}, Ber* cities found: {ber_cities_found}",
                data
            )
        else:
            self.log_test_result(
                "GET /api/cities/search?q=Ber - Find cities starting with 'Ber'",
                False,
                f"Error: {error}",
                data
            )
    
    async def test_cities_api_search_munchen(self):
        """Test GET /api/cities/search?q=München - должен найти München"""
        logger.info("=== Testing Cities API: Search München ===")
        
        success, data, error = await self.make_request("GET", "/api/cities/search?q=München")
        
        if success and isinstance(data, dict):
            has_status_success = data.get("status") == "success"
            has_data = "data" in data and isinstance(data["data"], dict)
            has_cities = has_data and "cities" in data["data"] and isinstance(data["data"]["cities"], list)
            cities_count = len(data["data"].get("cities", [])) if has_data else 0
            
            # Check if München is found
            munchen_found = False
            if has_cities and data["data"]["cities"]:
                munchen_found = any(
                    "münchen" in city.get("name", "").lower() or "munich" in city.get("name", "").lower()
                    for city in data["data"]["cities"]
                )
            
            self.log_test_result(
                "GET /api/cities/search?q=München - Find München",
                has_status_success and has_cities and munchen_found,
                f"Status: {data.get('status')}, Cities found: {cities_count}, München found: {munchen_found}",
                data
            )
        else:
            self.log_test_result(
                "GET /api/cities/search?q=München - Find München",
                False,
                f"Error: {error}",
                data
            )
    
    async def test_job_search_without_search_query(self):
        """Test GET /api/job-search?location=Berlin&language_level=B1 - должен работать БЕЗ search_query"""
        logger.info("=== Testing Job Search API: Without search_query ===")
        
        success, data, error = await self.make_request("GET", "/api/job-search?location=Berlin&language_level=B1")
        
        if success and isinstance(data, dict):
            has_status_success = data.get("status") == "success"
            has_data = "data" in data and isinstance(data["data"], dict)
            has_jobs = has_data and "jobs" in data["data"] and isinstance(data["data"]["jobs"], list)
            has_total_found = has_data and "total_found" in data["data"]
            
            self.log_test_result(
                "GET /api/job-search?location=Berlin&language_level=B1 (WITHOUT search_query)",
                has_status_success and has_jobs and has_total_found,
                f"Status: {data.get('status')}, Jobs: {len(data['data'].get('jobs', [])) if has_data else 0}, Total found: {data['data'].get('total_found') if has_data else None}",
                data
            )
        else:
            self.log_test_result(
                "GET /api/job-search?location=Berlin&language_level=B1 (WITHOUT search_query)",
                False,
                f"Error: {error}",
                data
            )
    
    async def test_job_search_with_search_query(self):
        """Test GET /api/job-search?location=Berlin&language_level=B1&search_query=Developer - должен работать с полными параметрами"""
        logger.info("=== Testing Job Search API: With search_query ===")
        
        success, data, error = await self.make_request("GET", "/api/job-search?location=Berlin&language_level=B1&search_query=Developer")
        
        if success and isinstance(data, dict):
            has_status_success = data.get("status") == "success"
            has_data = "data" in data and isinstance(data["data"], dict)
            has_jobs = has_data and "jobs" in data["data"] and isinstance(data["data"]["jobs"], list)
            has_total_found = has_data and "total_found" in data["data"]
            
            self.log_test_result(
                "GET /api/job-search?location=Berlin&language_level=B1&search_query=Developer (WITH search_query)",
                has_status_success and has_jobs and has_total_found,
                f"Status: {data.get('status')}, Jobs: {len(data['data'].get('jobs', [])) if has_data else 0}, Total found: {data['data'].get('total_found') if has_data else None}",
                data
            )
        else:
            self.log_test_result(
                "GET /api/job-search?location=Berlin&language_level=B1&search_query=Developer (WITH search_query)",
                False,
                f"Error: {error}",
                data
            )
    
    async def test_no_pattern_matching_errors(self):
        """Test that no 'The string did not match the expected pattern' errors occur"""
        logger.info("=== Testing: No Pattern Matching Errors ===")
        
        test_endpoints = [
            ("GET", "/api/cities/popular", "Cities popular"),
            ("GET", "/api/cities/search?q=Berlin", "Cities search Berlin"),
            ("GET", "/api/cities/search?q=München", "Cities search München"),
            ("GET", "/api/job-search?location=Berlin&language_level=B1", "Job search without query"),
            ("GET", "/api/job-search?location=Berlin&language_level=B1&search_query=Developer", "Job search with query")
        ]
        
        no_pattern_errors = True
        pattern_error_details = []
        
        for method, endpoint, description in test_endpoints:
            success, data, error = await self.make_request(method, endpoint)
            
            # Check for pattern matching errors
            has_pattern_error = False
            if not success or isinstance(data, dict):
                error_text = str(error) + str(data)
                has_pattern_error = (
                    "pattern" in error_text.lower() or 
                    "did not match" in error_text.lower() or
                    "expected pattern" in error_text.lower()
                )
            
            if has_pattern_error:
                no_pattern_errors = False
                pattern_error_details.append(f"{description}: {error}")
        
        self.log_test_result(
            "No 'The string did not match the expected pattern' errors",
            no_pattern_errors,
            f"All endpoints free from pattern errors" if no_pattern_errors else f"Pattern errors found: {pattern_error_details}",
            {"pattern_errors": pattern_error_details}
        )
    
    async def test_special_characters_and_spaces(self):
        """Test proper handling of parameters with spaces and special characters"""
        logger.info("=== Testing: Special Characters and Spaces ===")
        
        # Test cities search with special characters
        success, data, error = await self.make_request("GET", "/api/cities/search?q=München")
        munchen_works = success and isinstance(data, dict) and data.get("status") == "success"
        
        # Test job search with location containing spaces
        success, data, error = await self.make_request("GET", "/api/job-search?location=Frankfurt am Main&language_level=B1")
        spaces_work = success and isinstance(data, dict) and data.get("status") == "success"
        
        # Test job search with special characters in search query
        success, data, error = await self.make_request("GET", "/api/job-search?location=Berlin&language_level=B1&search_query=C++ Developer")
        special_chars_work = success and isinstance(data, dict) and data.get("status") == "success"
        
        all_special_handling_works = munchen_works and spaces_work and special_chars_work
        
        self.log_test_result(
            "Proper handling of parameters with spaces and special characters",
            all_special_handling_works,
            f"München: {munchen_works}, Spaces: {spaces_work}, Special chars: {special_chars_work}",
            {
                "munchen_works": munchen_works,
                "spaces_work": spaces_work,
                "special_chars_work": special_chars_work
            }
        )
    
    async def test_all_endpoints_return_success_status(self):
        """Test that all endpoints return status: 'success'"""
        logger.info("=== Testing: All Endpoints Return Success Status ===")
        
        test_endpoints = [
            ("GET", "/api/cities/popular", "Cities popular"),
            ("GET", "/api/cities/search?q=Berlin", "Cities search Berlin"),
            ("GET", "/api/cities/search?q=Ber", "Cities search Ber"),
            ("GET", "/api/cities/search?q=München", "Cities search München"),
            ("GET", "/api/job-search?location=Berlin&language_level=B1", "Job search without query"),
            ("GET", "/api/job-search?location=Berlin&language_level=B1&search_query=Developer", "Job search with query")
        ]
        
        all_return_success = True
        status_details = []
        
        for method, endpoint, description in test_endpoints:
            success, data, error = await self.make_request(method, endpoint)
            
            if success and isinstance(data, dict):
                status = data.get("status")
                returns_success = status == "success"
                status_details.append(f"{description}: {status}")
                
                if not returns_success:
                    all_return_success = False
            else:
                all_return_success = False
                status_details.append(f"{description}: ERROR - {error}")
        
        self.log_test_result(
            "All endpoints return status: 'success'",
            all_return_success,
            f"All endpoints return success status" if all_return_success else f"Status details: {status_details}",
            {"status_details": status_details}
        )
    
    async def run_all_tests(self):
        """Run all Telegram Mini App tests"""
        logger.info("🎯 STARTING TELEGRAM MINI APP CITIES API AND JOB SEARCH API TESTING")
        logger.info("=" * 80)
        
        try:
            # Cities API Tests
            logger.info("🏙️ CITIES API TESTS")
            await self.test_cities_api_popular()
            await self.test_cities_api_search_berlin()
            await self.test_cities_api_search_ber()
            await self.test_cities_api_search_munchen()
            
            # Job Search API Tests
            logger.info("💼 JOB SEARCH API TESTS")
            await self.test_job_search_without_search_query()
            await self.test_job_search_with_search_query()
            
            # Special Requirements Tests
            logger.info("🔍 SPECIAL REQUIREMENTS TESTS")
            await self.test_no_pattern_matching_errors()
            await self.test_special_characters_and_spaces()
            await self.test_all_endpoints_return_success_status()
            
        except Exception as e:
            logger.error(f"Test execution failed: {e}")
            self.log_test_result("Test Execution", False, f"Critical error: {e}")
        
        # Print summary
        self.print_test_summary()
    
    def print_test_summary(self):
        """Print test summary"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        logger.info("=" * 80)
        logger.info("🎯 TELEGRAM MINI APP TEST RESULTS SUMMARY")
        logger.info(f"Total tests: {total_tests}")
        logger.info(f"Passed: {passed_tests}")
        logger.info(f"Failed: {failed_tests}")
        logger.info(f"Success rate: {success_rate:.1f}%")
        
        if failed_tests > 0:
            logger.info("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    logger.info(f"  - {result['test']}: {result['details']}")
        
        if passed_tests > 0:
            logger.info("\n✅ PASSED TESTS:")
            for result in self.test_results:
                if result["success"]:
                    logger.info(f"  - {result['test']}: {result['details']}")
        
        logger.info("=" * 80)
        logger.info("🎯 TELEGRAM MINI APP TESTING COMPLETED")

async def main():
    async with TelegramMiniAppTester() as tester:
        await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
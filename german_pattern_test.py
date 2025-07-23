#!/usr/bin/env python3
"""
🎯 КРИТИЧЕСКОЕ ТЕСТИРОВАНИЕ: Проблема с немецкими городами и pattern matching ошибками

КОНТЕКСТ ПРОБЛЕМЫ:
- Пользователь сообщает об ошибке "The string did not match the expected pattern" 
- Проблема возникает при вводе немецких городов (Köln, München, Düsseldorf)
- Проблема возникает при поиске работы с параметрами location=Köln&language_level=B1

ЗАДАЧИ ДЛЯ ТЕСТИРОВАНИЯ:
1. Протестировать cities API с немецкими символами
2. Протестировать job search API с проблематичными параметрами  
3. Найти источник pattern matching ошибок
4. Проверить encoding немецких символов (ö, ü, ä, ß)
5. Получить полные stack traces для диагностики

ЦЕЛЬ: Найти точный источник ошибки "The string did not match the expected pattern"
"""

import asyncio
import aiohttp
import json
import logging
from pathlib import Path
import urllib.parse

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GermanPatternTester:
    def __init__(self):
        # Get backend URL from frontend .env file
        frontend_env_path = Path("/app/frontend/.env")
        self.backend_url = "https://6ad8821c-85b0-472c-8a4a-cb6f9c2bb16a.preview.emergentagent.com"
        
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
    
    def log_test_result(self, test_name: str, success: bool, details: str = "", response_data: any = None, error_details: str = ""):
        """Log test result with detailed error information"""
        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"{status} - {test_name}: {details}")
        
        if error_details:
            logger.error(f"ERROR DETAILS: {error_details}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "response_data": response_data,
            "error_details": error_details
        })
    
    async def make_request(self, method: str, endpoint: str, **kwargs) -> tuple[bool, any, str, str]:
        """Make HTTP request and return success, data, error, full_error_details"""
        try:
            url = f"{self.backend_url}{endpoint}"
            logger.info(f"Making {method} request to: {url}")
            
            async with self.session.request(method, url, **kwargs) as response:
                try:
                    data = await response.json()
                except:
                    data = await response.text()
                
                # Log response details
                logger.info(f"Response status: {response.status}")
                logger.info(f"Response headers: {dict(response.headers)}")
                
                if response.status < 400:
                    return True, data, "", ""
                else:
                    error_msg = f"HTTP {response.status}"
                    full_error = f"HTTP {response.status} - URL: {url} - Response: {data}"
                    return False, data, error_msg, full_error
                    
        except Exception as e:
            error_msg = str(e)
            full_error = f"Exception: {str(e)} - URL: {url if 'url' in locals() else endpoint}"
            logger.error(f"Request exception: {full_error}")
            return False, None, error_msg, full_error
    
    async def test_german_cities_search(self):
        """🎯 КРИТИЧЕСКИЙ ТЕСТ: Cities API с немецкими символами"""
        logger.info("=== 🎯 КРИТИЧЕСКИЙ ТЕСТ: Cities API с немецкими символами ===")
        
        # Test cases with German characters
        german_cities_tests = [
            ("Köln", "Cologne with ö umlaut"),
            ("München", "Munich with ü umlaut"), 
            ("Düsseldorf", "Düsseldorf with ü umlaut"),
            ("K", "Single character K"),
            ("Kö", "K with ö umlaut"),
            ("Mü", "Mü with ü umlaut"),
            ("Dü", "Dü with ü umlaut")
        ]
        
        for city_query, description in german_cities_tests:
            # Test with URL encoding
            encoded_query = urllib.parse.quote(city_query, safe='')
            endpoint = f"/api/cities/search?q={encoded_query}"
            
            success, data, error, full_error = await self.make_request("GET", endpoint)
            
            if success and isinstance(data, dict):
                has_status = "status" in data
                status_value = data.get("status")
                has_cities = "cities" in data and isinstance(data["cities"], list)
                cities_count = len(data.get("cities", []))
                
                # Check for pattern matching errors in response
                pattern_error = False
                if isinstance(data, dict):
                    data_str = str(data).lower()
                    pattern_error = "pattern" in data_str and ("match" in data_str or "matching" in data_str)
                
                self.log_test_result(
                    f"🎯 Cities search: {city_query} ({description})",
                    has_status and status_value == "success" and not pattern_error,
                    f"Status: {status_value}, Cities found: {cities_count}, Pattern error: {pattern_error}",
                    data,
                    full_error if pattern_error else ""
                )
            else:
                # Check if error contains pattern matching information
                pattern_error = False
                if isinstance(data, (dict, str)):
                    data_str = str(data).lower()
                    pattern_error = "pattern" in data_str and ("match" in data_str or "matching" in data_str)
                
                self.log_test_result(
                    f"🎯 Cities search: {city_query} ({description})",
                    False,
                    f"ОШИБКА: {error}. Pattern error detected: {pattern_error}",
                    data,
                    full_error
                )
    
    async def test_job_search_with_german_params(self):
        """🎯 КРИТИЧЕСКИЙ ТЕСТ: Job Search API с немецкими параметрами"""
        logger.info("=== 🎯 КРИТИЧЕСКИЙ ТЕСТ: Job Search API с немецкими параметрами ===")
        
        # Test cases that user reported as problematic
        job_search_tests = [
            {
                "params": {"location": "Köln", "language_level": "B1"},
                "description": "Köln + B1 (user reported issue)"
            },
            {
                "params": {"location": "München", "language_level": "B1"},
                "description": "München + B1"
            },
            {
                "params": {"location": "Düsseldorf", "language_level": "B1"},
                "description": "Düsseldorf + B1"
            },
            {
                "params": {"location": "Köln", "language_level": "A2"},
                "description": "Köln + A2"
            },
            {
                "params": {"location": "München", "language_level": "C1"},
                "description": "München + C1"
            }
        ]
        
        for test_case in job_search_tests:
            params = test_case["params"]
            description = test_case["description"]
            
            # Test GET request with URL parameters
            query_params = "&".join([f"{k}={urllib.parse.quote(str(v))}" for k, v in params.items()])
            endpoint = f"/api/job-search?{query_params}"
            
            success, data, error, full_error = await self.make_request("GET", endpoint)
            
            if success and isinstance(data, dict):
                has_status = "status" in data
                status_value = data.get("status")
                has_jobs = "jobs" in data
                
                # Check for pattern matching errors
                pattern_error = self.check_pattern_error(data)
                
                self.log_test_result(
                    f"🎯 Job search GET: {description}",
                    has_status and status_value == "success" and not pattern_error,
                    f"Status: {status_value}, Has jobs: {has_jobs}, Pattern error: {pattern_error}",
                    data,
                    full_error if pattern_error else ""
                )
            else:
                pattern_error = self.check_pattern_error(data)
                
                self.log_test_result(
                    f"🎯 Job search GET: {description}",
                    False,
                    f"ОШИБКА: {error}. Pattern error detected: {pattern_error}",
                    data,
                    full_error
                )
            
            # Test POST request with JSON body
            success, data, error, full_error = await self.make_request("POST", "/api/job-search", json=params)
            
            if success and isinstance(data, dict):
                has_status = "status" in data
                status_value = data.get("status")
                has_jobs = "jobs" in data
                
                # Check for pattern matching errors
                pattern_error = self.check_pattern_error(data)
                
                self.log_test_result(
                    f"🎯 Job search POST: {description}",
                    has_status and status_value == "success" and not pattern_error,
                    f"Status: {status_value}, Has jobs: {has_jobs}, Pattern error: {pattern_error}",
                    data,
                    full_error if pattern_error else ""
                )
            else:
                pattern_error = self.check_pattern_error(data)
                
                self.log_test_result(
                    f"🎯 Job search POST: {description}",
                    False,
                    f"ОШИБКА: {error}. Pattern error detected: {pattern_error}",
                    data,
                    full_error
                )
    
    def check_pattern_error(self, data) -> bool:
        """Check if response contains pattern matching error"""
        if not data:
            return False
            
        data_str = str(data).lower()
        
        # Look for specific error messages that indicate pattern matching issues
        pattern_error_phrases = [
            "string did not match the expected pattern",
            "pattern matching error",
            "regex error",
            "regular expression error",
            "invalid pattern",
            "pattern compilation failed"
        ]
        
        return any(phrase in data_str for phrase in pattern_error_phrases)
    
    async def test_encoding_issues(self):
        """🎯 КРИТИЧЕСКИЙ ТЕСТ: Проблемы с encoding немецких символов"""
        logger.info("=== 🎯 КРИТИЧЕСКИЙ ТЕСТ: Проблемы с encoding немецких символов ===")
        
        # Test different encoding approaches
        test_string = "Köln"
        
        encoding_tests = [
            (test_string, "UTF-8 direct"),
            (test_string.encode('utf-8').decode('utf-8'), "UTF-8 encode/decode"),
            (urllib.parse.quote(test_string), "URL encoded"),
            (urllib.parse.quote(test_string, safe=''), "URL encoded (no safe chars)"),
            (test_string.encode('latin1', errors='ignore').decode('latin1'), "Latin1 fallback")
        ]
        
        for encoded_string, description in encoding_tests:
            try:
                endpoint = f"/api/cities/search?q={encoded_string}"
                success, data, error, full_error = await self.make_request("GET", endpoint)
                
                if success and isinstance(data, dict):
                    status_value = data.get("status")
                    cities_count = len(data.get("cities", []))
                    pattern_error = self.check_pattern_error(data)
                    
                    self.log_test_result(
                        f"🎯 Encoding test: {description}",
                        status_value == "success" and not pattern_error,
                        f"Encoded as: '{encoded_string}', Status: {status_value}, Cities: {cities_count}, Pattern error: {pattern_error}",
                        data,
                        full_error if pattern_error else ""
                    )
                else:
                    pattern_error = self.check_pattern_error(data)
                    
                    self.log_test_result(
                        f"🎯 Encoding test: {description}",
                        False,
                        f"Encoded as: '{encoded_string}', Error: {error}, Pattern error: {pattern_error}",
                        data,
                        full_error
                    )
            except Exception as e:
                self.log_test_result(
                    f"🎯 Encoding test: {description}",
                    False,
                    f"Exception during encoding test: {str(e)}",
                    None,
                    str(e)
                )
    
    async def test_special_characters_comprehensive(self):
        """🎯 КРИТИЧЕСКИЙ ТЕСТ: Comprehensive test of German special characters"""
        logger.info("=== 🎯 КРИТИЧЕСКИЙ ТЕСТ: Comprehensive German special characters ===")
        
        # Test all German special characters
        special_chars_tests = [
            ("ä", "a-umlaut"),
            ("ö", "o-umlaut"), 
            ("ü", "u-umlaut"),
            ("Ä", "A-umlaut"),
            ("Ö", "O-umlaut"),
            ("Ü", "U-umlaut"),
            ("ß", "eszett/sharp-s"),
            ("Köln", "Full city name with ö"),
            ("München", "Full city name with ü"),
            ("Düsseldorf", "Full city name with ü"),
            ("Würzburg", "City with ü"),
            ("Nürnberg", "City with ü"),
            ("Lübeck", "City with ü")
        ]
        
        for char_test, description in special_chars_tests:
            endpoint = f"/api/cities/search?q={urllib.parse.quote(char_test)}"
            success, data, error, full_error = await self.make_request("GET", endpoint)
            
            if success and isinstance(data, dict):
                status_value = data.get("status")
                pattern_error = self.check_pattern_error(data)
                
                self.log_test_result(
                    f"🎯 Special char: {char_test} ({description})",
                    status_value == "success" and not pattern_error,
                    f"Status: {status_value}, Pattern error: {pattern_error}",
                    data,
                    full_error if pattern_error else ""
                )
            else:
                pattern_error = self.check_pattern_error(data)
                
                self.log_test_result(
                    f"🎯 Special char: {char_test} ({description})",
                    False,
                    f"Error: {error}, Pattern error: {pattern_error}",
                    data,
                    full_error
                )
    
    async def test_backend_health_first(self):
        """Test backend health before running pattern tests"""
        logger.info("=== Testing Backend Health First ===")
        
        # Test basic health
        success, data, error, full_error = await self.make_request("GET", "/health")
        
        if success:
            self.log_test_result(
                "Backend Health Check",
                True,
                f"Backend is healthy: {data}",
                data
            )
        else:
            self.log_test_result(
                "Backend Health Check",
                False,
                f"Backend health check failed: {error}",
                data,
                full_error
            )
        
        # Test API health
        success, data, error, full_error = await self.make_request("GET", "/api/health")
        
        if success:
            self.log_test_result(
                "API Health Check",
                True,
                f"API is healthy: {data}",
                data
            )
        else:
            self.log_test_result(
                "API Health Check", 
                False,
                f"API health check failed: {error}",
                data,
                full_error
            )
    
    async def run_all_tests(self):
        """Run all German pattern matching tests"""
        logger.info("🎯 STARTING GERMAN PATTERN MATCHING TESTS")
        
        # Test backend health first
        await self.test_backend_health_first()
        
        # Run specific pattern matching tests
        await self.test_german_cities_search()
        await self.test_job_search_with_german_params()
        await self.test_encoding_issues()
        await self.test_special_characters_comprehensive()
        
        # Print summary
        self.print_test_summary()
    
    def print_test_summary(self):
        """Print comprehensive test summary"""
        logger.info("=" * 80)
        logger.info("🎯 GERMAN PATTERN MATCHING TEST SUMMARY")
        logger.info("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        logger.info(f"Total tests: {total_tests}")
        logger.info(f"Passed: {passed_tests}")
        logger.info(f"Failed: {failed_tests}")
        logger.info(f"Success rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Show failed tests with pattern errors
        pattern_error_tests = []
        for result in self.test_results:
            if not result["success"] and result.get("error_details"):
                if "pattern" in result["error_details"].lower():
                    pattern_error_tests.append(result)
        
        if pattern_error_tests:
            logger.error("🚨 PATTERN MATCHING ERRORS FOUND:")
            for result in pattern_error_tests:
                logger.error(f"  - {result['test']}: {result['details']}")
                logger.error(f"    Full error: {result['error_details']}")
        else:
            logger.info("✅ NO PATTERN MATCHING ERRORS DETECTED")
        
        # Show all failed tests
        failed_test_results = [result for result in self.test_results if not result["success"]]
        if failed_test_results:
            logger.warning("❌ FAILED TESTS:")
            for result in failed_test_results:
                logger.warning(f"  - {result['test']}: {result['details']}")
        
        logger.info("=" * 80)

async def main():
    """Main test execution"""
    async with GermanPatternTester() as tester:
        await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
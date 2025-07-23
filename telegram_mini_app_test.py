#!/usr/bin/env python3
"""
🎯 КРИТИЧЕСКОЕ ТЕСТИРОВАНИЕ: Telegram Mini App Job Search API endpoints
Специфический тест для пользовательского запроса

ЗАДАЧИ:
1. Cities API тестирование:
   - GET /api/cities/popular - должен возвращать популярные города
   - GET /api/cities/search?q=Ber - поиск городов начинающихся с "Ber"
   - GET /api/cities/search?q=Köln - поиск города с немецкими символами
   - GET /api/cities/search?q=Köl - частичный поиск как на скриншоте

2. Job Search API тестирование:
   - GET /api/job-search?location=Berlin&language_level=B1 (без search_query)
   - GET /api/job-search?location=München&language_level=A2&search_query=Developer
   - Убедиться что нет pattern matching ошибок

3. Проверить все ответы:
   - status должен быть 'success'
   - data структура должна быть корректной
   - никаких pattern errors в ответах
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
        self.backend_url = "https://6ad8821c-85b0-472c-8a4a-cb6f9c2bb16a.preview.emergentagent.com"
        
        if frontend_env_path.exists():
            with open(frontend_env_path, 'r') as f:
                for line in f:
                    if line.startswith('REACT_APP_BACKEND_URL='):
                        self.backend_url = line.split('=', 1)[1].strip()
                        break
        
        logger.info(f"🎯 Testing Telegram Mini App backend at: {self.backend_url}")
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
    
    async def test_cities_api(self):
        """🎯 1. Cities API тестирование"""
        logger.info("=== 🎯 1. Cities API тестирование ===")
        
        # GET /api/cities/popular - должен возвращать популярные города
        success, data, error = await self.make_request("GET", "/api/cities/popular")
        
        if success and isinstance(data, dict):
            has_status = data.get("status") == "success"
            has_cities = "data" in data and "cities" in data["data"] and isinstance(data["data"]["cities"], list)
            cities_count = len(data.get("data", {}).get("cities", []))
            
            self.log_test_result(
                "GET /api/cities/popular - популярные города",
                has_status and has_cities and cities_count > 0,
                f"Status: {data.get('status')}, Cities count: {cities_count}",
                data
            )
        else:
            self.log_test_result(
                "GET /api/cities/popular - популярные города",
                False,
                f"ОШИБКА: {error}",
                data
            )
        
        # GET /api/cities/search?q=Ber - поиск городов начинающихся с "Ber"
        success, data, error = await self.make_request("GET", "/api/cities/search?q=Ber")
        
        if success and isinstance(data, dict):
            has_status = data.get("status") == "success"
            has_cities = "data" in data and "cities" in data["data"] and isinstance(data["data"]["cities"], list)
            cities_count = len(data.get("data", {}).get("cities", []))
            
            # Check if cities starting with "Ber" are found
            ber_cities_found = False
            if data.get("data", {}).get("cities"):
                ber_cities_found = any(city.get("name", "").lower().startswith("ber") for city in data["data"]["cities"])
            
            self.log_test_result(
                "GET /api/cities/search?q=Ber - поиск городов начинающихся с 'Ber'",
                has_status and has_cities and ber_cities_found,
                f"Status: {data.get('status')}, Cities found: {cities_count}, Ber cities found: {ber_cities_found}",
                data
            )
        else:
            self.log_test_result(
                "GET /api/cities/search?q=Ber - поиск городов начинающихся с 'Ber'",
                False,
                f"ОШИБКА: {error}",
                data
            )
        
        # GET /api/cities/search?q=Köln - поиск города с немецкими символами
        success, data, error = await self.make_request("GET", "/api/cities/search?q=Köln")
        
        if success and isinstance(data, dict):
            has_status = data.get("status") == "success"
            has_cities = "data" in data and "cities" in data["data"] and isinstance(data["data"]["cities"], list)
            cities_count = len(data.get("data", {}).get("cities", []))
            
            # Check if Köln is found with German symbols
            koln_found = False
            if data.get("data", {}).get("cities"):
                koln_found = any("köln" in city.get("name", "").lower() for city in data["data"]["cities"])
            
            self.log_test_result(
                "GET /api/cities/search?q=Köln - поиск города с немецкими символами",
                has_status and has_cities and koln_found,
                f"Status: {data.get('status')}, Cities found: {cities_count}, Köln found: {koln_found}",
                data
            )
        else:
            self.log_test_result(
                "GET /api/cities/search?q=Köln - поиск города с немецкими символами",
                False,
                f"ОШИБКА: {error}",
                data
            )
        
        # GET /api/cities/search?q=Köl - частичный поиск как на скриншоте
        success, data, error = await self.make_request("GET", "/api/cities/search?q=Köl")
        
        if success and isinstance(data, dict):
            has_status = data.get("status") == "success"
            has_cities = "data" in data and "cities" in data["data"] and isinstance(data["data"]["cities"], list)
            cities_count = len(data.get("data", {}).get("cities", []))
            
            # Check if partial search for Köl works
            kol_found = False
            if data.get("data", {}).get("cities"):
                kol_found = any("köl" in city.get("name", "").lower() for city in data["data"]["cities"])
            
            self.log_test_result(
                "GET /api/cities/search?q=Köl - частичный поиск как на скриншоте",
                has_status and has_cities and kol_found,
                f"Status: {data.get('status')}, Cities found: {cities_count}, Köl partial match found: {kol_found}",
                data
            )
        else:
            self.log_test_result(
                "GET /api/cities/search?q=Köl - частичный поиск как на скриншоте",
                False,
                f"ОШИБКА: {error}",
                data
            )
    
    async def test_job_search_api(self):
        """🎯 2. Job Search API тестирование"""
        logger.info("=== 🎯 2. Job Search API тестирование ===")
        
        # GET /api/job-search?location=Berlin&language_level=B1 (без search_query)
        success, data, error = await self.make_request("GET", "/api/job-search?location=Berlin&language_level=B1")
        
        if success and isinstance(data, dict):
            has_status = data.get("status") == "success"
            has_jobs = "data" in data and "jobs" in data["data"] and isinstance(data["data"]["jobs"], list)
            no_pattern_error = "pattern" not in str(data).lower() and "string did not match" not in str(data).lower()
            
            self.log_test_result(
                "GET /api/job-search?location=Berlin&language_level=B1 (без search_query)",
                has_status and has_jobs and no_pattern_error,
                f"Status: {data.get('status')}, Jobs: {len(data.get('data', {}).get('jobs', []))}, No pattern errors: {no_pattern_error}",
                data
            )
        else:
            pattern_error_detected = "pattern" in str(error).lower() or "string did not match" in str(error).lower()
            self.log_test_result(
                "GET /api/job-search?location=Berlin&language_level=B1 (без search_query)",
                False,
                f"ОШИБКА: {error}, Pattern error detected: {pattern_error_detected}",
                data
            )
        
        # GET /api/job-search?location=München&language_level=A2&search_query=Developer
        success, data, error = await self.make_request("GET", "/api/job-search?location=München&language_level=A2&search_query=Developer")
        
        if success and isinstance(data, dict):
            has_status = data.get("status") == "success"
            has_jobs = "data" in data and "jobs" in data["data"] and isinstance(data["data"]["jobs"], list)
            no_pattern_error = "pattern" not in str(data).lower() and "string did not match" not in str(data).lower()
            
            self.log_test_result(
                "GET /api/job-search?location=München&language_level=A2&search_query=Developer",
                has_status and has_jobs and no_pattern_error,
                f"Status: {data.get('status')}, Jobs: {len(data.get('data', {}).get('jobs', []))}, No pattern errors: {no_pattern_error}",
                data
            )
        else:
            pattern_error_detected = "pattern" in str(error).lower() or "string did not match" in str(error).lower()
            self.log_test_result(
                "GET /api/job-search?location=München&language_level=A2&search_query=Developer",
                False,
                f"ОШИБКА: {error}, Pattern error detected: {pattern_error_detected}",
                data
            )
    
    async def test_response_validation(self):
        """🎯 3. Проверить все ответы"""
        logger.info("=== 🎯 3. Проверка всех ответов ===")
        
        # Test additional job search scenarios to ensure no pattern matching errors
        test_scenarios = [
            ("Berlin", "B1", None, "Berlin B1 без search_query"),
            ("München", "A2", "Developer", "München A2 с Developer"),
            ("Hamburg", "C1", None, "Hamburg C1 без search_query"),
            ("Frankfurt am Main", "B2", "Engineer", "Frankfurt с пробелами и Engineer"),
            ("Köln", "B1", None, "Köln с умлаутом без search_query")
        ]
        
        all_responses_valid = True
        pattern_errors_found = []
        
        for location, language_level, search_query, description in test_scenarios:
            # Build URL
            url = f"/api/job-search?location={location}&language_level={language_level}"
            if search_query:
                url += f"&search_query={search_query}"
            
            success, data, error = await self.make_request("GET", url)
            
            if success and isinstance(data, dict):
                has_status = data.get("status") == "success"
                has_correct_structure = "data" in data and "jobs" in data["data"] and isinstance(data["data"]["jobs"], list)
                no_pattern_error = "pattern" not in str(data).lower() and "string did not match" not in str(data).lower()
                
                if not (has_status and has_correct_structure and no_pattern_error):
                    all_responses_valid = False
                    if not no_pattern_error:
                        pattern_errors_found.append(description)
                
                self.log_test_result(
                    f"Response validation: {description}",
                    has_status and has_correct_structure and no_pattern_error,
                    f"Status: {data.get('status')}, Structure OK: {has_correct_structure}, No pattern errors: {no_pattern_error}",
                    data
                )
            else:
                all_responses_valid = False
                pattern_error_detected = "pattern" in str(error).lower() or "string did not match" in str(error).lower()
                if pattern_error_detected:
                    pattern_errors_found.append(description)
                
                self.log_test_result(
                    f"Response validation: {description}",
                    False,
                    f"ОШИБКА: {error}, Pattern error: {pattern_error_detected}",
                    data
                )
        
        # Final summary
        self.log_test_result(
            "🎯 ИТОГОВЫЙ РЕЗУЛЬТАТ: Все ответы валидны и без pattern errors",
            all_responses_valid and len(pattern_errors_found) == 0,
            f"Все ответы валидны: {all_responses_valid}, Pattern errors найдено: {len(pattern_errors_found)} в {pattern_errors_found}",
            {"all_valid": all_responses_valid, "pattern_errors": pattern_errors_found}
        )
    
    async def run_all_tests(self):
        """Запустить все тесты для Telegram Mini App Job Search API"""
        logger.info("🎯 НАЧАЛО ТЕСТИРОВАНИЯ: Telegram Mini App Job Search API endpoints")
        logger.info("=" * 80)
        
        try:
            await self.test_cities_api()
            await self.test_job_search_api()
            await self.test_response_validation()
            
        except Exception as e:
            logger.error(f"Critical error during testing: {e}")
            self.log_test_result("Test Execution", False, f"Critical error: {e}", None)
        
        # Generate summary
        self.generate_summary()
    
    def generate_summary(self):
        """Generate test summary"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        logger.info("=" * 80)
        logger.info("🎯 TELEGRAM MINI APP JOB SEARCH API TESTING COMPLETED")
        logger.info(f"📊 OVERALL RESULTS: {passed_tests}/{total_tests} tests passed ({success_rate:.1f}% success)")
        logger.info(f"✅ Passed: {passed_tests}")
        logger.info(f"❌ Failed: {failed_tests}")
        logger.info("=" * 80)
        
        # Show failed tests
        if failed_tests > 0:
            logger.info("❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    logger.info(f"   - {result['test']}: {result['details']}")
        
        # Show passed tests
        if passed_tests > 0:
            logger.info("✅ PASSED TESTS:")
            for result in self.test_results:
                if result["success"]:
                    logger.info(f"   - {result['test']}: {result['details']}")
        
        logger.info("=" * 80)
        
        # Specific conclusions for user request
        cities_api_working = any("cities" in result["test"].lower() and result["success"] for result in self.test_results)
        job_search_working = any("job-search" in result["test"].lower() and result["success"] for result in self.test_results)
        no_pattern_errors = not any("pattern error detected: True" in result["details"] for result in self.test_results)
        
        logger.info("🎯 ВЫВОДЫ ПО ПОЛЬЗОВАТЕЛЬСКОМУ ЗАПРОСУ:")
        logger.info(f"   - Cities API работает: {'✅ ДА' if cities_api_working else '❌ НЕТ'}")
        logger.info(f"   - Job Search API работает: {'✅ ДА' if job_search_working else '❌ НЕТ'}")
        logger.info(f"   - Нет pattern matching ошибок: {'✅ ДА' if no_pattern_errors else '❌ НЕТ'}")
        logger.info("=" * 80)

async def main():
    async with TelegramMiniAppTester() as tester:
        await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
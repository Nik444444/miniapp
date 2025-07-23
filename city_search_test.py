#!/usr/bin/env python3
"""
🎯 КРИТИЧЕСКОЕ ТЕСТИРОВАНИЕ: City Search функциональность (NEW FEATURE)

НОВАЯ ФУНКЦИОНАЛЬНОСТЬ ДЛЯ ТЕСТИРОВАНИЯ:
1. GET /api/cities/search?q=Berlin - поиск конкретного города  
2. GET /api/cities/search?q=Mun - частичный поиск
3. GET /api/cities/popular - популярные города
4. GET /api/cities/info/Berlin - информация о городе

ФОКУС: Убедиться что новая City Search функциональность работает корректно.
"""

import asyncio
import aiohttp
import json
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CitySearchTester:
    def __init__(self):
        # Get backend URL from frontend .env file
        frontend_env_path = Path("/app/frontend/.env")
        self.backend_url = "https://miniapp-wvsxfa.fly.dev"
        
        if frontend_env_path.exists():
            with open(frontend_env_path, 'r') as f:
                for line in f:
                    if line.startswith('REACT_APP_BACKEND_URL='):
                        self.backend_url = line.split('=', 1)[1].strip()
                        break
            
        logger.info(f"Testing City Search at: {self.backend_url}")
        
        self.session = None
        self.test_results = []
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def log_test_result(self, test_name: str, success: bool, details: str = "", response_data=None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"{status} - {test_name}: {details}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "response_data": response_data
        })
    
    async def make_request(self, method: str, endpoint: str, **kwargs):
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
    
    async def test_city_search_specific_city(self):
        """🎯 NEW FEATURE: City Search - поиск конкретного города"""
        logger.info("=== 🎯 NEW FEATURE: City Search - Specific City ===")
        
        # Test GET /api/cities/search?q=Berlin
        success, data, error = await self.make_request("GET", "/api/cities/search?q=Berlin")
        
        if success and isinstance(data, dict):
            has_status = "status" in data
            has_cities = "cities" in data and isinstance(data["cities"], list)
            has_total = "total" in data
            
            # Check if Berlin is found
            cities = data.get("cities", [])
            berlin_found = any(city.get("name") == "Berlin" for city in cities)
            
            # Check city structure
            city_structure_valid = True
            if cities:
                first_city = cities[0]
                required_fields = ["name", "state", "population", "type"]
                city_structure_valid = all(field in first_city for field in required_fields)
            
            self.log_test_result(
                "🎯 GET /api/cities/search?q=Berlin - Find specific city",
                has_status and has_cities and has_total and berlin_found and city_structure_valid,
                f"Status: {data.get('status')}, Cities: {len(cities)}, Berlin found: {berlin_found}, Structure valid: {city_structure_valid}",
                data
            )
        else:
            self.log_test_result(
                "🎯 GET /api/cities/search?q=Berlin - Find specific city",
                False,
                f"City search failed: {error}",
                data
            )
    
    async def test_city_search_partial(self):
        """🎯 NEW FEATURE: City Search - частичный поиск"""
        logger.info("=== 🎯 NEW FEATURE: City Search - Partial Search ===")
        
        # Test GET /api/cities/search?q=Mun (should find München/Munich)
        success, data, error = await self.make_request("GET", "/api/cities/search?q=Mun")
        
        if success and isinstance(data, dict):
            cities = data.get("cities", [])
            munich_found = any(
                "München" in city.get("name", "") or 
                "Munich" in str(city.get("aliases", [])) or
                city.get("name") == "München"
                for city in cities
            )
            
            # Check if partial search returns relevant results
            has_results = len(cities) > 0
            
            self.log_test_result(
                "🎯 GET /api/cities/search?q=Mun - Partial search",
                has_results and munich_found,
                f"Cities found: {len(cities)}, Munich/München found: {munich_found}",
                data
            )
        else:
            self.log_test_result(
                "🎯 GET /api/cities/search?q=Mun - Partial search",
                False,
                f"Partial search failed: {error}",
                data
            )
        
        # Test another partial search
        success, data, error = await self.make_request("GET", "/api/cities/search?q=Ham")
        
        if success and isinstance(data, dict):
            cities = data.get("cities", [])
            hamburg_found = any("Hamburg" in city.get("name", "") for city in cities)
            
            self.log_test_result(
                "🎯 GET /api/cities/search?q=Ham - Partial search Hamburg",
                hamburg_found,
                f"Cities found: {len(cities)}, Hamburg found: {hamburg_found}",
                data
            )
        else:
            self.log_test_result(
                "🎯 GET /api/cities/search?q=Ham - Partial search Hamburg",
                False,
                f"Hamburg partial search failed: {error}",
                data
            )
    
    async def test_popular_cities(self):
        """🎯 NEW FEATURE: Popular Cities"""
        logger.info("=== 🎯 NEW FEATURE: Popular Cities ===")
        
        # Test GET /api/cities/popular
        success, data, error = await self.make_request("GET", "/api/cities/popular")
        
        if success and isinstance(data, dict):
            has_status = "status" in data
            has_cities = "cities" in data and isinstance(data["cities"], list)
            has_total = "total" in data
            
            cities = data.get("cities", [])
            has_major_cities = len(cities) >= 5  # Should have at least 5 popular cities
            
            # Check if major cities are included
            major_cities_found = []
            expected_major_cities = ["Berlin", "Hamburg", "München", "Köln", "Frankfurt am Main"]
            
            for city in cities:
                city_name = city.get("name", "")
                if city_name in expected_major_cities:
                    major_cities_found.append(city_name)
            
            # Check city structure
            city_structure_valid = True
            if cities:
                first_city = cities[0]
                required_fields = ["name", "state", "population", "type"]
                city_structure_valid = all(field in first_city for field in required_fields)
            
            self.log_test_result(
                "🎯 GET /api/cities/popular - Popular cities",
                has_status and has_cities and has_total and has_major_cities and city_structure_valid,
                f"Status: {data.get('status')}, Cities: {len(cities)}, Major cities: {major_cities_found}, Structure valid: {city_structure_valid}",
                data
            )
        else:
            self.log_test_result(
                "🎯 GET /api/cities/popular - Popular cities",
                False,
                f"Popular cities failed: {error}",
                data
            )
    
    async def test_city_info(self):
        """🎯 NEW FEATURE: City Information"""
        logger.info("=== 🎯 NEW FEATURE: City Information ===")
        
        # Test GET /api/cities/info/Berlin
        success, data, error = await self.make_request("GET", "/api/cities/info/Berlin")
        
        if success and isinstance(data, dict):
            has_status = "status" in data
            has_city_info = "city" in data and isinstance(data["city"], dict)
            
            if has_city_info:
                city_info = data["city"]
                has_name = "name" in city_info
                has_state = "state" in city_info
                has_population = "population" in city_info
                has_job_market = "job_market_info" in city_info
                
                # Check job market info structure
                job_market_valid = False
                if has_job_market:
                    job_market = city_info["job_market_info"]
                    if isinstance(job_market, dict):
                        required_job_fields = ["market_size", "main_industries", "avg_salary_range", "job_opportunities"]
                        job_market_valid = all(field in job_market for field in required_job_fields)
                
                city_info_complete = has_name and has_state and has_population and has_job_market and job_market_valid
            else:
                city_info_complete = False
            
            self.log_test_result(
                "🎯 GET /api/cities/info/Berlin - City information",
                has_status and has_city_info and city_info_complete,
                f"Status: {data.get('status')}, City info complete: {city_info_complete}, Job market info: {job_market_valid if has_city_info else False}",
                data
            )
        else:
            self.log_test_result(
                "🎯 GET /api/cities/info/Berlin - City information",
                False,
                f"City info failed: {error}",
                data
            )
        
        # Test another city
        success, data, error = await self.make_request("GET", "/api/cities/info/München")
        
        if success and isinstance(data, dict):
            has_city_info = "city" in data and isinstance(data["city"], dict)
            
            self.log_test_result(
                "🎯 GET /api/cities/info/München - Munich city information",
                has_city_info,
                f"Munich info available: {has_city_info}",
                data
            )
        else:
            self.log_test_result(
                "🎯 GET /api/cities/info/München - Munich city information",
                False,
                f"Munich city info failed: {error}",
                data
            )
        
        # Test city not found
        success, data, error = await self.make_request("GET", "/api/cities/info/NonExistentCity")
        
        if not success or (isinstance(data, dict) and data.get("status") == "error"):
            self.log_test_result(
                "🎯 GET /api/cities/info/NonExistentCity - Handles non-existent city",
                True,
                f"Correctly handles non-existent city: {error or 'Not found'}",
                data
            )
        else:
            self.log_test_result(
                "🎯 GET /api/cities/info/NonExistentCity - Handles non-existent city",
                False,
                f"Should return error for non-existent city but got: {data}",
                data
            )
    
    async def test_city_search_autocomplete(self):
        """🎯 NEW FEATURE: City Search Autocomplete"""
        logger.info("=== 🎯 NEW FEATURE: City Search Autocomplete ===")
        
        # Test various partial queries for autocomplete functionality
        test_queries = [
            ("Be", "Berlin"),
            ("Fra", "Frankfurt"),
            ("Mü", "München"),
            ("Dü", "Düsseldorf"),
            ("Stu", "Stuttgart")
        ]
        
        autocomplete_working = True
        
        for query, expected_city in test_queries:
            success, data, error = await self.make_request("GET", f"/api/cities/search?q={query}")
            
            if success and isinstance(data, dict):
                cities = data.get("cities", [])
                city_found = any(expected_city in city.get("name", "") for city in cities)
                
                if not city_found:
                    autocomplete_working = False
                    logger.warning(f"Autocomplete failed for '{query}' -> '{expected_city}'")
                
                self.log_test_result(
                    f"🎯 Autocomplete: '{query}' -> '{expected_city}'",
                    city_found,
                    f"Query: {query}, Expected: {expected_city}, Found: {city_found}, Cities: {len(cities)}",
                    data
                )
            else:
                autocomplete_working = False
                self.log_test_result(
                    f"🎯 Autocomplete: '{query}' -> '{expected_city}'",
                    False,
                    f"Autocomplete query failed: {error}",
                    data
                )
        
        self.log_test_result(
            "🎯 City Search Autocomplete - Overall functionality",
            autocomplete_working,
            f"All autocomplete queries work: {autocomplete_working}",
            {"tested_queries": test_queries}
        )
    
    async def run_all_tests(self):
        """Run all city search tests"""
        logger.info("🎯 НАЧАЛО ТЕСТИРОВАНИЯ CITY SEARCH ФУНКЦИОНАЛЬНОСТИ")
        logger.info("=" * 80)
        
        await self.test_city_search_specific_city()
        await self.test_city_search_partial()
        await self.test_popular_cities()
        await self.test_city_info()
        await self.test_city_search_autocomplete()
        
        # Summary
        total_tests = len(self.test_results)
        successful_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - successful_tests
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
        
        logger.info("=" * 80)
        logger.info("🎯 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ CITY SEARCH:")
        logger.info(f"Всего тестов: {total_tests}")
        logger.info(f"Успешных: {successful_tests}")
        logger.info(f"Неудачных: {failed_tests}")
        logger.info(f"Процент успеха: {success_rate:.1f}%")
        
        if failed_tests > 0:
            logger.info("\n❌ НЕУДАЧНЫЕ ТЕСТЫ:")
            for result in self.test_results:
                if not result["success"]:
                    logger.error(f"  - {result['test']}: {result['details']}")
        
        if successful_tests > 0:
            logger.info("\n✅ УСПЕШНЫЕ ТЕСТЫ:")
            for result in self.test_results:
                if result["success"]:
                    logger.info(f"  - {result['test']}")
        
        logger.info("🎯 ТЕСТИРОВАНИЕ CITY SEARCH ЗАВЕРШЕНО")

async def main():
    async with CitySearchTester() as tester:
        await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
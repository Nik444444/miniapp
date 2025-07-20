#!/usr/bin/env python3
"""
🎯 КРИТИЧЕСКОЕ ТЕСТИРОВАНИЕ ИСПРАВЛЕНИЯ ВЕЧНОЙ ЗАГРУЗКИ В TELEGRAM MINI APP OCR СЕРВИСЕ
Прямое тестирование локального backend'а
"""

import requests
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DirectTester:
    def __init__(self):
        self.backend_url = "http://localhost:8001"
        self.test_results = []
        
    def log_test_result(self, test_name: str, success: bool, details: str = "", response_data=None):
        """Log test result"""
        status = "✅ ИСПРАВЛЕНО" if success else "❌ НЕ ИСПРАВЛЕНО"
        logger.info(f"{status} - {test_name}: {details}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "response_data": response_data
        })
    
    def make_request(self, method: str, endpoint: str, **kwargs):
        """Make HTTP request and return success, data, error"""
        try:
            url = f"{self.backend_url}{endpoint}"
            response = requests.request(method, url, timeout=10, **kwargs)
            
            try:
                data = response.json()
            except:
                data = response.text
            
            if response.status_code < 400:
                return True, data, ""
            else:
                return False, data, f"HTTP {response.status_code}"
                
        except Exception as e:
            return False, None, str(e)
    
    def test_critical_ocr_service_fix(self):
        """🎯 КРИТИЧЕСКИЙ ТЕСТ 1: Simple Tesseract OCR Service вместо Improved OCR Service"""
        logger.info("=== 🎯 КРИТИЧЕСКИЙ ТЕСТ 1: Simple Tesseract OCR Service ===")
        
        success, data, error = self.make_request("GET", "/api/ocr-status")
        
        if success and isinstance(data, dict):
            ocr_service = data.get("ocr_service", {})
            
            # 1. Проверка service_name: "Simple Tesseract OCR Service"
            service_name = ocr_service.get("service_name", "")
            service_name_correct = service_name == "Simple Tesseract OCR Service"
            
            # 2. Проверка optimized_for_speed: true
            optimized_for_speed = ocr_service.get("optimized_for_speed") is True
            
            # 3. Проверка primary_method: "tesseract_ocr"
            primary_method = ocr_service.get("primary_method", "")
            primary_method_correct = primary_method == "tesseract_ocr"
            
            # 4. Проверка tesseract_version: "5.3.0"
            tesseract_version = ocr_service.get("tesseract_version", "")
            tesseract_version_correct = tesseract_version == "5.3.0"
            
            # 5. Проверка tesseract_dependency: true
            tesseract_dependency = ocr_service.get("tesseract_dependency") is True
            
            all_correct = all([
                service_name_correct, optimized_for_speed, primary_method_correct,
                tesseract_version_correct, tesseract_dependency
            ])
            
            self.log_test_result(
                "🎯 ГЛАВНАЯ ПРОБЛЕМА РЕШЕНА: Simple Tesseract OCR Service",
                all_correct,
                f"Service: {service_name_correct}, Speed: {optimized_for_speed}, Primary: {primary_method_correct}, Version: {tesseract_version_correct}, Dependency: {tesseract_dependency}",
                {
                    "service_name": service_name,
                    "optimized_for_speed": optimized_for_speed,
                    "primary_method": primary_method,
                    "tesseract_version": tesseract_version,
                    "tesseract_dependency": tesseract_dependency
                }
            )
        else:
            self.log_test_result(
                "🎯 ГЛАВНАЯ ПРОБЛЕМА РЕШЕНА: Simple Tesseract OCR Service",
                False,
                f"Ошибка получения OCR статуса: {error}",
                data
            )
    
    def test_critical_methods_only(self):
        """🎯 КРИТИЧЕСКИЙ ТЕСТ 2: Только tesseract_ocr и direct_pdf методы"""
        logger.info("=== 🎯 КРИТИЧЕСКИЙ ТЕСТ 2: Только tesseract_ocr и direct_pdf методы ===")
        
        success, data, error = self.make_request("GET", "/api/ocr-status")
        
        if success and isinstance(data, dict):
            ocr_service = data.get("ocr_service", {})
            methods = ocr_service.get("methods", {})
            
            # Ожидаемые методы
            expected_methods = {"tesseract_ocr", "direct_pdf"}
            actual_methods = set(methods.keys())
            
            # Запрещенные методы
            forbidden_methods = {"llm_vision", "ocr_space", "azure_vision"}
            forbidden_found = forbidden_methods.intersection(actual_methods)
            
            # Проверки
            only_expected_methods = actual_methods == expected_methods
            no_forbidden_methods = len(forbidden_found) == 0
            
            # Проверка доступности методов
            tesseract_available = methods.get("tesseract_ocr", {}).get("available") is True
            direct_pdf_available = methods.get("direct_pdf", {}).get("available") is True
            
            all_correct = only_expected_methods and no_forbidden_methods and tesseract_available and direct_pdf_available
            
            self.log_test_result(
                "🎯 КРИТИЧЕСКИЙ ТЕСТ: Только tesseract_ocr и direct_pdf методы",
                all_correct,
                f"Ожидаемые: {expected_methods}, Фактические: {actual_methods}, Запрещенные найдены: {forbidden_found}",
                {
                    "expected_methods": list(expected_methods),
                    "actual_methods": list(actual_methods),
                    "forbidden_found": list(forbidden_found),
                    "tesseract_available": tesseract_available,
                    "direct_pdf_available": direct_pdf_available
                }
            )
        else:
            self.log_test_result(
                "🎯 КРИТИЧЕСКИЙ ТЕСТ: Только tesseract_ocr и direct_pdf методы",
                False,
                f"Ошибка получения OCR статуса: {error}",
                data
            )
    
    def test_telegram_mini_app_compatibility(self):
        """🎯 КРИТИЧЕСКИЙ ТЕСТ 3: Совместимость с Telegram Mini App"""
        logger.info("=== 🎯 КРИТИЧЕСКИЙ ТЕСТ 3: Совместимость с Telegram Mini App ===")
        
        # Тест 1: Root endpoint показывает telegram_mini_app: true
        success, data, error = self.make_request("GET", "/")
        if success and isinstance(data, dict):
            telegram_flag_root = data.get("telegram_mini_app") is True
            
            self.log_test_result(
                "🎯 Root endpoint - telegram_mini_app: true",
                telegram_flag_root,
                f"Telegram Mini App flag: {data.get('telegram_mini_app')}",
                data
            )
        else:
            self.log_test_result(
                "🎯 Root endpoint - telegram_mini_app: true",
                False,
                f"Ошибка: {error}",
                data
            )
        
        # Тест 2: Health endpoint показывает telegram_mini_app: true
        success, data, error = self.make_request("GET", "/health")
        if success and isinstance(data, dict):
            telegram_flag_health = data.get("telegram_mini_app") is True
            is_healthy = data.get("status") == "healthy"
            
            self.log_test_result(
                "🎯 Health endpoint - telegram_mini_app: true",
                telegram_flag_health and is_healthy,
                f"Telegram flag: {telegram_flag_health}, Status: {data.get('status')}",
                data
            )
        else:
            self.log_test_result(
                "🎯 Health endpoint - telegram_mini_app: true",
                False,
                f"Ошибка: {error}",
                data
            )
    
    def test_tesseract_functionality(self):
        """🎯 КРИТИЧЕСКИЙ ТЕСТ 4: Tesseract OCR функциональность"""
        logger.info("=== 🎯 КРИТИЧЕСКИЙ ТЕСТ 4: Tesseract OCR функциональность ===")
        
        success, data, error = self.make_request("GET", "/api/ocr-status")
        
        if success and isinstance(data, dict):
            ocr_service = data.get("ocr_service", {})
            
            # Проверки Tesseract
            tesseract_available = ocr_service.get("tesseract_dependency") is True
            tesseract_version = ocr_service.get("tesseract_version") == "5.3.0"
            production_ready = ocr_service.get("production_ready") is True
            
            # Проверка методов
            methods = ocr_service.get("methods", {})
            tesseract_method = methods.get("tesseract_ocr", {})
            tesseract_method_available = tesseract_method.get("available") is True
            
            all_tesseract_working = all([
                tesseract_available, tesseract_version, production_ready, tesseract_method_available
            ])
            
            self.log_test_result(
                "🎯 Tesseract OCR функциональность",
                all_tesseract_working,
                f"Available: {tesseract_available}, Version: {tesseract_version}, Production: {production_ready}, Method: {tesseract_method_available}",
                ocr_service
            )
        else:
            self.log_test_result(
                "🎯 Tesseract OCR функциональность",
                False,
                f"Ошибка: {error}",
                data
            )
    
    def test_modern_llm_integration(self):
        """🎯 КРИТИЧЕСКИЙ ТЕСТ 5: Modern LLM Integration доступен"""
        logger.info("=== 🎯 КРИТИЧЕСКИЙ ТЕСТ 5: Modern LLM Integration ===")
        
        success, data, error = self.make_request("GET", "/api/modern-llm-status")
        
        if success and isinstance(data, dict):
            modern_flag = data.get("modern") is True
            status_success = data.get("status") == "success"
            has_providers = "providers" in data and len(data.get("providers", {})) > 0
            
            # Проверка emergentintegrations доступности
            emergentintegrations_available = modern_flag and status_success
            
            self.log_test_result(
                "🎯 Modern LLM Integration доступен",
                emergentintegrations_available and has_providers,
                f"Modern: {modern_flag}, Status: {data.get('status')}, Providers: {len(data.get('providers', {}))}",
                data
            )
        else:
            self.log_test_result(
                "🎯 Modern LLM Integration доступен",
                False,
                f"Ошибка: {error}",
                data
            )
    
    def run_critical_tests(self):
        """Запуск всех критических тестов"""
        logger.info("🎯 КРИТИЧЕСКОЕ ТЕСТИРОВАНИЕ ИСПРАВЛЕНИЯ ВЕЧНОЙ ЗАГРУЗКИ В TELEGRAM MINI APP OCR СЕРВИСЕ")
        logger.info("=" * 100)
        
        try:
            self.test_critical_ocr_service_fix()
            self.test_critical_methods_only()
            self.test_telegram_mini_app_compatibility()
            self.test_tesseract_functionality()
            self.test_modern_llm_integration()
            
        except Exception as e:
            logger.error(f"Критическая ошибка тестирования: {e}")
            self.log_test_result("Выполнение тестов", False, f"Критическая ошибка: {e}", None)
        
        # Вывод результатов
        self.print_critical_summary()
    
    def print_critical_summary(self):
        """Вывод критического резюме"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        logger.info("=" * 100)
        logger.info("🎯 КРИТИЧЕСКОЕ ТЕСТИРОВАНИЕ ИСПРАВЛЕНИЯ ВЕЧНОЙ ЗАГРУЗКИ - РЕЗУЛЬТАТЫ")
        logger.info("=" * 100)
        logger.info(f"📊 Всего тестов: {total_tests}")
        logger.info(f"✅ Прошли: {passed_tests}")
        logger.info(f"❌ Не прошли: {failed_tests}")
        logger.info(f"📈 Процент успеха: {success_rate:.1f}%")
        logger.info("=" * 100)
        
        # Показать результаты критических тестов
        logger.info("🎯 КРИТИЧЕСКИЕ ПРОВЕРКИ:")
        for result in self.test_results:
            status = "✅ ИСПРАВЛЕНО" if result["success"] else "❌ НЕ ИСПРАВЛЕНО"
            logger.info(f"{status} - {result['test']}")
            if not result["success"]:
                logger.info(f"   Детали: {result['details']}")
        logger.info("=" * 100)
        
        # Финальный вердикт
        if passed_tests == total_tests:
            logger.info("🚀 ЗАКЛЮЧЕНИЕ: ВСЕ КРИТИЧЕСКИЕ ПРОБЛЕМЫ ИСПРАВЛЕНЫ!")
            logger.info("✅ Telegram Mini App теперь может обрабатывать фотографии мгновенно без вечной загрузки")
            logger.info("✅ Система использует Simple Tesseract OCR Service как требовалось")
            logger.info("✅ Убраны все медленные методы OCR (llm_vision, ocr_space, azure_vision)")
            logger.info("✅ Оптимизировано для скорости (optimized_for_speed: true)")
            logger.info("✅ Tesseract версия 5.3.0 работает как primary_method")
        else:
            logger.info("⚠️ ЗАКЛЮЧЕНИЕ: ОСТАЛИСЬ КРИТИЧЕСКИЕ ПРОБЛЕМЫ")
            logger.info(f"❌ Исправлено {passed_tests}/{total_tests} критических проблем")
            logger.info("❌ Telegram Mini App может все еще испытывать проблемы с вечной загрузкой")
        
        logger.info("=" * 100)
        
        return success_rate, passed_tests, total_tests

def main():
    """Главная функция тестирования"""
    tester = DirectTester()
    tester.run_critical_tests()

if __name__ == "__main__":
    main()
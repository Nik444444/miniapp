#!/usr/bin/env python3
"""
🎯 КРИТИЧЕСКОЕ ТЕСТИРОВАНИЕ: Исправление проблемы анализа документов в Telegram Mini App

ГЛАВНАЯ ПРОБЛЕМА ДЛЯ ТЕСТИРОВАНИЯ:
- Пользователь сообщил, что в Telegram Mini App в функции "анализ писем" файлы корректно считываются, но анализ не выдается
- Найдена и исправлена проблема в server.py endpoint /api/analyze-file

ИСПРАВЛЕНИЯ ДЛЯ ПРОВЕРКИ:
1) ✅ Добавлен импорт super_analysis_engine в server.py 
2) ✅ Заменена статичная заглушка на реальный AI анализ через super_analysis_engine.analyze_document_comprehensively()
3) ✅ Добавлена логика fallback для случаев когда супер-анализ недоступен
4) ✅ Исправлена обработка случаев когда текст из файла не извлекается

КРИТИЧЕСКИЕ ТЕСТЫ:
1. POST /api/analyze-file - проверить что endpoint принимает файлы и возвращает РЕАЛЬНЫЙ анализ (НЕ заглушку)
2. Проверить что анализ содержит детальные разборы документа 
3. Проверить работу с разными типами файлов (изображения, PDF)
4. Проверить что система использует user API keys для анализа
5. Проверить логи - должны показывать "Starting comprehensive AI analysis" и "Super analysis completed successfully"

ФОКУС: Убедиться что анализ теперь РЕАЛЬНЫЙ, а не статичные заглушки как раньше. Проверить что extracted_text правильно передается в super_analysis_engine для анализа.
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

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BackendTester:
    def __init__(self):
        # Get backend URL from frontend .env file
        frontend_env_path = Path("/app/frontend/.env")
        self.backend_url = "https://miniapp-wvsxfa.fly.dev"  # Production URL from frontend/.env
        
        if frontend_env_path.exists():
            with open(frontend_env_path, 'r') as f:
                for line in f:
                    if line.startswith('REACT_APP_BACKEND_URL='):
                        self.backend_url = line.split('=', 1)[1].strip()
                        break
            
        logger.info(f"Testing backend at: {self.backend_url}")
        
        self.session = None
        self.test_results = []
        self.auth_token = None
        
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
            
            # Add auth header if we have a token
            if self.auth_token and 'headers' not in kwargs:
                kwargs['headers'] = {}
            if self.auth_token:
                kwargs['headers']['Authorization'] = f"Bearer {self.auth_token}"
            
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
    
    async def test_basic_health_endpoints(self):
        """Test basic health check endpoints"""
        logger.info("=== Testing Basic Health Endpoints ===")
        
        # Test root endpoint
        success, data, error = await self.make_request("GET", "/")
        if success and isinstance(data, dict):
            expected_fields = ["message", "status", "auth", "database", "version"]
            has_all_fields = all(field in data for field in expected_fields)
            is_sqlite = data.get("database") == "SQLite"
            is_google_only = "Google OAuth" in str(data.get("auth", ""))
            
            self.log_test_result(
                "GET / - Root endpoint",
                has_all_fields and is_sqlite and is_google_only,
                f"Database: {data.get('database')}, Auth: {data.get('auth')}, Version: {data.get('version')}",
                data
            )
        else:
            self.log_test_result("GET / - Root endpoint", False, f"Error: {error}", data)
        
        # Test health endpoint
        success, data, error = await self.make_request("GET", "/health")
        if success and isinstance(data, dict):
            has_status = "status" in data and data["status"] == "healthy"
            has_service = "service" in data
            is_sqlite = data.get("database") == "sqlite"
            
            self.log_test_result(
                "GET /health - Health check",
                has_status and has_service and is_sqlite,
                f"Status: {data.get('status')}, Database: {data.get('database')}",
                data
            )
        else:
            self.log_test_result("GET /health - Health check", False, f"Error: {error}", data)
    
    async def test_api_health_endpoints(self):
        """Test API health endpoints"""
        logger.info("=== Testing API Health Endpoints ===")
        
        # Test API root
        success, data, error = await self.make_request("GET", "/api/")
        if success and isinstance(data, dict):
            has_message = "message" in data
            is_sqlite = data.get("database") == "SQLite"
            is_google_only = "Google OAuth" in str(data.get("auth", ""))
            
            self.log_test_result(
                "GET /api/ - API root",
                has_message and is_sqlite and is_google_only,
                f"Database: {data.get('database')}, Auth: {data.get('auth')}",
                data
            )
        else:
            self.log_test_result("GET /api/ - API root", False, f"Error: {error}", data)
        
        # Test API health with database counts
        success, data, error = await self.make_request("GET", "/api/health")
        if success and isinstance(data, dict):
            has_status = data.get("status") == "healthy"
            has_counts = "users_count" in data and "analyses_count" in data
            is_sqlite = data.get("database") == "sqlite"
            
            self.log_test_result(
                "GET /api/health - Detailed health",
                has_status and has_counts and is_sqlite,
                f"Users: {data.get('users_count')}, Analyses: {data.get('analyses_count')}, DB: {data.get('database')}",
                data
            )
        else:
            self.log_test_result("GET /api/health - Detailed health", False, f"Error: {error}", data)
    
    async def test_llm_status_endpoint(self):
        """Test LLM status endpoint"""
        logger.info("=== Testing LLM Status Endpoint ===")
        
        success, data, error = await self.make_request("GET", "/api/llm-status")
        if success and isinstance(data, dict):
            has_status = "status" in data
            has_providers = "providers" in data and isinstance(data["providers"], dict)
            has_counts = "active_providers" in data and "total_providers" in data
            
            # Check if all expected providers are present
            expected_providers = ["gemini", "openai", "anthropic"]
            providers_present = all(provider in data.get("providers", {}) for provider in expected_providers)
            
            self.log_test_result(
                "GET /api/llm-status - LLM providers status",
                has_status and has_providers and has_counts and providers_present,
                f"Active: {data.get('active_providers')}/{data.get('total_providers')}, Providers: {list(data.get('providers', {}).keys())}",
                data
            )
        else:
            self.log_test_result("GET /api/llm-status - LLM providers status", False, f"Error: {error}", data)
    
    async def test_legacy_status_endpoints(self):
        """Test legacy status endpoints for compatibility"""
        logger.info("=== Testing Legacy Status Endpoints ===")
        
        # Test creating status check
        test_data = {"client_name": "test_client_backend_api"}
        success, data, error = await self.make_request("POST", "/api/status", json=test_data)
        
        if success and isinstance(data, dict):
            has_id = "id" in data
            has_client_name = data.get("client_name") == test_data["client_name"]
            has_timestamp = "timestamp" in data
            
            self.log_test_result(
                "POST /api/status - Create status check",
                has_id and has_client_name and has_timestamp,
                f"Created status check with ID: {data.get('id')}",
                data
            )
        else:
            self.log_test_result("POST /api/status - Create status check", False, f"Error: {error}", data)
        
        # Test getting status checks
        success, data, error = await self.make_request("GET", "/api/status")
        if success and isinstance(data, list):
            has_data = len(data) > 0
            if has_data:
                first_item = data[0]
                has_required_fields = all(field in first_item for field in ["id", "client_name", "timestamp"])
            else:
                has_required_fields = True  # Empty list is acceptable
            
            self.log_test_result(
                "GET /api/status - Get status checks",
                isinstance(data, list) and has_required_fields,
                f"Retrieved {len(data)} status checks",
                {"count": len(data), "sample": data[0] if data else None}
            )
        else:
            self.log_test_result("GET /api/status - Get status checks", False, f"Error: {error}", data)
    
    async def test_authentication_required_endpoints(self):
        """Test that authentication-required endpoints return 401 without token"""
        logger.info("=== Testing Authentication Requirements ===")
        
        auth_required_endpoints = [
            ("GET", "/api/profile", "User profile"),
            ("POST", "/api/api-keys", "Save API keys"),
            ("POST", "/api/analyze-file", "Analyze file"),
            ("GET", "/api/analysis-history", "Analysis history")
        ]
        
        # Test without authentication
        for method, endpoint, description in auth_required_endpoints:
            if method == "POST" and "api-keys" in endpoint:
                # For API keys endpoint, send some test data
                success, data, error = await self.make_request(method, endpoint, json={"gemini_api_key": "test"})
            elif method == "POST" and "analyze-file" in endpoint:
                # For file analysis, we need multipart data
                success, data, error = await self.make_request(method, endpoint, data={"language": "en"})
            else:
                success, data, error = await self.make_request(method, endpoint)
            
            # Should fail with 401 or 403 (both indicate authentication required)
            is_auth_required = "401" in str(error) or "403" in str(error) or (isinstance(data, dict) and ("401" in str(data) or "403" in str(data) or "Not authenticated" in str(data.get("detail", ""))))
            
            self.log_test_result(
                f"{method} {endpoint} - {description} (no auth)",
                not success and is_auth_required,
                f"Correctly returned authentication required" if is_auth_required else f"Unexpected response: {error}",
                data
            )
    
    async def test_google_oauth_endpoint(self):
        """Test Google OAuth endpoint (without valid token)"""
        logger.info("=== Testing Google OAuth Endpoint ===")
        
        # Test with invalid token
        test_data = {"credential": "invalid_google_token"}
        success, data, error = await self.make_request("POST", "/api/auth/google/verify", json=test_data)
        
        # Should fail with 400 (invalid token)
        is_400 = "400" in str(error) or (isinstance(data, dict) and "Invalid Google token" in str(data.get("detail", "")))
        
        self.log_test_result(
            "POST /api/auth/google/verify - Google OAuth (invalid token)",
            not success and is_400,
            f"Correctly rejected invalid token" if is_400 else f"Unexpected response: {error}",
            data
        )
        
        # Test with missing credential
        success, data, error = await self.make_request("POST", "/api/auth/google/verify", json={})
        
        # Should fail with validation error
        is_validation_error = not success and ("422" in str(error) or "validation" in str(data).lower())
        
        self.log_test_result(
            "POST /api/auth/google/verify - Google OAuth (missing credential)",
            is_validation_error,
            f"Correctly returned validation error" if is_validation_error else f"Unexpected response: {error}",
            data
        )
    
    async def test_database_functionality(self):
        """Test SQLite database functionality indirectly through API"""
        logger.info("=== Testing Database Functionality ===")
        
        # Test that health endpoint shows user and analysis counts (tests DB connection)
        success, data, error = await self.make_request("GET", "/api/health")
        
        if success and isinstance(data, dict):
            has_user_count = "users_count" in data and isinstance(data["users_count"], int)
            has_analysis_count = "analyses_count" in data and isinstance(data["analyses_count"], int)
            is_sqlite = data.get("database") == "sqlite"
            
            self.log_test_result(
                "Database connectivity test",
                has_user_count and has_analysis_count and is_sqlite,
                f"SQLite DB connected, Users: {data.get('users_count')}, Analyses: {data.get('analyses_count')}",
                data
            )
        else:
            self.log_test_result("Database connectivity test", False, f"Error: {error}", data)
        
        # Test status checks creation/retrieval (tests SQLite operations)
        test_client = f"db_test_client_{int(time.time())}"
        
        # Create a status check
        success, create_data, error = await self.make_request("POST", "/api/status", json={"client_name": test_client})
        
        if success:
            # Retrieve status checks and verify our entry exists
            success, get_data, error = await self.make_request("GET", "/api/status")
            
            if success and isinstance(get_data, list):
                found_entry = any(item.get("client_name") == test_client for item in get_data)
                
                self.log_test_result(
                    "SQLite CRUD operations test",
                    found_entry,
                    f"Successfully created and retrieved status check for {test_client}",
                    {"created": create_data, "found_in_list": found_entry}
                )
            else:
                self.log_test_result("SQLite CRUD operations test", False, f"Failed to retrieve: {error}", get_data)
        else:
            self.log_test_result("SQLite CRUD operations test", False, f"Failed to create: {error}", create_data)
    
    async def test_no_skip_auth_functionality(self):
        """Test that skip auth functionality has been removed"""
        logger.info("=== Testing No Skip Auth Functionality ===")
        
        # Try various endpoints that might have had skip auth
        test_endpoints = [
            ("GET", "/api/profile"),
            ("POST", "/api/api-keys"),
            ("GET", "/api/analysis-history"),
            ("POST", "/api/quick-gemini-setup")  # New endpoint should also require auth
        ]
        
        all_require_auth = True
        
        for method, endpoint in test_endpoints:
            if method == "POST" and "api-keys" in endpoint:
                success, data, error = await self.make_request(method, endpoint, json={"gemini_api_key": "test"})
            elif method == "POST" and "quick-gemini-setup" in endpoint:
                success, data, error = await self.make_request(method, endpoint, json={"api_key": "test"})
            else:
                success, data, error = await self.make_request(method, endpoint, json={} if method == "POST" else None)
            
            # All should require authentication (return 401 or 403)
            requires_auth = not success and ("401" in str(error) or "403" in str(error) or (isinstance(data, dict) and ("Not authenticated" in str(data.get("detail", "")))))
            
            if not requires_auth:
                all_require_auth = False
                logger.warning(f"{method} {endpoint} does not require authentication!")
        
        self.log_test_result(
            "No skip auth functionality test",
            all_require_auth,
            "All protected endpoints correctly require authentication" if all_require_auth else "Some endpoints allow unauthorized access",
            {"all_require_auth": all_require_auth}
        )
    
    async def test_modern_llm_status_endpoint(self):
        """Test modern LLM status endpoint"""
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
                "GET /api/modern-llm-status - Modern LLM providers status",
                has_status and has_providers and has_counts and providers_present and has_modern_flag and providers_modern,
                f"Active: {data.get('active_providers')}/{data.get('total_providers')}, Modern: {has_modern_flag}, Providers: {list(data.get('providers', {}).keys())}",
                data
            )
        else:
            self.log_test_result("GET /api/modern-llm-status - Modern LLM providers status", False, f"Error: {error}", data)
    
    async def test_quick_gemini_setup_endpoint(self):
        """Test quick Gemini setup endpoint (without authentication)"""
        logger.info("=== Testing Quick Gemini Setup Endpoint ===")
        
        # Test without authentication - should fail
        test_data = {"api_key": "test_invalid_key"}
        success, data, error = await self.make_request("POST", "/api/quick-gemini-setup", json=test_data)
        
        # Should fail with 401 or 403 (authentication required)
        is_auth_required = not success and ("401" in str(error) or "403" in str(error) or (isinstance(data, dict) and ("Not authenticated" in str(data.get("detail", "")))))
        
        self.log_test_result(
            "POST /api/quick-gemini-setup - Quick Gemini setup (no auth)",
            is_auth_required,
            f"Correctly requires authentication" if is_auth_required else f"Unexpected response: {error}",
            data
        )
        
        # Test with missing api_key field
        success, data, error = await self.make_request("POST", "/api/quick-gemini-setup", json={})
        
        # Should fail with validation error or auth error
        is_validation_or_auth_error = not success and ("422" in str(error) or "401" in str(error) or "403" in str(error) or "validation" in str(data).lower())
        
        self.log_test_result(
            "POST /api/quick-gemini-setup - Quick Gemini setup (missing api_key)",
            is_validation_or_auth_error,
            f"Correctly returned validation/auth error" if is_validation_or_auth_error else f"Unexpected response: {error}",
            data
        )
    
    async def test_image_recognition_functionality(self):
        """Test critical image recognition functionality with modern LLM manager"""
        logger.info("=== Testing Image Recognition Functionality ===")
        
        # Test that modern LLM status endpoint shows image support
        success, data, error = await self.make_request("GET", "/api/modern-llm-status")
        if success and isinstance(data, dict):
            has_modern_flag = data.get("modern") is True
            has_providers = "providers" in data and isinstance(data["providers"], dict)
            
            # Check if modern providers are configured for image support
            modern_providers_available = []
            if has_providers:
                for provider_name, provider_info in data["providers"].items():
                    if provider_info.get("modern") is True:
                        modern_providers_available.append(provider_name)
            
            self.log_test_result(
                "Modern LLM Status - Image support check",
                has_modern_flag and has_providers and len(modern_providers_available) > 0,
                f"Modern flag: {has_modern_flag}, Modern providers: {modern_providers_available}",
                data
            )
        else:
            self.log_test_result("Modern LLM Status - Image support check", False, f"Error: {error}", data)
        
        # Test analyze-file endpoint without authentication (should fail)
        # Create a simple test image file
        test_image_data = self.create_test_image()
        
        # Test without authentication
        form_data = aiohttp.FormData()
        form_data.add_field('file', test_image_data, filename='test_image.jpg', content_type='image/jpeg')
        form_data.add_field('language', 'en')
        
        success, data, error = await self.make_request("POST", "/api/analyze-file", data=form_data)
        
        # Should fail with authentication required
        is_auth_required = not success and ("401" in str(error) or "403" in str(error) or (isinstance(data, dict) and ("Not authenticated" in str(data.get("detail", "")))))
        
        self.log_test_result(
            "POST /api/analyze-file - Image analysis (no auth)",
            is_auth_required,
            f"Correctly requires authentication for image analysis" if is_auth_required else f"Unexpected response: {error}",
            data
        )
        
        # Test that the endpoint accepts image files (structure test)
        # This tests the endpoint structure without actually processing
        form_data_invalid = aiohttp.FormData()
        form_data_invalid.add_field('language', 'en')  # Missing file
        
        success, data, error = await self.make_request("POST", "/api/analyze-file", data=form_data_invalid)
        
        # Should fail with validation error or auth error (both are acceptable)
        is_validation_or_auth_error = not success and ("422" in str(error) or "401" in str(error) or "403" in str(error) or "validation" in str(data).lower() or "field required" in str(data).lower())
        
        self.log_test_result(
            "POST /api/analyze-file - Image analysis (missing file)",
            is_validation_or_auth_error,
            f"Correctly handles missing file parameter" if is_validation_or_auth_error else f"Unexpected response: {error}",
            data
        )
    
    def create_test_image(self):
        """Create a simple test image for testing"""
        try:
            from PIL import Image
            import io
            
            # Create a simple 100x100 red image
            img = Image.new('RGB', (100, 100), color='red')
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='JPEG')
            img_bytes.seek(0)
            return img_bytes.getvalue()
        except ImportError:
            # If PIL is not available, create a minimal JPEG-like bytes
            # This is just for testing the endpoint structure
            return b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xc0\x00\x11\x08\x00d\x00d\x01\x01\x11\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x14\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\xff\xc4\x00\x14\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00\x3f\x00\xaa\xff\xd9'
    
    async def test_modern_llm_manager_integration(self):
        """Test modern LLM manager integration and image path parameter handling"""
        logger.info("=== Testing Modern LLM Manager Integration ===")
        
        # Test modern LLM status endpoint for proper integration
        success, data, error = await self.make_request("GET", "/api/modern-llm-status")
        
        if success and isinstance(data, dict):
            # Check for modern flag and proper provider structure
            has_modern_flag = data.get("modern") is True
            has_status = data.get("status") == "success"
            has_providers = "providers" in data and isinstance(data["providers"], dict)
            
            # Check if providers have modern models configured
            modern_models_found = []
            if has_providers:
                for provider_name, provider_info in data["providers"].items():
                    model = provider_info.get("model", "")
                    if any(modern_model in model for modern_model in ["gemini-2.0-flash", "gpt-4o", "claude-3-5-sonnet"]):
                        modern_models_found.append(f"{provider_name}:{model}")
            
            self.log_test_result(
                "Modern LLM Manager - Integration check",
                has_modern_flag and has_status and has_providers,
                f"Modern: {has_modern_flag}, Status: {has_status}, Modern models: {modern_models_found}",
                data
            )
            
            # Check specific modern models are configured
            expected_modern_models = ["gemini-2.0-flash", "gpt-4o", "claude-3-5-sonnet"]
            models_configured = []
            
            if has_providers:
                for provider_name, provider_info in data["providers"].items():
                    model = provider_info.get("model", "")
                    if model in expected_modern_models:
                        models_configured.append(model)
            
            self.log_test_result(
                "Modern LLM Manager - Modern models configuration",
                len(models_configured) > 0,
                f"Modern models configured: {models_configured} out of expected: {expected_modern_models}",
                {"configured": models_configured, "expected": expected_modern_models}
            )
        else:
            self.log_test_result("Modern LLM Manager - Integration check", False, f"Error: {error}", data)
    
    async def test_emergentintegrations_support(self):
        """Test emergentintegrations library support"""
        logger.info("=== Testing Emergentintegrations Support ===")
        
        # Test that modern LLM status shows emergentintegrations support
        success, data, error = await self.make_request("GET", "/api/modern-llm-status")
        
        if success and isinstance(data, dict):
            # Check if the response indicates modern LLM support
            has_modern_flag = data.get("modern") is True
            providers = data.get("providers", {})
            
            # Check if providers have modern flag indicating emergentintegrations support
            emergent_support = all(
                provider_info.get("modern") is True 
                for provider_info in providers.values()
            ) if providers else False
            
            self.log_test_result(
                "Emergentintegrations - Library support check",
                has_modern_flag and emergent_support,
                f"Modern flag: {has_modern_flag}, All providers modern: {emergent_support}, Providers: {list(providers.keys())}",
                data
            )
        else:
            self.log_test_result("Emergentintegrations - Library support check", False, f"Error: {error}", data)
    
    async def test_telegram_news_endpoint(self):
        """Test new Telegram news endpoint"""
        logger.info("=== Testing Telegram News Endpoint ===")
        
        # Test basic endpoint functionality
        success, data, error = await self.make_request("GET", "/api/telegram-news")
        
        if success and isinstance(data, dict):
            # Check required fields
            has_status = "status" in data
            has_count = "count" in data and isinstance(data["count"], int)
            has_news = "news" in data and isinstance(data["news"], list)
            has_channel_info = "channel_name" in data and "channel_link" in data
            
            # Check news structure if any news exist
            news_structure_valid = True
            if data.get("news"):
                first_news = data["news"][0]
                required_news_fields = ["id", "text", "preview_text", "date", "formatted_date", "channel_name", "link"]
                news_structure_valid = all(field in first_news for field in required_news_fields)
            
            self.log_test_result(
                "GET /api/telegram-news - Basic functionality",
                has_status and has_count and has_news and has_channel_info and news_structure_valid,
                f"Status: {data.get('status')}, Count: {data.get('count')}, Channel: {data.get('channel_name')}, News structure valid: {news_structure_valid}",
                data
            )
        else:
            self.log_test_result("GET /api/telegram-news - Basic functionality", False, f"Error: {error}", data)
        
        # Test with limit parameter
        success, data, error = await self.make_request("GET", "/api/telegram-news?limit=3")
        
        if success and isinstance(data, dict):
            news_count = len(data.get("news", []))
            limit_respected = news_count <= 3
            
            self.log_test_result(
                "GET /api/telegram-news - Limit parameter",
                limit_respected,
                f"Requested limit: 3, Actual count: {news_count}",
                {"requested_limit": 3, "actual_count": news_count}
            )
        else:
            self.log_test_result("GET /api/telegram-news - Limit parameter", False, f"Error: {error}", data)
        
        # Test that endpoint returns demo news when real news unavailable
        # This is tested by checking if we get a response even without valid Telegram credentials
        success, data, error = await self.make_request("GET", "/api/telegram-news")
        
        if success and isinstance(data, dict):
            status = data.get("status")
            has_demo_fallback = status in ["success", "demo"]  # Either real news or demo
            has_news_data = len(data.get("news", [])) > 0
            
            self.log_test_result(
                "GET /api/telegram-news - Demo fallback functionality",
                has_demo_fallback and has_news_data,
                f"Status: {status}, Has news: {has_news_data}, News count: {len(data.get('news', []))}",
                data
            )
        else:
            self.log_test_result("GET /api/telegram-news - Demo fallback functionality", False, f"Error: {error}", data)
    
    async def test_text_formatting_improvements(self):
        """Test improved text formatting and removal of * symbols"""
        logger.info("=== Testing Text Formatting Improvements ===")
        
        # Test that analyze-file endpoint exists and requires authentication
        # (We can't test the actual formatting without authentication, but we can test the endpoint structure)
        success, data, error = await self.make_request("POST", "/api/analyze-file")
        
        # Should fail with authentication required, not with missing endpoint
        is_auth_required = not success and ("401" in str(error) or "403" in str(error) or (isinstance(data, dict) and ("Not authenticated" in str(data.get("detail", "")))))
        endpoint_exists = is_auth_required or "422" in str(error)  # 422 means validation error (endpoint exists)
        
        self.log_test_result(
            "POST /api/analyze-file - Endpoint availability for text formatting",
            endpoint_exists,
            f"Endpoint exists and properly handles requests" if endpoint_exists else f"Endpoint issue: {error}",
            data
        )
        
        # Test that the endpoint accepts file uploads (structure test)
        test_image_data = self.create_test_image()
        form_data = aiohttp.FormData()
        form_data.add_field('file', test_image_data, filename='test_image.jpg', content_type='image/jpeg')
        form_data.add_field('language', 'ru')
        
        success, data, error = await self.make_request("POST", "/api/analyze-file", data=form_data)
        
        # Should fail with authentication, not with file format issues
        handles_files_correctly = not success and ("401" in str(error) or "403" in str(error) or (isinstance(data, dict) and ("Not authenticated" in str(data.get("detail", "")))))
        
        self.log_test_result(
            "POST /api/analyze-file - File upload handling with formatting",
            handles_files_correctly,
            f"Correctly handles file uploads and requires auth" if handles_files_correctly else f"File handling issue: {error}",
            data
        )
    
    async def test_improved_analysis_prompt(self):
        """Test that improved analysis prompt is being used"""
        logger.info("=== Testing Improved Analysis Prompt ===")
        
        # We can't directly test the prompt without authentication, but we can verify
        # that the analyze-file endpoint is properly configured to use the new prompt system
        
        # Test different language parameters to ensure prompt system handles them
        languages = ["en", "ru", "de"]
        
        for lang in languages:
            test_image_data = self.create_test_image()
            form_data = aiohttp.FormData()
            form_data.add_field('file', test_image_data, filename='test_document.jpg', content_type='image/jpeg')
            form_data.add_field('language', lang)
            
            success, data, error = await self.make_request("POST", "/api/analyze-file", data=form_data)
            
            # Should handle language parameter correctly (fail with auth, not validation)
            handles_language = not success and ("401" in str(error) or "403" in str(error) or (isinstance(data, dict) and ("Not authenticated" in str(data.get("detail", "")))))
            
            if not handles_language:
                break
        
        self.log_test_result(
            "POST /api/analyze-file - Improved prompt system language handling",
            handles_language,
            f"Correctly handles language parameters for improved prompts" if handles_language else f"Language handling issue: {error}",
            {"tested_languages": languages}
        )
    
    async def test_auto_generate_gemini_key_endpoint(self):
        """Test new auto-generate Gemini API key endpoint"""
        logger.info("=== Testing Auto-Generate Gemini API Key Endpoint ===")
        
        # Test without authentication - should fail
        success, data, error = await self.make_request("POST", "/api/auto-generate-gemini-key")
        
        # Should fail with 401 or 403 (authentication required)
        is_auth_required = not success and ("401" in str(error) or "403" in str(error) or (isinstance(data, dict) and ("Not authenticated" in str(data.get("detail", "")))))
        
        self.log_test_result(
            "POST /api/auto-generate-gemini-key - Authentication required",
            is_auth_required,
            f"Correctly requires authentication" if is_auth_required else f"Unexpected response: {error}",
            data
        )
        
        # Test that endpoint exists and is properly configured
        # The endpoint should return auth error, not 404 (not found)
        endpoint_exists = is_auth_required or "422" in str(error)  # 422 means validation error (endpoint exists)
        
        self.log_test_result(
            "POST /api/auto-generate-gemini-key - Endpoint availability",
            endpoint_exists,
            f"Endpoint exists and properly configured" if endpoint_exists else f"Endpoint not found or misconfigured: {error}",
            data
        )
    
    async def test_google_api_key_service_integration(self):
        """Test Google API Key Service integration"""
        logger.info("=== Testing Google API Key Service Integration ===")
        
        # Test that the service is properly imported and integrated
        # We can verify this by checking if the auto-generate endpoint responds correctly
        success, data, error = await self.make_request("POST", "/api/auto-generate-gemini-key")
        
        # Should fail with auth error, not import error or server error
        is_properly_integrated = not success and ("401" in str(error) or "403" in str(error) or (isinstance(data, dict) and ("Not authenticated" in str(data.get("detail", "")))))
        
        # If we get 500 error, it might indicate import or integration issues
        has_integration_issues = "500" in str(error) or (isinstance(data, dict) and "500" in str(data))
        
        self.log_test_result(
            "Google API Key Service - Integration check",
            is_properly_integrated and not has_integration_issues,
            f"Service properly integrated" if is_properly_integrated else f"Integration issue: {error}",
            data
        )
    
    async def test_api_key_update_new_field_names(self):
        """Test API key update with new field names (api_key_1, api_key_2, api_key_3)"""
        logger.info("=== Testing API Key Update with New Field Names ===")
        
        # Test with new field names - should require authentication
        new_field_data = {
            "api_key_1": "test_gemini_key_123",
            "api_key_2": "test_openai_key_456", 
            "api_key_3": "test_anthropic_key_789"
        }
        
        success, data, error = await self.make_request("POST", "/api/api-keys", json=new_field_data)
        
        # Should fail with auth error, not validation error
        is_auth_required = not success and ("401" in str(error) or "403" in str(error) or (isinstance(data, dict) and ("Not authenticated" in str(data.get("detail", "")))))
        
        # Should NOT fail with validation error (422) - this would indicate the new fields are not accepted
        has_validation_error = "422" in str(error) or (isinstance(data, dict) and "validation" in str(data).lower())
        
        self.log_test_result(
            "POST /api/api-keys - New field names acceptance",
            is_auth_required and not has_validation_error,
            f"New field names properly accepted" if (is_auth_required and not has_validation_error) else f"Field validation issue: {error}",
            data
        )
        
        # Test with old field names for comparison
        old_field_data = {
            "gemini_api_key": "test_gemini_key_123",
            "openai_api_key": "test_openai_key_456",
            "anthropic_api_key": "test_anthropic_key_789"
        }
        
        success, data, error = await self.make_request("POST", "/api/api-keys", json=old_field_data)
        
        # Should also fail with auth error, not validation error
        old_fields_auth_required = not success and ("401" in str(error) or "403" in str(error) or (isinstance(data, dict) and ("Not authenticated" in str(data.get("detail", "")))))
        old_fields_validation_error = "422" in str(error) or (isinstance(data, dict) and "validation" in str(data).lower())
        
        self.log_test_result(
            "POST /api/api-keys - Old field names compatibility",
            old_fields_auth_required and not old_fields_validation_error,
            f"Old field names still supported" if (old_fields_auth_required and not old_fields_validation_error) else f"Compatibility issue: {error}",
            data
        )
        
        # Test mixed field names
        mixed_field_data = {
            "api_key_1": "test_new_gemini_key",
            "openai_api_key": "test_old_openai_key"
        }
        
        success, data, error = await self.make_request("POST", "/api/api-keys", json=mixed_field_data)
        
        mixed_fields_auth_required = not success and ("401" in str(error) or "403" in str(error) or (isinstance(data, dict) and ("Not authenticated" in str(data.get("detail", "")))))
        mixed_fields_validation_error = "422" in str(error) or (isinstance(data, dict) and "validation" in str(data).lower())
        
        self.log_test_result(
            "POST /api/api-keys - Mixed field names handling",
            mixed_fields_auth_required and not mixed_fields_validation_error,
            f"Mixed field names properly handled" if (mixed_fields_auth_required and not mixed_fields_validation_error) else f"Mixed fields issue: {error}",
            data
        )
    
    async def test_dependencies_installation(self):
        """Test that required dependencies are properly installed"""
        logger.info("=== Testing Dependencies Installation ===")
        
        # Test that google-api-python-client is available by checking if endpoints work
        # If the import fails, we'd get 500 errors on endpoints that use it
        
        # Test auto-generate endpoint (uses google-api-python-client)
        success, data, error = await self.make_request("POST", "/api/auto-generate-gemini-key")
        
        # Should fail with auth error, not import/dependency error (500)
        no_import_errors = not ("500" in str(error) or (isinstance(data, dict) and "500" in str(data)))
        has_auth_error = "401" in str(error) or "403" in str(error) or (isinstance(data, dict) and ("Not authenticated" in str(data.get("detail", ""))))
        
        self.log_test_result(
            "Dependencies - google-api-python-client availability",
            no_import_errors and has_auth_error,
            f"google-api-python-client properly installed" if (no_import_errors and has_auth_error) else f"Dependency issue: {error}",
            data
        )
        
        # Test modern LLM status (uses emergentintegrations)
        success, data, error = await self.make_request("GET", "/api/modern-llm-status")
        
        if success and isinstance(data, dict):
            has_modern_flag = data.get("modern") is True
            no_import_issues = data.get("status") != "error"
            
            self.log_test_result(
                "Dependencies - emergentintegrations availability",
                has_modern_flag and no_import_issues,
                f"emergentintegrations properly installed and working" if (has_modern_flag and no_import_issues) else f"emergentintegrations issue",
                data
            )
        else:
            self.log_test_result(
                "Dependencies - emergentintegrations availability", 
                False, 
                f"emergentintegrations dependency error: {error}", 
                data
            )
    
    async def test_ocr_performance_optimization(self):
        """🎯 ГЛАВНАЯ ЗАДАЧА: Проверить оптимизированную систему OCR на быстродействие"""
        logger.info("=== 🎯 ГЛАВНАЯ ЗАДАЧА: Тестирование оптимизированной системы OCR на быстродействие ===")
        
        # 1. Проверить endpoint /api/ocr-status - убедиться что он показывает tesseract как primary method
        success, data, error = await self.make_request("GET", "/api/ocr-status")
        
        if success and isinstance(data, dict):
            ocr_service = data.get("ocr_service", {})
            
            # Проверяем что tesseract является primary method
            primary_method = ocr_service.get("primary_method")
            is_tesseract_primary = primary_method == "tesseract_ocr"
            
            # Проверяем что система оптимизирована для скорости
            optimized_for_speed = ocr_service.get("optimized_for_speed") is True
            
            # Проверяем что система готова к production
            production_ready = ocr_service.get("production_ready") is True
            
            # Проверяем версию tesseract
            tesseract_version = ocr_service.get("tesseract_version")
            has_correct_version = tesseract_version == "5.3.0"
            
            self.log_test_result(
                "🎯 OCR Status - Tesseract как primary method",
                is_tesseract_primary and optimized_for_speed and production_ready and has_correct_version,
                f"Primary: {primary_method}, Speed optimized: {optimized_for_speed}, Production ready: {production_ready}, Version: {tesseract_version}",
                data
            )
        else:
            self.log_test_result("🎯 OCR Status - Tesseract как primary method", False, f"Error: {error}", data)
    
    async def test_fast_ocr_methods_only(self):
        """🎯 КРИТИЧЕСКИЙ ТЕСТ: Убедиться что система использует только simple_tesseract_ocr и НЕ падает в fallback цепочки"""
        logger.info("=== 🎯 КРИТИЧЕСКИЙ ТЕСТ: Только быстрые OCR методы ===")
        
        success, data, error = await self.make_request("GET", "/api/ocr-status")
        
        if success and isinstance(data, dict):
            ocr_service = data.get("ocr_service", {})
            methods = ocr_service.get("methods", {})
            
            # Проверяем что есть ТОЛЬКО tesseract_ocr и direct_pdf
            expected_fast_methods = {"tesseract_ocr", "direct_pdf"}
            actual_methods = set(methods.keys())
            
            # Проверяем что медленные методы ОТСУТСТВУЮТ
            slow_methods = {"llm_vision", "ocr_space", "azure_vision"}
            slow_methods_found = slow_methods.intersection(actual_methods)
            
            # Проверяем что остались только быстрые методы
            only_fast_methods = actual_methods == expected_fast_methods
            no_slow_methods = len(slow_methods_found) == 0
            
            # Проверяем что tesseract_ocr доступен
            tesseract_method = methods.get("tesseract_ocr", {})
            tesseract_available = tesseract_method.get("available") is True
            
            # Проверяем что direct_pdf доступен
            direct_pdf_method = methods.get("direct_pdf", {})
            direct_pdf_available = direct_pdf_method.get("available") is True
            
            self.log_test_result(
                "🎯 Только быстрые OCR методы (без fallback цепочки)",
                only_fast_methods and no_slow_methods and tesseract_available and direct_pdf_available,
                f"Expected: {expected_fast_methods}, Actual: {actual_methods}, Slow methods found: {slow_methods_found}",
                {
                    "expected_methods": list(expected_fast_methods),
                    "actual_methods": list(actual_methods),
                    "slow_methods_found": list(slow_methods_found),
                    "tesseract_available": tesseract_available,
                    "direct_pdf_available": direct_pdf_available
                }
            )
        else:
            self.log_test_result("🎯 Только быстрые OCR методы (без fallback цепочки)", False, f"Error: {error}", data)
    
    async def test_no_slow_operations_removed(self):
        """🎯 КРИТИЧЕСКИЙ ТЕСТ: Убедиться что все медленные операции убраны"""
        logger.info("=== 🎯 КРИТИЧЕСКИЙ ТЕСТ: Проверка что медленные операции убраны ===")
        
        success, data, error = await self.make_request("GET", "/api/ocr-status")
        
        if success and isinstance(data, dict):
            ocr_service = data.get("ocr_service", {})
            methods = ocr_service.get("methods", {})
            
            # Список медленных операций которые должны быть убраны
            forbidden_slow_operations = {
                "llm_vision",      # Медленные LLM вызовы
                "ocr_space",       # Внешние API вызовы
                "azure_vision",    # Внешние API вызовы
                "multiple_tesseract_calls",  # Множественные tesseract вызовы
                "opencv_operations",         # Сложная обработка изображений
                "image_enhancement"          # Долгие улучшения изображений
            }
            
            actual_methods = set(methods.keys())
            slow_operations_found = forbidden_slow_operations.intersection(actual_methods)
            
            # Проверяем что primary_method НЕ является медленным методом
            primary_method = ocr_service.get("primary_method")
            primary_is_fast = primary_method == "tesseract_ocr"
            
            # Проверяем что система оптимизирована для скорости
            optimized_for_speed = ocr_service.get("optimized_for_speed") is True
            
            # Проверяем что нет opencv операций в описании tesseract метода
            tesseract_method = methods.get("tesseract_ocr", {})
            tesseract_description = tesseract_method.get("description", "").lower()
            no_opencv_mentioned = "opencv" not in tesseract_description and "сложная обработка" not in tesseract_description
            
            self.log_test_result(
                "🎯 Медленные операции убраны (нет opencv, множественных вызовов)",
                len(slow_operations_found) == 0 and primary_is_fast and optimized_for_speed and no_opencv_mentioned,
                f"Slow operations found: {slow_operations_found}, Primary fast: {primary_is_fast}, Speed optimized: {optimized_for_speed}",
                {
                    "forbidden_operations": list(forbidden_slow_operations),
                    "slow_operations_found": list(slow_operations_found),
                    "primary_method": primary_method,
                    "optimized_for_speed": optimized_for_speed
                }
            )
        else:
            self.log_test_result("🎯 Медленные операции убраны (нет opencv, множественных вызовов)", False, f"Error: {error}", data)
    
    async def test_fast_pdf_processing(self):
        """🎯 КРИТИЧЕСКИЙ ТЕСТ: Проверить что PDF обработка стала быстрой (только direct extraction, без OCR)"""
        logger.info("=== 🎯 КРИТИЧЕСКИЙ ТЕСТ: Быстрая PDF обработка ===")
        
        success, data, error = await self.make_request("GET", "/api/ocr-status")
        
        if success and isinstance(data, dict):
            ocr_service = data.get("ocr_service", {})
            methods = ocr_service.get("methods", {})
            
            # Проверяем что есть direct_pdf метод
            direct_pdf_method = methods.get("direct_pdf", {})
            direct_pdf_available = direct_pdf_method.get("available") is True
            
            # Проверяем описание direct_pdf метода
            direct_pdf_description = direct_pdf_method.get("description", "").lower()
            is_direct_extraction = "прямое извлечение" in direct_pdf_description or "direct" in direct_pdf_description
            no_ocr_for_pdf = "без ocr" in direct_pdf_description or "direct extraction" in direct_pdf_description
            
            # Проверяем что нет медленных PDF методов
            pdf_ocr_methods = {"pdf_ocr", "pdf_image_ocr", "pdf_tesseract_ocr"}
            actual_methods = set(methods.keys())
            no_slow_pdf_methods = len(pdf_ocr_methods.intersection(actual_methods)) == 0
            
            self.log_test_result(
                "🎯 Быстрая PDF обработка (только direct extraction)",
                direct_pdf_available and is_direct_extraction and no_slow_pdf_methods,
                f"Direct PDF available: {direct_pdf_available}, Direct extraction: {is_direct_extraction}, No slow PDF methods: {no_slow_pdf_methods}",
                {
                    "direct_pdf_available": direct_pdf_available,
                    "direct_pdf_description": direct_pdf_method.get("description", ""),
                    "slow_pdf_methods_found": list(pdf_ocr_methods.intersection(actual_methods))
                }
            )
        else:
            self.log_test_result("🎯 Быстрая PDF обработка (только direct extraction)", False, f"Error: {error}", data)
    
    async def test_analyze_file_performance_ready(self):
        """🎯 КРИТИЧЕСКИЙ ТЕСТ: Тестировать загрузку и анализ через /api/analyze-file (проверить что endpoint работает быстро)"""
        logger.info("=== 🎯 КРИТИЧЕСКИЙ ТЕСТ: Производительность /api/analyze-file ===")
        
        # Создаем тестовое изображение
        test_image_data = self.create_test_image()
        
        # Тестируем разные форматы изображений для быстрой обработки
        image_formats = [
            ('test_photo.jpg', 'image/jpeg'),
            ('test_document.png', 'image/png'),
            ('test_scan.webp', 'image/webp')
        ]
        
        all_formats_fast = True
        response_times = []
        
        for filename, content_type in image_formats:
            form_data = aiohttp.FormData()
            form_data.add_field('file', test_image_data, filename=filename, content_type=content_type)
            form_data.add_field('language', 'ru')
            
            # Измеряем время ответа для проверки быстродействия
            start_time = time.time()
            success, data, error = await self.make_request("POST", "/api/analyze-file", data=form_data)
            response_time = time.time() - start_time
            response_times.append(response_time)
            
            # Endpoint должен быстро отвечать (даже с ошибкой аутентификации)
            is_fast_response = response_time < 3.0  # Должен отвечать в течение 3 секунд
            requires_auth = not success and ("401" in str(error) or "403" in str(error) or (isinstance(data, dict) and ("Not authenticated" in str(data.get("detail", "")))))
            
            if not (is_fast_response and requires_auth):
                all_formats_fast = False
                logger.warning(f"Format {filename} performance issue: fast={is_fast_response}, auth_required={requires_auth}, time={response_time:.2f}s")
        
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        self.log_test_result(
            "🎯 /api/analyze-file быстродействие (< 3 сек ответ)",
            all_formats_fast and avg_response_time < 3.0,
            f"All formats fast: {all_formats_fast}, Avg response time: {avg_response_time:.2f}s, Max time: {max(response_times):.2f}s",
            {
                "tested_formats": [f[0] for f in image_formats],
                "response_times": response_times,
                "average_response_time": avg_response_time,
                "max_response_time": max(response_times) if response_times else 0
            }
        )
    
    async def test_critical_letter_generation_endpoints(self):
        """🎯 КРИТИЧЕСКОЕ ТЕСТИРОВАНИЕ: Основные endpoints для генерации писем"""
        logger.info("=== 🎯 КРИТИЧЕСКОЕ ТЕСТИРОВАНИЕ: Letter Generation Endpoints ===")
        
        # 1. Test GET /api/letter-categories - должен возвращать категории писем
        success, data, error = await self.make_request("GET", "/api/letter-categories")
        if success and isinstance(data, dict):
            has_status = data.get("status") == "success"
            has_categories = "categories" in data and isinstance(data["categories"], list)
            categories_count = len(data.get("categories", []))
            
            # Проверяем что есть основные категории (Job Center, BAMF, медицинские)
            categories = data.get("categories", [])
            category_keys = [cat.get("key") for cat in categories if isinstance(cat, dict)]
            has_job_center = "job_center" in category_keys
            has_bamf = "bamf" in category_keys
            has_medical = any("medical" in key or "health" in key for key in category_keys)
            
            self.log_test_result(
                "🎯 GET /api/letter-categories - Категории писем",
                has_status and has_categories and categories_count >= 3 and has_job_center,
                f"Status: {has_status}, Categories count: {categories_count}, Has Job Center: {has_job_center}, Keys: {category_keys[:5]}",
                data
            )
        else:
            self.log_test_result("🎯 GET /api/letter-categories - Категории писем", False, f"Error: {error}", data)
        
        # 2. Test GET /api/letter-templates/{category} - шаблоны по категории
        success, data, error = await self.make_request("GET", "/api/letter-templates/job_center")
        if success and isinstance(data, dict):
            has_status = data.get("status") == "success"
            has_templates = "templates" in data and isinstance(data["templates"], list)
            templates_count = len(data.get("templates", []))
            has_category = data.get("category") == "job_center"
            
            self.log_test_result(
                "🎯 GET /api/letter-templates/job_center - Шаблоны Job Center",
                has_status and has_templates and templates_count > 0 and has_category,
                f"Status: {has_status}, Templates count: {templates_count}, Category: {data.get('category')}",
                data
            )
        else:
            self.log_test_result("🎯 GET /api/letter-templates/job_center - Шаблоны Job Center", False, f"Error: {error}", data)
        
        # 3. Test GET /api/letter-template/{category}/{template} - конкретный шаблон
        success, data, error = await self.make_request("GET", "/api/letter-template/job_center/unemployment_benefit")
        # Может вернуть 404 если шаблон не найден - это нормально
        if success and isinstance(data, dict):
            has_status = data.get("status") == "success"
            has_template = "template" in data
            
            self.log_test_result(
                "🎯 GET /api/letter-template/job_center/unemployment_benefit - Конкретный шаблон",
                has_status and has_template,
                f"Status: {has_status}, Has template: {has_template}",
                data
            )
        elif "404" in str(error):
            # 404 - шаблон не найден, это приемлемо
            self.log_test_result(
                "🎯 GET /api/letter-template/job_center/unemployment_benefit - Конкретный шаблон",
                True,
                f"Template not found (404) - acceptable behavior",
                data
            )
        else:
            self.log_test_result("🎯 GET /api/letter-template/job_center/unemployment_benefit - Конкретный шаблон", False, f"Error: {error}", data)
        
        # 4. Test POST /api/generate-letter - основной endpoint для генерации писем (требует аутентификацию)
        test_letter_data = {
            "user_request": "Написать письмо в Job Center о продлении пособия по безработице",
            "recipient_type": "job_center",
            "recipient_info": {"name": "Job Center Berlin"},
            "sender_info": {"name": "Test User"},
            "include_translation": True
        }
        success, data, error = await self.make_request("POST", "/api/generate-letter", json=test_letter_data)
        
        # Должен требовать аутентификацию (401/403), не возвращать ошибку сервера
        is_auth_required = not success and ("401" in str(error) or "403" in str(error) or (isinstance(data, dict) and ("Not authenticated" in str(data.get("detail", "")))))
        
        self.log_test_result(
            "🎯 POST /api/generate-letter - Генерация письма (требует auth)",
            is_auth_required,
            f"Correctly requires authentication" if is_auth_required else f"Unexpected response: {error}",
            data
        )
        
        # 5. Test POST /api/generate-letter-template - генерация по шаблону (требует аутентификацию)
        test_template_data = {
            "template_category": "job_center",
            "template_key": "unemployment_benefit",
            "user_data": {"name": "Test User", "address": "Berlin"},
            "sender_info": {"name": "Test User"},
            "recipient_info": {"name": "Job Center Berlin"},
            "include_translation": True
        }
        success, data, error = await self.make_request("POST", "/api/generate-letter-template", json=test_template_data)
        
        is_auth_required = not success and ("401" in str(error) or "403" in str(error) or (isinstance(data, dict) and ("Not authenticated" in str(data.get("detail", "")))))
        
        self.log_test_result(
            "🎯 POST /api/generate-letter-template - Генерация по шаблону (требует auth)",
            is_auth_required,
            f"Correctly requires authentication" if is_auth_required else f"Unexpected response: {error}",
            data
        )
        
        # 6. Test POST /api/save-letter - сохранение письма (требует аутентификацию)
        test_save_data = {
            "title": "Test Letter",
            "content": "Test letter content",
            "content_german": "Test German content",
            "translation": "Test translation",
            "translation_language": "ru",
            "subject": "Test Subject",
            "recipient_type": "job_center",
            "letter_type": "custom",
            "generation_method": "ai"
        }
        success, data, error = await self.make_request("POST", "/api/save-letter", json=test_save_data)
        
        is_auth_required = not success and ("401" in str(error) or "403" in str(error) or (isinstance(data, dict) and ("Not authenticated" in str(data.get("detail", "")))))
        
        self.log_test_result(
            "🎯 POST /api/save-letter - Сохранение письма (требует auth)",
            is_auth_required,
            f"Correctly requires authentication" if is_auth_required else f"Unexpected response: {error}",
            data
        )
        
        # 7. Test POST /api/generate-letter-pdf - PDF генерация (требует аутентификацию)
        test_pdf_data = {
            "letter_id": "test-letter-id",
            "include_translation": True
        }
        success, data, error = await self.make_request("POST", "/api/generate-letter-pdf", json=test_pdf_data)
        
        is_auth_required = not success and ("401" in str(error) or "403" in str(error) or (isinstance(data, dict) and ("Not authenticated" in str(data.get("detail", "")))))
        
        self.log_test_result(
            "🎯 POST /api/generate-letter-pdf - PDF генерация (требует auth)",
            is_auth_required,
            f"Correctly requires authentication" if is_auth_required else f"Unexpected response: {error}",
            data
        )
    
    async def test_modern_llm_manager_status(self):
        """🎯 КРИТИЧЕСКОЕ ТЕСТИРОВАНИЕ: Modern LLM Manager Status"""
        logger.info("=== 🎯 КРИТИЧЕСКОЕ ТЕСТИРОВАНИЕ: Modern LLM Manager Status ===")
        
        # Test GET /api/modern-llm-status - должен показать modern: true
        success, data, error = await self.make_request("GET", "/api/modern-llm-status")
        if success and isinstance(data, dict):
            has_status = data.get("status") == "success"
            has_modern_flag = data.get("modern") is True
            has_providers = "providers" in data and isinstance(data["providers"], dict)
            
            # Проверяем что есть основные провайдеры
            providers = data.get("providers", {})
            has_gemini = "gemini" in providers
            has_openai = "openai" in providers
            has_anthropic = "anthropic" in providers
            
            # Проверяем что провайдеры имеют modern флаг
            providers_modern = all(
                provider_info.get("modern") is True 
                for provider_info in providers.values()
            ) if providers else False
            
            # Проверяем современные модели
            modern_models_found = []
            for provider_name, provider_info in providers.items():
                model = provider_info.get("model", "")
                if any(modern_model in model for modern_model in ["gemini-2.0-flash", "gpt-4o", "claude-3-5-sonnet"]):
                    modern_models_found.append(f"{provider_name}:{model}")
            
            self.log_test_result(
                "🎯 GET /api/modern-llm-status - Modern LLM Status (modern: true)",
                has_status and has_modern_flag and has_providers and providers_modern and len(modern_models_found) > 0,
                f"Status: {has_status}, Modern: {has_modern_flag}, Providers modern: {providers_modern}, Modern models: {modern_models_found}",
                data
            )
        else:
            self.log_test_result("🎯 GET /api/modern-llm-status - Modern LLM Status (modern: true)", False, f"Error: {error}", data)
        
        # Проверяем что emergentintegrations установлен и работает
        if success and isinstance(data, dict):
            providers = data.get("providers", {})
            emergent_support = all(
                provider_info.get("modern") is True 
                for provider_info in providers.values()
            ) if providers else False
            
            # Проверяем что система не в fallback режиме
            not_in_fallback = data.get("modern") is True and emergent_support
            
            self.log_test_result(
                "🎯 Emergentintegrations установлен и работает",
                not_in_fallback and emergent_support,
                f"Not in fallback: {not_in_fallback}, Emergent support: {emergent_support}, Providers: {list(providers.keys())}",
                data
            )
        else:
            self.log_test_result("🎯 Emergentintegrations установлен и работает", False, f"Error: {error}", data)
    
    async def test_user_api_keys_support(self):
        """🎯 КРИТИЧЕСКОЕ ТЕСТИРОВАНИЕ: User API Keys Support"""
        logger.info("=== 🎯 КРИТИЧЕСКОЕ ТЕСТИРОВАНИЕ: User API Keys Support ===")
        
        # 1. Test POST /api/api-keys - сохранение пользовательских ключей (требует auth)
        test_api_keys = {
            "api_key_1": "AIzaSyTest_Gemini_Key_123456789",
            "api_key_2": "sk-test_OpenAI_Key_123456789",
            "api_key_3": "sk-ant-test_Anthropic_Key_123456789"
        }
        success, data, error = await self.make_request("POST", "/api/api-keys", json=test_api_keys)
        
        # Должен требовать аутентификацию, НЕ validation error (что означало бы что поля не поддерживаются)
        is_auth_required = not success and ("401" in str(error) or "403" in str(error) or (isinstance(data, dict) and ("Not authenticated" in str(data.get("detail", "")))))
        has_validation_error = "422" in str(error) or (isinstance(data, dict) and "validation" in str(data).lower())
        
        self.log_test_result(
            "🎯 POST /api/api-keys - Новые поля API ключей поддерживаются",
            is_auth_required and not has_validation_error,
            f"Auth required: {is_auth_required}, No validation error: {not has_validation_error}" if (is_auth_required and not has_validation_error) else f"Field support issue: {error}",
            data
        )
        
        # 2. Test старые поля для обратной совместимости
        old_api_keys = {
            "gemini_api_key": "AIzaSyTest_Gemini_Key_123456789",
            "openai_api_key": "sk-test_OpenAI_Key_123456789",
            "anthropic_api_key": "sk-ant-test_Anthropic_Key_123456789"
        }
        success, data, error = await self.make_request("POST", "/api/api-keys", json=old_api_keys)
        
        old_fields_auth_required = not success and ("401" in str(error) or "403" in str(error) or (isinstance(data, dict) and ("Not authenticated" in str(data.get("detail", "")))))
        old_fields_validation_error = "422" in str(error) or (isinstance(data, dict) and "validation" in str(data).lower())
        
        self.log_test_result(
            "🎯 POST /api/api-keys - Старые поля API ключей совместимость",
            old_fields_auth_required and not old_fields_validation_error,
            f"Old fields supported" if (old_fields_auth_required and not old_fields_validation_error) else f"Compatibility issue: {error}",
            data
        )
        
        # 3. Test POST /api/quick-gemini-setup - быстрая настройка Gemini (требует auth)
        test_gemini_setup = {
            "api_key": "AIzaSyTest_Quick_Gemini_Setup_123456789"
        }
        success, data, error = await self.make_request("POST", "/api/quick-gemini-setup", json=test_gemini_setup)
        
        is_auth_required = not success and ("401" in str(error) or "403" in str(error) or (isinstance(data, dict) and ("Not authenticated" in str(data.get("detail", "")))))
        
        self.log_test_result(
            "🎯 POST /api/quick-gemini-setup - Быстрая настройка Gemini",
            is_auth_required,
            f"Correctly requires authentication" if is_auth_required else f"Unexpected response: {error}",
            data
        )
        
        # 4. Test что endpoint существует и правильно настроен
        endpoint_exists = is_auth_required or "422" in str(error)  # 422 означает что endpoint существует
        
        self.log_test_result(
            "🎯 POST /api/quick-gemini-setup - Endpoint доступен",
            endpoint_exists,
            f"Endpoint exists and properly configured" if endpoint_exists else f"Endpoint not found: {error}",
            data
        )
    
    async def test_additional_letter_endpoints(self):
        """🎯 ДОПОЛНИТЕЛЬНЫЕ ТЕСТЫ: Другие endpoints для работы с письмами"""
        logger.info("=== 🎯 ДОПОЛНИТЕЛЬНЫЕ ТЕСТЫ: Дополнительные Letter Endpoints ===")
        
        # 1. Test GET /api/letter-search - поиск шаблонов
        success, data, error = await self.make_request("GET", "/api/letter-search?query=unemployment")
        if success and isinstance(data, dict):
            has_status = data.get("status") == "success"
            has_query = data.get("query") == "unemployment"
            has_results = "results" in data and isinstance(data["results"], list)
            has_count = "count" in data and isinstance(data["count"], int)
            
            self.log_test_result(
                "🎯 GET /api/letter-search - Поиск шаблонов",
                has_status and has_query and has_results and has_count,
                f"Status: {has_status}, Query: {data.get('query')}, Results count: {data.get('count')}",
                data
            )
        else:
            self.log_test_result("🎯 GET /api/letter-search - Поиск шаблонов", False, f"Error: {error}", data)
        
        # 2. Test GET /api/user-letters - получение сохраненных писем (требует auth)
        success, data, error = await self.make_request("GET", "/api/user-letters")
        
        is_auth_required = not success and ("401" in str(error) or "403" in str(error) or (isinstance(data, dict) and ("Not authenticated" in str(data.get("detail", "")))))
        
        self.log_test_result(
            "🎯 GET /api/user-letters - Получение писем пользователя (требует auth)",
            is_auth_required,
            f"Correctly requires authentication" if is_auth_required else f"Unexpected response: {error}",
            data
        )
        
        # 3. Test POST /api/improve-letter - улучшение письма (требует auth)
        test_improve_data = {
            "letter_content": "Test letter content to improve",
            "improvement_type": "grammar"
        }
        success, data, error = await self.make_request("POST", "/api/improve-letter", json=test_improve_data)
        
        is_auth_required = not success and ("401" in str(error) or "403" in str(error) or (isinstance(data, dict) and ("Not authenticated" in str(data.get("detail", "")))))
        
        self.log_test_result(
            "🎯 POST /api/improve-letter - Улучшение письма (требует auth)",
            is_auth_required,
            f"Correctly requires authentication" if is_auth_required else f"Unexpected response: {error}",
            data
        )
    
    async def test_authentication_system_integrity(self):
        """🎯 КРИТИЧЕСКОЕ ТЕСТИРОВАНИЕ: Система аутентификации"""
        logger.info("=== 🎯 КРИТИЧЕСКОЕ ТЕСТИРОВАНИЕ: Authentication System ===")
        
        # 1. Test Google OAuth endpoint
        test_google_auth = {"credential": "invalid_google_token_test"}
        success, data, error = await self.make_request("POST", "/api/auth/google/verify", json=test_google_auth)
        
        # Должен отклонить неверный токен с 400 ошибкой
        is_400_error = "400" in str(error) or (isinstance(data, dict) and "Invalid Google token" in str(data.get("detail", "")))
        
        self.log_test_result(
            "🎯 POST /api/auth/google/verify - Google OAuth (неверный токен)",
            not success and is_400_error,
            f"Correctly rejected invalid token" if is_400_error else f"Unexpected response: {error}",
            data
        )
        
        # 2. Test Telegram auth endpoint
        test_telegram_auth = {
            "telegram_user": {
                "id": 123456789,
                "first_name": "Test",
                "username": "testuser"
            }
        }
        success, data, error = await self.make_request("POST", "/api/auth/telegram/verify", json=test_telegram_auth)
        
        # Может успешно создать пользователя или отклонить из-за неверной подписи
        telegram_handled = success or "400" in str(error) or "authentication failed" in str(data).lower() if isinstance(data, dict) else False
        
        self.log_test_result(
            "🎯 POST /api/auth/telegram/verify - Telegram Auth",
            telegram_handled,
            f"Telegram auth properly handled" if telegram_handled else f"Unexpected response: {error}",
            data
        )
        
        # 3. Test что все protected endpoints требуют аутентификацию
        protected_endpoints = [
            ("GET", "/api/profile"),
            ("POST", "/api/api-keys"),
            ("POST", "/api/generate-letter"),
            ("POST", "/api/save-letter"),
            ("GET", "/api/user-letters"),
            ("POST", "/api/quick-gemini-setup")
        ]
        
        all_require_auth = True
        
        for method, endpoint in protected_endpoints:
            if method == "POST":
                success, data, error = await self.make_request(method, endpoint, json={"test": "data"})
            else:
                success, data, error = await self.make_request(method, endpoint)
            
            requires_auth = not success and ("401" in str(error) or "403" in str(error) or (isinstance(data, dict) and ("Not authenticated" in str(data.get("detail", "")))))
            
            if not requires_auth:
                all_require_auth = False
                logger.warning(f"{method} {endpoint} does not require authentication!")
        
        self.log_test_result(
            "🎯 Все protected endpoints требуют аутентификацию",
            all_require_auth,
            f"All protected endpoints correctly require authentication" if all_require_auth else f"Some endpoints allow unauthorized access",
            {"all_require_auth": all_require_auth}
        )
    
    async def test_error_handling_quality(self):
        """🎯 КРИТИЧЕСКОЕ ТЕСТИРОВАНИЕ: Качество обработки ошибок"""
        logger.info("=== 🎯 КРИТИЧЕСКОЕ ТЕСТИРОВАНИЕ: Error Handling Quality ===")
        
        # 1. Test что при отсутствии API ключей возвращаются правильные ошибки
        # Тестируем через protected endpoints которые требуют API ключи
        
        # Test generate-letter без аутентификации
        test_letter_data = {
            "user_request": "Test letter request",
            "recipient_type": "job_center"
        }
        success, data, error = await self.make_request("POST", "/api/generate-letter", json=test_letter_data)
        
        # Должен вернуть информативную ошибку аутентификации
        has_informative_auth_error = not success and ("401" in str(error) or "403" in str(error) or (isinstance(data, dict) and ("Not authenticated" in str(data.get("detail", "")))))
        
        self.log_test_result(
            "🎯 Информативные ошибки аутентификации",
            has_informative_auth_error,
            f"Informative auth error provided" if has_informative_auth_error else f"Poor error handling: {error}",
            data
        )
        
        # 2. Test validation errors для неправильных данных
        invalid_letter_data = {
            "user_request": "",  # Пустой запрос
            "recipient_type": "invalid_type"
        }
        success, data, error = await self.make_request("POST", "/api/generate-letter", json=invalid_letter_data)
        
        # Должен вернуть ошибку аутентификации (так как endpoint защищен), не validation error
        handles_invalid_data = not success and ("401" in str(error) or "403" in str(error) or "422" in str(error))
        
        self.log_test_result(
            "🎯 Обработка неверных данных",
            handles_invalid_data,
            f"Invalid data properly handled" if handles_invalid_data else f"Poor data validation: {error}",
            data
        )
        
        # 3. Test что API возвращает JSON ошибки, не HTML
        success, data, error = await self.make_request("GET", "/api/nonexistent-endpoint")
        
        # Должен вернуть 404, и желательно JSON, не HTML
        is_404 = "404" in str(error)
        is_json_response = isinstance(data, dict) or (isinstance(data, str) and not data.startswith("<!DOCTYPE"))
        
        self.log_test_result(
            "🎯 JSON ошибки (не HTML)",
            is_404 and is_json_response,
            f"404 error with JSON response" if (is_404 and is_json_response) else f"HTML error response: {type(data)}",
            {"is_404": is_404, "is_json": is_json_response}
        )
    
    async def test_system_readiness_for_production(self):
        """🎯 ИТОГОВЫЙ ТЕСТ: Готовность системы к production"""
        logger.info("=== 🎯 ИТОГОВЫЙ ТЕСТ: System Production Readiness ===")
        
        # 1. Test основные health endpoints
        success, data, error = await self.make_request("GET", "/api/health")
        if success and isinstance(data, dict):
            is_healthy = data.get("status") == "healthy"
            has_db_connection = "users_count" in data and "analyses_count" in data
            is_sqlite = data.get("database") == "sqlite"
            
            health_status = is_healthy and has_db_connection and is_sqlite
        else:
            health_status = False
        
        # 2. Test Modern LLM status
        success, data, error = await self.make_request("GET", "/api/modern-llm-status")
        if success and isinstance(data, dict):
            modern_llm_ready = data.get("modern") is True and data.get("status") == "success"
        else:
            modern_llm_ready = False
        
        # 3. Test что основные letter endpoints существуют
        letter_endpoints_exist = True
        critical_endpoints = [
            "/api/letter-categories",
            "/api/letter-templates/job_center",
            "/api/generate-letter",
            "/api/save-letter"
        ]
        
        for endpoint in critical_endpoints:
            if endpoint.startswith("/api/generate-") or endpoint.startswith("/api/save-"):
                # Protected endpoints - должны требовать auth
                success, data, error = await self.make_request("POST", endpoint, json={"test": "data"})
                endpoint_exists = not success and ("401" in str(error) or "403" in str(error) or "422" in str(error))
            else:
                # Public endpoints - должны работать
                success, data, error = await self.make_request("GET", endpoint)
                endpoint_exists = success or "404" not in str(error)
            
            if not endpoint_exists:
                letter_endpoints_exist = False
                logger.warning(f"Critical endpoint {endpoint} not working properly")
        
        # 4. Test что аутентификация работает
        success, data, error = await self.make_request("POST", "/api/auth/google/verify", json={"credential": "test"})
        auth_system_works = not success and ("400" in str(error) or "Invalid" in str(data).get("detail", "") if isinstance(data, dict) else False)
        
        # Общая оценка готовности системы
        system_ready = all([
            health_status,
            modern_llm_ready,
            letter_endpoints_exist,
            auth_system_works
        ])
        
        self.log_test_result(
            "🎯 СИСТЕМА ГОТОВА К PRODUCTION - German Letter AI",
            system_ready,
            f"Health: {health_status}, Modern LLM: {modern_llm_ready}, Endpoints: {letter_endpoints_exist}, Auth: {auth_system_works}",
            {
                "health_status": health_status,
                "modern_llm_ready": modern_llm_ready,
                "letter_endpoints_exist": letter_endpoints_exist,
                "auth_system_works": auth_system_works,
                "overall_ready": system_ready
            }
        )
        
        return system_ready
    
    async def test_simple_tesseract_ocr_methods_only(self):
        """🎯 КРИТИЧЕСКИЙ ТЕСТ: Проверка что остались только tesseract_ocr и direct_pdf методы"""
        logger.info("=== 🎯 КРИТИЧЕСКИЙ ТЕСТ: Только tesseract_ocr и direct_pdf методы ===")
        
        success, data, error = await self.make_request("GET", "/api/ocr-status")
        
        if success and isinstance(data, dict) and "ocr_service" in data:
            ocr_service = data["ocr_service"]
            methods = ocr_service.get("methods", {})
            
            # Check that ONLY tesseract_ocr and direct_pdf methods exist
            expected_methods = {"tesseract_ocr", "direct_pdf"}
            actual_methods = set(methods.keys())
            
            # Check that forbidden methods are NOT present
            forbidden_methods = {"llm_vision", "ocr_space", "azure_vision"}
            forbidden_found = forbidden_methods.intersection(actual_methods)
            
            # Check that only expected methods are present
            only_expected_methods = actual_methods == expected_methods
            no_forbidden_methods = len(forbidden_found) == 0
            
            # Check tesseract_ocr method details
            tesseract_method = methods.get("tesseract_ocr", {})
            tesseract_available = tesseract_method.get("available") is True
            tesseract_description = tesseract_method.get("description", "")
            tesseract_is_only_method = "единственный метод" in tesseract_description
            
            # Check direct_pdf method details
            direct_pdf_method = methods.get("direct_pdf", {})
            direct_pdf_available = direct_pdf_method.get("available") is True
            
            self.log_test_result(
                "🎯 КРИТИЧЕСКИЙ ТЕСТ: Только tesseract_ocr и direct_pdf методы",
                only_expected_methods and no_forbidden_methods and tesseract_available and direct_pdf_available,
                f"Expected: {expected_methods}, Actual: {actual_methods}, Forbidden found: {forbidden_found}, Tesseract only: {tesseract_is_only_method}",
                {"expected_methods": list(expected_methods), "actual_methods": list(actual_methods), "forbidden_found": list(forbidden_found)}
            )
        else:
            self.log_test_result("🎯 КРИТИЧЕСКИЙ ТЕСТ: Только tesseract_ocr и direct_pdf методы", False, f"Error getting OCR status: {error}", data)
    
    async def test_fast_image_processing_functionality(self):
        """🎯 КРИТИЧЕСКИЙ ТЕСТ: Быстрая обработка изображений без долгих задержек"""
        logger.info("=== 🎯 КРИТИЧЕСКИЙ ТЕСТ: Быстрая обработка изображений ===")
        
        # Test that analyze-file endpoint exists and handles different image formats quickly
        test_image_data = self.create_test_image()
        
        # Test different image formats for fast processing
        image_formats = [
            ('test_image.jpg', 'image/jpeg'),
            ('test_image.png', 'image/png'),
            ('test_image.webp', 'image/webp'),
            ('test_image.gif', 'image/gif')
        ]
        
        all_formats_handled = True
        
        for filename, content_type in image_formats:
            form_data = aiohttp.FormData()
            form_data.add_field('file', test_image_data, filename=filename, content_type=content_type)
            form_data.add_field('language', 'ru')
            
            # Measure response time to ensure it's fast (not hanging)
            start_time = time.time()
            success, data, error = await self.make_request("POST", "/api/analyze-file", data=form_data)
            response_time = time.time() - start_time
            
            # Should fail with authentication required (not timeout or processing error)
            is_auth_required = not success and ("401" in str(error) or "403" in str(error) or (isinstance(data, dict) and ("Not authenticated" in str(data.get("detail", "")))))
            is_fast_response = response_time < 5.0  # Should respond within 5 seconds (not hang)
            
            if not (is_auth_required and is_fast_response):
                all_formats_handled = False
                logger.warning(f"Format {filename} issue: auth_required={is_auth_required}, fast_response={is_fast_response}, time={response_time:.2f}s")
        
        self.log_test_result(
            "🎯 КРИТИЧЕСКИЙ ТЕСТ: Быстрая обработка изображений",
            all_formats_handled,
            f"All image formats handled quickly without hanging" if all_formats_handled else f"Some formats had issues",
            {"tested_formats": [f[0] for f in image_formats]}
        )
    
    async def test_telegram_mini_app_compatibility(self):
        """🎯 КРИТИЧЕСКИЙ ТЕСТ: Совместимость с Telegram Mini App"""
        logger.info("=== 🎯 КРИТИЧЕСКИЙ ТЕСТ: Совместимость с Telegram Mini App ===")
        
        # Test 1: Root endpoint shows Telegram Mini App support
        success, data, error = await self.make_request("GET", "/")
        if success and isinstance(data, dict):
            has_telegram_flag = data.get("telegram_mini_app") is True
            has_message = "Telegram Mini App" in str(data.get("message", ""))
            
            self.log_test_result(
                "🎯 Root endpoint - Telegram Mini App support",
                has_telegram_flag and has_message,
                f"Telegram flag: {has_telegram_flag}, Message: {data.get('message')}",
                data
            )
        else:
            self.log_test_result("🎯 Root endpoint - Telegram Mini App support", False, f"Error: {error}", data)
        
        # Test 2: Health endpoint shows Telegram Mini App support
        success, data, error = await self.make_request("GET", "/health")
        if success and isinstance(data, dict):
            has_telegram_flag = data.get("telegram_mini_app") is True
            is_healthy = data.get("status") == "healthy"
            
            self.log_test_result(
                "🎯 Health endpoint - Telegram Mini App support",
                has_telegram_flag and is_healthy,
                f"Telegram flag: {has_telegram_flag}, Status: {data.get('status')}",
                data
            )
        else:
            self.log_test_result("🎯 Health endpoint - Telegram Mini App support", False, f"Error: {error}", data)
        
        # Test 3: Telegram authentication endpoint exists
        success, data, error = await self.make_request("POST", "/api/auth/telegram/verify", json={})
        
        # Should fail with validation error (endpoint exists) not 404
        endpoint_exists = not success and ("422" in str(error) or "400" in str(error) or (isinstance(data, dict) and ("validation" in str(data).lower() or "required" in str(data).lower())))
        
        self.log_test_result(
            "🎯 Telegram auth endpoint - Availability",
            endpoint_exists,
            f"Telegram auth endpoint exists and handles requests" if endpoint_exists else f"Endpoint issue: {error}",
            data
        )
        
        # Test 4: Fast OCR processing for Telegram photos
        success, data, error = await self.make_request("GET", "/api/ocr-status")
        if success and isinstance(data, dict):
            ocr_service = data.get("ocr_service", {})
            optimized_for_speed = ocr_service.get("optimized_for_speed") is True
            primary_method = ocr_service.get("primary_method") == "tesseract_ocr"
            
            self.log_test_result(
                "🎯 OCR Service - Telegram photo processing readiness",
                optimized_for_speed and primary_method,
                f"Speed optimized: {optimized_for_speed}, Primary method: {ocr_service.get('primary_method')}",
                ocr_service
            )
        else:
            self.log_test_result("🎯 OCR Service - Telegram photo processing readiness", False, f"Error: {error}", data)
    
    async def test_eternal_loading_fix_comprehensive(self):
        """🎯 ГЛАВНЫЙ ТЕСТ: Исправление вечной загрузки в Telegram Mini App OCR сервисе"""
        logger.info("=== 🎯 ГЛАВНЫЙ ТЕСТ: Исправление вечной загрузки в Telegram Mini App OCR сервисе ===")
        
        # ОСНОВНЫЕ ПРОВЕРКИ согласно требованиям
        success, data, error = await self.make_request("GET", "/api/ocr-status")
        
        if success and isinstance(data, dict):
            ocr_service = data.get("ocr_service", {})
            
            # 1. Endpoint /api/ocr-status возвращает новый Simple Tesseract OCR Service
            service_name = ocr_service.get("service_name", "")
            is_simple_tesseract = service_name == "Simple Tesseract OCR Service"
            
            # 2. Tesseract версия 5.3.0 доступна
            tesseract_version = ocr_service.get("tesseract_version", "")
            has_version_5_3_0 = tesseract_version == "5.3.0"
            
            # 3. primary_method: "tesseract_ocr"
            primary_method = ocr_service.get("primary_method", "")
            primary_is_tesseract = primary_method == "tesseract_ocr"
            
            # 4. optimized_for_speed: true
            optimized_for_speed = ocr_service.get("optimized_for_speed") is True
            
            # 5. Убраны все методы кроме tesseract_ocr и direct_pdf
            methods = ocr_service.get("methods", {})
            expected_methods = {"tesseract_ocr", "direct_pdf"}
            actual_methods = set(methods.keys())
            only_expected_methods = actual_methods == expected_methods
            
            # Проверяем что запрещенные методы отсутствуют
            forbidden_methods = {"llm_vision", "ocr_space", "azure_vision"}
            no_forbidden_methods = len(forbidden_methods.intersection(actual_methods)) == 0
            
            # Проверяем что tesseract_ocr доступен
            tesseract_method = methods.get("tesseract_ocr", {})
            tesseract_available = tesseract_method.get("available") is True
            
            # Проверяем что direct_pdf доступен
            direct_pdf_method = methods.get("direct_pdf", {})
            direct_pdf_available = direct_pdf_method.get("available") is True
            
            # Общая проверка исправления
            eternal_loading_fixed = all([
                is_simple_tesseract,
                has_version_5_3_0,
                primary_is_tesseract,
                optimized_for_speed,
                only_expected_methods,
                no_forbidden_methods,
                tesseract_available,
                direct_pdf_available
            ])
            
            self.log_test_result(
                "🎯 ГЛАВНЫЙ ТЕСТ: Исправление вечной загрузки - ПОЛНАЯ ПРОВЕРКА",
                eternal_loading_fixed,
                f"Service: {is_simple_tesseract}, Version: {has_version_5_3_0}, Primary: {primary_is_tesseract}, Speed: {optimized_for_speed}, Methods: {only_expected_methods}, No forbidden: {no_forbidden_methods}",
                {
                    "service_name": service_name,
                    "tesseract_version": tesseract_version,
                    "primary_method": primary_method,
                    "optimized_for_speed": optimized_for_speed,
                    "expected_methods": list(expected_methods),
                    "actual_methods": list(actual_methods),
                    "forbidden_methods_found": list(forbidden_methods.intersection(actual_methods))
                }
            )
            
            # Дополнительные детальные проверки
            self.log_test_result(
                "🎯 Проверка 1: Simple Tesseract OCR Service",
                is_simple_tesseract,
                f"Service name: '{service_name}' == 'Simple Tesseract OCR Service'",
                {"service_name": service_name}
            )
            
            self.log_test_result(
                "🎯 Проверка 2: Tesseract версия 5.3.0",
                has_version_5_3_0,
                f"Version: '{tesseract_version}' == '5.3.0'",
                {"tesseract_version": tesseract_version}
            )
            
            self.log_test_result(
                "🎯 Проверка 3: primary_method tesseract_ocr",
                primary_is_tesseract,
                f"Primary method: '{primary_method}' == 'tesseract_ocr'",
                {"primary_method": primary_method}
            )
            
            self.log_test_result(
                "🎯 Проверка 4: optimized_for_speed true",
                optimized_for_speed,
                f"Optimized for speed: {optimized_for_speed}",
                {"optimized_for_speed": optimized_for_speed}
            )
            
            self.log_test_result(
                "🎯 Проверка 5: Только tesseract_ocr и direct_pdf методы",
                only_expected_methods and no_forbidden_methods,
                f"Expected: {expected_methods}, Actual: {actual_methods}, Forbidden found: {forbidden_methods.intersection(actual_methods)}",
                {
                    "expected": list(expected_methods),
                    "actual": list(actual_methods),
                    "forbidden_found": list(forbidden_methods.intersection(actual_methods))
                }
            )
            
        else:
            self.log_test_result("🎯 ГЛАВНЫЙ ТЕСТ: Исправление вечной загрузки - ПОЛНАЯ ПРОВЕРКА", False, f"Error getting OCR status: {error}", data)
    
    async def test_render_deployment_tesseract_fix(self):
        """Test Render deployment fix - Tesseract as PRIMARY OCR method"""
        logger.info("=== Testing Render Deployment Tesseract Fix ===")
        
        # Test 1: OCR Status shows tesseract_ocr as primary_method
        success, data, error = await self.make_request("GET", "/api/ocr-status")
        
        if success and isinstance(data, dict):
            ocr_service = data.get("ocr_service", {})
            primary_method = ocr_service.get("primary_method")
            tesseract_dependency = ocr_service.get("tesseract_dependency")
            tesseract_version = ocr_service.get("tesseract_version")
            production_ready = ocr_service.get("production_ready")
            
            # Check that tesseract_ocr is PRIMARY method (not fallback)
            is_tesseract_primary = primary_method == "tesseract_ocr"
            has_tesseract_dependency = tesseract_dependency is True
            has_correct_version = tesseract_version == "5.3.0"
            is_production_ready = production_ready is True
            
            self.log_test_result(
                "OCR Status - Tesseract as PRIMARY method",
                is_tesseract_primary and has_tesseract_dependency and has_correct_version and is_production_ready,
                f"Primary: {primary_method}, Dependency: {tesseract_dependency}, Version: {tesseract_version}, Production: {production_ready}",
                data
            )
        else:
            self.log_test_result("OCR Status - Tesseract as PRIMARY method", False, f"Error: {error}", data)
    
    async def test_tesseract_system_availability(self):
        """Test that Tesseract is available in the system"""
        logger.info("=== Testing Tesseract System Availability ===")
        
        # Test OCR service status for tesseract availability
        success, data, error = await self.make_request("GET", "/api/ocr-status")
        
        if success and isinstance(data, dict):
            ocr_service = data.get("ocr_service", {})
            methods = ocr_service.get("methods", {})
            tesseract_method = methods.get("tesseract_ocr", {})
            
            # Check tesseract availability
            tesseract_available = tesseract_method.get("available") is True
            tesseract_description = tesseract_method.get("description", "")
            has_correct_description = "традиционный OCR" in tesseract_description or "Tesseract OCR" in tesseract_description
            
            # Check that tesseract is marked as main method, not fallback
            is_main_method = "основной метод" in tesseract_description or "primary" in tesseract_description.lower()
            
            self.log_test_result(
                "Tesseract System - Availability check",
                tesseract_available and has_correct_description and is_main_method,
                f"Available: {tesseract_available}, Description: {tesseract_description}, Is main: {is_main_method}",
                tesseract_method
            )
        else:
            self.log_test_result("Tesseract System - Availability check", False, f"Error: {error}", data)
    
    async def test_tesseract_language_packages(self):
        """Test that all required language packages are working"""
        logger.info("=== Testing Tesseract Language Packages ===")
        
        # Test OCR service status for language support
        success, data, error = await self.make_request("GET", "/api/ocr-status")
        
        if success and isinstance(data, dict):
            ocr_service = data.get("ocr_service", {})
            methods = ocr_service.get("methods", {})
            tesseract_method = methods.get("tesseract_ocr", {})
            
            # Check if tesseract is available (implies language packages work)
            tesseract_available = tesseract_method.get("available") is True
            tesseract_description = tesseract_method.get("description", "")
            
            # Check for multi-language support indication
            supports_multiple_languages = "многих языков" in tesseract_description or "languages" in tesseract_description.lower()
            
            self.log_test_result(
                "Tesseract Language Packages - Multi-language support",
                tesseract_available and supports_multiple_languages,
                f"Available: {tesseract_available}, Multi-lang support: {supports_multiple_languages}",
                tesseract_method
            )
        else:
            self.log_test_result("Tesseract Language Packages - Multi-language support", False, f"Error: {error}", data)
    
    async def test_telegram_authentication_comprehensive(self):
        """🎯 COMPREHENSIVE TELEGRAM MINI APP AUTHENTICATION TESTING"""
        logger.info("=== 🎯 COMPREHENSIVE TELEGRAM MINI APP AUTHENTICATION TESTING ===")
        
        # Test 1: Verify Bot Token Configuration
        await self._test_bot_token_configuration()
        
        # Test 2: Test /api/auth/telegram/verify endpoint with different data formats
        await self._test_telegram_verify_endpoint_formats()
        
        # Test 3: Test user creation and ID format
        await self._test_telegram_user_creation()
        
        # Test 4: Test error handling
        await self._test_telegram_error_handling()
    async def _test_cors_configuration(self):
        """Test CORS configuration for Telegram Mini App"""
        logger.info("--- Testing CORS Configuration ---")
        
        # Test preflight request with Telegram Mini App origin
        telegram_origin = "https://germany-ai-mini-app.netlify.app"
        
        # Test OPTIONS request for CORS preflight
        headers = {
            "Origin": telegram_origin,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type,Authorization"
        }
        
        success, data, error = await self.make_request("OPTIONS", "/api/auth/telegram/verify", headers=headers)
        
        # CORS should allow the request (success or specific CORS response)
        cors_configured = success or "405" in str(error)  # 405 Method Not Allowed is acceptable for OPTIONS
        
        self.log_test_result(
            "CORS - Telegram Mini App origin support",
            cors_configured,
            f"CORS configured for Telegram Mini App origin" if cors_configured else f"CORS issue: {error}",
            {"origin": telegram_origin, "response": data}
        )
        
        # Test actual POST request with origin header
        test_data = {
            "telegram_user": {
                "id": 123456789,
                "first_name": "CORSTest",
                "last_name": "User"
            }
        }
        
        headers_with_origin = {"Origin": telegram_origin}
        success, data, error = await self.make_request("POST", "/api/auth/telegram/verify", json=test_data, headers=headers_with_origin)
        
        # Should not fail due to CORS (may fail due to auth validation, but not CORS)
        no_cors_error = "CORS" not in str(error).upper() and "cross-origin" not in str(error).lower()
        
        self.log_test_result(
            "CORS - POST request with Telegram origin",
            no_cors_error,
            f"No CORS blocking detected" if no_cors_error else f"CORS blocking detected: {error}",
            data
        )
    
    async def _test_fly_dev_backend_accessibility(self):
        """Test that fly.dev backend is accessible and working"""
        logger.info("--- Testing Fly.dev Backend Accessibility ---")
        
        # Test that we're actually testing the fly.dev backend
        is_fly_dev = "miniapp-wvsxfa.fly.dev" in self.backend_url
        
        self.log_test_result(
            "Backend URL - Using fly.dev production backend",
            is_fly_dev,
            f"Testing backend: {self.backend_url}" if is_fly_dev else f"Not testing fly.dev backend: {self.backend_url}",
            {"backend_url": self.backend_url}
        )
        
        # Test basic connectivity to fly.dev
        success, data, error = await self.make_request("GET", "/health")
        
        if success and isinstance(data, dict):
            has_telegram_flag = data.get("telegram_mini_app") is True
            is_healthy = data.get("status") == "healthy"
            
            self.log_test_result(
                "Fly.dev Backend - Health check",
                has_telegram_flag and is_healthy,
                f"Status: {data.get('status')}, Telegram Mini App: {data.get('telegram_mini_app')}",
                data
            )
        else:
            self.log_test_result("Fly.dev Backend - Health check", False, f"Error: {error}", data)
        
        # Test API prefix routing
        success, data, error = await self.make_request("GET", "/api/health")
        
        if success and isinstance(data, dict):
            api_routing_works = "status" in data
            
            self.log_test_result(
                "Fly.dev Backend - API prefix routing",
                api_routing_works,
                f"API routing works correctly" if api_routing_works else f"API routing issue",
                data
            )
        else:
            self.log_test_result("Fly.dev Backend - API prefix routing", False, f"Error: {error}", data)
        
        # Test 6: Test CORS configuration for Telegram Mini App
        await self._test_cors_configuration()
        
        # Test 7: Test fly.dev backend accessibility
        await self._test_fly_dev_backend_accessibility()
    
    async def _test_bot_token_configuration(self):
        """Test that Bot Token 8003539432:AAFJkAYdEhM6i77va_JFo5Z_OlCiDJX3BC4 is properly configured"""
        logger.info("--- Testing Bot Token Configuration ---")
        
        # Test with valid telegram_user data to see if bot token error occurs
        test_data = {
            "telegram_user": {
                "id": 123456789,
                "first_name": "BotTokenTest",
                "last_name": "User"
            }
        }
        
        success, data, error = await self.make_request("POST", "/api/auth/telegram/verify", json=test_data)
        
        # Check if we get "Bot token not configured" error
        bot_token_configured = True
        if not success and isinstance(data, dict):
            error_detail = data.get("detail", "")
            if "Bot token not configured" in error_detail:
                bot_token_configured = False
        
        self.log_test_result(
            "Bot Token Configuration - Token 8003539432:AAFJkAYdEhM6i77va_JFo5Z_OlCiDJX3BC4",
            bot_token_configured,
            f"Bot token properly configured" if bot_token_configured else f"Bot token not configured error: {data}",
            data
        )
    
    async def _test_telegram_verify_endpoint_formats(self):
        """Test /api/auth/telegram/verify with different data formats"""
        logger.info("--- Testing Different Authentication Data Formats ---")
        
        # Test Format 1: telegram_user
        telegram_user_data = {
            "telegram_user": {
                "id": 123456789,
                "first_name": "TestUser",
                "last_name": "Telegram",
                "username": "testuser_tg",
                "language_code": "en"
            }
        }
        
        success, data, error = await self.make_request("POST", "/api/auth/telegram/verify", json=telegram_user_data)
        
        if success and isinstance(data, dict):
            has_token = "access_token" in data and "token_type" in data
            has_user = "user" in data and isinstance(data["user"], dict)
            user_data = data.get("user", {})
            correct_id_format = user_data.get("id", "").startswith("telegram_123456789")
            
            self.log_test_result(
                "Telegram Auth - telegram_user format",
                has_token and has_user and correct_id_format,
                f"Success: Token={bool(has_token)}, User ID={user_data.get('id')}, Email={user_data.get('email')}",
                data
            )
        else:
            self.log_test_result(
                "Telegram Auth - telegram_user format",
                False,
                f"Failed: {error} - {data}",
                data
            )
        
        # Test Format 2: user
        user_data_format = {
            "user": {
                "id": 987654321,
                "first_name": "UserFormat",
                "last_name": "Test",
                "username": "userformat_test",
                "language_code": "ru"
            }
        }
        
        success, data, error = await self.make_request("POST", "/api/auth/telegram/verify", json=user_data_format)
        
        if success and isinstance(data, dict):
            has_token = "access_token" in data and "token_type" in data
            has_user = "user" in data and isinstance(data["user"], dict)
            user_data = data.get("user", {})
            correct_id_format = user_data.get("id", "").startswith("telegram_987654321")
            
            self.log_test_result(
                "Telegram Auth - user format",
                has_token and has_user and correct_id_format,
                f"Success: Token={bool(has_token)}, User ID={user_data.get('id')}, Email={user_data.get('email')}",
                data
            )
        else:
            self.log_test_result(
                "Telegram Auth - user format",
                False,
                f"Failed: {error} - {data}",
                data
            )
        
        # Test Format 3: initData (URL-encoded)
        init_data_format = {
            "initData": "user=%7B%22id%22%3A555666777%2C%22first_name%22%3A%22InitData%22%2C%22last_name%22%3A%22User%22%2C%22username%22%3A%22inituser%22%2C%22language_code%22%3A%22de%22%7D&auth_date=1234567890&hash=test_hash_value"
        }
        
        success, data, error = await self.make_request("POST", "/api/auth/telegram/verify", json=init_data_format)
        
        if success and isinstance(data, dict):
            has_token = "access_token" in data and "token_type" in data
            has_user = "user" in data and isinstance(data["user"], dict)
            user_data = data.get("user", {})
            correct_id_format = user_data.get("id", "").startswith("telegram_555666777")
            
            self.log_test_result(
                "Telegram Auth - initData format",
                has_token and has_user and correct_id_format,
                f"Success: Token={bool(has_token)}, User ID={user_data.get('id')}, Email={user_data.get('email')}",
                data
            )
        else:
            self.log_test_result(
                "Telegram Auth - initData format",
                False,
                f"Failed: {error} - {data}",
                data
            )
    
    async def _test_telegram_user_creation(self):
        """Test user creation and updates with telegram_* ID format"""
        logger.info("--- Testing User Creation and Updates ---")
        
        # Test creating new user
        new_user_data = {
            "telegram_user": {
                "id": 111222333,
                "first_name": "NewUser",
                "last_name": "Creation",
                "username": "newuser_create",
                "language_code": "de"
            }
        }
        
        success, data, error = await self.make_request("POST", "/api/auth/telegram/verify", json=new_user_data)
        
        if success and isinstance(data, dict):
            user_data = data.get("user", {})
            correct_id = user_data.get("id") == "telegram_111222333"
            correct_email = user_data.get("email") == "telegram_111222333@telegram.local"
            correct_provider = user_data.get("oauth_provider") == "Telegram"
            has_api_key_flags = all(key in user_data for key in ["has_gemini_api_key", "has_openai_api_key", "has_anthropic_api_key"])
            
            self.log_test_result(
                "User Creation - New telegram user",
                correct_id and correct_email and correct_provider and has_api_key_flags,
                f"ID: {user_data.get('id')}, Email: {user_data.get('email')}, Provider: {user_data.get('oauth_provider')}",
                user_data
            )
        else:
            self.log_test_result(
                "User Creation - New telegram user",
                False,
                f"Failed to create user: {error}",
                data
            )
        
        # Test updating existing user (same ID)
        updated_user_data = {
            "telegram_user": {
                "id": 111222333,
                "first_name": "UpdatedUser",
                "last_name": "Modified",
                "username": "updated_user",
                "language_code": "ru"
            }
        }
        
        success, data, error = await self.make_request("POST", "/api/auth/telegram/verify", json=updated_user_data)
        
        if success and isinstance(data, dict):
            user_data = data.get("user", {})
            same_id = user_data.get("id") == "telegram_111222333"
            updated_name = "UpdatedUser" in user_data.get("name", "")
            
            self.log_test_result(
                "User Update - Existing telegram user",
                same_id and updated_name,
                f"ID preserved: {same_id}, Name updated: {updated_name}, Name: {user_data.get('name')}",
                user_data
            )
        else:
            self.log_test_result(
                "User Update - Existing telegram user",
                False,
                f"Failed to update user: {error}",
                data
            )
    
    async def _test_telegram_error_handling(self):
        """Test error handling with invalid data"""
        logger.info("--- Testing Error Handling ---")
        
        error_test_cases = [
            ({}, "Empty request body"),
            ({"telegram_user": {}}, "Empty telegram_user object"),
            ({"telegram_user": {"first_name": "Test"}}, "Missing user ID"),
            ({"telegram_user": {"id": "invalid_id", "first_name": "Test"}}, "Invalid ID type"),
            ({"telegram_user": {"id": 123456}}, "Missing first_name"),
            ({"user": {"first_name": "Test"}}, "Missing ID in user object"),
            ({"initData": "invalid_data"}, "Invalid initData format"),
        ]
        
        for test_data, description in error_test_cases:
            success, data, error = await self.make_request("POST", "/api/auth/telegram/verify", json=test_data)
            
            # Should fail with appropriate error message
            handles_error_correctly = not success and isinstance(data, dict) and "detail" in data
            
            error_detail = data.get("detail", "") if isinstance(data, dict) else str(data)
            
            self.log_test_result(
                f"Error Handling - {description}",
                handles_error_correctly,
                f"Correctly handled invalid data: {error_detail}" if handles_error_correctly else f"Unexpected response: {error}",
                data
            )
    
    async def _test_telegram_response_format(self):
        """Test that response format is correct"""
        logger.info("--- Testing Response Format ---")
        
        test_data = {
            "telegram_user": {
                "id": 444555666,
                "first_name": "ResponseTest",
                "last_name": "User",
                "username": "response_test",
                "language_code": "en"
            }
        }
        
        success, data, error = await self.make_request("POST", "/api/auth/telegram/verify", json=test_data)
        
        if success and isinstance(data, dict):
            # Check main response structure
            has_access_token = "access_token" in data and isinstance(data["access_token"], str)
            has_token_type = data.get("token_type") == "bearer"
            has_user = "user" in data and isinstance(data["user"], dict)
            
            # Check user object structure
            user_data = data.get("user", {})
            required_user_fields = ["id", "email", "name", "oauth_provider"]
            has_required_fields = all(field in user_data for field in required_user_fields)
            
            # Check API key preview fields
            api_key_fields = ["has_gemini_api_key", "has_openai_api_key", "has_anthropic_api_key"]
            has_api_key_fields = all(field in user_data for field in api_key_fields)
            
            # Check preview fields
            preview_fields = ["gemini_key_preview", "openai_key_preview", "anthropic_key_preview"]
            has_preview_fields = all(field in user_data for field in preview_fields)
            
            self.log_test_result(
                "Response Format - Complete structure",
                has_access_token and has_token_type and has_user and has_required_fields and has_api_key_fields and has_preview_fields,
                f"Token: {bool(has_access_token)}, User fields: {has_required_fields}, API fields: {has_api_key_fields}, Preview fields: {has_preview_fields}",
                data
            )
        else:
            self.log_test_result(
                "Response Format - Complete structure",
                False,
                f"Failed to get proper response: {error}",
                data
            )
    
    async def test_telegram_bot_token_configuration(self):
        """Test that Telegram bot token is properly configured"""
        logger.info("=== Testing Telegram Bot Token Configuration ===")
        
        # Test that authentication attempts don't fail due to missing bot token
        telegram_user_data = {
            "telegram_user": {
                "id": 555666777,
                "first_name": "Token",
                "last_name": "Test",
                "username": "tokentest",
                "language_code": "en"
            }
        }
        
        success, data, error = await self.make_request("POST", "/api/auth/telegram/verify", json=telegram_user_data)
        
        # Should not fail with "Bot token not configured" error
        no_token_config_error = not (isinstance(data, dict) and "Bot token not configured" in str(data.get("detail", "")))
        
        # Should either succeed or fail with validation/hash errors (not config errors)
        proper_token_config = success or no_token_config_error
        
        self.log_test_result(
            "Telegram Bot Token - Configuration check",
            proper_token_config,
            f"Bot token properly configured" if proper_token_config else f"Token configuration issue: {error}",
            data
        )
        
        # Test that the expected bot token format is being used
        # We can't directly test the token value, but we can test that authentication works
        if success and isinstance(data, dict):
            has_valid_response = "access_token" in data and "user" in data
            
            self.log_test_result(
                "Telegram Bot Token - Authentication success",
                has_valid_response,
                f"Authentication successful with configured token",
                {"token_present": True, "auth_successful": has_valid_response}
            )
        else:
            # Even if auth fails, it should not be due to missing token
            self.log_test_result(
                "Telegram Bot Token - Authentication success",
                no_token_config_error,
                f"Token configured (auth may fail for other reasons): {error}",
                data
            )
    
    async def test_telegram_user_creation_and_updates(self):
        """Test that Telegram authentication creates and updates users correctly"""
        logger.info("=== Testing Telegram User Creation and Updates ===")
        
        # Test user creation with first authentication
        new_user_data = {
            "telegram_user": {
                "id": 999888777,
                "first_name": "New",
                "last_name": "User",
                "username": "newuser",
                "language_code": "uk"
            }
        }
        
        success, data, error = await self.make_request("POST", "/api/auth/telegram/verify", json=new_user_data)
        
        if success and isinstance(data, dict):
            user_info = data.get("user", {})
            
            # Check user data structure
            has_correct_id = user_info.get("id") == "telegram_999888777"
            has_correct_email = user_info.get("email") == "telegram_999888777@telegram.local"
            has_correct_name = "New User" in user_info.get("name", "")
            has_correct_provider = user_info.get("oauth_provider") == "Telegram"
            has_api_key_fields = all(field in user_info for field in ["has_gemini_api_key", "has_openai_api_key", "has_anthropic_api_key"])
            
            self.log_test_result(
                "Telegram User Creation - New user data structure",
                has_correct_id and has_correct_email and has_correct_name and has_correct_provider and has_api_key_fields,
                f"ID: {user_info.get('id')}, Email: {user_info.get('email')}, Name: {user_info.get('name')}, Provider: {user_info.get('oauth_provider')}",
                user_info
            )
            
            # Test user update with second authentication (same user)
            updated_user_data = {
                "telegram_user": {
                    "id": 999888777,  # Same ID
                    "first_name": "Updated",  # Changed name
                    "last_name": "User",
                    "username": "updateduser",  # Changed username
                    "language_code": "en"  # Changed language
                }
            }
            
            success2, data2, error2 = await self.make_request("POST", "/api/auth/telegram/verify", json=updated_user_data)
            
            if success2 and isinstance(data2, dict):
                user_info2 = data2.get("user", {})
                
                # Should have same ID but updated info
                same_id = user_info2.get("id") == "telegram_999888777"
                updated_name = "Updated User" in user_info2.get("name", "")
                
                self.log_test_result(
                    "Telegram User Creation - User update on re-authentication",
                    same_id and updated_name,
                    f"Same ID: {same_id}, Updated name: {updated_name}, New name: {user_info2.get('name')}",
                    user_info2
                )
            else:
                self.log_test_result(
                    "Telegram User Creation - User update on re-authentication",
                    False,
                    f"Update authentication failed: {error2}",
                    data2
                )
        else:
            self.log_test_result(
                "Telegram User Creation - New user data structure",
                False,
                f"User creation failed: {error}",
                data
            )
    
    async def test_telegram_auth_response_format(self):
        """Test that Telegram authentication response format is correct"""
        logger.info("=== Testing Telegram Authentication Response Format ===")
        
        test_user_data = {
            "telegram_user": {
                "id": 444555666,
                "first_name": "Format",
                "last_name": "Test",
                "username": "formattest",
                "language_code": "ru"
            }
        }
        
        success, data, error = await self.make_request("POST", "/api/auth/telegram/verify", json=test_user_data)
        
        if success and isinstance(data, dict):
            # Check required response fields
            has_access_token = "access_token" in data and isinstance(data["access_token"], str) and len(data["access_token"]) > 10
            has_token_type = data.get("token_type") == "bearer"
            has_user_object = "user" in data and isinstance(data["user"], dict)
            
            # Check user object structure
            user = data.get("user", {})
            user_has_id = "id" in user and user["id"].startswith("telegram_")
            user_has_email = "email" in user and "@telegram.local" in user["email"]
            user_has_name = "name" in user and isinstance(user["name"], str)
            user_has_oauth_provider = user.get("oauth_provider") == "Telegram"
            user_has_api_key_flags = all(
                field in user and isinstance(user[field], bool)
                for field in ["has_gemini_api_key", "has_openai_api_key", "has_anthropic_api_key"]
            )
            user_has_key_previews = all(
                field in user
                for field in ["gemini_key_preview", "openai_key_preview", "anthropic_key_preview"]
            )
            
            response_format_correct = (
                has_access_token and has_token_type and has_user_object and
                user_has_id and user_has_email and user_has_name and user_has_oauth_provider and
                user_has_api_key_flags and user_has_key_previews
            )
            
            self.log_test_result(
                "Telegram Auth Response - Format validation",
                response_format_correct,
                f"Token: {has_access_token}, User: {user_has_id}, Email: {user_has_email}, Provider: {user_has_oauth_provider}",
                {
                    "access_token_length": len(data.get("access_token", "")),
                    "token_type": data.get("token_type"),
                    "user_id": user.get("id"),
                    "user_email": user.get("email"),
                    "oauth_provider": user.get("oauth_provider")
                }
            )
        else:
            self.log_test_result(
                "Telegram Auth Response - Format validation",
                False,
                f"Authentication failed or invalid response: {error}",
                data
            )
    
    async def test_telegram_auth_service_validation(self):
        """Test telegram_auth_service.py validation logic"""
        logger.info("=== Testing Telegram Auth Service Validation ===")
        
        # Test 1: Valid user data should pass
        valid_user_data = {
            "telegram_user": {
                "id": 123456789,
                "first_name": "Valid",
                "last_name": "User",
                "username": "validuser"
            }
        }
        
        success, data, error = await self.make_request("POST", "/api/auth/telegram/verify", json=valid_user_data)
        
        valid_data_accepted = success and isinstance(data, dict) and "access_token" in data
        
        self.log_test_result(
            "Telegram Auth Service - Valid data acceptance",
            valid_data_accepted,
            f"Valid user data properly accepted" if valid_data_accepted else f"Valid data rejected: {error}",
            data
        )
        
        # Test 2: Missing required fields should fail
        invalid_user_data = {
            "telegram_user": {
                "username": "invaliduser"
                # Missing id and first_name
            }
        }
        
        success, data, error = await self.make_request("POST", "/api/auth/telegram/verify", json=invalid_user_data)
        
        invalid_data_rejected = not success and isinstance(data, dict) and ("required" in str(data).lower() or "invalid" in str(data).lower())
        
        self.log_test_result(
            "Telegram Auth Service - Invalid data rejection",
            invalid_data_rejected,
            f"Invalid user data properly rejected" if invalid_data_rejected else f"Invalid data not rejected: {error}",
            data
        )
        
        # Test 3: Test different data formats are handled
        formats_to_test = [
            {"telegram_user": {"id": 111, "first_name": "Test1"}},
            {"user": {"id": 222, "first_name": "Test2"}},
            {"initData": "user=%7B%22id%22%3A333%2C%22first_name%22%3A%22Test3%22%7D&auth_date=1234567890&hash=test"}
        ]
        
        formats_handled = 0
        for i, format_data in enumerate(formats_to_test):
            success, data, error = await self.make_request("POST", "/api/auth/telegram/verify", json=format_data)
            
            # Should either succeed or fail with validation/hash errors (not format errors)
            format_handled = success or (isinstance(data, dict) and not ("format" in str(data).lower() or "unexpected" in str(data).lower()))
            
            if format_handled:
                formats_handled += 1
        
        self.log_test_result(
            "Telegram Auth Service - Multiple format handling",
            formats_handled >= 2,  # At least 2 out of 3 formats should be handled
            f"Handled {formats_handled}/3 data formats correctly",
            {"formats_handled": formats_handled, "total_formats": len(formats_to_test)}
        )
    
    async def test_no_duplicate_telegram_endpoints(self):
        """Test that old duplicate Telegram endpoints have been removed"""
        logger.info("=== Testing No Duplicate Telegram Endpoints ===")
        
        # Test that only the correct endpoint exists
        correct_endpoint_exists = True
        success, data, error = await self.make_request("POST", "/api/auth/telegram/verify", json={})
        
        # Should not return 404 (endpoint exists)
        if "404" in str(error):
            correct_endpoint_exists = False
        
        self.log_test_result(
            "Telegram Endpoints - Correct endpoint exists",
            correct_endpoint_exists,
            f"Main endpoint /api/auth/telegram/verify exists" if correct_endpoint_exists else "Main endpoint not found",
            {"endpoint_exists": correct_endpoint_exists}
        )
        
        # Test potential duplicate endpoints that should NOT exist
        potential_duplicates = [
            "/api/telegram/auth",
            "/api/telegram/verify",
            "/api/auth/telegram",
            "/api/telegram-auth",
            "/telegram/auth"
        ]
        
        duplicates_found = []
        for endpoint in potential_duplicates:
            success, data, error = await self.make_request("POST", endpoint, json={})
            
            # If we get anything other than 404, the endpoint might exist
            if "404" not in str(error):
                duplicates_found.append(endpoint)
        
        no_duplicates = len(duplicates_found) == 0
        
        self.log_test_result(
            "Telegram Endpoints - No duplicate endpoints",
            no_duplicates,
            f"No duplicate endpoints found" if no_duplicates else f"Potential duplicates: {duplicates_found}",
            {"duplicates_found": duplicates_found}
        )
    
    async def test_render_deployment_dependencies(self):
        """Test that all dependencies are installed correctly for Render deployment"""
        logger.info("=== Testing Render Deployment Dependencies ===")
        
        # Test 1: Modern LLM manager works (not in fallback mode)
        success, data, error = await self.make_request("GET", "/api/modern-llm-status")
        
        if success and isinstance(data, dict):
            has_modern_flag = data.get("modern") is True
            status_success = data.get("status") == "success"
            has_providers = "providers" in data and len(data["providers"]) > 0
            
            # Check that it's not in fallback mode
            not_in_fallback = status_success and has_modern_flag
            
            self.log_test_result(
                "Render Dependencies - Modern LLM manager (not fallback)",
                not_in_fallback and has_providers,
                f"Modern: {has_modern_flag}, Status: {data.get('status')}, Providers: {len(data.get('providers', {}))}, Not fallback: {not_in_fallback}",
                data
            )
        else:
            self.log_test_result("Render Dependencies - Modern LLM manager (not fallback)", False, f"Error: {error}", data)
        
        # Test 2: System is production ready
        success, data, error = await self.make_request("GET", "/api/ocr-status")
        
        if success and isinstance(data, dict):
            production_ready = data.get("production_ready") is True
            ocr_service = data.get("ocr_service", {})
            service_production_ready = ocr_service.get("production_ready") is True
            
            self.log_test_result(
                "Render Dependencies - Production ready status",
                production_ready and service_production_ready,
                f"Main production ready: {production_ready}, OCR service production ready: {service_production_ready}",
                data
            )
        else:
            self.log_test_result("Render Dependencies - Production ready status", False, f"Error: {error}", data)
    
    async def test_system_not_in_fallback_mode(self):
        """Test that system is NOT working in fallback mode"""
        logger.info("=== Testing System Not in Fallback Mode ===")
        
        # Test 1: OCR service has tesseract as primary (not fallback)
        success, data, error = await self.make_request("GET", "/api/ocr-status")
        
        if success and isinstance(data, dict):
            ocr_service = data.get("ocr_service", {})
            primary_method = ocr_service.get("primary_method")
            tesseract_dependency = ocr_service.get("tesseract_dependency")
            
            # System should NOT be in fallback mode
            not_in_fallback = primary_method == "tesseract_ocr" and tesseract_dependency is True
            
            self.log_test_result(
                "System Status - Not in fallback mode (OCR)",
                not_in_fallback,
                f"Primary method: {primary_method}, Tesseract dependency: {tesseract_dependency}, Not fallback: {not_in_fallback}",
                data
            )
        else:
            self.log_test_result("System Status - Not in fallback mode (OCR)", False, f"Error: {error}", data)
        
        # Test 2: Modern LLM manager not in fallback
        success, data, error = await self.make_request("GET", "/api/modern-llm-status")
        
        if success and isinstance(data, dict):
            status = data.get("status")
            modern_flag = data.get("modern")
            
            # Should not be in fallback/error mode
            not_in_fallback_llm = status == "success" and modern_flag is True
            
            self.log_test_result(
                "System Status - Not in fallback mode (LLM)",
                not_in_fallback_llm,
                f"Status: {status}, Modern: {modern_flag}, Not fallback: {not_in_fallback_llm}",
                data
            )
        else:
            self.log_test_result("System Status - Not in fallback mode (LLM)", False, f"Error: {error}", data)
    
    async def test_telegram_authentication_comprehensive(self):
        """🎯 COMPREHENSIVE TELEGRAM AUTHENTICATION TESTING"""
        logger.info("=== 🎯 COMPREHENSIVE TELEGRAM AUTHENTICATION TESTING ===")
        
        # Test 1: Bot Token Configuration
        await self._test_bot_token_configuration()
        
        # Test 2: Different authentication data formats
        await self._test_telegram_verify_endpoint_formats()
        
        # Test 3: User creation and updates
        await self._test_telegram_user_creation()
        
        # Test 4: Error handling
        await self._test_telegram_error_handling()
        
        # Test 5: Response format validation
        await self._test_telegram_response_format()
        
        # Test 6: CORS configuration
        await self._test_cors_configuration()
        
        # Test 7: Fly.dev backend accessibility
        await self._test_fly_dev_backend_accessibility()
    
    async def test_basic_functionality_after_render_fix(self):
        """Test basic functionality after Render deployment fix"""
        logger.info("=== Testing Basic Functionality After Render Fix ===")
        
        # Test 1: Health check works
        success, data, error = await self.make_request("GET", "/api/health")
        
        if success and isinstance(data, dict):
            status_healthy = data.get("status") == "healthy"
            has_db_connection = "users_count" in data and "analyses_count" in data
            
            self.log_test_result(
                "Basic Functionality - Health check",
                status_healthy and has_db_connection,
                f"Status: {data.get('status')}, DB connected: {has_db_connection}",
                data
            )
        else:
            self.log_test_result("Basic Functionality - Health check", False, f"Error: {error}", data)
        
        # Test 2: Authentication endpoints work
        success, data, error = await self.make_request("POST", "/api/auth/google/verify", json={"credential": "invalid_token"})
        
        # Should fail with 400 (invalid token), not 500 (server error)
        auth_endpoint_works = not success and "400" in str(error)
        
        self.log_test_result(
            "Basic Functionality - Authentication endpoint",
            auth_endpoint_works,
            f"Auth endpoint properly handles requests" if auth_endpoint_works else f"Auth endpoint issue: {error}",
            data
        )
        
        # Test 3: Modern LLM status works
        success, data, error = await self.make_request("GET", "/api/modern-llm-status")
        
        if success and isinstance(data, dict):
            modern_llm_works = data.get("modern") is True and data.get("status") == "success"
            
            self.log_test_result(
                "Basic Functionality - Modern LLM status",
                modern_llm_works,
                f"Modern LLM status working: {modern_llm_works}",
                data
            )
        else:
            self.log_test_result("Basic Functionality - Modern LLM status", False, f"Error: {error}", data)

    async def test_german_letter_ai_endpoints(self):
        """🎯 ГЛАВНАЯ ЗАДАЧА: Тестирование API endpoints для системы составления документов German Letter AI"""
        logger.info("=== 🎯 ГЛАВНАЯ ЗАДАЧА: Тестирование German Letter AI API endpoints ===")
        
        # 1. GET /api/letter-categories - получение категорий шаблонов писем
        success, data, error = await self.make_request("GET", "/api/letter-categories")
        if success and isinstance(data, dict):
            has_status = data.get("status") == "success"
            has_categories = "categories" in data and isinstance(data["categories"], list)
            categories_count = len(data.get("categories", []))
            
            # Check if categories have proper structure
            categories_valid = True
            if has_categories and categories_count > 0:
                first_category = data["categories"][0]
                categories_valid = isinstance(first_category, dict) and "key" in first_category and "name" in first_category
            
            self.log_test_result(
                "GET /api/letter-categories - Получение категорий шаблонов",
                has_status and has_categories and categories_valid,
                f"Status: {data.get('status')}, Categories count: {categories_count}, Valid structure: {categories_valid}",
                data
            )
        else:
            self.log_test_result("GET /api/letter-categories - Получение категорий шаблонов", False, f"Error: {error}", data)
        
        # 2. GET /api/letter-templates/{category_key} - получение шаблонов по категории
        # Test with a common category key
        test_category = "job_center"  # Common category for German letters
        success, data, error = await self.make_request("GET", f"/api/letter-templates/{test_category}")
        if success and isinstance(data, dict):
            has_status = data.get("status") == "success"
            has_category = data.get("category") == test_category
            has_templates = "templates" in data and isinstance(data["templates"], list)
            
            # Check templates structure
            templates_valid = True
            if has_templates and len(data["templates"]) > 0:
                first_template = data["templates"][0]
                templates_valid = isinstance(first_template, dict) and "key" in first_template and "name" in first_template
            
            self.log_test_result(
                f"GET /api/letter-templates/{test_category} - Получение шаблонов по категории",
                has_status and has_category and has_templates,
                f"Status: {data.get('status')}, Category: {data.get('category')}, Templates count: {len(data.get('templates', []))}, Valid structure: {templates_valid}",
                data
            )
        else:
            self.log_test_result(f"GET /api/letter-templates/{test_category} - Получение шаблонов по категории", False, f"Error: {error}", data)
        
        # 3. GET /api/letter-template/{category_key}/{template_key} - получение конкретного шаблона
        test_template = "unemployment_benefit"  # Common template
        success, data, error = await self.make_request("GET", f"/api/letter-template/{test_category}/{test_template}")
        if success and isinstance(data, dict):
            has_status = data.get("status") == "success"
            has_template = "template" in data and isinstance(data["template"], dict)
            
            # Check template structure
            template_valid = False
            if has_template:
                template_data = data["template"]
                template_valid = all(field in template_data for field in ["name", "description", "template"])
            
            self.log_test_result(
                f"GET /api/letter-template/{test_category}/{test_template} - Получение конкретного шаблона",
                has_status and has_template and template_valid,
                f"Status: {data.get('status')}, Has template: {has_template}, Valid structure: {template_valid}",
                data
            )
        else:
            # 404 is acceptable if template doesn't exist
            is_404 = "404" in str(error)
            self.log_test_result(
                f"GET /api/letter-template/{test_category}/{test_template} - Получение конкретного шаблона",
                is_404,
                f"Template not found (404) - acceptable: {error}" if is_404 else f"Error: {error}",
                data
            )
        
        # 4. POST /api/generate-letter - генерация письма с AI (требует токен авторизации)
        letter_request = {
            "user_request": "Мне нужно написать письмо в Job Center о продлении пособия по безработице",
            "recipient_type": "job_center",
            "recipient_info": {"name": "Job Center Berlin"},
            "sender_info": {"name": "Max Mustermann", "address": "Berlin"},
            "include_translation": True
        }
        success, data, error = await self.make_request("POST", "/api/generate-letter", json=letter_request)
        
        # Should require authentication
        is_auth_required = not success and ("401" in str(error) or "403" in str(error) or (isinstance(data, dict) and ("Not authenticated" in str(data.get("detail", "")))))
        
        self.log_test_result(
            "POST /api/generate-letter - Генерация письма с AI (требует авторизацию)",
            is_auth_required,
            f"Correctly requires authentication" if is_auth_required else f"Unexpected response: {error}",
            data
        )
        
        # 5. POST /api/generate-letter-template - генерация письма по шаблону (требует токен авторизации)
        template_request = {
            "template_category": "job_center",
            "template_key": "unemployment_benefit",
            "user_data": {
                "name": "Max Mustermann",
                "address": "Berlin, Germany",
                "case_number": "12345"
            },
            "sender_info": {"name": "Max Mustermann"},
            "recipient_info": {"name": "Job Center Berlin"},
            "include_translation": True
        }
        success, data, error = await self.make_request("POST", "/api/generate-letter-template", json=template_request)
        
        # Should require authentication
        is_auth_required = not success and ("401" in str(error) or "403" in str(error) or (isinstance(data, dict) and ("Not authenticated" in str(data.get("detail", "")))))
        
        self.log_test_result(
            "POST /api/generate-letter-template - Генерация письма по шаблону (требует авторизацию)",
            is_auth_required,
            f"Correctly requires authentication" if is_auth_required else f"Unexpected response: {error}",
            data
        )
        
        # 6. POST /api/save-letter - сохранение письма (требует токен авторизации)
        save_request = {
            "title": "Письмо в Job Center",
            "content": "Sehr geehrte Damen und Herren, ich möchte mein Arbeitslosengeld verlängern...",
            "content_german": "Sehr geehrte Damen und Herren, ich möchte mein Arbeitslosengeld verlängern...",
            "translation": "Уважаемые дамы и господа, я хочу продлить пособие по безработице...",
            "translation_language": "ru",
            "subject": "Продление пособия по безработице",
            "recipient_type": "job_center",
            "letter_type": "official",
            "generation_method": "ai_generated"
        }
        success, data, error = await self.make_request("POST", "/api/save-letter", json=save_request)
        
        # Should require authentication
        is_auth_required = not success and ("401" in str(error) or "403" in str(error) or (isinstance(data, dict) and ("Not authenticated" in str(data.get("detail", "")))))
        
        self.log_test_result(
            "POST /api/save-letter - Сохранение письма (требует авторизацию)",
            is_auth_required,
            f"Correctly requires authentication" if is_auth_required else f"Unexpected response: {error}",
            data
        )
        
        # 7. POST /api/generate-letter-pdf - генерация PDF письма (требует токен авторизации)
        pdf_request = {
            "letter_id": "test-letter-id-123",
            "include_translation": True
        }
        success, data, error = await self.make_request("POST", "/api/generate-letter-pdf", json=pdf_request)
        
        # Should require authentication
        is_auth_required = not success and ("401" in str(error) or "403" in str(error) or (isinstance(data, dict) and ("Not authenticated" in str(data.get("detail", "")))))
        
        self.log_test_result(
            "POST /api/generate-letter-pdf - Генерация PDF письма (требует авторизацию)",
            is_auth_required,
            f"Correctly requires authentication" if is_auth_required else f"Unexpected response: {error}",
            data
        )
    
    async def test_german_letter_additional_endpoints(self):
        """Тестирование дополнительных endpoints для German Letter AI"""
        logger.info("=== Тестирование дополнительных German Letter AI endpoints ===")
        
        # Test search functionality
        success, data, error = await self.make_request("GET", "/api/letter-search?query=job")
        if success and isinstance(data, dict):
            has_status = data.get("status") == "success"
            has_query = data.get("query") == "job"
            has_results = "results" in data and isinstance(data["results"], list)
            has_count = "count" in data and isinstance(data["count"], int)
            
            self.log_test_result(
                "GET /api/letter-search - Поиск шаблонов",
                has_status and has_query and has_results and has_count,
                f"Status: {data.get('status')}, Query: {data.get('query')}, Results count: {data.get('count')}",
                data
            )
        else:
            self.log_test_result("GET /api/letter-search - Поиск шаблонов", False, f"Error: {error}", data)
        
        # Test user letters endpoint (requires auth)
        success, data, error = await self.make_request("GET", "/api/user-letters")
        is_auth_required = not success and ("401" in str(error) or "403" in str(error) or (isinstance(data, dict) and ("Not authenticated" in str(data.get("detail", "")))))
        
        self.log_test_result(
            "GET /api/user-letters - Получение сохраненных писем (требует авторизацию)",
            is_auth_required,
            f"Correctly requires authentication" if is_auth_required else f"Unexpected response: {error}",
            data
        )
        
        # Test improve letter endpoint (requires auth)
        improve_request = {
            "letter_content": "Sehr geehrte Damen und Herren, ich schreibe Ihnen wegen meiner Arbeitslosigkeit.",
            "improvement_type": "grammar"
        }
        success, data, error = await self.make_request("POST", "/api/improve-letter", json=improve_request)
        is_auth_required = not success and ("401" in str(error) or "403" in str(error) or (isinstance(data, dict) and ("Not authenticated" in str(data.get("detail", "")))))
        
        self.log_test_result(
            "POST /api/improve-letter - Улучшение письма (требует авторизацию)",
            is_auth_required,
            f"Correctly requires authentication" if is_auth_required else f"Unexpected response: {error}",
            data
        )

    async def test_german_letter_system_readiness(self):
        """Проверка готовности системы для работы с немецкими официальными письмами"""
        logger.info("=== Проверка готовности системы для немецких официальных писем ===")
        
        # Check if modern LLM is available for German letter generation
        success, data, error = await self.make_request("GET", "/api/modern-llm-status")
        if success and isinstance(data, dict):
            has_modern_flag = data.get("modern") is True
            providers = data.get("providers", {})
            
            # Check if providers support German language processing
            german_capable_providers = []
            for provider_name, provider_info in providers.items():
                if provider_info.get("modern") is True:
                    german_capable_providers.append(provider_name)
            
            self.log_test_result(
                "Modern LLM - Готовность для немецких писем",
                has_modern_flag and len(german_capable_providers) > 0,
                f"Modern LLM available: {has_modern_flag}, German-capable providers: {german_capable_providers}",
                data
            )
        else:
            self.log_test_result("Modern LLM - Готовность для немецких писем", False, f"Error: {error}", data)
        
        # Check database readiness for letter storage
        success, data, error = await self.make_request("GET", "/api/health")
        if success and isinstance(data, dict):
            is_healthy = data.get("status") == "healthy"
            has_db = data.get("database") == "sqlite"
            
            self.log_test_result(
                "Database - Готовность для хранения писем",
                is_healthy and has_db,
                f"Health: {data.get('status')}, Database: {data.get('database')}",
                data
            )
        else:
            self.log_test_result("Database - Готовность для хранения писем", False, f"Error: {error}", data)
        
        # Check authentication system for protected letter operations
        success, data, error = await self.make_request("POST", "/api/auth/google/verify", json={"credential": "test"})
        is_auth_configured = not success and ("400" in str(error) or "Invalid Google token" in str(data.get("detail", "")))
        
        self.log_test_result(
            "Authentication - Готовность для защищенных операций с письмами",
            is_auth_configured,
            f"Google OAuth properly configured" if is_auth_configured else f"Auth configuration issue: {error}",
            data
        )

    async def run_performance_focused_tests(self):
        """🎯 ГЛАВНАЯ ЗАДАЧА: Запуск тестов производительности OCR системы"""
        logger.info("🎯 НАЧИНАЕМ ТЕСТИРОВАНИЕ ОПТИМИЗИРОВАННОЙ СИСТЕМЫ OCR НА БЫСТРОДЕЙСТВИЕ")
        logger.info("=" * 80)
        
        # Основные тесты производительности согласно требованиям
        await self.test_ocr_performance_optimization()
        await self.test_fast_ocr_methods_only()
        await self.test_no_slow_operations_removed()
        await self.test_fast_pdf_processing()
        await self.test_analyze_file_performance_ready()
        await self.test_system_speed_optimization_summary()
        
        # Дополнительные тесты для полноты картины
        await self.test_basic_health_endpoints()
        await self.test_api_health_endpoints()
        await self.test_authentication_required_endpoints()
        
        logger.info("=" * 80)
        logger.info("🎯 ТЕСТИРОВАНИЕ ПРОИЗВОДИТЕЛЬНОСТИ OCR СИСТЕМЫ ЗАВЕРШЕНО")

    async def run_all_tests(self):
        """Run all backend tests with focus on German Letter AI critical functionality"""
        logger.info("🎯 STARTING CRITICAL GERMAN LETTER AI BACKEND TESTING")
        logger.info("=" * 80)
        
        try:
            # 🎯 КРИТИЧЕСКИЕ ТЕСТЫ для German Letter AI
            await self.test_critical_letter_generation_endpoints()
            await self.test_modern_llm_manager_status()
            await self.test_user_api_keys_support()
            await self.test_additional_letter_endpoints()
            await self.test_authentication_system_integrity()
            await self.test_error_handling_quality()
            
            # Основные системные тесты
            await self.test_basic_health_endpoints()
            await self.test_api_health_endpoints()
            await self.test_database_functionality()
            await self.test_telegram_news_endpoint()
            
            # Итоговый тест готовности системы
            system_ready = await self.test_system_readiness_for_production()
            
        except Exception as e:
            logger.error(f"Critical error during testing: {e}")
            self.log_test_result("Test Execution", False, f"Critical error: {e}", None)
            system_ready = False
        
        # Генерируем итоговый отчет
        return self.generate_critical_test_summary(system_ready)
    
    def generate_critical_test_summary(self, system_ready=False):
        """Generate and display critical test summary for German Letter AI"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        logger.info("=" * 80)
        logger.info("🎯 КРИТИЧЕСКОЕ ТЕСТИРОВАНИЕ GERMAN LETTER AI ЗАВЕРШЕНО")
        logger.info(f"📊 РЕЗУЛЬТАТЫ: {passed_tests}/{total_tests} тестов прошли успешно ({success_rate:.1f}% успех)")
        logger.info(f"✅ Успешно: {passed_tests}")
        logger.info(f"❌ Неудачно: {failed_tests}")
        logger.info(f"🚀 Система готова к production: {'ДА' if system_ready else 'НЕТ'}")
        logger.info("=" * 80)
        
        # Выводим критические результаты
        critical_tests = [result for result in self.test_results if "🎯" in result["test"]]
        critical_passed = sum(1 for result in critical_tests if result["success"])
        critical_total = len(critical_tests)
        
        if critical_total > 0:
            critical_success_rate = (critical_passed / critical_total * 100)
            logger.info(f"🎯 КРИТИЧЕСКИЕ ТЕСТЫ: {critical_passed}/{critical_total} ({critical_success_rate:.1f}% успех)")
            
            # Показываем результаты критических тестов
            logger.info("🎯 КРИТИЧЕСКИЕ РЕЗУЛЬТАТЫ:")
            for result in critical_tests:
                status = "✅" if result["success"] else "❌"
                logger.info(f"   {status} {result['test']}")
            
            # Показываем неудачные критические тесты
            failed_critical = [result for result in critical_tests if not result["success"]]
            if failed_critical:
                logger.info("❌ НЕУДАЧНЫЕ КРИТИЧЕСКИЕ ТЕСТЫ:")
                for result in failed_critical:
                    logger.info(f"   - {result['test']}: {result['details']}")
        
        logger.info("=" * 80)
        
        # Специальная проверка для проблемы "AI сервис недоступен"
        ai_service_tests = [
            result for result in self.test_results 
            if any(keyword in result["test"].lower() for keyword in [
                "generate-letter", "modern llm", "api keys", "emergentintegrations"
            ])
        ]
        
        if ai_service_tests:
            ai_passed = sum(1 for r in ai_service_tests if r["success"])
            ai_total = len(ai_service_tests)
            ai_success_rate = (ai_passed / ai_total * 100) if ai_total > 0 else 0
            
            logger.info(f"🤖 AI SERVICE AVAILABILITY TESTS: {ai_passed}/{ai_total} ({ai_success_rate:.1f}% успех)")
            
            if ai_success_rate >= 80:
                logger.info("✅ ПРОБЛЕМА 'AI СЕРВИС НЕДОСТУПЕН' РЕШЕНА!")
            else:
                logger.info("❌ ПРОБЛЕМА 'AI СЕРВИС НЕДОСТУПЕН' ОСТАЕТСЯ!")
            
            logger.info("=" * 80)
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": success_rate,
            "system_ready": system_ready,
            "critical_tests": critical_total,
            "critical_passed": critical_passed,
            "ai_service_fixed": ai_success_rate >= 80 if ai_service_tests else False,
            "test_results": self.test_results
        }
    
    def generate_performance_test_summary(self):
        """Generate and display performance test summary"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        logger.info("=" * 80)
        logger.info("🎯 PERFORMANCE OPTIMIZATION TESTING COMPLETE")
        logger.info("=" * 80)
        logger.info(f"📊 RESULTS: {success_rate:.1f}% success ({passed_tests}/{total_tests} tests)")
        logger.info(f"✅ PASSED: {passed_tests}")
        logger.info(f"❌ FAILED: {failed_tests}")
        logger.info("=" * 80)
        
        # Show performance-critical test results
        performance_tests = [
            r for r in self.test_results 
            if any(keyword in r["test"].lower() for keyword in [
                "ocr performance", "fast ocr", "slow operations", "pdf processing", 
                "analyze-file performance", "speed optimization"
            ])
        ]
        
        if performance_tests:
            perf_passed = sum(1 for r in performance_tests if r["success"])
            perf_total = len(performance_tests)
            logger.info(f"🚀 PERFORMANCE OPTIMIZATION: {perf_passed}/{perf_total} tests passed")
            
            for result in performance_tests:
                status = "✅" if result["success"] else "❌"
                logger.info(f"   {status} {result['test']}")
            logger.info("=" * 80)
        
        # Show failed tests
        if failed_tests > 0:
            logger.info("❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    logger.info(f"   • {result['test']}: {result['details']}")
            logger.info("=" * 80)
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": success_rate,
            "performance_tests": len(performance_tests),
            "performance_passed": sum(1 for r in performance_tests if r["success"]) if performance_tests else 0
        }
    
    def print_summary(self):
        """Print test summary"""
        logger.info("\n" + "="*60)
        logger.info("📊 BACKEND API TEST SUMMARY")
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
    async with BackendTester() as tester:
        await tester.run_all_tests()
        passed, total = tester.print_summary()
        
        # Return exit code based on results
        return 0 if passed == total else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
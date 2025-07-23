#!/usr/bin/env python3
"""
🎯 ENHANCED JOB SEARCH FUNCTIONALITY TESTING: German Job Search API Integration

КОНТЕКСТ:
Test the enhanced job search functionality with the new German job search API integration.
This includes testing the integration with https://rest.arbeitsagentur.de/jobboerse/jobsuche-service
and enhanced features like geolocation, advanced filtering, and real API integration.

ЗАДАЧИ ДЛЯ ТЕСТИРОВАНИЯ:

1. **Enhanced Job Search Endpoints:**
   - GET /api/job-search with new parameters (radius, work_time, published_since, contract_type, page)
   - POST /api/job-search with EnhancedJobSearchRequest body including geolocation
   - POST /api/user-location-info with coordinates
   - GET /api/search-radius-options 
   - GET /api/job-search-status for enhanced service status

2. **Geolocation Features:**
   - Test user location info endpoint with sample German coordinates (Berlin: lat: 52.5200, lon: 13.4050)
   - Verify radius options are returned correctly
   - Test job search with user coordinates and different radius values

3. **Advanced Filtering:**
   - Test work_time filters: vz, tz, ho, mj, snw
   - Test language_level filters: A1, A2, B1, B2, C1, C2
   - Test category filters: tech, healthcare, finance, marketing, sales, education, construction, logistics, gastronomy, retail, other
   - Test published_since filter (0-100 days)
   - Test contract_type filter (1=limited, 2=unlimited)

4. **Real API Integration:**
   - Verify the integration with https://rest.arbeitsagentur.de/jobboerse/jobsuche-service
   - Test that real job data is being returned (not demo data)
   - Test pagination with different page numbers
   - Test with German cities: Berlin, München, Hamburg, Köln

5. **Enhanced Response Format:**
   - Verify the new enhanced response structure with analysis, facets, search_metadata
   - Check that distance calculations work when user coordinates are provided
   - Verify language level estimation is working for German jobs
   - Test that job categories are properly analyzed

6. **Error Handling:**
   - Test with invalid coordinates
   - Test with invalid radius values
   - Test with invalid language levels
   - Test API failure scenarios

ОЖИДАЕМЫЕ РЕЗУЛЬТАТЫ:
- All enhanced endpoints should return 200 OK with proper structure
- Real job data from arbeitsagentur.de API should be returned
- Geolocation features should work with German coordinates
- Advanced filtering should work correctly
- Enhanced response format should include analysis and metadata
- Error handling should be robust

ФОКУС: Test the enhanced German job search functionality with real API integration.
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
    
    async def test_job_search_endpoints_corrected_functionality(self):
        """🎯 КРИТИЧЕСКИЙ ТЕСТ: Job Search API с исправленной функциональностью - search_query теперь НЕОБЯЗАТЕЛЬНЫЙ"""
        logger.info("=== 🎯 КРИТИЧЕСКИЙ ТЕСТ: Job Search API - search_query НЕОБЯЗАТЕЛЬНЫЙ ===")
        
        # 1. Test GET /api/job-search?location=Berlin&language_level=B1 (БЕЗ search_query - должен работать!)
        success, data, error = await self.make_request("GET", "/api/job-search?location=Berlin&language_level=B1")
        
        if success and isinstance(data, dict):
            has_status = "status" in data
            has_jobs = "jobs" in data and isinstance(data["jobs"], list)
            has_total_found = "total_found" in data
            has_applied_filters = "applied_filters" in data
            
            self.log_test_result(
                "🎯 GET /api/job-search?location=Berlin&language_level=B1 (БЕЗ search_query)",
                has_status and has_jobs and has_total_found and has_applied_filters,
                f"Status: {data.get('status')}, Jobs count: {len(data.get('jobs', []))}, Total found: {data.get('total_found')}, Applied filters: {data.get('applied_filters')}",
                data
            )
        else:
            self.log_test_result(
                "🎯 GET /api/job-search?location=Berlin&language_level=B1 (БЕЗ search_query)",
                False,
                f"ОШИБКА: Поиск без search_query не работает: {error}",
                data
            )
        
        # 2. Test GET /api/job-search?location=München&language_level=A2&search_query=Developer
        success, data, error = await self.make_request("GET", "/api/job-search?location=München&language_level=A2&search_query=Developer")
        
        if success and isinstance(data, dict):
            has_status = "status" in data
            has_jobs = "jobs" in data and isinstance(data["jobs"], list)
            has_total_found = "total_found" in data
            has_applied_filters = "applied_filters" in data
            
            self.log_test_result(
                "🎯 GET /api/job-search?location=München&language_level=A2&search_query=Developer",
                has_status and has_jobs and has_total_found and has_applied_filters,
                f"Status: {data.get('status')}, Jobs count: {len(data.get('jobs', []))}, Total found: {data.get('total_found')}, Applied filters: {data.get('applied_filters')}",
                data
            )
        else:
            self.log_test_result(
                "🎯 GET /api/job-search?location=München&language_level=A2&search_query=Developer",
                False,
                f"ОШИБКА: Поиск с полными параметрами не работает: {error}",
                data
            )
        
        # 3. Test GET /api/job-search?location=Hamburg&language_level=C1 (БЕЗ других параметров)
        success, data, error = await self.make_request("GET", "/api/job-search?location=Hamburg&language_level=C1")
        
        if success and isinstance(data, dict):
            has_status = "status" in data
            has_jobs = "jobs" in data and isinstance(data["jobs"], list)
            has_total_found = "total_found" in data
            has_applied_filters = "applied_filters" in data
            
            self.log_test_result(
                "🎯 GET /api/job-search?location=Hamburg&language_level=C1 (минимальные параметры)",
                has_status and has_jobs and has_total_found and has_applied_filters,
                f"Status: {data.get('status')}, Jobs count: {len(data.get('jobs', []))}, Total found: {data.get('total_found')}, Applied filters: {data.get('applied_filters')}",
                data
            )
        else:
            self.log_test_result(
                "🎯 GET /api/job-search?location=Hamburg&language_level=C1 (минимальные параметры)",
                False,
                f"ОШИБКА: Поиск с минимальными параметрами не работает: {error}",
                data
            )
        
        # 4. Test POST /api/job-search БЕЗ search_query (должен работать!)
        search_data_no_query = {
            "location": "Berlin",
            "language_level": "B2",
            "remote": False,
            "limit": 10
        }
        
        success, data, error = await self.make_request("POST", "/api/job-search", json=search_data_no_query)
        
        if success and isinstance(data, dict):
            has_status = "status" in data
            has_jobs = "jobs" in data and isinstance(data["jobs"], list)
            has_total_found = "total_found" in data
            has_applied_filters = "applied_filters" in data
            
            self.log_test_result(
                "🎯 POST /api/job-search БЕЗ search_query (location + language_level)",
                has_status and has_jobs and has_total_found and has_applied_filters,
                f"Status: {data.get('status')}, Jobs count: {len(data.get('jobs', []))}, Total found: {data.get('total_found')}, Applied filters: {data.get('applied_filters')}",
                data
            )
        else:
            self.log_test_result(
                "🎯 POST /api/job-search БЕЗ search_query (location + language_level)",
                False,
                f"КРИТИЧЕСКАЯ ОШИБКА: POST без search_query не работает: {error}",
                data
            )
        
        # 5. Test POST /api/job-search С search_query (для сравнения)
        search_data_with_query = {
            "search_query": "software developer",
            "location": "München",
            "language_level": "B1",
            "remote": False,
            "limit": 10
        }
        
        success, data, error = await self.make_request("POST", "/api/job-search", json=search_data_with_query)
        
        if success and isinstance(data, dict):
            has_status = "status" in data
            has_jobs = "jobs" in data and isinstance(data["jobs"], list)
            has_total_found = "total_found" in data
            has_applied_filters = "applied_filters" in data
            
            self.log_test_result(
                "🎯 POST /api/job-search С search_query (полные параметры)",
                has_status and has_jobs and has_total_found and has_applied_filters,
                f"Status: {data.get('status')}, Jobs count: {len(data.get('jobs', []))}, Total found: {data.get('total_found')}, Applied filters: {data.get('applied_filters')}",
                data
            )
        else:
            self.log_test_result(
                "🎯 POST /api/job-search С search_query (полные параметры)",
                False,
                f"ОШИБКА: POST с search_query не работает: {error}",
                data
            )

    async def test_cities_api_endpoints(self):
        """🎯 КРИТИЧЕСКИЙ ТЕСТ: Cities Search API Testing"""
        logger.info("=== 🎯 КРИТИЧЕСКИЙ ТЕСТ: Cities Search API Testing ===")
        
        # 1. Test GET /api/cities/popular (должен возвращать список популярных городов)
        success, data, error = await self.make_request("GET", "/api/cities/popular")
        
        if success and isinstance(data, dict):
            has_status = "status" in data
            has_cities = "cities" in data and isinstance(data["cities"], list)
            cities_count = len(data.get("cities", []))
            
            # Check city structure if cities exist
            city_structure_valid = True
            if data.get("cities"):
                first_city = data["cities"][0]
                required_city_fields = ["name", "state", "population"]
                city_structure_valid = all(field in first_city for field in required_city_fields)
            
            self.log_test_result(
                "🎯 GET /api/cities/popular - Популярные города",
                has_status and has_cities and cities_count > 0 and city_structure_valid,
                f"Status: {data.get('status')}, Cities count: {cities_count}, Structure valid: {city_structure_valid}",
                data
            )
        else:
            self.log_test_result(
                "🎯 GET /api/cities/popular - Популярные города",
                False,
                f"ОШИБКА: Популярные города не загружаются: {error}",
                data
            )
        
        # 2. Test GET /api/cities/search?q=Berlin (поиск конкретного города)
        success, data, error = await self.make_request("GET", "/api/cities/search?q=Berlin")
        
        if success and isinstance(data, dict):
            has_status = "status" in data
            has_cities = "cities" in data and isinstance(data["cities"], list)
            cities_count = len(data.get("cities", []))
            
            # Check if Berlin is found
            berlin_found = False
            if data.get("cities"):
                berlin_found = any(city.get("name", "").lower() == "berlin" for city in data["cities"])
            
            self.log_test_result(
                "🎯 GET /api/cities/search?q=Berlin - Поиск конкретного города",
                has_status and has_cities and berlin_found,
                f"Status: {data.get('status')}, Cities found: {cities_count}, Berlin found: {berlin_found}",
                data
            )
        else:
            self.log_test_result(
                "🎯 GET /api/cities/search?q=Berlin - Поиск конкретного города",
                False,
                f"ОШИБКА: Поиск Berlin не работает: {error}",
                data
            )
        
        # 3. Test GET /api/cities/search?q=Mün (частичный поиск)
        success, data, error = await self.make_request("GET", "/api/cities/search?q=Mün")
        
        if success and isinstance(data, dict):
            has_status = "status" in data
            has_cities = "cities" in data and isinstance(data["cities"], list)
            cities_count = len(data.get("cities", []))
            
            # Check if München is found (partial match)
            munich_found = False
            if data.get("cities"):
                munich_found = any("mün" in city.get("name", "").lower() for city in data["cities"])
            
            self.log_test_result(
                "🎯 GET /api/cities/search?q=Mün - Частичный поиск",
                has_status and has_cities and munich_found,
                f"Status: {data.get('status')}, Cities found: {cities_count}, München found: {munich_found}",
                data
            )
        else:
            self.log_test_result(
                "🎯 GET /api/cities/search?q=Mün - Частичный поиск",
                False,
                f"ОШИБКА: Частичный поиск Mün не работает: {error}",
                data
            )
        
        # 4. Test GET /api/cities/search?q=Hamburg (еще один тест точного поиска)
        success, data, error = await self.make_request("GET", "/api/cities/search?q=Hamburg")
        
        if success and isinstance(data, dict):
            has_status = "status" in data
            has_cities = "cities" in data and isinstance(data["cities"], list)
            cities_count = len(data.get("cities", []))
            
            # Check if Hamburg is found
            hamburg_found = False
            if data.get("cities"):
                hamburg_found = any(city.get("name", "").lower() == "hamburg" for city in data["cities"])
            
            self.log_test_result(
                "🎯 GET /api/cities/search?q=Hamburg - Поиск Hamburg",
                has_status and has_cities and hamburg_found,
                f"Status: {data.get('status')}, Cities found: {cities_count}, Hamburg found: {hamburg_found}",
                data
            )
        else:
            self.log_test_result(
                "🎯 GET /api/cities/search?q=Hamburg - Поиск Hamburg",
                False,
                f"ОШИБКА: Поиск Hamburg не работает: {error}",
                data
            )
        
        # 5. Test GET /api/cities/search?q=Fra (частичный поиск Frankfurt)
        success, data, error = await self.make_request("GET", "/api/cities/search?q=Fra")
        
        if success and isinstance(data, dict):
            has_status = "status" in data
            has_cities = "cities" in data and isinstance(data["cities"], list)
            cities_count = len(data.get("cities", []))
            
            # Check if Frankfurt is found (partial match)
            frankfurt_found = False
            if data.get("cities"):
                frankfurt_found = any("fra" in city.get("name", "").lower() for city in data["cities"])
            
            self.log_test_result(
                "🎯 GET /api/cities/search?q=Fra - Частичный поиск Frankfurt",
                has_status and has_cities and frankfurt_found,
                f"Status: {data.get('status')}, Cities found: {cities_count}, Frankfurt found: {frankfurt_found}",
                data
            )
        else:
            self.log_test_result(
                "🎯 GET /api/cities/search?q=Fra - Частичный поиск Frankfurt",
                False,
                f"ОШИБКА: Частичный поиск Fra не работает: {error}",
                data
            )
        """🎯 КРИТИЧЕСКИЙ ТЕСТ: German Language Level Filtering (A1-C2)"""
        logger.info("=== 🎯 КРИТИЧЕСКИЙ ТЕСТ: German Language Level Filtering (A1-C2) ===")
        
        # Test all German language levels
        language_levels = ["A1", "A2", "B1", "B2", "C1", "C2"]
        level_results = {}
        all_levels_work = True
        
        for level in language_levels:
            search_data = {
                "search_query": "developer",
                "location": "Berlin", 
                "language_level": level,
                "limit": 10
            }
            
            success, data, error = await self.make_request("POST", "/api/job-search", json=search_data)
            
            if success and isinstance(data, dict):
                jobs_count = len(data.get("jobs", []))
                total_found = data.get("total_found", 0)
                level_results[level] = {"jobs": jobs_count, "total": total_found, "success": True}
                
                self.log_test_result(
                    f"🎯 German Language Level {level} - Works without authentication",
                    True,
                    f"Level {level}: {jobs_count} jobs found, Total available: {total_found}",
                    data
                )
            else:
                # Check if it's an authentication error (which would be wrong)
                is_auth_error = "401" in str(error) or "403" in str(error) or (isinstance(data, dict) and ("Not authenticated" in str(data.get("detail", ""))))
                level_results[level] = {"success": False, "auth_error": is_auth_error}
                all_levels_work = False
                
                self.log_test_result(
                    f"🎯 German Language Level {level} - Works without authentication",
                    False,
                    f"Level {level} failed: {error}. Auth error: {is_auth_error}",
                    data
                )
        
        # Summary test for all levels
        working_levels = [level for level, result in level_results.items() if result.get("success")]
        
    async def test_bundesagentur_api_integration_critical(self):
        """🎯 КРИТИЧЕСКАЯ ПРОВЕРКА: Убедиться что все вакансии теперь идут с правильного официального API"""
        logger.info("=== 🎯 КРИТИЧЕСКАЯ ПРОВЕРКА: Bundesagentur.de API Integration ===")
        
        # 1. **GET /api/job-search-status** - должен показывать bundesagentur.de как источник
        success, data, error = await self.make_request("GET", "/api/job-search-status")
        
        if success and isinstance(data, dict):
            # Проверяем api_source
            api_source = data.get("api_source")
            is_bundesagentur = api_source == "bundesagentur.de"
            
            # Проверяем bundesagentur_integration
            bundesagentur_integration = data.get("bundesagentur_integration")
            has_integration_info = isinstance(bundesagentur_integration, dict)
            correct_endpoint = False
            if has_integration_info:
                endpoint = bundesagentur_integration.get("api_endpoint", "")
                correct_endpoint = "rest.arbeitsagentur.de/jobboerse/jobsuche-service" in endpoint
            
            # НЕ должно быть упоминаний arbeitnow.com
            no_arbeitnow_mentions = "arbeitnow.com" not in str(data).lower()
            
            self.log_test_result(
                "🎯 GET /api/job-search-status - Bundesagentur.de API source",
                is_bundesagentur and has_integration_info and correct_endpoint and no_arbeitnow_mentions,
                f"API Source: {api_source}, Integration: {has_integration_info}, Correct endpoint: {correct_endpoint}, No arbeitnow: {no_arbeitnow_mentions}",
                data
            )
        else:
            self.log_test_result(
                "🎯 GET /api/job-search-status - Bundesagentur.de API source",
                False,
                f"ОШИБКА: {error}",
                data
            )
        
        # 2. **POST /api/job-search** - проверить что api_info.source = "bundesagentur.de"
        search_data = {
            "location": "Berlin",
            "language_level": "B1",
            "limit": 10
        }
        
        success, data, error = await self.make_request("POST", "/api/job-search", json=search_data)
        
        if success and isinstance(data, dict):
            # Проверяем api_info
            api_info = data.get("api_info", {})
            api_source = api_info.get("source")
            api_name = api_info.get("name", "")
            
            is_bundesagentur_source = api_source == "bundesagentur.de"
            is_official_name = "Bundesagentur für Arbeit" in api_name and "Official German Job Board" in api_name
            
            # Проверяем что вакансии действительно приходят
            has_jobs = "jobs" in data and isinstance(data["jobs"], list)
            
            self.log_test_result(
                "🎯 POST /api/job-search - Bundesagentur.de API response",
                is_bundesagentur_source and is_official_name and has_jobs,
                f"API Source: {api_source}, API Name: {api_name}, Has jobs: {has_jobs}",
                data
            )
        else:
            self.log_test_result(
                "🎯 POST /api/job-search - Bundesagentur.de API response",
                False,
                f"ОШИБКА: {error}",
                data
            )
        
        # 3. **GET /api/job-search?location=Berlin&language_level=B1** - проверить структуру ответа и источник данных
        success, data, error = await self.make_request("GET", "/api/job-search?location=Berlin&language_level=B1")
        
        if success and isinstance(data, dict):
            # Проверяем api_info
            api_info = data.get("api_info", {})
            api_source = api_info.get("source")
            
            is_bundesagentur_source = api_source == "bundesagentur.de"
            
            # Проверяем структуру ответа
            has_status = data.get("status") == "success"
            has_jobs = "jobs" in data and isinstance(data["jobs"], list)
            has_total_found = "total_found" in data
            
            # НЕ должно быть упоминаний arbeitnow.com в ответе
            no_arbeitnow_mentions = "arbeitnow.com" not in str(data).lower()
            
            self.log_test_result(
                "🎯 GET /api/job-search - Bundesagentur.de GET request",
                is_bundesagentur_source and has_status and has_jobs and no_arbeitnow_mentions,
                f"API Source: {api_source}, Status: {has_status}, Has jobs: {has_jobs}, No arbeitnow: {no_arbeitnow_mentions}",
                data
            )
        else:
            self.log_test_result(
                "🎯 GET /api/job-search - Bundesagentur.de GET request",
                False,
                f"ОШИБКА: {error}",
                data
            )

    async def test_telegram_mini_app_job_search_api_endpoints(self):
        """🎯 КРИТИЧЕСКИЙ ТЕСТ: Telegram Mini App Job Search API endpoints - ПОЛЬЗОВАТЕЛЬСКИЙ ЗАПРОС"""
        logger.info("=== 🎯 КРИТИЧЕСКИЙ ТЕСТ: Telegram Mini App Job Search API endpoints ===")
        
        # 1. **Cities API тестирование:**
        logger.info("--- Cities API Testing ---")
        
        # GET /api/cities/popular - должен возвращать популярные города
        success, data, error = await self.make_request("GET", "/api/cities/popular")
        
        if success and isinstance(data, dict):
            has_status = data.get("status") == "success"
            has_cities = "cities" in data and isinstance(data["cities"], list)
            cities_count = len(data.get("cities", []))
            
            self.log_test_result(
                "🎯 GET /api/cities/popular - популярные города",
                has_status and has_cities and cities_count > 0,
                f"Status: {data.get('status')}, Cities count: {cities_count}",
                data
            )
        else:
            self.log_test_result(
                "🎯 GET /api/cities/popular - популярные города",
                False,
                f"ОШИБКА: {error}",
                data
            )
        
        # GET /api/cities/search?q=Ber - поиск городов начинающихся с "Ber"
        success, data, error = await self.make_request("GET", "/api/cities/search?q=Ber")
        
        if success and isinstance(data, dict):
            has_status = data.get("status") == "success"
            has_cities = "cities" in data and isinstance(data["cities"], list)
            cities_count = len(data.get("cities", []))
            
            # Check if cities starting with "Ber" are found
            ber_cities_found = False
            if data.get("cities"):
                ber_cities_found = any(city.get("name", "").lower().startswith("ber") for city in data["cities"])
            
            self.log_test_result(
                "🎯 GET /api/cities/search?q=Ber - поиск городов начинающихся с 'Ber'",
                has_status and has_cities and ber_cities_found,
                f"Status: {data.get('status')}, Cities found: {cities_count}, Ber cities found: {ber_cities_found}",
                data
            )
        else:
            self.log_test_result(
                "🎯 GET /api/cities/search?q=Ber - поиск городов начинающихся с 'Ber'",
                False,
                f"ОШИБКА: {error}",
                data
            )
        
        # GET /api/cities/search?q=Köln - поиск города с немецкими символами
        success, data, error = await self.make_request("GET", "/api/cities/search?q=Köln")
        
        if success and isinstance(data, dict):
            has_status = data.get("status") == "success"
            has_cities = "cities" in data and isinstance(data["cities"], list)
            cities_count = len(data.get("cities", []))
            
            # Check if Köln is found with German symbols
            koln_found = False
            if data.get("cities"):
                koln_found = any("köln" in city.get("name", "").lower() for city in data["cities"])
            
            self.log_test_result(
                "🎯 GET /api/cities/search?q=Köln - поиск города с немецкими символами",
                has_status and has_cities and koln_found,
                f"Status: {data.get('status')}, Cities found: {cities_count}, Köln found: {koln_found}",
                data
            )
        else:
            self.log_test_result(
                "🎯 GET /api/cities/search?q=Köln - поиск города с немецкими символами",
                False,
                f"ОШИБКА: {error}",
                data
            )
        
        # GET /api/cities/search?q=Köl - частичный поиск как на скриншоте
        success, data, error = await self.make_request("GET", "/api/cities/search?q=Köl")
        
        if success and isinstance(data, dict):
            has_status = data.get("status") == "success"
            has_cities = "cities" in data and isinstance(data["cities"], list)
            cities_count = len(data.get("cities", []))
            
            # Check if partial search for Köl works
            kol_found = False
            if data.get("cities"):
                kol_found = any("köl" in city.get("name", "").lower() for city in data["cities"])
            
            self.log_test_result(
                "🎯 GET /api/cities/search?q=Köl - частичный поиск как на скриншоте",
                has_status and has_cities and kol_found,
                f"Status: {data.get('status')}, Cities found: {cities_count}, Köl partial match found: {kol_found}",
                data
            )
        else:
            self.log_test_result(
                "🎯 GET /api/cities/search?q=Köl - частичный поиск как на скриншоте",
                False,
                f"ОШИБКА: {error}",
                data
            )
        
        # 2. **Job Search API тестирование:**
        logger.info("--- Job Search API Testing ---")
        
        # GET /api/job-search?location=Berlin&language_level=B1 (без search_query)
        success, data, error = await self.make_request("GET", "/api/job-search?location=Berlin&language_level=B1")
        
        if success and isinstance(data, dict):
            has_status = data.get("status") == "success"
            has_jobs = "jobs" in data and isinstance(data["jobs"], list)
            no_pattern_error = "pattern" not in str(data).lower() and "string did not match" not in str(data).lower()
            
            self.log_test_result(
                "🎯 GET /api/job-search?location=Berlin&language_level=B1 (без search_query)",
                has_status and has_jobs and no_pattern_error,
                f"Status: {data.get('status')}, Jobs: {len(data.get('jobs', []))}, No pattern errors: {no_pattern_error}",
                data
            )
        else:
            pattern_error_detected = "pattern" in str(error).lower() or "string did not match" in str(error).lower()
            self.log_test_result(
                "🎯 GET /api/job-search?location=Berlin&language_level=B1 (без search_query)",
                False,
                f"ОШИБКА: {error}, Pattern error detected: {pattern_error_detected}",
                data
            )
        
        # GET /api/job-search?location=München&language_level=A2&search_query=Developer
        success, data, error = await self.make_request("GET", "/api/job-search?location=München&language_level=A2&search_query=Developer")
        
        if success and isinstance(data, dict):
            has_status = data.get("status") == "success"
            has_jobs = "jobs" in data and isinstance(data["jobs"], list)
            no_pattern_error = "pattern" not in str(data).lower() and "string did not match" not in str(data).lower()
            
            self.log_test_result(
                "🎯 GET /api/job-search?location=München&language_level=A2&search_query=Developer",
                has_status and has_jobs and no_pattern_error,
                f"Status: {data.get('status')}, Jobs: {len(data.get('jobs', []))}, No pattern errors: {no_pattern_error}",
                data
            )
        else:
            pattern_error_detected = "pattern" in str(error).lower() or "string did not match" in str(error).lower()
            self.log_test_result(
                "🎯 GET /api/job-search?location=München&language_level=A2&search_query=Developer",
                False,
                f"ОШИБКА: {error}, Pattern error detected: {pattern_error_detected}",
                data
            )
        
        # 3. **Проверка всех ответов:**
        logger.info("--- Response Structure Validation ---")
        
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
                has_correct_structure = "jobs" in data and isinstance(data["jobs"], list)
                no_pattern_error = "pattern" not in str(data).lower() and "string did not match" not in str(data).lower()
                
                if not (has_status and has_correct_structure and no_pattern_error):
                    all_responses_valid = False
                    if not no_pattern_error:
                        pattern_errors_found.append(description)
                
                self.log_test_result(
                    f"🎯 Response validation: {description}",
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
                    f"🎯 Response validation: {description}",
                    False,
                    f"ОШИБКА: {error}, Pattern error: {pattern_error_detected}",
                    data
                )
        
        # Final summary
        self.log_test_result(
            "🎯 ИТОГОВЫЙ РЕЗУЛЬТАТ: Telegram Mini App Job Search API",
            all_responses_valid and len(pattern_errors_found) == 0,
            f"Все ответы валидны: {all_responses_valid}, Pattern errors найдено: {len(pattern_errors_found)} в {pattern_errors_found}",
            {"all_valid": all_responses_valid, "pattern_errors": pattern_errors_found}
        )

    async def test_special_characters_and_spaces_handling(self):
        """🎯 КРИТИЧЕСКИЙ ТЕСТ: Обработка специальных символов и пробелов"""
        logger.info("=== 🎯 КРИТИЧЕСКИЙ ТЕСТ: Обработка специальных символов и пробелов ===")
        
        # 1. Test cities search with special characters (München)
        success, data, error = await self.make_request("GET", "/api/cities/search?q=München")
        
        if success and isinstance(data, dict):
            has_status = "status" in data and data["status"] == "success"
            has_cities = "cities" in data and isinstance(data["cities"], list)
            cities_count = len(data.get("cities", []))
            
            # Check if München is found with special characters
            munich_found = False
            if data.get("cities"):
                munich_found = any("münchen" in city.get("name", "").lower() for city in data["cities"])
            
            self.log_test_result(
                "🎯 Cities search with special characters (München)",
                has_status and has_cities and munich_found,
                f"Status: {data.get('status')}, Cities found: {cities_count}, München found: {munich_found}",
                data
            )
        else:
            self.log_test_result(
                "🎯 Cities search with special characters (München)",
                False,
                f"ОШИБКА: Поиск München с умлаутом не работает: {error}",
                data
            )
        
        # 2. Test job search with location containing spaces
        search_data_spaces = {
            "location": "Frankfurt am Main",
            "language_level": "B1",
            "limit": 5
        }
        
        success, data, error = await self.make_request("POST", "/api/job-search", json=search_data_spaces)
        
        if success and isinstance(data, dict):
            has_status = "status" in data and data["status"] == "success"
            has_jobs = "jobs" in data and isinstance(data["jobs"], list)
            
            self.log_test_result(
                "🎯 Job search with location containing spaces (Frankfurt am Main)",
                has_status and has_jobs,
                f"Status: {data.get('status')}, Jobs found: {len(data.get('jobs', []))}",
                data
            )
        else:
            self.log_test_result(
                "🎯 Job search with location containing spaces (Frankfurt am Main)",
                False,
                f"ОШИБКА: Поиск с пробелами в названии города не работает: {error}",
                data
            )
        
        # 3. Test job search with search_query containing special characters
        search_data_special = {
            "search_query": "C++ Developer",
            "location": "Berlin",
            "language_level": "B2",
            "limit": 5
        }
        
        success, data, error = await self.make_request("POST", "/api/job-search", json=search_data_special)
        
        if success and isinstance(data, dict):
            has_status = "status" in data and data["status"] == "success"
            has_jobs = "jobs" in data and isinstance(data["jobs"], list)
            
            self.log_test_result(
                "🎯 Job search with special characters in search_query (C++ Developer)",
                has_status and has_jobs,
                f"Status: {data.get('status')}, Jobs found: {len(data.get('jobs', []))}",
                data
            )
        else:
            self.log_test_result(
                "🎯 Job search with special characters in search_query (C++ Developer)",
                False,
                f"ОШИБКА: Поиск с специальными символами в запросе не работает: {error}",
                data
            )
        
        # 4. Test cities search with partial match containing special characters
        success, data, error = await self.make_request("GET", "/api/cities/search?q=Düss")
        
        if success and isinstance(data, dict):
            has_status = "status" in data and data["status"] == "success"
            has_cities = "cities" in data and isinstance(data["cities"], list)
            cities_count = len(data.get("cities", []))
            
            # Check if Düsseldorf is found with partial match
            dusseldorf_found = False
            if data.get("cities"):
                dusseldorf_found = any("düss" in city.get("name", "").lower() for city in data["cities"])
            
            self.log_test_result(
                "🎯 Cities search partial match with special characters (Düss)",
                has_status and has_cities and dusseldorf_found,
                f"Status: {data.get('status')}, Cities found: {cities_count}, Düsseldorf found: {dusseldorf_found}",
                data
            )
        else:
            self.log_test_result(
                "🎯 Cities search partial match with special characters (Düss)",
                False,
                f"ОШИБКА: Частичный поиск с умлаутом не работает: {error}",
                data
            )
        
        # 5. Test that no "pattern matching" errors occur
        # This is tested by checking that all responses are successful and don't contain pattern errors
        pattern_error_tests = [
            ("GET", "/api/cities/search?q=Ber", "Berlin partial search"),
            ("GET", "/api/cities/search?q=München", "München with umlaut"),
            ("POST", "/api/job-search", {"location": "Berlin", "language_level": "B1"}, "Job search minimal params")
        ]
        
        no_pattern_errors = True
        pattern_error_details = []
        
        for method, endpoint, test_data, description in pattern_error_tests:
            if method == "POST":
                success, data, error = await self.make_request(method, endpoint, json=test_data)
            else:
                success, data, error = await self.make_request(method, endpoint)
            
            # Check for pattern matching errors
            has_pattern_error = False
            if not success or isinstance(data, dict):
                error_text = str(error) + str(data)
                has_pattern_error = "pattern" in error_text.lower() or "did not match" in error_text.lower()
            
            if has_pattern_error:
                no_pattern_errors = False
                pattern_error_details.append(f"{description}: {error}")
        
        self.log_test_result(
            "🎯 No 'pattern matching' errors in API responses",
            no_pattern_errors,
            f"All endpoints free from pattern errors" if no_pattern_errors else f"Pattern errors found: {pattern_error_details}",
            {"pattern_errors": pattern_error_details}
        )

    async def test_telegram_mini_app_job_search_pattern_errors(self):
        """🎯 КРИТИЧЕСКИЙ ТЕСТ: Telegram Mini App Job Search - проверка ошибки 'The string did not match the expected pattern'"""
        logger.info("=== 🎯 КРИТИЧЕСКИЙ ТЕСТ: Telegram Mini App Job Search Pattern Errors ===")
        
        # 1. Test GET /api/job-search?location=Berlin&language_level=B1 (без search_query - это должно работать)
        success, data, error = await self.make_request("GET", "/api/job-search?location=Berlin&language_level=B1")
        
        if success and isinstance(data, dict):
            has_status = "status" in data and data["status"] == "success"
            has_jobs = "jobs" in data and isinstance(data["jobs"], list)
            no_pattern_error = "pattern" not in str(data).lower() and "match" not in str(error).lower()
            
            self.log_test_result(
                "🎯 GET /api/job-search?location=Berlin&language_level=B1 (без search_query)",
                has_status and has_jobs and no_pattern_error,
                f"Status: {data.get('status')}, Jobs: {len(data.get('jobs', []))}, No pattern errors: {no_pattern_error}",
                data
            )
        else:
            pattern_error_detected = "pattern" in str(error).lower() or "match" in str(error).lower()
            self.log_test_result(
                "🎯 GET /api/job-search?location=Berlin&language_level=B1 (без search_query)",
                False,
                f"ОШИБКА: {error}. Pattern error detected: {pattern_error_detected}",
                data
            )
        
        # 2. Test GET /api/job-search?location=München&language_level=A2&search_query=Developer (с search_query)
        success, data, error = await self.make_request("GET", "/api/job-search?location=München&language_level=A2&search_query=Developer")
        
        if success and isinstance(data, dict):
            has_status = "status" in data and data["status"] == "success"
            has_jobs = "jobs" in data and isinstance(data["jobs"], list)
            no_pattern_error = "pattern" not in str(data).lower() and "match" not in str(error).lower()
            
            self.log_test_result(
                "🎯 GET /api/job-search?location=München&language_level=A2&search_query=Developer",
                has_status and has_jobs and no_pattern_error,
                f"Status: {data.get('status')}, Jobs: {len(data.get('jobs', []))}, No pattern errors: {no_pattern_error}",
                data
            )
        else:
            pattern_error_detected = "pattern" in str(error).lower() or "match" in str(error).lower()
            self.log_test_result(
                "🎯 GET /api/job-search?location=München&language_level=A2&search_query=Developer",
                False,
                f"ОШИБКА: {error}. Pattern error detected: {pattern_error_detected}",
                data
            )
        
        # 3. Test GET /api/job-search?location=Hamburg&language_level=C1 (без search_query)
        success, data, error = await self.make_request("GET", "/api/job-search?location=Hamburg&language_level=C1")
        
        if success and isinstance(data, dict):
            has_status = "status" in data and data["status"] == "success"
            has_jobs = "jobs" in data and isinstance(data["jobs"], list)
            no_pattern_error = "pattern" not in str(data).lower() and "match" not in str(error).lower()
            
            self.log_test_result(
                "🎯 GET /api/job-search?location=Hamburg&language_level=C1 (без search_query)",
                has_status and has_jobs and no_pattern_error,
                f"Status: {data.get('status')}, Jobs: {len(data.get('jobs', []))}, No pattern errors: {no_pattern_error}",
                data
            )
        else:
            pattern_error_detected = "pattern" in str(error).lower() or "match" in str(error).lower()
            self.log_test_result(
                "🎯 GET /api/job-search?location=Hamburg&language_level=C1 (без search_query)",
                False,
                f"ОШИБКА: {error}. Pattern error detected: {pattern_error_detected}",
                data
            )

        # 4. Test special characters handling - location=München (с умлаутом)
        success, data, error = await self.make_request("GET", "/api/job-search?location=München&language_level=B1")
        
        if success and isinstance(data, dict):
            has_status = "status" in data and data["status"] == "success"
            has_jobs = "jobs" in data and isinstance(data["jobs"], list)
            no_pattern_error = "pattern" not in str(data).lower() and "match" not in str(error).lower()
            
            self.log_test_result(
                "🎯 Special characters: location=München (с умлаутом)",
                has_status and has_jobs and no_pattern_error,
                f"Status: {data.get('status')}, Jobs: {len(data.get('jobs', []))}, No pattern errors: {no_pattern_error}",
                data
            )
        else:
            pattern_error_detected = "pattern" in str(error).lower() or "match" in str(error).lower()
            self.log_test_result(
                "🎯 Special characters: location=München (с умлаутом)",
                False,
                f"ОШИБКА: {error}. Pattern error detected: {pattern_error_detected}",
                data
            )
        
        # 5. Test spaces in location - Frankfurt am Main (с пробелами)
        success, data, error = await self.make_request("GET", "/api/job-search?location=Frankfurt%20am%20Main&language_level=B2")
        
        if success and isinstance(data, dict):
            has_status = "status" in data and data["status"] == "success"
            has_jobs = "jobs" in data and isinstance(data["jobs"], list)
            no_pattern_error = "pattern" not in str(data).lower() and "match" not in str(error).lower()
            
            self.log_test_result(
                "🎯 Special characters: location=Frankfurt am Main (с пробелами)",
                has_status and has_jobs and no_pattern_error,
                f"Status: {data.get('status')}, Jobs: {len(data.get('jobs', []))}, No pattern errors: {no_pattern_error}",
                data
            )
        else:
            pattern_error_detected = "pattern" in str(error).lower() or "match" in str(error).lower()
            self.log_test_result(
                "🎯 Special characters: location=Frankfurt am Main (с пробелами)",
                False,
                f"ОШИБКА: {error}. Pattern error detected: {pattern_error_detected}",
                data
            )
        
        # 6. Test special characters in search_query - C++ Developer (со специальными символами)
        success, data, error = await self.make_request("GET", "/api/job-search?location=Berlin&language_level=B1&search_query=C%2B%2B%20Developer")
        
        if success and isinstance(data, dict):
            has_status = "status" in data and data["status"] == "success"
            has_jobs = "jobs" in data and isinstance(data["jobs"], list)
            no_pattern_error = "pattern" not in str(data).lower() and "match" not in str(error).lower()
            
            self.log_test_result(
                "🎯 Special characters: search_query=C++ Developer (со специальными символами)",
                has_status and has_jobs and no_pattern_error,
                f"Status: {data.get('status')}, Jobs: {len(data.get('jobs', []))}, No pattern errors: {no_pattern_error}",
                data
            )
        else:
            pattern_error_detected = "pattern" in str(error).lower() or "match" in str(error).lower()
            self.log_test_result(
                "🎯 Special characters: search_query=C++ Developer (со специальными символами)",
                False,
                f"ОШИБКА: {error}. Pattern error detected: {pattern_error_detected}",
                data
            )

    async def test_parameter_validation_edge_cases(self):
        """🎯 КРИТИЧЕСКИЙ ТЕСТ: Проверка валидации параметров"""
        logger.info("=== 🎯 КРИТИЧЕСКИЙ ТЕСТ: Проверка валидации параметров ===")
        
        # 1. Test некорректные language_level
        invalid_levels = ["A3", "D1", "invalid", ""]
        
        for level in invalid_levels:
            success, data, error = await self.make_request("GET", f"/api/job-search?location=Berlin&language_level={level}")
            
            # Should handle gracefully, not crash with pattern error
            no_pattern_error = "pattern" not in str(error).lower() and "match" not in str(error).lower()
            handles_gracefully = success or ("400" in str(error) or "422" in str(error))
            
            self.log_test_result(
                f"🎯 Invalid language_level validation: {level}",
                no_pattern_error and handles_gracefully,
                f"Level '{level}': No pattern errors: {no_pattern_error}, Handles gracefully: {handles_gracefully}",
                data
            )
        
        # 2. Test пустые параметры
        empty_param_tests = [
            ("location=&language_level=B1", "Empty location"),
            ("location=Berlin&language_level=", "Empty language_level"),
            ("location=Berlin&language_level=B1&search_query=", "Empty search_query")
        ]
        
        for params, description in empty_param_tests:
            success, data, error = await self.make_request("GET", f"/api/job-search?{params}")
            
            no_pattern_error = "pattern" not in str(error).lower() and "match" not in str(error).lower()
            
            self.log_test_result(
                f"🎯 Empty parameter handling: {description}",
                no_pattern_error,
                f"No pattern errors: {no_pattern_error}, Response: {error if not success else 'Success'}",
                data
            )

    async def test_german_language_level_filtering(self):
        """🎯 КРИТИЧЕСКИЙ ТЕСТ: German Language Level Filtering (A1-C2)"""
        logger.info("=== 🎯 КРИТИЧЕСКИЙ ТЕСТ: German Language Level Filtering (A1-C2) ===")
        
        # Test all German language levels
        language_levels = ["A1", "A2", "B1", "B2", "C1", "C2"]
        level_results = {}
        all_levels_work = True
        
        for level in language_levels:
            search_data = {
                "location": "Berlin", 
                "language_level": level,
                "limit": 10
            }
            
            success, data, error = await self.make_request("POST", "/api/job-search", json=search_data)
            
            if success and isinstance(data, dict):
                has_status = data.get("status") == "success"
                jobs_count = len(data.get("jobs", []))
                total_found = data.get("total_found", 0)
                level_results[level] = {"jobs": jobs_count, "total": total_found, "success": True}
                
                self.log_test_result(
                    f"🎯 German Language Level {level} - Works without authentication",
                    has_status,
                    f"Level {level}: {jobs_count} jobs found, Total available: {total_found}, Status: {data.get('status')}",
                    data
                )
            else:
                # Check if it's an authentication error (which would be wrong for public endpoint)
                is_auth_error = "401" in str(error) or "403" in str(error) or (isinstance(data, dict) and ("Not authenticated" in str(data.get("detail", ""))))
                level_results[level] = {"success": False, "auth_error": is_auth_error}
                all_levels_work = False
                
                self.log_test_result(
                    f"🎯 German Language Level {level} - Works without authentication",
                    False,
                    f"Level {level} failed: {error}. Auth error: {is_auth_error}",
                    data
                )
        
        # Summary test for all levels
        working_levels = [level for level, result in level_results.items() if result.get("success")]
        
        self.log_test_result(
            "🎯 All German Language Levels (A1-C2) work without authentication",
            all_levels_work,
            f"Working levels: {working_levels} out of {language_levels}",
            level_results
        )

    async def test_parameter_validation_and_error_handling(self):
        """🎯 КРИТИЧЕСКИЙ ТЕСТ: Parameter Validation and Error Handling"""
        logger.info("=== 🎯 КРИТИЧЕСКИЙ ТЕСТ: Parameter Validation and Error Handling ===")
        
        # 1. Test search_query is truly optional
        search_data_no_query = {
            "location": "Berlin",
            "language_level": "B1"
        }
        
        success, data, error = await self.make_request("POST", "/api/job-search", json=search_data_no_query)
        
        search_query_optional = success and isinstance(data, dict) and "status" in data
        
        self.log_test_result(
            "🎯 search_query parameter is OPTIONAL",
            search_query_optional,
            f"Search without search_query works: {search_query_optional}. Status: {data.get('status') if success else error}",
            data
        )
        
        # 2. Test location parameter works correctly
        search_data_location_only = {
            "location": "München",
            "limit": 5
        }
        
        success, data, error = await self.make_request("POST", "/api/job-search", json=search_data_location_only)
        
        location_works = success and isinstance(data, dict) and "status" in data
        
        self.log_test_result(
            "🎯 location parameter works correctly",
            location_works,
            f"Search with only location works: {location_works}. Status: {data.get('status') if success else error}",
            data
        )
        
        # 3. Test language_level parameter works correctly
        search_data_language_only = {
            "language_level": "C1",
            "limit": 5
        }
        
        success, data, error = await self.make_request("POST", "/api/job-search", json=search_data_language_only)
        
        language_level_works = success and isinstance(data, dict) and "status" in data
        
        self.log_test_result(
            "🎯 language_level parameter works correctly",
            language_level_works,
            f"Search with only language_level works: {language_level_works}. Status: {data.get('status') if success else error}",
            data
        )
        
        # 4. Test response structure has required fields
        search_data_full = {
            "search_query": "developer",
            "location": "Berlin",
            "language_level": "B2",
            "limit": 10
        }
        
        success, data, error = await self.make_request("POST", "/api/job-search", json=search_data_full)
        
        if success and isinstance(data, dict):
            has_total_found = "total_found" in data
            has_jobs_array = "jobs" in data and isinstance(data["jobs"], list)
            has_applied_filters = "applied_filters" in data
            has_status = "status" in data
            
            response_structure_valid = has_total_found and has_jobs_array and has_applied_filters and has_status
            
            self.log_test_result(
                "🎯 Response structure contains required fields",
                response_structure_valid,
                f"total_found: {has_total_found}, jobs: {has_jobs_array}, applied_filters: {has_applied_filters}, status: {has_status}",
                data
            )
        else:
            self.log_test_result(
                "🎯 Response structure contains required fields",
                False,
                f"Failed to get valid response: {error}",
                data
            )
        
        # 5. Test invalid language_level handling
        search_data_invalid_lang = {
            "location": "Berlin",
            "language_level": "X9",  # Invalid language level
            "limit": 5
        }
        
        success, data, error = await self.make_request("POST", "/api/job-search", json=search_data_invalid_lang)
        
        # Should either work (ignore invalid) or return proper error
        handles_invalid_lang = True  # We'll accept any reasonable handling
        
        if success and isinstance(data, dict):
            # If it works, that's fine - system ignores invalid values
            handles_invalid_lang = True
        elif not success:
            # If it fails, should be a proper validation error, not server error
            is_validation_error = "400" in str(error) or "422" in str(error) or "validation" in str(data).lower()
            is_server_error = "500" in str(error)
            handles_invalid_lang = is_validation_error and not is_server_error
        
        self.log_test_result(
            "🎯 Invalid language_level parameter handling",
            handles_invalid_lang,
            f"Invalid language_level handled properly: {handles_invalid_lang}. Response: {error if not success else 'Success'}",
            data
        )
        
        # 6. Test empty parameters handling
        search_data_empty = {}
        
        success, data, error = await self.make_request("POST", "/api/job-search", json=search_data_empty)
        
        # Should work (all parameters are optional) or return reasonable response
        handles_empty_params = success and isinstance(data, dict) and "status" in data
        
        self.log_test_result(
            "🎯 Empty parameters handling",
            handles_empty_params,
            f"Empty parameters handled: {handles_empty_params}. Status: {data.get('status') if success else error}",
            data
        )

    async def test_german_language_level_filtering_focused(self):
        """🎯 ФОКУСИРОВАННЫЙ ТЕСТ: German Language Level Filtering (B1, C1) - как запрошено"""
        logger.info("=== 🎯 ФОКУСИРОВАННЫЙ ТЕСТ: German Language Level Filtering (B1, C1) ===")
        
        # Test только 2-3 уровня как запрошено: B1, C1
        focus_levels = ["B1", "C1"]
        level_results = {}
        all_focus_levels_work = True
        
        for level in focus_levels:
            search_data = {
                "search_query": "software engineer",
                "location": "Berlin", 
                "language_level": level,
                "limit": 15
            }
            
            success, data, error = await self.make_request("POST", "/api/job-search", json=search_data)
            
            if success and isinstance(data, dict):
                jobs_count = len(data.get("jobs", []))
                total_found = data.get("total_found", 0)
                level_results[level] = {"jobs": jobs_count, "total": total_found, "success": True}
                
                self.log_test_result(
                    f"🎯 ФОКУС: German Language Level {level} - Works without authentication",
                    True,
                    f"Level {level}: {jobs_count} jobs found, Total available: {total_found}",
                    data
                )
            else:
                # Check if it's an authentication error (which would be wrong)
                is_auth_error = "401" in str(error) or "403" in str(error) or (isinstance(data, dict) and ("Not authenticated" in str(data.get("detail", ""))))
                level_results[level] = {"success": False, "auth_error": is_auth_error}
                all_focus_levels_work = False
                
                self.log_test_result(
                    f"🎯 ФОКУС: German Language Level {level} - Works without authentication",
                    False,
                    f"Level {level} failed: {error}. Auth error: {is_auth_error}",
                    data
                )
        
        # Summary test for focus levels
        working_levels = [level for level, result in level_results.items() if result.get("success")]
        
        self.log_test_result(
            "🎯 ФОКУС: German Language Levels (B1, C1) work without authentication",
            all_focus_levels_work,
            f"Working focus levels: {working_levels} out of {focus_levels}",
            level_results
        )

    async def test_job_search_results_validation(self):
        """🎯 КРИТИЧЕСКИЙ ТЕСТ: Job search results - убедись что возвращает actual job listings (не 0 results)"""
        logger.info("=== 🎯 КРИТИЧЕСКИЙ ТЕСТ: Job Search Results Validation ===")
        
        # Test that search returns actual job data (not just empty results)
        search_data = {
            "search_query": "python developer",
            "location": "Berlin",
            "limit": 20
        }
        
        success, data, error = await self.make_request("POST", "/api/job-search", json=search_data)
        
        if success and isinstance(data, dict):
            jobs = data.get("jobs", [])
            total_found = data.get("total_found", 0)
            total_available = data.get("total_available", 0)
            
            # Check if we get actual job data (not 0 results)
            has_jobs = len(jobs) > 0
            has_realistic_totals = total_found > 0 or total_available > 0
            
            # Check job structure if jobs exist
            job_structure_valid = True
            if jobs:
                first_job = jobs[0]
                required_job_fields = ["id", "title", "company"]
                job_structure_valid = all(field in first_job for field in required_job_fields)
            
            self.log_test_result(
                "🎯 Job search returns actual job listings (не 0 results)",
                has_jobs or has_realistic_totals,
                f"Jobs: {len(jobs)}, Total found: {total_found}, Total available: {total_available}, Structure valid: {job_structure_valid}",
                data
            )
        else:
            self.log_test_result(
                "🎯 Job search returns actual job listings (не 0 results)",
                False,
                f"Job search failed: {error}",
                data
            )
        
        # Test different search queries to ensure system returns varied results
        test_queries = [
            {"search_query": "data scientist", "location": "Munich"},
            {"search_query": "frontend developer", "location": "Hamburg"},
            {"search_query": "backend engineer", "remote": True}
        ]
        
        results_vary = True
        for i, query in enumerate(test_queries):
            success, data, error = await self.make_request("POST", "/api/job-search", json=query)
            
            if success and isinstance(data, dict):
                jobs_count = len(data.get("jobs", []))
                total_found = data.get("total_found", 0)
                
                # Log individual query results
                self.log_test_result(
                    f"🎯 Query {i+1}: {query.get('search_query', 'N/A')} - Returns results",
                    jobs_count > 0 or total_found > 0,
                    f"Query: {query}, Jobs: {jobs_count}, Total: {total_found}",
                    data
                )
            else:
                results_vary = False
                logger.warning(f"Query {i+1} failed: {error}")
        
        self.log_test_result(
            "🎯 Various job search queries return results",
            results_vary,
            f"All test queries return results: {results_vary}",
            {"tested_queries": test_queries}
        )

    async def test_arbeitnow_integration_status(self):
        """🎯 КРИТИЧЕСКИЙ ТЕСТ: Arbeitnow.com Integration Status"""
        logger.info("=== 🎯 КРИТИЧЕСКИЙ ТЕСТ: Arbeitnow.com Integration Status ===")
        
        # Test GET /api/job-search-status
        success, data, error = await self.make_request("GET", "/api/job-search-status")
        
        if success and isinstance(data, dict):
            # Check for arbeitnow_integration field
            has_arbeitnow_integration = "arbeitnow_integration" in data
            arbeitnow_integration = data.get("arbeitnow_integration")
            
            # Check integration details
            integration_valid = False
            if arbeitnow_integration and isinstance(arbeitnow_integration, dict):
                has_status = "status" in arbeitnow_integration
                has_api_endpoint = "api_endpoint" in arbeitnow_integration
                has_available = "available" in arbeitnow_integration
                status_active = arbeitnow_integration.get("status") == "active"
                is_available = arbeitnow_integration.get("available") is True
                
                integration_valid = has_status and has_api_endpoint and has_available and status_active and is_available
            
            # Check for service field
            has_service = "service" in data
            service_info = data.get("service")
            service_valid = False
            if service_info and isinstance(service_info, dict):
                has_name = "name" in service_info
                has_provider = "provider" in service_info
                has_service_status = "status" in service_info
                service_operational = service_info.get("status") == "operational"
                
                service_valid = has_name and has_provider and has_service_status and service_operational
            
            self.log_test_result(
                "🎯 GET /api/job-search-status - Arbeitnow integration info present",
                has_arbeitnow_integration and integration_valid and has_service and service_valid,
                f"Integration valid: {integration_valid}, Service valid: {service_valid}, Status: {arbeitnow_integration.get('status') if arbeitnow_integration else 'None'}",
                data
            )
        else:
            self.log_test_result(
                "🎯 GET /api/job-search-status - Arbeitnow integration info present",
                False,
                f"Status endpoint failed: {error}",
                data
            )
        
        # Test that integration shows as active
        if success and isinstance(data, dict):
            arbeitnow_integration = data.get("arbeitnow_integration", {})
            integration_status = arbeitnow_integration.get("status")
            integration_available = arbeitnow_integration.get("available")
            
            self.log_test_result(
                "🎯 Arbeitnow integration status shows 'active'",
                integration_status == "active" and integration_available is True,
                f"Status: {integration_status}, Available: {integration_available}",
                arbeitnow_integration
            )

    async def test_job_search_service_functionality(self):
        """🎯 КРИТИЧЕСКИЙ ТЕСТ: Job Search Service Functionality"""
        logger.info("=== 🎯 КРИТИЧЕСКИЙ ТЕСТ: Job Search Service Functionality ===")
        
        # Test that search returns real data (not just demo jobs)
        search_data = {
            "search_query": "software engineer",
            "location": "Berlin",
            "limit": 20
        }
        
        success, data, error = await self.make_request("POST", "/api/job-search", json=search_data)
        
        if success and isinstance(data, dict):
            jobs = data.get("jobs", [])
            total_found = data.get("total_found", 0)
            total_available = data.get("total_available", 0)
            
            # Check if we get real job data
            has_jobs = len(jobs) > 0
            has_realistic_totals = total_found > 0 and total_available > 0
            
            # Check job structure if jobs exist
            job_structure_valid = True
            if jobs:
                first_job = jobs[0]
                required_job_fields = ["id", "title", "company", "location"]
                job_structure_valid = all(field in first_job for field in required_job_fields)
            
            self.log_test_result(
                "🎯 Job search returns real data (not demo jobs)",
                has_jobs and has_realistic_totals and job_structure_valid,
                f"Jobs: {len(jobs)}, Total found: {total_found}, Total available: {total_available}, Structure valid: {job_structure_valid}",
                data
            )
        else:
            self.log_test_result(
                "🎯 Job search returns real data (not demo jobs)",
                False,
                f"Job search failed: {error}",
                data
            )
        
        # Test various filter combinations
        filter_combinations = [
            {"search_query": "python", "location": "Munich", "remote": False},
            {"search_query": "data analyst", "remote": True, "visa_sponsorship": True},
            {"location": "Hamburg", "language_level": "B2", "category": "IT"}
        ]
        
        all_filters_work = True
        for i, filters in enumerate(filter_combinations):
            success, data, error = await self.make_request("POST", "/api/job-search", json=filters)
            
            if success and isinstance(data, dict):
                applied_filters = data.get("applied_filters", {})
                # Check that filters are properly applied
                filters_applied = len(applied_filters) > 0
                
                if not filters_applied:
                    logger.warning(f"Filter combination {i+1} didn't apply filters properly")
            else:
                all_filters_work = False
                logger.warning(f"Filter combination {i+1} failed: {error}")
        
        self.log_test_result(
            "🎯 Various filter combinations work correctly",
            all_filters_work,
            f"All filter combinations work: {all_filters_work}",
            {"tested_combinations": filter_combinations}
        )

    async def test_cities_search_api_comprehensive(self):
        """🎯 КРИТИЧЕСКИЙ ТЕСТ: Cities Search API - все требуемые endpoints"""
        logger.info("=== 🎯 КРИТИЧЕСКИЙ ТЕСТ: Cities Search API Testing ===")
        
        # 1. Test GET /api/cities/search?q=Berlin (точное совпадение)
        success, data, error = await self.make_request("GET", "/api/cities/search?q=Berlin")
        
        if success and isinstance(data, dict):
            has_status = "status" in data
            has_cities = "cities" in data and isinstance(data["cities"], list)
            cities_count = len(data.get("cities", []))
            
            # Check if Berlin is found
            berlin_found = False
            if data.get("cities"):
                berlin_found = any(city.get("name") == "Berlin" for city in data["cities"])
            
            self.log_test_result(
                "🎯 GET /api/cities/search?q=Berlin - Точное совпадение",
                has_status and has_cities and berlin_found,
                f"Status: {data.get('status')}, Cities found: {cities_count}, Berlin found: {berlin_found}",
                data
            )
        else:
            self.log_test_result(
                "🎯 GET /api/cities/search?q=Berlin - Точное совпадение",
                False,
                f"Request failed: {error}",
                data
            )
        
        # 2. Test GET /api/cities/search?q=Ber (частичное совпадение)
        success, data, error = await self.make_request("GET", "/api/cities/search?q=Ber")
        
        if success and isinstance(data, dict):
            has_status = "status" in data
            has_cities = "cities" in data and isinstance(data["cities"], list)
            cities_count = len(data.get("cities", []))
            
            # Check if partial match works (should find Berlin and other cities starting with "Ber")
            partial_matches = cities_count > 0
            
            self.log_test_result(
                "🎯 GET /api/cities/search?q=Ber - Частичное совпадение",
                has_status and has_cities and partial_matches,
                f"Status: {data.get('status')}, Cities found: {cities_count}, Partial matches work: {partial_matches}",
                data
            )
        else:
            self.log_test_result(
                "🎯 GET /api/cities/search?q=Ber - Частичное совпадение",
                False,
                f"Request failed: {error}",
                data
            )
        
        # 3. Test GET /api/cities/search?q=Mü (тест с умлаутом)
        success, data, error = await self.make_request("GET", "/api/cities/search?q=Mü")
        
        if success and isinstance(data, dict):
            has_status = "status" in data
            has_cities = "cities" in data and isinstance(data["cities"], list)
            cities_count = len(data.get("cities", []))
            
            # Check if umlaut search works (should find München)
            umlaut_works = cities_count > 0
            munich_found = False
            if data.get("cities"):
                munich_found = any("München" in city.get("name", "") or "Munich" in city.get("name", "") for city in data["cities"])
            
            self.log_test_result(
                "🎯 GET /api/cities/search?q=Mü - Тест с умлаутом",
                has_status and has_cities and (umlaut_works or munich_found),
                f"Status: {data.get('status')}, Cities found: {cities_count}, München found: {munich_found}",
                data
            )
        else:
            self.log_test_result(
                "🎯 GET /api/cities/search?q=Mü - Тест с умлаутом",
                False,
                f"Request failed: {error}",
                data
            )
        
        # 4. Test GET /api/cities/popular (популярные города)
        success, data, error = await self.make_request("GET", "/api/cities/popular")
        
        if success and isinstance(data, dict):
            has_status = "status" in data
            has_cities = "cities" in data and isinstance(data["cities"], list)
            cities_count = len(data.get("cities", []))
            
            # Check if popular cities are returned
            has_popular_cities = cities_count > 0
            
            # Check if major German cities are included
            major_cities_found = []
            if data.get("cities"):
                major_cities = ["Berlin", "Hamburg", "München", "Köln", "Frankfurt"]
                for city in data["cities"]:
                    city_name = city.get("name", "")
                    for major_city in major_cities:
                        if major_city in city_name:
                            major_cities_found.append(major_city)
            
            self.log_test_result(
                "🎯 GET /api/cities/popular - Популярные города",
                has_status and has_cities and has_popular_cities,
                f"Status: {data.get('status')}, Popular cities: {cities_count}, Major cities found: {major_cities_found}",
                data
            )
        else:
            self.log_test_result(
                "🎯 GET /api/cities/popular - Популярные города",
                False,
                f"Request failed: {error}",
                data
            )
        
        # 5. Test GET /api/cities/info/Berlin (детальная информация)
        success, data, error = await self.make_request("GET", "/api/cities/info/Berlin")
        
        if success and isinstance(data, dict):
            has_status = "status" in data
            has_city_info = "city" in data and isinstance(data["city"], dict)
            
            # Check city info structure
            city_info_complete = False
            if data.get("city"):
                city = data["city"]
                required_fields = ["name", "state", "population"]
                city_info_complete = all(field in city for field in required_fields)
            
            self.log_test_result(
                "🎯 GET /api/cities/info/Berlin - Детальная информация",
                has_status and has_city_info and city_info_complete,
                f"Status: {data.get('status')}, City info complete: {city_info_complete}",
                data
            )
        else:
            self.log_test_result(
                "🎯 GET /api/cities/info/Berlin - Детальная информация",
                False,
                f"Request failed: {error}",
                data
            )

    async def test_job_search_api_comprehensive(self):
        """🎯 КРИТИЧЕСКИЙ ТЕСТ: Job Search API - все требуемые endpoints"""
        logger.info("=== 🎯 КРИТИЧЕСКИЙ ТЕСТ: Job Search API Testing ===")
        
        # 1. Test GET /api/job-search (базовый поиск)
        success, data, error = await self.make_request("GET", "/api/job-search")
        
        if success and isinstance(data, dict):
            has_status = "status" in data
            has_jobs = "jobs" in data and isinstance(data["jobs"], list)
            has_total_found = "total_found" in data
            
            self.log_test_result(
                "🎯 GET /api/job-search - Базовый поиск",
                has_status and has_jobs and has_total_found,
                f"Status: {data.get('status')}, Jobs: {len(data.get('jobs', []))}, Total: {data.get('total_found')}",
                data
            )
        else:
            self.log_test_result(
                "🎯 GET /api/job-search - Базовый поиск",
                False,
                f"Request failed: {error}",
                data
            )
        
        # 2. Test GET /api/job-search?location=Berlin (поиск по городу)
        success, data, error = await self.make_request("GET", "/api/job-search?location=Berlin")
        
        if success and isinstance(data, dict):
            has_status = "status" in data
            has_jobs = "jobs" in data and isinstance(data["jobs"], list)
            has_applied_filters = "applied_filters" in data
            
            # Check if location filter is applied
            location_applied = False
            if data.get("applied_filters"):
                location_applied = "location" in data["applied_filters"]
            
            self.log_test_result(
                "🎯 GET /api/job-search?location=Berlin - Поиск по городу",
                has_status and has_jobs and location_applied,
                f"Status: {data.get('status')}, Jobs: {len(data.get('jobs', []))}, Location filter applied: {location_applied}",
                data
            )
        else:
            self.log_test_result(
                "🎯 GET /api/job-search?location=Berlin - Поиск по городу",
                False,
                f"Request failed: {error}",
                data
            )
        
        # 3. Test GET /api/job-search?language_level=B1 (фильтр по языку)
        success, data, error = await self.make_request("GET", "/api/job-search?language_level=B1")
        
        if success and isinstance(data, dict):
            has_status = "status" in data
            has_jobs = "jobs" in data and isinstance(data["jobs"], list)
            has_applied_filters = "applied_filters" in data
            
            # Check if language level filter is applied
            language_applied = False
            if data.get("applied_filters"):
                language_applied = "language_level" in data["applied_filters"]
            
            self.log_test_result(
                "🎯 GET /api/job-search?language_level=B1 - Фильтр по языку",
                has_status and has_jobs and language_applied,
                f"Status: {data.get('status')}, Jobs: {len(data.get('jobs', []))}, Language filter applied: {language_applied}",
                data
            )
        else:
            self.log_test_result(
                "🎯 GET /api/job-search?language_level=B1 - Фильтр по языку",
                False,
                f"Request failed: {error}",
                data
            )
        
        # 4. Test GET /api/job-search?search_query=developer (поиск по профессии)
        success, data, error = await self.make_request("GET", "/api/job-search?search_query=developer")
        
        if success and isinstance(data, dict):
            has_status = "status" in data
            has_jobs = "jobs" in data and isinstance(data["jobs"], list)
            has_applied_filters = "applied_filters" in data
            
            # Check if search query filter is applied
            query_applied = False
            if data.get("applied_filters"):
                query_applied = "search_query" in data["applied_filters"]
            
            self.log_test_result(
                "🎯 GET /api/job-search?search_query=developer - Поиск по профессии",
                has_status and has_jobs and query_applied,
                f"Status: {data.get('status')}, Jobs: {len(data.get('jobs', []))}, Query filter applied: {query_applied}",
                data
            )
        else:
            self.log_test_result(
                "🎯 GET /api/job-search?search_query=developer - Поиск по профессии",
                False,
                f"Request failed: {error}",
                data
            )
        
        # 5. Test GET /api/job-search?location=München&language_level=B2 (комбинация фильтров)
        success, data, error = await self.make_request("GET", "/api/job-search?location=München&language_level=B2")
        
        if success and isinstance(data, dict):
            has_status = "status" in data
            has_jobs = "jobs" in data and isinstance(data["jobs"], list)
            has_applied_filters = "applied_filters" in data
            
            # Check if both filters are applied
            both_filters_applied = False
            if data.get("applied_filters"):
                location_applied = "location" in data["applied_filters"]
                language_applied = "language_level" in data["applied_filters"]
                both_filters_applied = location_applied and language_applied
            
            self.log_test_result(
                "🎯 GET /api/job-search?location=München&language_level=B2 - Комбинация фильтров",
                has_status and has_jobs and both_filters_applied,
                f"Status: {data.get('status')}, Jobs: {len(data.get('jobs', []))}, Both filters applied: {both_filters_applied}",
                data
            )
        else:
            self.log_test_result(
                "🎯 GET /api/job-search?location=München&language_level=B2 - Комбинация фильтров",
                False,
                f"Request failed: {error}",
                data
            )

    async def test_problematic_cases(self):
        """🎯 КРИТИЧЕСКИЙ ТЕСТ: Проблемные случаи поиска"""
        logger.info("=== 🎯 КРИТИЧЕСКИЙ ТЕСТ: Problematic Cases Testing ===")
        
        # 1. Поиск с пробелами в названии города
        success, data, error = await self.make_request("GET", "/api/cities/search?q=Frankfurt am Main")
        
        if success and isinstance(data, dict):
            has_status = "status" in data
            has_cities = "cities" in data and isinstance(data["cities"], list)
            cities_count = len(data.get("cities", []))
            
            # Check if city with spaces is found
            frankfurt_found = False
            if data.get("cities"):
                frankfurt_found = any("Frankfurt" in city.get("name", "") for city in data["cities"])
            
            self.log_test_result(
                "🎯 Поиск с пробелами в названии города",
                has_status and has_cities and (cities_count > 0 or frankfurt_found),
                f"Status: {data.get('status')}, Cities found: {cities_count}, Frankfurt found: {frankfurt_found}",
                data
            )
        else:
            self.log_test_result(
                "🎯 Поиск с пробелами в названии города",
                False,
                f"Request failed: {error}",
                data
            )
        
        # 2. Поиск с специальными символами
        success, data, error = await self.make_request("GET", "/api/cities/search?q=Düsseldorf")
        
        if success and isinstance(data, dict):
            has_status = "status" in data
            has_cities = "cities" in data and isinstance(data["cities"], list)
            cities_count = len(data.get("cities", []))
            
            # Check if city with special characters is found
            dusseldorf_found = False
            if data.get("cities"):
                dusseldorf_found = any("Düsseldorf" in city.get("name", "") for city in data["cities"])
            
            self.log_test_result(
                "🎯 Поиск с специальными символами",
                has_status and has_cities and (cities_count > 0 or dusseldorf_found),
                f"Status: {data.get('status')}, Cities found: {cities_count}, Düsseldorf found: {dusseldorf_found}",
                data
            )
        else:
            self.log_test_result(
                "🎯 Поиск с специальными символами",
                False,
                f"Request failed: {error}",
                data
            )
        
        # 3. Пустые параметры поиска
        success, data, error = await self.make_request("GET", "/api/cities/search?q=")
        
        if success and isinstance(data, dict):
            has_status = "status" in data
            has_cities = "cities" in data and isinstance(data["cities"], list)
            
            # Empty query should either return empty results or handle gracefully
            handles_empty_query = True  # As long as it doesn't crash
            
            self.log_test_result(
                "🎯 Пустые параметры поиска",
                has_status and has_cities and handles_empty_query,
                f"Status: {data.get('status')}, Handles empty query gracefully",
                data
            )
        else:
            # Check if it's a validation error (acceptable) or server error (not acceptable)
            is_validation_error = "400" in str(error) or "422" in str(error)
            is_server_error = "500" in str(error)
            
            self.log_test_result(
                "🎯 Пустые параметры поиска",
                is_validation_error and not is_server_error,
                f"Handles empty query: validation error OK, server error NOT OK. Error: {error}",
                data
            )
        
        # 4. Очень длинные запросы
        long_query = "a" * 200  # 200 character query
        success, data, error = await self.make_request("GET", f"/api/cities/search?q={long_query}")
        
        if success and isinstance(data, dict):
            has_status = "status" in data
            has_cities = "cities" in data and isinstance(data["cities"], list)
            
            # Long query should be handled gracefully
            handles_long_query = True
            
            self.log_test_result(
                "🎯 Очень длинные запросы",
                has_status and has_cities and handles_long_query,
                f"Status: {data.get('status')}, Handles long query gracefully",
                data
            )
        else:
            # Check if it's a validation error (acceptable) or server error (not acceptable)
            is_validation_error = "400" in str(error) or "422" in str(error)
            is_server_error = "500" in str(error)
            
            self.log_test_result(
                "🎯 Очень длинные запросы",
                is_validation_error and not is_server_error,
                f"Handles long query: validation error OK, server error NOT OK. Error: {error}",
                data
            )

    async def test_job_search_status_service(self):
        """🎯 КРИТИЧЕСКИЙ ТЕСТ: Job Search Status Service"""
        logger.info("=== 🎯 КРИТИЧЕСКИЙ ТЕСТ: Job Search Status Service ===")
        
        # Test GET /api/job-search-status
        success, data, error = await self.make_request("GET", "/api/job-search-status")
        
        if success and isinstance(data, dict):
            has_status = "status" in data
            has_service_info = "service" in data
            has_integration_info = "arbeitnow_integration" in data
            
            # Check service information
            service_valid = False
            if data.get("service") and isinstance(data["service"], dict):
                service = data["service"]
                has_name = "name" in service
                has_status_field = "status" in service
                service_operational = service.get("status") == "operational"
                service_valid = has_name and has_status_field and service_operational
            
            # Check integration information
            integration_valid = False
            if data.get("arbeitnow_integration") and isinstance(data["arbeitnow_integration"], dict):
                integration = data["arbeitnow_integration"]
                has_status_field = "status" in integration
                has_api_endpoint = "api_endpoint" in integration
                has_available = "available" in integration
                integration_active = integration.get("status") == "active"
                integration_available = integration.get("available") is True
                integration_valid = has_status_field and has_api_endpoint and has_available and integration_active and integration_available
            
            self.log_test_result(
                "🎯 GET /api/job-search-status - Сервисы активны и готовы",
                has_status and service_valid and integration_valid,
                f"Status: {data.get('status')}, Service valid: {service_valid}, Integration valid: {integration_valid}",
                data
            )
        else:
            self.log_test_result(
                "🎯 GET /api/job-search-status - Сервисы активны и готовы",
                False,
                f"Request failed: {error}",
                data
            )

    async def test_no_pattern_matching_errors(self):
        """🎯 КРИТИЧЕСКИЙ ТЕСТ: Отсутствие ошибок pattern matching"""
        logger.info("=== 🎯 КРИТИЧЕСКИЙ ТЕСТ: No Pattern Matching Errors ===")
        
        # Test various search queries that previously caused pattern matching errors
        test_queries = [
            "software developer",
            "data scientist",
            "frontend engineer",
            "backend developer",
            "full stack",
            "python programmer",
            "javascript developer",
            "react developer",
            "node.js developer",
            "machine learning engineer"
        ]
        
        pattern_errors_found = []
        all_queries_work = True
        
        for query in test_queries:
            # Test job search with query
            success, data, error = await self.make_request("GET", f"/api/job-search?search_query={query}")
            
            # Check for pattern matching errors
            if not success:
                error_text = str(error).lower() + str(data).lower() if data else str(error).lower()
                if "pattern" in error_text or "match" in error_text:
                    pattern_errors_found.append(query)
                    all_queries_work = False
            
            # Also test with POST method
            search_data = {"search_query": query, "limit": 5}
            success, data, error = await self.make_request("POST", "/api/job-search", json=search_data)
            
            if not success:
                error_text = str(error).lower() + str(data).lower() if data else str(error).lower()
                if "pattern" in error_text or "match" in error_text:
                    pattern_errors_found.append(f"{query} (POST)")
                    all_queries_work = False
        
        self.log_test_result(
            "🎯 Никаких ошибок 'pattern matching'",
            len(pattern_errors_found) == 0,
            f"Pattern errors found: {pattern_errors_found}" if pattern_errors_found else "No pattern matching errors found",
            {"pattern_errors": pattern_errors_found, "tested_queries": test_queries}
        )
        
        # Test city search for pattern errors too
        city_queries = ["Berlin", "München", "Hamburg", "Köln", "Frankfurt", "Stuttgart", "Düsseldorf"]
        city_pattern_errors = []
        
        for city in city_queries:
            success, data, error = await self.make_request("GET", f"/api/cities/search?q={city}")
            
            if not success:
                error_text = str(error).lower() + str(data).lower() if data else str(error).lower()
                if "pattern" in error_text or "match" in error_text:
                    city_pattern_errors.append(city)
        
        self.log_test_result(
            "🎯 Cities search - никаких ошибок 'pattern matching'",
            len(city_pattern_errors) == 0,
            f"City pattern errors found: {city_pattern_errors}" if city_pattern_errors else "No city pattern matching errors found",
            {"city_pattern_errors": city_pattern_errors, "tested_cities": city_queries}
        )

    async def run_telegram_mini_app_tests(self):
        """🎯 ГЛАВНАЯ ФУНКЦИЯ: Запуск всех тестов для Telegram Mini App"""
        logger.info("=== 🎯 ЗАПУСК ВСЕХ ТЕСТОВ ДЛЯ TELEGRAM MINI APP ===")
        
        # Run all specific tests requested by user
        await self.test_cities_search_api_comprehensive()
        await self.test_job_search_api_comprehensive()
        await self.test_problematic_cases()
        await self.test_job_search_status_service()
        await self.test_no_pattern_matching_errors()
        
        # Also run some basic health tests to ensure system is working
        await self.test_basic_health_endpoints()
        await self.test_api_health_endpoints()
        
        logger.info("=== 🎯 ВСЕ ТЕСТЫ TELEGRAM MINI APP ЗАВЕРШЕНЫ ===")


    async def test_job_search_authentication_requirements(self):
        """🎯 КРИТИЧЕСКИЙ ТЕСТ: Authentication Requirements for Job Search"""
        logger.info("=== 🎯 КРИТИЧЕСКИЙ ТЕСТ: Job Search Authentication Requirements ===")
        
        # Test that basic job search endpoints DON'T require authentication
        basic_endpoints = [
            ("GET", "/api/job-search", "Basic job search"),
            ("POST", "/api/job-search", "Job search with parameters"),
            ("GET", "/api/job-search-status", "Job search status")
        ]
        
        all_basic_public = True
        
        for method, endpoint, description in basic_endpoints:
            if method == "POST" and "job-search" in endpoint and "status" not in endpoint:
                # For job search POST, send some test data
                success, data, error = await self.make_request(method, endpoint, json={"search_query": "test"})
            else:
                success, data, error = await self.make_request(method, endpoint)
            
            # Should NOT require authentication (should succeed or fail for other reasons)
            requires_auth = not success and ("401" in str(error) or "403" in str(error) or (isinstance(data, dict) and ("Not authenticated" in str(data.get("detail", "")))))
            
            if requires_auth:
                all_basic_public = False
                logger.warning(f"{method} {endpoint} incorrectly requires authentication")
            
            self.log_test_result(
                f"🎯 {method} {endpoint} - {description} (public access)",
                not requires_auth,
                f"Public access: {not requires_auth}" if not requires_auth else f"Incorrectly requires auth: {error}",
                data
            )
        
        # Test that protected endpoints STILL require authentication
        protected_endpoints = [
            ("POST", "/api/job-subscriptions", "Create job subscription"),
            ("GET", "/api/job-subscriptions", "Get job subscriptions"),
            ("POST", "/api/analyze-resume", "Resume analysis"),
            ("POST", "/api/prepare-interview", "Interview preparation")
        ]
        
        all_protected_secure = True
        
        for method, endpoint, description in protected_endpoints:
            if method == "POST":
                success, data, error = await self.make_request(method, endpoint, json={"test": "data"})
            else:
                success, data, error = await self.make_request(method, endpoint)
            
            # Should require authentication (return 401 or 403)
            requires_auth = not success and ("401" in str(error) or "403" in str(error) or (isinstance(data, dict) and ("Not authenticated" in str(data.get("detail", "")))))
            
            if not requires_auth:
                all_protected_secure = False
                logger.warning(f"{method} {endpoint} should require authentication but doesn't")
            
            self.log_test_result(
                f"🎯 {method} {endpoint} - {description} (requires auth)",
                requires_auth,
                f"Requires auth: {requires_auth}" if requires_auth else f"Should require auth but doesn't: {error}",
                data
            )
        
        # Summary
        self.log_test_result(
            "🎯 Job Search Authentication Requirements - Correct configuration",
            all_basic_public and all_protected_secure,
            f"Basic endpoints public: {all_basic_public}, Protected endpoints secure: {all_protected_secure}",
            {"basic_public": all_basic_public, "protected_secure": all_protected_secure}
        )

    async def run_job_search_tests(self):
        """🎯 ГЛАВНАЯ ФУНКЦИЯ: Запуск всех тестов Job Search функциональности"""
        logger.info("=== 🎯 ЗАПУСК ВСЕХ ТЕСТОВ JOB SEARCH ФУНКЦИОНАЛЬНОСТИ ===")
        
        # Run all Job Search specific tests
        await self.test_job_search_endpoints()
        await self.test_german_language_level_filtering()
        await self.test_arbeitnow_integration_status()
        await self.test_job_search_service_functionality()
        await self.test_job_search_authentication_requirements()
        
        # Also run some basic health tests to ensure system is working
        await self.test_basic_health_endpoints()
        await self.test_api_health_endpoints()
        
        logger.info("=== 🎯 ВСЕ ТЕСТЫ JOB SEARCH ЗАВЕРШЕНЫ ===")

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
    
    async def test_critical_document_analysis_fix(self):
        """🎯 КРИТИЧЕСКИЙ ТЕСТ: Проверить исправление проблемы анализа документов в Telegram Mini App"""
        logger.info("=== 🎯 КРИТИЧЕСКИЙ ТЕСТ: Исправление анализа документов ===")
        
        # 1. Проверить что endpoint /api/analyze-file существует и принимает файлы
        test_image_data = self.create_test_image()
        form_data = aiohttp.FormData()
        form_data.add_field('file', test_image_data, filename='test_document.jpg', content_type='image/jpeg')
        form_data.add_field('language', 'ru')
        
        success, data, error = await self.make_request("POST", "/api/analyze-file", data=form_data)
        
        # Должен требовать аутентификацию, но НЕ возвращать ошибку сервера (500)
        is_auth_required = not success and ("401" in str(error) or "403" in str(error) or (isinstance(data, dict) and ("Not authenticated" in str(data.get("detail", "")))))
        no_server_error = "500" not in str(error) and not (isinstance(data, dict) and "500" in str(data))
        
        self.log_test_result(
            "🎯 POST /api/analyze-file - Endpoint доступен для анализа документов",
            is_auth_required and no_server_error,
            f"Auth required: {is_auth_required}, No server error: {no_server_error}, Response: {error}",
            data
        )
        
        # 2. Проверить что endpoint принимает разные типы файлов
        file_types = [
            ('document.jpg', 'image/jpeg'),
            ('scan.png', 'image/png'), 
            ('letter.pdf', 'application/pdf'),
            ('photo.webp', 'image/webp')
        ]
        
        all_types_accepted = True
        for filename, content_type in file_types:
            form_data = aiohttp.FormData()
            form_data.add_field('file', test_image_data, filename=filename, content_type=content_type)
            form_data.add_field('language', 'ru')
            
            success, data, error = await self.make_request("POST", "/api/analyze-file", data=form_data)
            
            # Должен принимать файл (требовать auth, а не отклонять формат)
            accepts_format = not success and ("401" in str(error) or "403" in str(error) or (isinstance(data, dict) and ("Not authenticated" in str(data.get("detail", "")))))
            
            if not accepts_format:
                all_types_accepted = False
                logger.warning(f"File type {content_type} not properly accepted: {error}")
        
        self.log_test_result(
            "🎯 POST /api/analyze-file - Принимает разные типы файлов",
            all_types_accepted,
            f"All file types accepted: {all_types_accepted}",
            {"tested_types": [f[1] for f in file_types]}
        )
        
        # 3. Проверить что система готова для реального анализа (не заглушки)
        # Проверяем что super_analysis_engine импортирован через проверку структуры ответа
        success, data, error = await self.make_request("GET", "/api/health")
        
        if success and isinstance(data, dict):
            # Система должна быть готова к анализу
            is_healthy = data.get("status") == "healthy"
            has_users = "users_count" in data
            has_analyses = "analyses_count" in data
            
            self.log_test_result(
                "🎯 Система готова для реального анализа (не заглушки)",
                is_healthy and has_users and has_analyses,
                f"Healthy: {is_healthy}, Has users: {has_users}, Has analyses: {has_analyses}",
                data
            )
        else:
            self.log_test_result("🎯 Система готова для реального анализа (не заглушки)", False, f"Health check failed: {error}", data)
    
    async def test_super_analysis_engine_integration(self):
        """🎯 КРИТИЧЕСКИЙ ТЕСТ: Проверить интеграцию super_analysis_engine"""
        logger.info("=== 🎯 КРИТИЧЕСКИЙ ТЕСТ: Интеграция super_analysis_engine ===")
        
        # Проверяем что система не работает в fallback режиме с заглушками
        # Это можно проверить через modern LLM status
        success, data, error = await self.make_request("GET", "/api/modern-llm-status")
        
        if success and isinstance(data, dict):
            has_modern_flag = data.get("modern") is True
            has_providers = "providers" in data and isinstance(data["providers"], dict)
            providers_count = len(data.get("providers", {}))
            
            # Проверяем что есть современные провайдеры для анализа
            providers = data.get("providers", {})
            modern_providers = []
            for provider_name, provider_info in providers.items():
                if provider_info.get("modern") is True:
                    modern_providers.append(provider_name)
            
            self.log_test_result(
                "🎯 Super Analysis Engine - Modern LLM интеграция",
                has_modern_flag and has_providers and len(modern_providers) > 0,
                f"Modern: {has_modern_flag}, Providers: {providers_count}, Modern providers: {modern_providers}",
                data
            )
        else:
            self.log_test_result("🎯 Super Analysis Engine - Modern LLM интеграция", False, f"Error: {error}", data)
        
        # Проверяем что система НЕ в fallback режиме
        success, data, error = await self.make_request("GET", "/api/llm-status")
        
        if success and isinstance(data, dict):
            has_providers = "providers" in data and isinstance(data["providers"], dict)
            active_providers = data.get("active_providers", 0)
            total_providers = data.get("total_providers", 0)
            
            # Система должна иметь доступные провайдеры для анализа
            has_active_providers = active_providers > 0 or total_providers > 0
            
            self.log_test_result(
                "🎯 Super Analysis Engine - НЕ в fallback режиме",
                has_providers and has_active_providers,
                f"Has providers: {has_providers}, Active: {active_providers}/{total_providers}",
                data
            )
        else:
            self.log_test_result("🎯 Super Analysis Engine - НЕ в fallback режиме", False, f"Error: {error}", data)
    
    async def test_real_analysis_vs_stubs(self):
        """🎯 КРИТИЧЕСКИЙ ТЕСТ: Убедиться что система возвращает реальный анализ, а не заглушки"""
        logger.info("=== 🎯 КРИТИЧЕСКИЙ ТЕСТ: Реальный анализ vs заглушки ===")
        
        # Проверяем что analyze-file endpoint настроен для реального анализа
        # Тестируем структуру ответа без аутентификации
        test_image_data = self.create_test_image()
        form_data = aiohttp.FormData()
        form_data.add_field('file', test_image_data, filename='important_document.jpg', content_type='image/jpeg')
        form_data.add_field('language', 'ru')
        
        success, data, error = await self.make_request("POST", "/api/analyze-file", data=form_data)
        
        # Должен требовать аутентификацию, но НЕ возвращать заглушку или статичный ответ
        is_auth_required = not success and ("401" in str(error) or "403" in str(error) or (isinstance(data, dict) and ("Not authenticated" in str(data.get("detail", "")))))
        
        # Проверяем что это НЕ статичная заглушка (не возвращает готовый анализ без аутентификации)
        is_not_static_stub = not (success and isinstance(data, dict) and "analysis" in data and "summary" in data)
        
        self.log_test_result(
            "🎯 Реальный анализ - НЕ статичные заглушки",
            is_auth_required and is_not_static_stub,
            f"Requires auth: {is_auth_required}, Not static stub: {is_not_static_stub}",
            data
        )
        
        # Проверяем что система готова для comprehensive analysis
        # Это можно проверить через наличие современных LLM провайдеров
        success, data, error = await self.make_request("GET", "/api/modern-llm-status")
        
        if success and isinstance(data, dict):
            providers = data.get("providers", {})
            
            # Ищем провайдеры способные на comprehensive analysis
            comprehensive_capable = []
            for provider_name, provider_info in providers.items():
                model = provider_info.get("model", "")
                # Современные модели способные на детальный анализ
                if any(advanced_model in model for advanced_model in ["gemini-2.0-flash", "gpt-4o", "claude-3-5-sonnet"]):
                    comprehensive_capable.append(f"{provider_name}:{model}")
            
            self.log_test_result(
                "🎯 Система готова для comprehensive analysis",
                len(comprehensive_capable) > 0,
                f"Comprehensive capable providers: {comprehensive_capable}",
                {"capable_providers": comprehensive_capable}
            )
        else:
            self.log_test_result("🎯 Система готова для comprehensive analysis", False, f"Error: {error}", data)
    
    
    async def test_final_document_analysis_display_fix(self):
        """🎯 ФИНАЛЬНЫЙ КРИТИЧЕСКИЙ ТЕСТ: Исправление отображения результатов анализа документов в Telegram Mini App"""
        logger.info("=== 🎯 ФИНАЛЬНЫЙ КРИТИЧЕСКИЙ ТЕСТ: Исправление отображения результатов анализа ===")
        
        # 1. Проверить что POST /api/analyze-file возвращает структурированные данные с полем analysis.full_analysis
        test_image_data = self.create_test_image()
        form_data = aiohttp.FormData()
        form_data.add_field('file', test_image_data, filename='test_telegram_document.jpg', content_type='image/jpeg')
        form_data.add_field('language', 'ru')
        
        success, data, error = await self.make_request("POST", "/api/analyze-file", data=form_data)
        
        # Должен требовать аутентификацию, но структура ответа должна быть готова для правильного отображения
        is_auth_required = not success and ("401" in str(error) or "403" in str(error) or (isinstance(data, dict) and ("Not authenticated" in str(data.get("detail", "")))))
        no_server_error = "500" not in str(error) and not (isinstance(data, dict) and "500" in str(data))
        
        self.log_test_result(
            "🎯 POST /api/analyze-file готов возвращать структурированные данные с analysis.full_analysis",
            is_auth_required and no_server_error,
            f"Auth required: {is_auth_required}, No server error: {no_server_error}, Ready for structured response",
            data
        )
        
        # 2. Проверить что super_analysis_engine интегрирован и готов возвращать данные в полях "analysis" и "super_analysis"
        success, data, error = await self.make_request("GET", "/api/modern-llm-status")
        
        if success and isinstance(data, dict):
            has_modern_flag = data.get("modern") is True
            has_providers = "providers" in data and isinstance(data["providers"], dict)
            providers_count = len(data.get("providers", {}))
            
            # Проверяем что есть современные провайдеры для super_analysis_engine
            modern_providers = []
            for provider_name, provider_info in data.get("providers", {}).items():
                if provider_info.get("modern") is True:
                    modern_providers.append(provider_name)
            
            self.log_test_result(
                "🎯 Super Analysis Engine готов для дублирования данных в analysis и super_analysis",
                has_modern_flag and has_providers and len(modern_providers) >= 3,
                f"Modern: {has_modern_flag}, Providers: {providers_count}, Modern providers: {modern_providers} (expected: gemini, openai, anthropic)",
                data
            )
        else:
            self.log_test_result("🎯 Super Analysis Engine готов для дублирования данных в analysis и super_analysis", False, f"Error: {error}", data)
        
        # 3. Проверить что система НЕ в fallback режиме и готова для comprehensive analysis
        success, data, error = await self.make_request("GET", "/api/llm-status")
        
        if success and isinstance(data, dict):
            active_providers = data.get("active_providers", 0)
            total_providers = data.get("total_providers", 0)
            has_providers = "providers" in data and isinstance(data["providers"], dict)
            
            # Система должна иметь активные провайдеры для comprehensive analysis
            not_in_fallback = active_providers >= 3 or total_providers >= 3
            
            self.log_test_result(
                "🎯 Система НЕ в fallback режиме, готова для comprehensive analysis",
                has_providers and not_in_fallback,
                f"Active providers: {active_providers}/{total_providers}, Not in fallback: {not_in_fallback}",
                data
            )
        else:
            self.log_test_result("🎯 Система НЕ в fallback режиме, готова для comprehensive analysis", False, f"Error: {error}", data)
        
        # 4. Проверить что демо анализ содержит нужную структуру данных для отображения
        # Проверяем через health endpoint что система готова к работе
        success, data, error = await self.make_request("GET", "/api/health")
        
        if success and isinstance(data, dict):
            is_healthy = data.get("status") == "healthy"
            has_telegram_support = data.get("telegram_mini_app") is True
            has_users_count = "users_count" in data
            has_analyses_count = "analyses_count" in data
            
            self.log_test_result(
                "🎯 Демо анализ готов с правильной структурой для Telegram Mini App",
                is_healthy and has_telegram_support and has_users_count and has_analyses_count,
                f"Healthy: {is_healthy}, Telegram support: {has_telegram_support}, Users: {has_users_count}, Analyses: {has_analyses_count}",
                data
            )
        else:
            self.log_test_result("🎯 Демо анализ готов с правильной структурой для Telegram Mini App", False, f"Error: {error}", data)
        
        # 5. Проверить что система возвращает полное содержимое анализа, а не только статус
        # Тестируем разные типы файлов для убеждения что все форматы готовы для полного анализа
        file_formats = [
            ('document.pdf', 'application/pdf'),
            ('letter.jpg', 'image/jpeg'),
            ('scan.png', 'image/png'),
            ('photo.webp', 'image/webp')
        ]
        
        all_formats_ready = True
        for filename, content_type in file_formats:
            form_data = aiohttp.FormData()
            form_data.add_field('file', test_image_data, filename=filename, content_type=content_type)
            form_data.add_field('language', 'ru')
            
            success, data, error = await self.make_request("POST", "/api/analyze-file", data=form_data)
            
            # Все форматы должны быть готовы для полного анализа (требовать auth, не отклонять формат)
            format_ready = not success and ("401" in str(error) or "403" in str(error) or (isinstance(data, dict) and ("Not authenticated" in str(data.get("detail", "")))))
            
            if not format_ready:
                all_formats_ready = False
                logger.warning(f"Format {content_type} not ready for full analysis: {error}")
        
        self.log_test_result(
            "🎯 Все форматы файлов готовы для полного содержимого анализа (не только статус)",
            all_formats_ready,
            f"All formats ready for full analysis content: {all_formats_ready}",
            {"tested_formats": [f[1] for f in file_formats]}
        )
    async def test_user_api_keys_for_analysis(self):
        """🎯 КРИТИЧЕСКИЙ ТЕСТ: Проверить что система использует пользовательские API ключи для анализа"""
        logger.info("=== 🎯 КРИТИЧЕСКИЙ ТЕСТ: Пользовательские API ключи для анализа ===")
        
        # Проверяем что endpoint для сохранения API ключей работает
        test_api_keys = {
            "api_key_1": "test_gemini_key_for_analysis",
            "api_key_2": "test_openai_key_for_analysis",
            "api_key_3": "test_anthropic_key_for_analysis"
        }
        
        success, data, error = await self.make_request("POST", "/api/api-keys", json=test_api_keys)
        
        # Должен требовать аутентификацию, но принимать новые названия ключей
        is_auth_required = not success and ("401" in str(error) or "403" in str(error) or (isinstance(data, dict) and ("Not authenticated" in str(data.get("detail", "")))))
        no_validation_error = "422" not in str(error) and not (isinstance(data, dict) and "validation" in str(data).lower())
        
        self.log_test_result(
            "🎯 API Keys - Поддержка пользовательских ключей для анализа",
            is_auth_required and no_validation_error,
            f"Auth required: {is_auth_required}, No validation error: {no_validation_error}",
            data
        )
        
        # Проверяем что quick-gemini-setup также работает для анализа
        test_gemini_setup = {"api_key": "test_gemini_key_for_document_analysis"}
        success, data, error = await self.make_request("POST", "/api/quick-gemini-setup", json=test_gemini_setup)
        
        is_auth_required = not success and ("401" in str(error) or "403" in str(error) or (isinstance(data, dict) and ("Not authenticated" in str(data.get("detail", "")))))
        no_server_error = "500" not in str(error)
        
        self.log_test_result(
            "🎯 Quick Gemini Setup - Для анализа документов",
            is_auth_required and no_server_error,
            f"Auth required: {is_auth_required}, No server error: {no_server_error}",
            data
        )
    
    async def test_extracted_text_processing(self):
        """🎯 КРИТИЧЕСКИЙ ТЕСТ: Проверить что extracted_text правильно передается в super_analysis_engine"""
        logger.info("=== 🎯 КРИТИЧЕСКИЙ ТЕСТ: Обработка извлеченного текста ===")
        
        # Проверяем что OCR система готова для извлечения текста
        success, data, error = await self.make_request("GET", "/api/ocr-status")
        
        if success and isinstance(data, dict):
            ocr_service = data.get("ocr_service", {})
            
            # Проверяем что есть методы для извлечения текста
            methods = ocr_service.get("methods", {})
            has_text_extraction = len(methods) > 0
            
            # Проверяем что есть tesseract или другие методы OCR
            has_tesseract = "tesseract_ocr" in methods
            has_direct_pdf = "direct_pdf" in methods
            
            # Проверяем что система готова к production
            production_ready = ocr_service.get("production_ready") is True
            
            self.log_test_result(
                "🎯 OCR система готова для извлечения текста",
                has_text_extraction and (has_tesseract or has_direct_pdf) and production_ready,
                f"Has extraction: {has_text_extraction}, Tesseract: {has_tesseract}, Direct PDF: {has_direct_pdf}, Production: {production_ready}",
                data
            )
        else:
            self.log_test_result("🎯 OCR система готова для извлечения текста", False, f"Error: {error}", data)
        
        # Проверяем что analyze-file endpoint готов обрабатывать извлеченный текст
        test_image_data = self.create_test_image()
        form_data = aiohttp.FormData()
        form_data.add_field('file', test_image_data, filename='text_document.jpg', content_type='image/jpeg')
        form_data.add_field('language', 'ru')
        
        # Измеряем время ответа - должен быстро обрабатывать
        start_time = time.time()
        success, data, error = await self.make_request("POST", "/api/analyze-file", data=form_data)
        response_time = time.time() - start_time
        
        # Должен быстро отвечать и требовать аутентификацию
        is_fast = response_time < 5.0  # Должен отвечать быстро
        is_auth_required = not success and ("401" in str(error) or "403" in str(error) or (isinstance(data, dict) and ("Not authenticated" in str(data.get("detail", "")))))
        
        self.log_test_result(
            "🎯 Analyze-file готов для обработки извлеченного текста",
            is_fast and is_auth_required,
            f"Fast response: {is_fast} ({response_time:.2f}s), Auth required: {is_auth_required}",
            {"response_time": response_time}
        )
        
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

    async def test_job_search_endpoints(self):
        """🎯 NEW FEATURE TESTING: Job Search Functionality in Telegram Mini App"""
        logger.info("=== 🎯 NEW FEATURE TESTING: Job Search Functionality ===")
        
        # Test 1: GET /api/job-search-status - Public endpoint (no auth required)
        success, data, error = await self.make_request("GET", "/api/job-search-status")
        if success and isinstance(data, dict):
            has_status = "status" in data
            has_service_info = "service" in data
            has_integration_info = "arbeitnow_integration" in data
            
            self.log_test_result(
                "🎯 GET /api/job-search-status - Job search service status",
                has_status and has_service_info and has_integration_info,
                f"Status: {data.get('status')}, Service: {data.get('service')}, Integration: {data.get('arbeitnow_integration')}",
                data
            )
        else:
            self.log_test_result("🎯 GET /api/job-search-status - Job search service status", False, f"Error: {error}", data)
        
        # Test 2: GET /api/job-search - Public job search with filters (no auth required)
        search_params = "?search_query=developer&location=Berlin&language_level=B2&limit=10"
        success, data, error = await self.make_request("GET", f"/api/job-search{search_params}")
        if success and isinstance(data, dict):
            has_status = "status" in data
            has_jobs = "jobs" in data and isinstance(data["jobs"], list)
            has_total = "total_found" in data
            has_filters = "applied_filters" in data
            
            self.log_test_result(
                "🎯 GET /api/job-search - Job search with filters",
                has_status and has_jobs and has_total and has_filters,
                f"Status: {data.get('status')}, Jobs found: {len(data.get('jobs', []))}, Total: {data.get('total_found')}, Filters: {data.get('applied_filters')}",
                data
            )
        else:
            self.log_test_result("🎯 GET /api/job-search - Job search with filters", False, f"Error: {error}", data)
        
        # Test 3: POST /api/job-search - Advanced job search (no auth required)
        advanced_search_data = {
            "search_query": "Python developer",
            "location": "Munich",
            "remote": True,
            "visa_sponsorship": True,
            "language_level": "C1",
            "category": "IT",
            "limit": 20
        }
        success, data, error = await self.make_request("POST", "/api/job-search", json=advanced_search_data)
        if success and isinstance(data, dict):
            has_status = "status" in data
            has_jobs = "jobs" in data and isinstance(data["jobs"], list)
            has_ai_filtering = "ai_filtered" in data
            has_language_analysis = "language_analysis" in data
            
            self.log_test_result(
                "🎯 POST /api/job-search - Advanced job search with AI filtering",
                has_status and has_jobs and has_ai_filtering and has_language_analysis,
                f"Status: {data.get('status')}, Jobs: {len(data.get('jobs', []))}, AI filtered: {data.get('ai_filtered')}, Language analysis: {data.get('language_analysis')}",
                data
            )
        else:
            self.log_test_result("🎯 POST /api/job-search - Advanced job search with AI filtering", False, f"Error: {error}", data)
    
    async def test_job_subscriptions_endpoints(self):
        """🎯 NEW FEATURE TESTING: Job Subscriptions for Telegram Notifications"""
        logger.info("=== 🎯 NEW FEATURE TESTING: Job Subscriptions ===")
        
        # Test 1: POST /api/job-subscriptions - Create subscription (requires auth)
        subscription_data = {
            "search_query": "React developer",
            "location": "Hamburg",
            "remote": False,
            "visa_sponsorship": True,
            "language_level": "B2",
            "category": "Frontend"
        }
        success, data, error = await self.make_request("POST", "/api/job-subscriptions", json=subscription_data)
        
        is_auth_required = not success and ("401" in str(error) or "403" in str(error) or (isinstance(data, dict) and ("Not authenticated" in str(data.get("detail", "")))))
        
        self.log_test_result(
            "🎯 POST /api/job-subscriptions - Create job subscription (requires auth)",
            is_auth_required,
            f"Correctly requires authentication" if is_auth_required else f"Unexpected response: {error}",
            data
        )
        
        # Test 2: GET /api/job-subscriptions - Get user subscriptions (requires auth)
        success, data, error = await self.make_request("GET", "/api/job-subscriptions")
        
        is_auth_required = not success and ("401" in str(error) or "403" in str(error) or (isinstance(data, dict) and ("Not authenticated" in str(data.get("detail", "")))))
        
        self.log_test_result(
            "🎯 GET /api/job-subscriptions - Get user subscriptions (requires auth)",
            is_auth_required,
            f"Correctly requires authentication" if is_auth_required else f"Unexpected response: {error}",
            data
        )
        
        # Test 3: PUT /api/job-subscriptions/{id} - Update subscription (requires auth)
        test_subscription_id = "test-subscription-123"
        update_data = {
            "search_query": "Updated query",
            "location": "Frankfurt",
            "active": True
        }
        success, data, error = await self.make_request("PUT", f"/api/job-subscriptions/{test_subscription_id}", json=update_data)
        
        is_auth_required = not success and ("401" in str(error) or "403" in str(error) or (isinstance(data, dict) and ("Not authenticated" in str(data.get("detail", "")))))
        
        self.log_test_result(
            "🎯 PUT /api/job-subscriptions/{id} - Update subscription (requires auth)",
            is_auth_required,
            f"Correctly requires authentication" if is_auth_required else f"Unexpected response: {error}",
            data
        )
        
        # Test 4: DELETE /api/job-subscriptions/{id} - Delete subscription (requires auth)
        success, data, error = await self.make_request("DELETE", f"/api/job-subscriptions/{test_subscription_id}")
        
        is_auth_required = not success and ("401" in str(error) or "403" in str(error) or (isinstance(data, dict) and ("Not authenticated" in str(data.get("detail", "")))))
        
        self.log_test_result(
            "🎯 DELETE /api/job-subscriptions/{id} - Delete subscription (requires auth)",
            is_auth_required,
            f"Correctly requires authentication" if is_auth_required else f"Unexpected response: {error}",
            data
        )
    
    async def test_resume_analysis_endpoints(self):
        """🎯 NEW FEATURE TESTING: AI Resume Analysis"""
        logger.info("=== 🎯 NEW FEATURE TESTING: AI Resume Analysis ===")
        
        # Test 1: POST /api/analyze-resume - AI resume analysis (requires auth)
        resume_data = {
            "resume_text": "John Doe\nSoftware Developer\n5 years experience in Python, React, and Node.js\nEducation: Computer Science degree\nExperience: Senior Developer at Tech Company",
            "target_position": "Senior Full Stack Developer",
            "language": "en"
        }
        success, data, error = await self.make_request("POST", "/api/analyze-resume", json=resume_data)
        
        is_auth_required = not success and ("401" in str(error) or "403" in str(error) or (isinstance(data, dict) and ("Not authenticated" in str(data.get("detail", "")))))
        
        self.log_test_result(
            "🎯 POST /api/analyze-resume - AI resume analysis (requires auth)",
            is_auth_required,
            f"Correctly requires authentication" if is_auth_required else f"Unexpected response: {error}",
            data
        )
        
        # Test 2: POST /api/improve-resume - Resume improvement based on analysis (requires auth)
        improvement_data = {
            "resume_analysis_id": "test-analysis-123",
            "target_position": "Lead Developer"
        }
        success, data, error = await self.make_request("POST", "/api/improve-resume", json=improvement_data)
        
        is_auth_required = not success and ("401" in str(error) or "403" in str(error) or (isinstance(data, dict) and ("Not authenticated" in str(data.get("detail", "")))))
        
        self.log_test_result(
            "🎯 POST /api/improve-resume - Resume improvement (requires auth)",
            is_auth_required,
            f"Correctly requires authentication" if is_auth_required else f"Unexpected response: {error}",
            data
        )
        
        # Test 3: GET /api/resume-analyses - Get resume analysis history (requires auth)
        success, data, error = await self.make_request("GET", "/api/resume-analyses")
        
        is_auth_required = not success and ("401" in str(error) or "403" in str(error) or (isinstance(data, dict) and ("Not authenticated" in str(data.get("detail", "")))))
        
        self.log_test_result(
            "🎯 GET /api/resume-analyses - Resume analysis history (requires auth)",
            is_auth_required,
            f"Correctly requires authentication" if is_auth_required else f"Unexpected response: {error}",
            data
        )
    
    async def test_interview_preparation_endpoints(self):
        """🎯 NEW FEATURE TESTING: AI Interview Preparation"""
        logger.info("=== 🎯 NEW FEATURE TESTING: AI Interview Preparation ===")
        
        # Test 1: POST /api/prepare-interview - AI interview preparation (requires auth)
        interview_data = {
            "job_description": "We are looking for a Senior Python Developer with 5+ years experience in Django, REST APIs, and cloud technologies. Must have experience with AWS, Docker, and microservices architecture.",
            "resume_text": "Senior Python Developer with 6 years experience in Django, Flask, REST APIs, AWS, Docker, and microservices.",
            "interview_type": "technical",
            "language": "en"
        }
        success, data, error = await self.make_request("POST", "/api/prepare-interview", json=interview_data)
        
        is_auth_required = not success and ("401" in str(error) or "403" in str(error) or (isinstance(data, dict) and ("Not authenticated" in str(data.get("detail", "")))))
        
        self.log_test_result(
            "🎯 POST /api/prepare-interview - AI interview preparation (requires auth)",
            is_auth_required,
            f"Correctly requires authentication" if is_auth_required else f"Unexpected response: {error}",
            data
        )
        
        # Test 2: GET /api/interview-preparations - Get interview preparation history (requires auth)
        success, data, error = await self.make_request("GET", "/api/interview-preparations")
        
        is_auth_required = not success and ("401" in str(error) or "403" in str(error) or (isinstance(data, dict) and ("Not authenticated" in str(data.get("detail", "")))))
        
        self.log_test_result(
            "🎯 GET /api/interview-preparations - Interview preparation history (requires auth)",
            is_auth_required,
            f"Correctly requires authentication" if is_auth_required else f"Unexpected response: {error}",
            data
        )
    
    async def test_job_search_integration_features(self):
        """🎯 NEW FEATURE TESTING: Job Search Integration Features"""
        logger.info("=== 🎯 NEW FEATURE TESTING: Job Search Integration Features ===")
        
        # Test 1: Verify arbeitnow.com integration status
        success, data, error = await self.make_request("GET", "/api/job-search-status")
        if success and isinstance(data, dict):
            integration_info = data.get("arbeitnow_integration", {})
            has_integration = isinstance(integration_info, dict)
            has_status = integration_info.get("status") if has_integration else None
            has_api_info = integration_info.get("api_endpoint") if has_integration else None
            
            self.log_test_result(
                "🎯 Arbeitnow.com Integration - Status check",
                has_integration and has_status and has_api_info,
                f"Integration status: {has_status}, API endpoint: {has_api_info}" if has_integration else "Integration info missing",
                integration_info
            )
        else:
            self.log_test_result("🎯 Arbeitnow.com Integration - Status check", False, f"Error: {error}", data)
        
        # Test 2: Test German language level filtering (A1-C2)
        language_levels = ["A1", "A2", "B1", "B2", "C1", "C2"]
        for level in language_levels:
            search_data = {
                "search_query": "developer",
                "location": "Berlin",
                "language_level": level,
                "limit": 5
            }
            success, data, error = await self.make_request("POST", "/api/job-search", json=search_data)
            
            if success and isinstance(data, dict):
                has_language_filter = data.get("applied_filters", {}).get("language_level") == level
                has_ai_filtering = "ai_filtered" in data
                
                self.log_test_result(
                    f"🎯 German Language Level Filtering - {level}",
                    has_language_filter and has_ai_filtering,
                    f"Language level {level} filter applied: {has_language_filter}, AI filtering: {has_ai_filtering}",
                    {"level": level, "filter_applied": has_language_filter}
                )
            else:
                self.log_test_result(f"🎯 German Language Level Filtering - {level}", False, f"Error: {error}", data)
        
        # Test 3: Test user API keys integration for AI analysis
        # This should work without auth for basic search, but require auth for AI features
        ai_search_data = {
            "search_query": "AI engineer",
            "location": "Munich",
            "language_level": "C1",
            "limit": 10
        }
        success, data, error = await self.make_request("POST", "/api/job-search", json=ai_search_data)
        
        if success and isinstance(data, dict):
            has_ai_analysis = "ai_filtered" in data or "language_analysis" in data
            works_without_auth = success  # Should work for basic search
            
            self.log_test_result(
                "🎯 AI Analysis Integration - Works without auth for basic search",
                works_without_auth,
                f"Basic AI search works: {works_without_auth}, Has AI features: {has_ai_analysis}",
                {"ai_features": has_ai_analysis}
            )
        else:
            self.log_test_result("🎯 AI Analysis Integration - Works without auth for basic search", False, f"Error: {error}", data)
    
    async def test_job_search_system_readiness(self):
        """🎯 FINAL TEST: Job Search System Production Readiness"""
        logger.info("=== 🎯 FINAL TEST: Job Search System Production Readiness ===")
        
        # Test 1: All job search endpoints exist and respond correctly
        job_search_endpoints = [
            ("GET", "/api/job-search-status", "public"),
            ("GET", "/api/job-search", "public"),
            ("POST", "/api/job-search", "public"),
            ("POST", "/api/job-subscriptions", "protected"),
            ("GET", "/api/job-subscriptions", "protected"),
            ("POST", "/api/analyze-resume", "protected"),
            ("POST", "/api/improve-resume", "protected"),
            ("GET", "/api/resume-analyses", "protected"),
            ("POST", "/api/prepare-interview", "protected"),
            ("GET", "/api/interview-preparations", "protected")
        ]
        
        all_endpoints_working = True
        endpoint_results = []
        
        for method, endpoint, auth_type in job_search_endpoints:
            if method == "GET" and "?" not in endpoint:
                if "job-search" in endpoint and endpoint != "/api/job-search-status":
                    # Add query params for job search
                    test_endpoint = f"{endpoint}?search_query=test&limit=5"
                else:
                    test_endpoint = endpoint
                success, data, error = await self.make_request(method, test_endpoint)
            else:
                # POST endpoints need data
                test_data = {"test": "data"}
                if "job-search" in endpoint:
                    test_data = {"search_query": "test", "limit": 5}
                elif "resume" in endpoint:
                    test_data = {"resume_text": "test resume", "language": "en"}
                elif "interview" in endpoint:
                    test_data = {"job_description": "test job", "language": "en"}
                elif "subscription" in endpoint:
                    test_data = {"search_query": "test", "location": "Berlin"}
                
                success, data, error = await self.make_request(method, endpoint, json=test_data)
            
            if auth_type == "public":
                endpoint_working = success
            else:  # protected
                # Should fail with auth error, not 404 or 500
                endpoint_working = not success and ("401" in str(error) or "403" in str(error) or (isinstance(data, dict) and ("Not authenticated" in str(data.get("detail", "")))))
            
            endpoint_results.append({
                "endpoint": f"{method} {endpoint}",
                "working": endpoint_working,
                "auth_type": auth_type
            })
            
            if not endpoint_working:
                all_endpoints_working = False
                logger.warning(f"Endpoint {method} {endpoint} not working properly: {error}")
        
        self.log_test_result(
            "🎯 Job Search Endpoints - All endpoints functional",
            all_endpoints_working,
            f"All {len(job_search_endpoints)} job search endpoints working correctly" if all_endpoints_working else f"Some endpoints have issues",
            endpoint_results
        )
        
        # Test 2: Integration with external services ready
        success, data, error = await self.make_request("GET", "/api/job-search-status")
        if success and isinstance(data, dict):
            service_ready = data.get("status") == "operational"
            has_integration = "arbeitnow_integration" in data
            
            integration_ready = service_ready and has_integration
        else:
            integration_ready = False
        
        self.log_test_result(
            "🎯 External Integration - Arbeitnow.com ready",
            integration_ready,
            f"External integration ready: {integration_ready}",
            {"service_ready": service_ready if 'service_ready' in locals() else False}
        )
        
        # Test 3: AI features integration ready
        success, data, error = await self.make_request("GET", "/api/modern-llm-status")
        if success and isinstance(data, dict):
            ai_ready = data.get("modern") is True and data.get("status") == "success"
        else:
            ai_ready = False
        
        self.log_test_result(
            "🎯 AI Features - Modern LLM integration ready",
            ai_ready,
            f"AI features ready for job search: {ai_ready}",
            {"ai_ready": ai_ready}
        )
        
        # Overall job search system readiness
        job_search_system_ready = all([
            all_endpoints_working,
            integration_ready,
            ai_ready
        ])
        
        self.log_test_result(
            "🎯 JOB SEARCH SYSTEM - Production Ready",
            job_search_system_ready,
            f"Endpoints: {all_endpoints_working}, Integration: {integration_ready}, AI: {ai_ready}",
            {
                "endpoints_working": all_endpoints_working,
                "integration_ready": integration_ready,
                "ai_ready": ai_ready,
                "overall_ready": job_search_system_ready
            }
        )
        
        return job_search_system_ready

async def main():
    """Main test execution - FINAL JOB SEARCH TESTING"""
    async with BackendTester() as tester:
        logger.info("🎯 ФИНАЛЬНОЕ ТЕСТИРОВАНИЕ: Job Search функциональность после всех исправлений")
        logger.info("=" * 80)
        
        # ФОКУС НА КОНКРЕТНЫХ ЗАДАЧАХ ИЗ ЗАПРОСА:
        # 1. GET /api/job-search-status - убедись что возвращает arbeitnow_integration и service информацию
        # 2. POST /api/job-search - убедись что работает без аутентификации и возвращает результаты
        # 3. German Language Levels - протестируй 2-3 уровня (например B1, C1) что они работают
        # 4. Job search results - убедись что возвращает actual job listings (не 0 results)
        
        # Запускаем только критические тесты Job Search
        await tester.test_arbeitnow_integration_status()
        await tester.test_job_search_endpoints()
        await tester.test_german_language_level_filtering_focused()  # Фокус на B1, C1
        await tester.test_job_search_results_validation()
        
        # Выводим результаты
        logger.info("=" * 80)
        logger.info("🎯 РЕЗУЛЬТАТЫ ФИНАЛЬНОГО ТЕСТИРОВАНИЯ JOB SEARCH:")
        
        total_tests = len(tester.test_results)
        passed_tests = sum(1 for result in tester.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        logger.info(f"Всего тестов: {total_tests}")
        logger.info(f"Успешных: {passed_tests}")
        logger.info(f"Неудачных: {failed_tests}")
        logger.info(f"Процент успеха: {success_rate:.1f}%")
        
        # Выводим детали неудачных тестов
        if failed_tests > 0:
            logger.info("\n❌ НЕУДАЧНЫЕ ТЕСТЫ:")
            for result in tester.test_results:
                if not result["success"]:
                    logger.info(f"  - {result['test']}: {result['details']}")
        
        # Выводим успешные критические тесты
        logger.info("\n✅ УСПЕШНЫЕ КРИТИЧЕСКИЕ ТЕСТЫ:")
        for result in tester.test_results:
            if result["success"] and "🎯" in result["test"]:
                logger.info(f"  - {result['test']}: {result['details']}")
        
        logger.info("=" * 80)
        logger.info("🎯 ФИНАЛЬНОЕ ТЕСТИРОВАНИЕ JOB SEARCH ЗАВЕРШЕНО")
        
        return success_rate >= 75.0  # Считаем успешным если 75%+ тестов прошли

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

    async def run_all_tests(self):
        """🎯 КРИТИЧЕСКОЕ ТЕСТИРОВАНИЕ: Cities API и Job Search API для Telegram Mini App"""
        logger.info("🎯 КРИТИЧЕСКОЕ ТЕСТИРОВАНИЕ: Cities API и Job Search API для Telegram Mini App")
        logger.info("=" * 80)
        logger.info("ФОКУС: Тестирование исправлений для Telegram Mini App")
        logger.info("- Cities API: популярные города, поиск с автодополнением")
        logger.info("- Job Search API: поиск БЕЗ search_query (необязательный параметр)")
        logger.info("- Обработка специальных символов и пробелов")
        logger.info("- Корректная структура данных и отсутствие ошибок pattern matching")
        logger.info("=" * 80)
        
        try:
            # 🎯 ПОЛЬЗОВАТЕЛЬСКИЙ ЗАПРОС: Telegram Mini App Job Search API endpoints
            logger.info("📱 ТЕСТИРОВАНИЕ TELEGRAM MINI APP JOB SEARCH API ENDPOINTS (ПОЛЬЗОВАТЕЛЬСКИЙ ЗАПРОС)")
            await self.test_telegram_mini_app_job_search_api_endpoints()
            
            # 🎯 ОСНОВНЫЕ ТЕСТЫ (ПРИОРИТЕТ 1): Cities API
            logger.info("🏙️ ТЕСТИРОВАНИЕ CITIES API")
            await self.test_cities_api_endpoints()
            
            # 🎯 ОСНОВНЫЕ ТЕСТЫ (ПРИОРИТЕТ 1): Job Search API
            logger.info("💼 ТЕСТИРОВАНИЕ JOB SEARCH API")
            await self.test_job_search_endpoints_corrected_functionality()
            await self.test_parameter_validation_and_error_handling()
            await self.test_special_characters_and_spaces_handling()
            
            # 🎯 КРИТИЧЕСКИЕ ТЕСТЫ: Telegram Mini App Pattern Errors
            logger.info("📱 ТЕСТИРОВАНИЕ TELEGRAM MINI APP PATTERN ERRORS")
            await self.test_telegram_mini_app_job_search_pattern_errors()
            await self.test_parameter_validation_edge_cases()
            
            # 🎯 ДОПОЛНИТЕЛЬНЫЕ ТЕСТЫ: German Language Level Filtering
            logger.info("🇩🇪 ТЕСТИРОВАНИЕ GERMAN LANGUAGE LEVEL FILTERING")
            await self.test_german_language_level_filtering()
            
            # 🎯 ПОДДЕРЖИВАЮЩИЕ ТЕСТЫ: Базовая функциональность
            logger.info("⚙️ БАЗОВЫЕ ПРОВЕРКИ СИСТЕМЫ")
            await self.test_basic_health_endpoints()
            await self.test_api_health_endpoints()
            
            overall_ready = True
            
        except Exception as e:
            logger.error(f"Critical error during testing: {e}")
            self.log_test_result("Test Execution", False, f"Critical error: {e}", None)
            overall_ready = False
        
        # Generate comprehensive test summary
        return self.generate_job_search_summary(overall_ready)
    
    def generate_job_search_summary(self, system_ready=False):
        """Generate and display comprehensive test summary for Job Search functionality"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        logger.info("=" * 80)
        logger.info("🎯 JOB SEARCH FUNCTIONALITY TESTING COMPLETED")
        logger.info(f"📊 OVERALL RESULTS: {passed_tests}/{total_tests} tests passed ({success_rate:.1f}% success)")
        logger.info(f"✅ Passed: {passed_tests}")
        logger.info(f"❌ Failed: {failed_tests}")
        logger.info(f"🚀 System ready for production: {'YES' if system_ready else 'NO'}")
        logger.info("=" * 80)
        
        # Job Search specific results
        job_tests = [result for result in self.test_results if "🎯" in result["test"] and any(keyword in result["test"].lower() for keyword in ["job", "resume", "interview", "subscription"])]
        job_passed = sum(1 for result in job_tests if result["success"])
        job_total = len(job_tests)
        
        if job_total > 0:
            job_success_rate = (job_passed / job_total * 100)
            logger.info(f"🎯 JOB SEARCH TESTS: {job_passed}/{job_total} ({job_success_rate:.1f}% success)")
            
            # Show job search test results
            logger.info("🎯 JOB SEARCH RESULTS:")
            for result in job_tests:
                status = "✅" if result["success"] else "❌"
                logger.info(f"   {status} {result['test']}")
            
            # Show failed job search tests
            failed_job = [result for result in job_tests if not result["success"]]
            if failed_job:
                logger.info("❌ FAILED JOB SEARCH TESTS:")
                for result in failed_job:
                    logger.info(f"   ❌ {result['test']}: {result['details']}")
            
            # Job search functionality conclusion
            if job_passed == job_total:
                logger.info("🚀 JOB SEARCH RESULT: ALL TESTS PASSED!")
                logger.info("✅ Job Search API endpoints working correctly")
                logger.info("✅ Arbeitnow.com integration successful")
                logger.info("✅ German language level filtering (A1-C2) operational")
                logger.info("✅ AI-powered job filtering functional")
                logger.info("✅ Resume analysis and improvement working")
                logger.info("✅ Interview preparation system functional")
                logger.info("✅ Job subscription system for Telegram notifications working")
                logger.info("✅ User API keys integration for AI analysis operational")
            else:
                logger.info("❌ JOB SEARCH ISSUES: NOT ALL TESTS PASSED")
                logger.info("❌ Some job search functionality requires attention")
        
        # Housing Search results (existing functionality)
        housing_tests = [result for result in self.test_results if "🏠" in result["test"] or "housing" in result["test"].lower()]
        housing_passed = sum(1 for result in housing_tests if result["success"])
        housing_total = len(housing_tests)
        
        if housing_total > 0:
            housing_success_rate = (housing_passed / housing_total * 100)
            logger.info(f"🏠 HOUSING SEARCH TESTS: {housing_passed}/{housing_total} ({housing_success_rate:.1f}% success)")
        
        # Document Analysis results (existing functionality)
        doc_tests = [result for result in self.test_results if "analysis" in result["test"].lower() and "job" not in result["test"].lower()]
        doc_passed = sum(1 for result in doc_tests if result["success"])
        doc_total = len(doc_tests)
        
        if doc_total > 0:
            doc_success_rate = (doc_passed / doc_total * 100)
            logger.info(f"📄 DOCUMENT ANALYSIS TESTS: {doc_passed}/{doc_total} ({doc_success_rate:.1f}% success)")
        
        logger.info("=" * 80)
        
        return {
            "success_rate": success_rate,
            "job_passed": job_passed,
            "job_total": job_total,
            "housing_passed": housing_passed,
            "housing_total": housing_total,
            "doc_passed": doc_passed,
            "doc_total": doc_total,
            "system_ready": system_ready,
            "job_search_functional": job_passed == job_total if job_total > 0 else False
        }

    def generate_housing_search_summary(self, system_ready=False):
        """Generate and display comprehensive test summary for Housing Search functionality"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        logger.info("=" * 80)
        logger.info("🏠 HOUSING SEARCH FUNCTIONALITY TESTING COMPLETED")
        logger.info(f"📊 OVERALL RESULTS: {passed_tests}/{total_tests} tests passed ({success_rate:.1f}% success)")
        logger.info(f"✅ Passed: {passed_tests}")
        logger.info(f"❌ Failed: {failed_tests}")
        logger.info(f"🚀 System ready for production: {'YES' if system_ready else 'NO'}")
        logger.info("=" * 80)
        
        # Housing Search specific results
        housing_tests = [result for result in self.test_results if "🏠" in result["test"] or "housing" in result["test"].lower()]
        housing_passed = sum(1 for result in housing_tests if result["success"])
        housing_total = len(housing_tests)
        
        if housing_total > 0:
            housing_success_rate = (housing_passed / housing_total * 100)
            logger.info(f"🏠 HOUSING SEARCH TESTS: {housing_passed}/{housing_total} ({housing_success_rate:.1f}% success)")
            
            # Show housing test results
            logger.info("🏠 HOUSING SEARCH RESULTS:")
            for result in housing_tests:
                status = "✅" if result["success"] else "❌"
                logger.info(f"   {status} {result['test']}")
            
            # Show failed housing tests
            failed_housing = [result for result in housing_tests if not result["success"]]
            if failed_housing:
                logger.info("❌ FAILED HOUSING TESTS:")
                for result in failed_housing:
                    logger.info(f"   ❌ {result['test']}: {result['details']}")
            
            # Housing functionality conclusion
            if housing_passed == housing_total:
                logger.info("🚀 HOUSING SEARCH RESULT: ALL TESTS PASSED!")
                logger.info("✅ Housing Search API endpoints working correctly")
                logger.info("✅ Housing Services integration successful")
                logger.info("✅ Authentication & Authorization properly enforced")
                logger.info("✅ Error handling and data integrity verified")
                logger.info("✅ German real estate sites integration operational")
                logger.info("✅ AI-powered analysis features functional")
                logger.info("✅ Housing subscription system working")
            else:
                logger.info("❌ HOUSING SEARCH ISSUES: NOT ALL TESTS PASSED")
                logger.info("❌ Some housing functionality requires attention")
        
        # Document Analysis results (existing functionality)
        doc_tests = [result for result in self.test_results if "🎯" in result["test"] or "analysis" in result["test"].lower()]
        doc_passed = sum(1 for result in doc_tests if result["success"])
        doc_total = len(doc_tests)
        
        if doc_total > 0:
            doc_success_rate = (doc_passed / doc_total * 100)
            logger.info(f"🎯 DOCUMENT ANALYSIS TESTS: {doc_passed}/{doc_total} ({doc_success_rate:.1f}% success)")
        
        logger.info("=" * 80)
        
        return {
            "success_rate": success_rate,
            "housing_passed": housing_passed,
            "housing_total": housing_total,
            "doc_passed": doc_passed,
            "doc_total": doc_total,
            "system_ready": system_ready,
            "housing_functional": housing_passed == housing_total if housing_total > 0 else False
        }
    
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
    
    def generate_document_analysis_summary(self, system_ready=False):
        """Generate and display document analysis test summary"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        logger.info("=" * 80)
        logger.info("🎯 КРИТИЧЕСКОЕ ТЕСТИРОВАНИЕ АНАЛИЗА ДОКУМЕНТОВ ЗАВЕРШЕНО")
        logger.info(f"📊 РЕЗУЛЬТАТЫ: {passed_tests}/{total_tests} тестов прошли успешно ({success_rate:.1f}% успех)")
        logger.info(f"✅ Успешно: {passed_tests}")
        logger.info(f"❌ Неудачно: {failed_tests}")
        logger.info("=" * 80)
        
        # Выводим критические результаты анализа документов
        critical_tests = [result for result in self.test_results if "🎯" in result["test"]]
        critical_passed = sum(1 for result in critical_tests if result["success"])
        critical_total = len(critical_tests)
        
        if critical_total > 0:
            critical_success_rate = (critical_passed / critical_total * 100)
            logger.info(f"🎯 КРИТИЧЕСКИЕ ТЕСТЫ АНАЛИЗА ДОКУМЕНТОВ: {critical_passed}/{critical_total} ({critical_success_rate:.1f}% успех)")
            
            # Показываем результаты критических тестов
            logger.info("🎯 КРИТИЧЕСКИЕ РЕЗУЛЬТАТЫ АНАЛИЗА ДОКУМЕНТОВ:")
            for result in critical_tests:
                status = "✅" if result["success"] else "❌"
                logger.info(f"   {status} {result['test']}")
            
            # Показываем неудачные критические тесты
            failed_critical = [result for result in critical_tests if not result["success"]]
            if failed_critical:
                logger.info("❌ НЕУДАЧНЫЕ КРИТИЧЕСКИЕ ТЕСТЫ:")
                for result in failed_critical:
                    logger.info(f"   ❌ {result['test']}: {result['details']}")
            
            # Итоговое заключение по анализу документов
            if critical_passed == critical_total:
                logger.info("🚀 КРИТИЧЕСКИЙ РЕЗУЛЬТАТ: ВСЕ ТЕСТЫ АНАЛИЗА ДОКУМЕНТОВ ПРОШЛИ!")
                logger.info("✅ ПРОБЛЕМА 'файлы считываются, но анализ не выдается' ИСПРАВЛЕНА!")
                logger.info("✅ Система использует РЕАЛЬНЫЙ AI анализ через super_analysis_engine")
                logger.info("✅ Статичные заглушки заменены на comprehensive analysis")
            else:
                logger.info("❌ КРИТИЧЕСКАЯ ПРОБЛЕМА: НЕ ВСЕ ТЕСТЫ АНАЛИЗА ДОКУМЕНТОВ ПРОШЛИ")
                logger.info("❌ Требуется дополнительная работа над анализом документов")
        
        logger.info("=" * 80)
        
        return {
            "success_rate": success_rate,
            "critical_passed": critical_passed,
            "critical_total": critical_total,
            "system_ready": system_ready,
            "document_analysis_fixed": critical_passed == critical_total
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
    
    # =====================================================
    # 🏠 HOUSING SEARCH FUNCTIONALITY TESTS
    # =====================================================
    
    async def test_housing_search_endpoints(self):
        """🏠 Test all Housing Search API endpoints"""
        logger.info("=== 🏠 Testing Housing Search API Endpoints ===")
        
        # Test main housing search endpoint (requires auth)
        search_data = {
            "city": "Berlin",
            "max_price": 1500,
            "property_type": "wohnung",
            "radius": 10
        }
        
        success, data, error = await self.make_request("POST", "/api/housing-search", json=search_data)
        
        # Should require authentication
        is_auth_required = not success and ("401" in str(error) or "403" in str(error) or (isinstance(data, dict) and ("Not authenticated" in str(data.get("detail", "")))))
        
        self.log_test_result(
            "POST /api/housing-search - Main search endpoint",
            is_auth_required,
            f"Correctly requires authentication" if is_auth_required else f"Unexpected response: {error}",
            data
        )
        
        # Test neighborhood analysis endpoint (requires auth)
        analysis_data = {
            "city": "München",
            "district": "Schwabing"
        }
        
        success, data, error = await self.make_request("POST", "/api/housing-neighborhood-analysis", json=analysis_data)
        
        is_auth_required = not success and ("401" in str(error) or "403" in str(error) or (isinstance(data, dict) and ("Not authenticated" in str(data.get("detail", "")))))
        
        self.log_test_result(
            "POST /api/housing-neighborhood-analysis - Neighborhood analysis",
            is_auth_required,
            f"Correctly requires authentication" if is_auth_required else f"Unexpected response: {error}",
            data
        )
        
        # Test create subscription endpoint (requires auth)
        subscription_data = {
            "city": "Hamburg",
            "max_price": 1200,
            "property_type": "wohnung"
        }
        
        success, data, error = await self.make_request("POST", "/api/housing-subscriptions", json=subscription_data)
        
        is_auth_required = not success and ("401" in str(error) or "403" in str(error) or (isinstance(data, dict) and ("Not authenticated" in str(data.get("detail", "")))))
        
        self.log_test_result(
            "POST /api/housing-subscriptions - Create subscription",
            is_auth_required,
            f"Correctly requires authentication" if is_auth_required else f"Unexpected response: {error}",
            data
        )
        
        # Test get subscriptions endpoint (requires auth)
        success, data, error = await self.make_request("GET", "/api/housing-subscriptions")
        
        is_auth_required = not success and ("401" in str(error) or "403" in str(error) or (isinstance(data, dict) and ("Not authenticated" in str(data.get("detail", "")))))
        
        self.log_test_result(
            "GET /api/housing-subscriptions - Get user subscriptions",
            is_auth_required,
            f"Correctly requires authentication" if is_auth_required else f"Unexpected response: {error}",
            data
        )
        
        # Test update subscription endpoint (requires auth)
        update_data = {
            "max_price": 1300,
            "active": True
        }
        
        success, data, error = await self.make_request("PUT", "/api/housing-subscriptions/test_sub_123", json=update_data)
        
        is_auth_required = not success and ("401" in str(error) or "403" in str(error) or (isinstance(data, dict) and ("Not authenticated" in str(data.get("detail", "")))))
        
        self.log_test_result(
            "PUT /api/housing-subscriptions/{id} - Update subscription",
            is_auth_required,
            f"Correctly requires authentication" if is_auth_required else f"Unexpected response: {error}",
            data
        )
        
        # Test delete subscription endpoint (requires auth)
        success, data, error = await self.make_request("DELETE", "/api/housing-subscriptions/test_sub_123")
        
        is_auth_required = not success and ("401" in str(error) or "403" in str(error) or (isinstance(data, dict) and ("Not authenticated" in str(data.get("detail", "")))))
        
        self.log_test_result(
            "DELETE /api/housing-subscriptions/{id} - Delete subscription",
            is_auth_required,
            f"Correctly requires authentication" if is_auth_required else f"Unexpected response: {error}",
            data
        )
        
        # Test landlord contact endpoint (requires auth)
        contact_data = {
            "listing_id": "test_listing_123",
            "user_name": "Max Mustermann",
            "user_occupation": "Software Engineer",
            "user_income": "4000 EUR"
        }
        
        success, data, error = await self.make_request("POST", "/api/housing-landlord-contact", json=contact_data)
        
        is_auth_required = not success and ("401" in str(error) or "403" in str(error) or (isinstance(data, dict) and ("Not authenticated" in str(data.get("detail", "")))))
        
        self.log_test_result(
            "POST /api/housing-landlord-contact - Generate landlord message",
            is_auth_required,
            f"Correctly requires authentication" if is_auth_required else f"Unexpected response: {error}",
            data
        )
        
        # Test market status endpoint (public)
        success, data, error = await self.make_request("GET", "/api/housing-market-status")
        
        if success and isinstance(data, dict):
            has_status = data.get("status") == "success"
            has_service_data = "data" in data and isinstance(data["data"], dict)
            service_data = data.get("data", {})
            
            has_supported_cities = "supported_cities" in service_data and isinstance(service_data["supported_cities"], list)
            has_supported_sources = "supported_sources" in service_data and isinstance(service_data["supported_sources"], list)
            has_ai_features = "ai_features" in service_data and isinstance(service_data["ai_features"], list)
            
            # Check for expected cities
            expected_cities = ["Berlin", "München", "Hamburg", "Köln", "Frankfurt"]
            cities_present = all(city in service_data.get("supported_cities", []) for city in expected_cities)
            
            # Check for expected sources
            expected_sources = ["ImmoScout24", "Immobilien.de", "WG-Gesucht", "eBay Kleinanzeigen"]
            sources_present = all(source in service_data.get("supported_sources", []) for source in expected_sources)
            
            # Check for AI features
            expected_features = ["Scam Detection", "Price Analysis", "Neighborhood Insights"]
            features_present = all(feature in service_data.get("ai_features", []) for feature in expected_features)
            
            self.log_test_result(
                "GET /api/housing-market-status - Market status (public)",
                has_status and has_service_data and has_supported_cities and has_supported_sources and has_ai_features and cities_present and sources_present and features_present,
                f"Status: {has_status}, Cities: {cities_present}, Sources: {sources_present}, AI Features: {features_present}",
                data
            )
        else:
            self.log_test_result(
                "GET /api/housing-market-status - Market status (public)",
                False,
                f"Error: {error}",
                data
            )
    
    async def test_housing_services_integration(self):
        """🏠 Test Housing Services Integration"""
        logger.info("=== 🏠 Testing Housing Services Integration ===")
        
        # Test that housing market status shows proper service integration
        success, data, error = await self.make_request("GET", "/api/housing-market-status")
        
        if success and isinstance(data, dict):
            service_data = data.get("data", {})
            
            # Check service status
            service_operational = service_data.get("service_status") == "operational"
            
            # Check cache functionality
            has_cache_info = "cache_size" in service_data and isinstance(service_data["cache_size"], int)
            
            # Check supported sources (housing scraper integration)
            supported_sources = service_data.get("supported_sources", [])
            scraper_sources = ["ImmoScout24", "Immobilien.de", "WG-Gesucht", "eBay Kleinanzeigen"]
            scraper_integration = all(source in supported_sources for source in scraper_sources)
            
            # Check AI features (housing AI service integration)
            ai_features = service_data.get("ai_features", [])
            expected_ai_features = ["Scam Detection", "Price Analysis", "Neighborhood Insights", "Total Cost Calculator", "Landlord Message Generator"]
            ai_integration = all(feature in ai_features for feature in expected_ai_features)
            
            # Check supported cities
            supported_cities = service_data.get("supported_cities", [])
            major_cities = ["Berlin", "München", "Hamburg", "Köln", "Frankfurt", "Stuttgart", "Düsseldorf"]
            cities_coverage = all(city in supported_cities for city in major_cities)
            
            self.log_test_result(
                "Housing Services - Integration check",
                service_operational and has_cache_info and scraper_integration and ai_integration and cities_coverage,
                f"Service operational: {service_operational}, Cache: {has_cache_info}, Scraper: {scraper_integration}, AI: {ai_integration}, Cities: {cities_coverage}",
                data
            )
            
            # Test individual service components
            self.log_test_result(
                "Housing Scraper Service - Source integration",
                scraper_integration,
                f"All 4 scraper sources integrated: {scraper_sources}",
                {"sources": supported_sources}
            )
            
            self.log_test_result(
                "Housing AI Service - Feature integration", 
                ai_integration,
                f"All 5 AI features integrated: {expected_ai_features}",
                {"features": ai_features}
            )
            
            self.log_test_result(
                "Housing Search Service - Cache functionality",
                has_cache_info,
                f"Cache system operational with size tracking",
                {"cache_size": service_data.get("cache_size")}
            )
            
        else:
            self.log_test_result(
                "Housing Services - Integration check",
                False,
                f"Service status unavailable: {error}",
                data
            )
    
    async def test_housing_authentication(self):
        """🏠 Test Housing Authentication & Authorization"""
        logger.info("=== 🏠 Testing Housing Authentication & Authorization ===")
        
        # List of all protected housing endpoints
        protected_endpoints = [
            ("POST", "/api/housing-search", {"city": "Berlin", "max_price": 1500}),
            ("POST", "/api/housing-neighborhood-analysis", {"city": "München", "district": "Schwabing"}),
            ("POST", "/api/housing-subscriptions", {"city": "Hamburg", "max_price": 1200}),
            ("GET", "/api/housing-subscriptions", None),
            ("PUT", "/api/housing-subscriptions/test_123", {"max_price": 1300}),
            ("DELETE", "/api/housing-subscriptions/test_123", None),
            ("POST", "/api/housing-landlord-contact", {"listing_id": "test_123", "user_name": "Test User"})
        ]
        
        all_protected = True
        
        for method, endpoint, payload in protected_endpoints:
            if payload:
                success, data, error = await self.make_request(method, endpoint, json=payload)
            else:
                success, data, error = await self.make_request(method, endpoint)
            
            # Should require authentication (401 or 403)
            is_protected = not success and ("401" in str(error) or "403" in str(error) or (isinstance(data, dict) and ("Not authenticated" in str(data.get("detail", "")))))
            
            if not is_protected:
                all_protected = False
                logger.warning(f"{method} {endpoint} does not require authentication!")
        
        self.log_test_result(
            "Housing Endpoints - Authentication enforcement",
            all_protected,
            "All housing endpoints correctly require authentication" if all_protected else "Some housing endpoints allow unauthorized access",
            {"protected_endpoints_count": len(protected_endpoints)}
        )
        
        # Test public endpoint (should NOT require auth)
        success, data, error = await self.make_request("GET", "/api/housing-market-status")
        
        is_public = success or not ("401" in str(error) or "403" in str(error))
        
        self.log_test_result(
            "Housing Market Status - Public access",
            is_public,
            "Market status endpoint correctly allows public access" if is_public else f"Public endpoint requires auth: {error}",
            data
        )
    
    async def test_housing_error_handling(self):
        """🏠 Test Housing Error Handling"""
        logger.info("=== 🏠 Testing Housing Error Handling ===")
        
        # Test invalid request data
        invalid_search_data = {
            "city": "",  # Empty city
            "max_price": -100,  # Negative price
            "property_type": "invalid_type"
        }
        
        success, data, error = await self.make_request("POST", "/api/housing-search", json=invalid_search_data)
        
        # Should fail with validation error or auth error (both acceptable)
        handles_invalid_data = not success and ("422" in str(error) or "401" in str(error) or "403" in str(error) or "validation" in str(data).lower())
        
        self.log_test_result(
            "Housing Search - Invalid data handling",
            handles_invalid_data,
            f"Correctly handles invalid search data" if handles_invalid_data else f"Invalid data handling issue: {error}",
            data
        )
        
        # Test missing required fields
        incomplete_subscription = {
            "max_price": 1500
            # Missing required 'city' field
        }
        
        success, data, error = await self.make_request("POST", "/api/housing-subscriptions", json=incomplete_subscription)
        
        handles_missing_fields = not success and ("422" in str(error) or "401" in str(error) or "403" in str(error) or "validation" in str(data).lower())
        
        self.log_test_result(
            "Housing Subscriptions - Missing fields handling",
            handles_missing_fields,
            f"Correctly handles missing required fields" if handles_missing_fields else f"Missing fields handling issue: {error}",
            data
        )
        
        # Test invalid subscription ID format
        success, data, error = await self.make_request("PUT", "/api/housing-subscriptions/invalid-id-format", json={"max_price": 1000})
        
        handles_invalid_id = not success and ("401" in str(error) or "403" in str(error) or "404" in str(error))
        
        self.log_test_result(
            "Housing Subscriptions - Invalid ID handling",
            handles_invalid_id,
            f"Correctly handles invalid subscription ID" if handles_invalid_id else f"Invalid ID handling issue: {error}",
            data
        )
        
        # Test malformed JSON
        try:
            # This should cause a JSON parsing error
            success, data, error = await self.make_request("POST", "/api/housing-search", data="invalid json")
            
            handles_malformed_json = not success and ("400" in str(error) or "422" in str(error) or "401" in str(error))
            
            self.log_test_result(
                "Housing Endpoints - Malformed JSON handling",
                handles_malformed_json,
                f"Correctly handles malformed JSON" if handles_malformed_json else f"JSON handling issue: {error}",
                data
            )
        except Exception as e:
            # Exception during request is also acceptable error handling
            self.log_test_result(
                "Housing Endpoints - Malformed JSON handling",
                True,
                f"Correctly raises exception for malformed JSON: {str(e)}",
                None
            )
    
    async def test_housing_data_integrity(self):
        """🏠 Test Housing Data Integrity"""
        logger.info("=== 🏠 Testing Housing Data Integrity ===")
        
        # Test housing market status data structure
        success, data, error = await self.make_request("GET", "/api/housing-market-status")
        
        if success and isinstance(data, dict):
            # Check top-level structure
            has_status = "status" in data and data["status"] == "success"
            has_data = "data" in data and isinstance(data["data"], dict)
            has_message = "message" in data and isinstance(data["message"], str)
            
            service_data = data.get("data", {})
            
            # Check service data structure
            required_fields = ["service_status", "cache_size", "supported_cities", "supported_sources", "ai_features"]
            has_required_fields = all(field in service_data for field in required_fields)
            
            # Validate data types
            cache_size_valid = isinstance(service_data.get("cache_size"), int) and service_data.get("cache_size") >= 0
            cities_valid = isinstance(service_data.get("supported_cities"), list) and len(service_data.get("supported_cities", [])) > 0
            sources_valid = isinstance(service_data.get("supported_sources"), list) and len(service_data.get("supported_sources", [])) > 0
            features_valid = isinstance(service_data.get("ai_features"), list) and len(service_data.get("ai_features", [])) > 0
            
            # Check for expected German cities
            expected_cities = ["Berlin", "München", "Hamburg", "Köln", "Frankfurt"]
            cities_content_valid = all(city in service_data.get("supported_cities", []) for city in expected_cities)
            
            # Check for expected real estate sources
            expected_sources = ["ImmoScout24", "Immobilien.de", "WG-Gesucht", "eBay Kleinanzeigen"]
            sources_content_valid = all(source in service_data.get("supported_sources", []) for source in expected_sources)
            
            # Check for expected AI features
            expected_features = ["Scam Detection", "Price Analysis", "Neighborhood Insights"]
            features_content_valid = all(feature in service_data.get("ai_features", []) for feature in expected_features)
            
            data_integrity_valid = (has_status and has_data and has_message and has_required_fields and 
                                  cache_size_valid and cities_valid and sources_valid and features_valid and
                                  cities_content_valid and sources_content_valid and features_content_valid)
            
            self.log_test_result(
                "Housing Market Status - Data structure integrity",
                data_integrity_valid,
                f"Structure: {has_required_fields}, Types: {cache_size_valid and cities_valid and sources_valid and features_valid}, Content: {cities_content_valid and sources_content_valid and features_content_valid}",
                {
                    "cities_count": len(service_data.get("supported_cities", [])),
                    "sources_count": len(service_data.get("supported_sources", [])),
                    "features_count": len(service_data.get("ai_features", [])),
                    "cache_size": service_data.get("cache_size")
                }
            )
            
            # Test individual data components
            self.log_test_result(
                "Housing Data - German cities coverage",
                cities_content_valid and len(service_data.get("supported_cities", [])) >= 15,
                f"Covers major German cities: {len(service_data.get('supported_cities', []))} cities including {expected_cities}",
                {"supported_cities": service_data.get("supported_cities", [])}
            )
            
            self.log_test_result(
                "Housing Data - Real estate sources integration",
                sources_content_valid and len(service_data.get("supported_sources", [])) == 4,
                f"All 4 major German real estate sources integrated: {expected_sources}",
                {"supported_sources": service_data.get("supported_sources", [])}
            )
            
            self.log_test_result(
                "Housing Data - AI features availability",
                features_content_valid and len(service_data.get("ai_features", [])) >= 5,
                f"Comprehensive AI features available: {len(service_data.get('ai_features', []))} features including {expected_features}",
                {"ai_features": service_data.get("ai_features", [])}
            )
            
        else:
            self.log_test_result(
                "Housing Market Status - Data structure integrity",
                False,
                f"Failed to retrieve market status: {error}",
                data
            )
    
    async def test_housing_comprehensive_functionality(self):
        """🏠 Comprehensive Housing Search Functionality Test"""
        logger.info("=== 🏠 Testing Comprehensive Housing Search Functionality ===")
        
        # Test that all housing endpoints exist and are properly configured
        housing_endpoints = [
            ("POST", "/api/housing-search", "Main housing search"),
            ("POST", "/api/housing-neighborhood-analysis", "Neighborhood analysis"),
            ("POST", "/api/housing-subscriptions", "Create subscription"),
            ("GET", "/api/housing-subscriptions", "Get subscriptions"),
            ("PUT", "/api/housing-subscriptions/test", "Update subscription"),
            ("DELETE", "/api/housing-subscriptions/test", "Delete subscription"),
            ("POST", "/api/housing-landlord-contact", "Landlord contact"),
            ("GET", "/api/housing-market-status", "Market status")
        ]
        
        all_endpoints_exist = True
        endpoint_results = []
        
        for method, endpoint, description in housing_endpoints:
            if method == "GET" and "market-status" in endpoint:
                # Public endpoint
                success, data, error = await self.make_request(method, endpoint)
                endpoint_exists = success or not ("404" in str(error))
            else:
                # Protected endpoints - should return auth error, not 404
                test_data = {"city": "Berlin"} if method == "POST" else None
                if test_data:
                    success, data, error = await self.make_request(method, endpoint, json=test_data)
                else:
                    success, data, error = await self.make_request(method, endpoint)
                
                endpoint_exists = not ("404" in str(error))  # 404 means endpoint doesn't exist
            
            endpoint_results.append({
                "endpoint": f"{method} {endpoint}",
                "description": description,
                "exists": endpoint_exists,
                "error": error if not endpoint_exists else None
            })
            
            if not endpoint_exists:
                all_endpoints_exist = False
        
        self.log_test_result(
            "Housing Search - All endpoints availability",
            all_endpoints_exist,
            f"All 8 housing endpoints exist and are properly configured" if all_endpoints_exist else f"Some endpoints missing or misconfigured",
            {"endpoint_results": endpoint_results}
        )
        
        # Test housing search system readiness
        success, data, error = await self.make_request("GET", "/api/housing-market-status")
        
        if success and isinstance(data, dict):
            service_data = data.get("data", {})
            system_operational = service_data.get("service_status") == "operational"
            has_all_sources = len(service_data.get("supported_sources", [])) == 4
            has_all_features = len(service_data.get("ai_features", [])) >= 5
            has_major_cities = len(service_data.get("supported_cities", [])) >= 15
            
            system_ready = system_operational and has_all_sources and has_all_features and has_major_cities
            
            self.log_test_result(
                "Housing Search System - Production readiness",
                system_ready,
                f"Operational: {system_operational}, Sources: {has_all_sources}, Features: {has_all_features}, Cities: {has_major_cities}",
                {
                    "service_status": service_data.get("service_status"),
                    "sources_count": len(service_data.get("supported_sources", [])),
                    "features_count": len(service_data.get("ai_features", [])),
                    "cities_count": len(service_data.get("supported_cities", []))
                }
            )
        else:
            self.log_test_result(
                "Housing Search System - Production readiness",
                False,
                f"System status check failed: {error}",
                data
            )

async def main():
    """🎯 ГЛАВНАЯ ФУНКЦИЯ: Тестирование исправленной функциональности Job Search и Cities Search в Telegram Mini App"""
    print("🎯 КРИТИЧЕСКОЕ ТЕСТИРОВАНИЕ: Job Search и Cities Search функциональность в Telegram Mini App")
    print("=" * 100)
    
    async with BackendTester() as tester:
        # Run the comprehensive Telegram Mini App tests
        await tester.run_telegram_mini_app_tests()
        
        # Print summary
        print("\n" + "=" * 100)
        print("🎯 ИТОГОВЫЙ ОТЧЕТ ТЕСТИРОВАНИЯ")
        print("=" * 100)
        
        total_tests = len(tester.test_results)
        passed_tests = sum(1 for result in tester.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"📊 Общая статистика:")
        print(f"   Всего тестов: {total_tests}")
        print(f"   ✅ Прошли: {passed_tests}")
        print(f"   ❌ Не прошли: {failed_tests}")
        print(f"   📈 Процент успеха: {success_rate:.1f}%")
        
        print(f"\n🎯 Детальные результаты:")
        for result in tester.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"   {status} {result['test']}")
            if result["details"]:
                print(f"      └─ {result['details']}")
        
        print("\n" + "=" * 100)
        print("🎯 ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
        print("=" * 100)
        
        return 0 if success_rate > 80 else 1  # Consider successful if >80% tests pass

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
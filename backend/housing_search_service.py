"""
🏠 HOUSING SEARCH SERVICE
Основной сервис поиска жилья с кешированием и интеграцией AI анализа
"""

import logging
from typing import Dict, Any, List, Optional
import time
import json
import hashlib
from datetime import datetime, timedelta
from housing_scraper_service import housing_scraper
from housing_ai_service import housing_ai_service
from database import db

logger = logging.getLogger(__name__)

class HousingSearchService:
    def __init__(self):
        # In-memory cache for search results
        self.search_cache = {}
        self.cache_duration = 1800  # 30 minutes
        
        # Market data cache
        self.market_cache = {}
        self.market_cache_duration = 3600  # 1 hour
        
    def _get_cache_key(self, city: str, max_price: int = None, property_type: str = "wohnung", radius: int = None) -> str:
        """Generate cache key for search parameters"""
        params = f"{city.lower()}_{max_price}_{property_type}_{radius}"
        return hashlib.md5(params.encode()).hexdigest()
    
    def _is_cache_valid(self, cache_entry: Dict, duration: int) -> bool:
        """Check if cache entry is still valid"""
        if not cache_entry or 'timestamp' not in cache_entry:
            return False
        return time.time() - cache_entry['timestamp'] < duration
    
    def search_housing(self, 
                      city: str, 
                      max_price: int = None, 
                      property_type: str = "wohnung",
                      radius: int = None,
                      user_providers: Dict = None) -> Dict[str, Any]:
        """
        Main housing search function with caching and AI analysis
        """
        try:
            logger.info(f"🔍 Housing search request: {city}, max_price: {max_price}, type: {property_type}")
            
            # Check cache first
            cache_key = self._get_cache_key(city, max_price, property_type, radius)
            
            if cache_key in self.search_cache and self._is_cache_valid(self.search_cache[cache_key], self.cache_duration):
                logger.info("📦 Returning cached results")
                cached_result = self.search_cache[cache_key]
                cached_result['from_cache'] = True
                return cached_result
            
            # Perform fresh search
            start_time = time.time()
            listings = housing_scraper.search_all_sources(city, max_price, property_type)
            search_time = time.time() - start_time
            
            if not listings:
                return {
                    'status': 'no_results',
                    'listings': [],
                    'total_found': 0,
                    'search_time': search_time,
                    'message': f'Не найдено объявлений в городе {city} с указанными параметрами',
                    'from_cache': False
                }
            
            # Get market context for AI analysis
            market_context = self._get_market_context(city, listings)
            
            # Add AI analysis to each listing
            enhanced_listings = []
            for listing in listings[:20]:  # Limit to 20 for performance
                try:
                    # Scam detection
                    scam_analysis = housing_ai_service.analyze_listing_for_scam(listing, market_context)
                    
                    # Cost calculation
                    cost_analysis = housing_ai_service.calculate_total_living_costs(listing, city)
                    
                    # Enhanced listing
                    enhanced_listing = {
                        **listing,
                        'ai_analysis': {
                            'scam_detection': scam_analysis,
                            'cost_calculation': cost_analysis,
                        },
                        'enhanced_at': time.time()
                    }
                    
                    enhanced_listings.append(enhanced_listing)
                    
                except Exception as e:
                    logger.error(f"Error enhancing listing: {str(e)}")
                    # Add listing without AI analysis
                    enhanced_listings.append(listing)
            
            # Prepare result
            result = {
                'status': 'success',
                'listings': enhanced_listings,
                'total_found': len(enhanced_listings),
                'search_time': search_time,
                'search_params': {
                    'city': city,
                    'max_price': max_price,
                    'property_type': property_type,
                    'radius': radius
                },
                'market_context': market_context,
                'from_cache': False,
                'cached_until': time.time() + self.cache_duration
            }
            
            # Cache the result
            self.search_cache[cache_key] = {
                **result,
                'timestamp': time.time()
            }
            
            logger.info(f"✅ Search completed: {len(enhanced_listings)} enhanced listings in {search_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Housing search failed: {str(e)}")
            return {
                'status': 'error',
                'listings': [],
                'total_found': 0,
                'error': str(e),
                'message': 'Произошла ошибка при поиске жилья. Попробуйте позже.',
                'from_cache': False
            }
    
    def _get_market_context(self, city: str, listings: List[Dict]) -> Dict[str, Any]:
        """Calculate market context from current listings"""
        try:
            if not listings:
                return {}
            
            prices = [listing.get('price') for listing in listings if listing.get('price')]
            areas = [listing.get('area') for listing in listings if listing.get('area')]
            
            if not prices:
                return {'city': city}
            
            # Calculate statistics
            avg_price = sum(prices) / len(prices)
            min_price = min(prices)
            max_price = max(prices)
            
            price_per_sqm_list = []
            for listing in listings:
                price = listing.get('price')
                area = listing.get('area')
                if price and area and area > 0:
                    price_per_sqm_list.append(price / area)
            
            avg_price_per_sqm = sum(price_per_sqm_list) / len(price_per_sqm_list) if price_per_sqm_list else None
            
            # Source distribution
            sources = {}
            for listing in listings:
                source = listing.get('source', 'Unknown')
                sources[source] = sources.get(source, 0) + 1
            
            return {
                'city': city,
                'total_listings': len(listings),
                'price_stats': {
                    'average': round(avg_price, 2),
                    'min': min_price,
                    'max': max_price,
                    'avg_per_sqm': round(avg_price_per_sqm, 2) if avg_price_per_sqm else None
                },
                'sources': sources,
                'analysis_time': time.time()
            }
            
        except Exception as e:
            logger.error(f"Market context calculation failed: {str(e)}")
            return {'city': city, 'error': 'Market analysis unavailable'}
    
    def get_neighborhood_analysis(self, city: str, district: str = None, user_providers: Dict = None) -> Dict[str, Any]:
        """Get AI-powered neighborhood analysis with caching"""
        cache_key = f"neighborhood_{city}_{district}".lower()
        
        # Check cache
        if cache_key in self.market_cache and self._is_cache_valid(self.market_cache[cache_key], self.market_cache_duration):
            cached_result = self.market_cache[cache_key]
            cached_result['from_cache'] = True
            return cached_result
        
        # Get fresh analysis
        analysis = housing_ai_service.analyze_neighborhood(city, district, user_providers)
        analysis['from_cache'] = False
        
        # Cache result
        self.market_cache[cache_key] = {
            **analysis,
            'timestamp': time.time()
        }
        
        return analysis
    
    def generate_landlord_contact(self, listing_id: str, user_info: Dict, user_providers: Dict = None) -> Dict[str, Any]:
        """Generate landlord contact message"""
        try:
            # In a real app, you'd fetch listing by ID from cache or database
            # For now, return a generic template
            
            return housing_ai_service.generate_landlord_message(
                listing={'title': 'Wohnung', 'price': 'N/A'},
                user_info=user_info,
                user_providers=user_providers
            )
            
        except Exception as e:
            logger.error(f"Landlord contact generation failed: {str(e)}")
            return {
                'status': 'error',
                'message': 'Не удалось создать сообщение арендодателю',
                'error': str(e)
            }
    
    def save_user_search_subscription(self, user_id: str, search_params: Dict) -> Dict[str, Any]:
        """Save user search subscription to database"""
        try:
            subscription_id = f"sub_{int(time.time())}_{user_id}"
            
            subscription_data = {
                'id': subscription_id,
                'user_id': user_id,
                'city': search_params.get('city'),
                'max_price': search_params.get('max_price'),
                'property_type': search_params.get('property_type', 'wohnung'),
                'radius': search_params.get('radius'),
                'active': True,
                'created_at': datetime.utcnow().isoformat(),
                'last_checked': datetime.utcnow().isoformat(),
                'notification_count': 0
            }
            
            # Save to database
            db.create_housing_subscription(subscription_data)
            
            logger.info(f"✅ Created housing subscription {subscription_id} for user {user_id}")
            
            return {
                'status': 'success',
                'subscription_id': subscription_id,
                'message': f'Подписка на поиск в городе {search_params.get("city")} создана',
                'subscription': subscription_data
            }
            
        except Exception as e:
            logger.error(f"Failed to save subscription: {str(e)}")
            return {
                'status': 'error',
                'message': 'Не удалось создать подписку',
                'error': str(e)
            }
    
    def get_user_subscriptions(self, user_id: str) -> List[Dict]:
        """Get user's active subscriptions"""
        try:
            subscriptions = db.get_user_housing_subscriptions(user_id)
            return subscriptions
        except Exception as e:
            logger.error(f"Failed to get subscriptions: {str(e)}")
            return []
    
    def update_subscription(self, subscription_id: str, user_id: str, updates: Dict) -> Dict[str, Any]:
        """Update subscription settings"""
        try:
            success = db.update_housing_subscription(subscription_id, user_id, updates)
            
            if success:
                return {
                    'status': 'success',
                    'message': 'Подписка обновлена'
                }
            else:
                return {
                    'status': 'error',
                    'message': 'Подписка не найдена'
                }
                
        except Exception as e:
            logger.error(f"Failed to update subscription: {str(e)}")
            return {
                'status': 'error',
                'message': 'Ошибка обновления подписки'
            }
    
    def delete_subscription(self, subscription_id: str, user_id: str) -> Dict[str, Any]:
        """Delete subscription"""
        try:
            success = db.delete_housing_subscription(subscription_id, user_id)
            
            if success:
                return {
                    'status': 'success',
                    'message': 'Подписка удалена'
                }
            else:
                return {
                    'status': 'error',
                    'message': 'Подписка не найдена'
                }
                
        except Exception as e:
            logger.error(f"Failed to delete subscription: {str(e)}")
            return {
                'status': 'error',
                'message': 'Ошибка удаления подписки'
            }
    
    def clear_cache(self):
        """Clear all caches"""
        self.search_cache.clear()
        self.market_cache.clear()
        logger.info("🧹 Housing search cache cleared")

# Initialize global service
housing_search_service = HousingSearchService()
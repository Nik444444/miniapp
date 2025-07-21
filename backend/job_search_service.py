"""
🔍 Job Search Service - Integration with Arbeitnow API and AI-powered features
Интеграция с API вакансий и ИИ-функции для поиска работы
"""

import aiohttp
import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import re
from database import db

logger = logging.getLogger(__name__)

class JobSearchService:
    def __init__(self):
        self.base_url = "https://www.arbeitnow.com/api/job-board-api"
        self.session = None
        
        # Language level mappings for German proficiency
        self.language_levels = {
            'A1': {'min_score': 0, 'max_score': 20, 'description': 'Beginner'},
            'A2': {'min_score': 21, 'max_score': 35, 'description': 'Elementary'},
            'B1': {'min_score': 36, 'max_score': 50, 'description': 'Intermediate'},
            'B2': {'min_score': 51, 'max_score': 65, 'description': 'Upper-Intermediate'},
            'C1': {'min_score': 66, 'max_score': 80, 'description': 'Advanced'},
            'C2': {'min_score': 81, 'max_score': 100, 'description': 'Proficiency'}
        }
        
        # Job categories for better organization
        self.job_categories = {
            'tech': ['software', 'developer', 'engineer', 'programmer', 'data', 'it', 'tech'],
            'marketing': ['marketing', 'seo', 'content', 'social media', 'advertising'],
            'finance': ['finance', 'accounting', 'controller', 'analyst', 'banking'],
            'sales': ['sales', 'account manager', 'business development', 'customer'],
            'design': ['design', 'ui', 'ux', 'graphic', 'creative'],
            'management': ['manager', 'director', 'lead', 'head', 'chief'],
            'healthcare': ['medical', 'nurse', 'doctor', 'healthcare', 'pharma'],
            'education': ['teacher', 'education', 'training', 'instructor'],
            'other': []
        }

    async def _get_session(self):
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session

    async def close_session(self):
        """Close aiohttp session"""
        if self.session and not self.session.closed:
            await self.session.close()

    async def search_jobs(self, 
                         search_query: str = None,
                         location: str = None,
                         remote: bool = None,
                         visa_sponsorship: bool = None,
                         language_level: str = None,
                         category: str = None,
                         limit: int = 50) -> Dict[str, Any]:
        """
        🔍 Search jobs with filters
        """
        try:
            session = await self._get_session()
            
            # Build query parameters
            params = {}
            if visa_sponsorship is not None:
                params['visa_sponsorship'] = str(visa_sponsorship).lower()
            
            logger.info(f"Searching jobs with params: {params}")
            
            async with session.get(self.base_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    jobs = data.get('data', [])
                    
                    logger.info(f"Found {len(jobs)} jobs from API")
                    
                    # Apply filters
                    filtered_jobs = self._filter_jobs(
                        jobs=jobs,
                        search_query=search_query,
                        location=location,
                        remote=remote,
                        language_level=language_level,
                        category=category
                    )
                    
                    # Limit results
                    filtered_jobs = filtered_jobs[:limit]
                    
                    # Categorize jobs
                    categorized_jobs = self._categorize_jobs(filtered_jobs)
                    
                    logger.info(f"Returning {len(filtered_jobs)} filtered jobs")
                    
                    return {
                        'status': 'success',
                        'total_found': len(filtered_jobs),
                        'total_available': len(jobs),
                        'jobs': filtered_jobs,
                        'categories': categorized_jobs['categories'],
                        'filters_applied': {
                            'search_query': search_query,
                            'location': location,
                            'remote': remote,
                            'visa_sponsorship': visa_sponsorship,
                            'language_level': language_level,
                            'category': category
                        },
                        'language_levels': self.language_levels,
                        'pagination': data.get('links', {}),
                        'ai_recommendations': self._generate_search_recommendations(search_query, filtered_jobs)
                    }
                else:
                    logger.error(f"API request failed with status: {response.status}")
                    return await self._get_fallback_jobs()
                    
        except Exception as e:
            logger.error(f"Job search failed: {e}")
            return await self._get_fallback_jobs()

    def _filter_jobs(self, 
                     jobs: List[Dict],
                     search_query: str = None,
                     location: str = None,
                     remote: bool = None,
                     language_level: str = None,
                     category: str = None) -> List[Dict]:
        """Apply filters to job listings"""
        
        filtered = jobs.copy()
        
        # Search query filter
        if search_query:
            query_lower = search_query.lower()
            filtered = [job for job in filtered if 
                       query_lower in job.get('title', '').lower() or
                       query_lower in job.get('description', '').lower() or
                       query_lower in job.get('company_name', '').lower()]
        
        # Location filter
        if location:
            location_lower = location.lower()
            filtered = [job for job in filtered if 
                       location_lower in job.get('location', '').lower()]
        
        # Remote filter
        if remote is not None:
            filtered = [job for job in filtered if job.get('remote', False) == remote]
        
        # Language level filter (AI-based estimation)
        if language_level and language_level in self.language_levels:
            filtered = [job for job in filtered if 
                       self._estimate_language_requirement(job) <= self.language_levels[language_level]['max_score']]
        
        # Category filter
        if category and category in self.job_categories:
            category_keywords = self.job_categories[category]
            filtered = [job for job in filtered if 
                       any(keyword in job.get('title', '').lower() for keyword in category_keywords)]
        
        return filtered

    def _estimate_language_requirement(self, job: Dict) -> int:
        """
        🤖 AI-based estimation of German language requirement (0-100)
        """
        title = job.get('title', '').lower()
        description = job.get('description', '').lower()
        location = job.get('location', '').lower()
        
        score = 30  # Base score
        
        # Keywords indicating higher German requirement
        high_german_keywords = [
            'kundenkontakt', 'kundenbetreuung', 'vertrieb', 'sales', 'beratung',
            'kommunikation', 'präsentation', 'führung', 'management', 'teamleitung',
            'öffentlicher dienst', 'behörde', 'verwaltung', 'sozial'
        ]
        
        # Keywords indicating lower German requirement  
        low_german_keywords = [
            'english', 'international', 'startup', 'tech', 'developer',
            'programmer', 'data scientist', 'remote', 'freelance'
        ]
        
        # Check for high German requirement indicators
        for keyword in high_german_keywords:
            if keyword in title or keyword in description:
                score += 15
        
        # Check for low German requirement indicators
        for keyword in low_german_keywords:
            if keyword in title or keyword in description:
                score -= 10
        
        # Location factor
        if 'berlin' in location or 'munich' in location or 'hamburg' in location:
            score -= 5  # International cities, potentially lower requirement
        
        # Remote jobs typically have lower language requirements
        if job.get('remote', False):
            score -= 10
        
        return max(10, min(90, score))  # Keep score between 10-90

    def _categorize_jobs(self, jobs: List[Dict]) -> Dict[str, Any]:
        """Categorize jobs by type"""
        categorized = {category: [] for category in self.job_categories.keys()}
        
        for job in jobs:
            title = job.get('title', '').lower()
            assigned = False
            
            for category, keywords in self.job_categories.items():
                if category != 'other' and any(keyword in title for keyword in keywords):
                    categorized[category].append(job)
                    assigned = True
                    break
            
            if not assigned:
                categorized['other'].append(job)
        
        # Generate category statistics
        categories_stats = {}
        for category, category_jobs in categorized.items():
            if category_jobs:
                categories_stats[category] = {
                    'count': len(category_jobs),
                    'percentage': round((len(category_jobs) / len(jobs)) * 100, 1),
                    'top_companies': list(set([job.get('company_name', 'Unknown') 
                                             for job in category_jobs[:5]]))
                }
        
        return {
            'categories': categorized,
            'stats': categories_stats
        }

    def _generate_search_recommendations(self, search_query: str, jobs: List[Dict]) -> List[str]:
        """Generate AI-powered search recommendations"""
        recommendations = []
        
        if not jobs:
            recommendations.append("Попробуйте расширить поисковый запрос или убрать фильтры")
            recommendations.append("Рассмотрите удаленную работу - добавьте фильтр 'Remote'")
        
        if search_query:
            # Suggest related searches
            if 'developer' in search_query.lower():
                recommendations.append("Также ищите: Software Engineer, Frontend, Backend")
            elif 'marketing' in search_query.lower():
                recommendations.append("Также ищите: Digital Marketing, SEO, Content Marketing")
        
        # Location-based recommendations
        locations = [job.get('location', '') for job in jobs]
        common_locations = {}
        for location in locations:
            if location:
                common_locations[location] = common_locations.get(location, 0) + 1
        
        if common_locations:
            top_location = max(common_locations.keys(), key=lambda k: common_locations[k])
            recommendations.append(f"Много вакансий найдено в: {top_location}")
        
        return recommendations[:3]  # Limit to 3 recommendations

    async def _get_fallback_jobs(self) -> Dict[str, Any]:
        """Return demo jobs when API is unavailable"""
        demo_jobs = [
            {
                'id': 'demo_1',
                'title': 'Senior Software Developer',
                'company_name': 'TechStart GmbH',
                'location': 'Berlin, Germany',
                'description': 'We are looking for a Senior Software Developer with experience in Python and React.',
                'remote': True,
                'visa_sponsorship': True,
                'published_at': '2024-12-20T10:00:00Z',
                'job_types': ['Full-time'],
                'url': 'https://example.com/job/demo_1',
                'estimated_german_level': 'B1'
            },
            {
                'id': 'demo_2', 
                'title': 'Marketing Manager',
                'company_name': 'Digital Solutions AG',
                'location': 'Munich, Germany',
                'description': 'Marketing Manager position for digital campaigns and customer acquisition.',
                'remote': False,
                'visa_sponsorship': False,
                'published_at': '2024-12-20T09:30:00Z',
                'job_types': ['Full-time'],
                'url': 'https://example.com/job/demo_2',
                'estimated_german_level': 'C1'
            },
            {
                'id': 'demo_3',
                'title': 'Data Scientist',
                'company_name': 'AI Innovations',
                'location': 'Hamburg, Germany', 
                'description': 'Data Scientist role focusing on machine learning and analytics.',
                'remote': True,
                'visa_sponsorship': True,
                'published_at': '2024-12-20T08:15:00Z',
                'job_types': ['Full-time'],
                'url': 'https://example.com/job/demo_3',
                'estimated_german_level': 'B2'
            }
        ]
        
        return {
            'status': 'demo',
            'total_found': len(demo_jobs),
            'total_available': len(demo_jobs),
            'jobs': demo_jobs,
            'categories': self._categorize_jobs(demo_jobs)['categories'],
            'language_levels': self.language_levels,
            'note': 'Demo mode - showing sample jobs',
            'ai_recommendations': ['Попробуйте позже для реальных данных', 'Настройте API для полного доступа']
        }

    async def save_job_subscription(self, 
                                  user_id: str,
                                  search_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        📬 Save user job subscription for notifications
        """
        try:
            subscription_data = {
                'id': f"job_sub_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'user_id': user_id,
                'search_query': search_params.get('search_query'),
                'location': search_params.get('location'),
                'remote': search_params.get('remote'),
                'visa_sponsorship': search_params.get('visa_sponsorship'),
                'language_level': search_params.get('language_level'),
                'category': search_params.get('category'),
                'active': True,
                'created_at': datetime.now().isoformat(),
                'last_check': None,
                'notification_count': 0
            }
            
            # Save to database
            await db.save_job_subscription(subscription_data)
            
            logger.info(f"Job subscription created for user {user_id}")
            
            return {
                'status': 'success',
                'subscription_id': subscription_data['id'],
                'message': 'Подписка на вакансии создана! Вы будете получать уведомления о новых подходящих вакансиях.'
            }
            
        except Exception as e:
            logger.error(f"Failed to save job subscription: {e}")
            return {
                'status': 'error',
                'message': f'Ошибка создания подписки: {str(e)}'
            }

    async def get_user_subscriptions(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user's job subscriptions"""
        try:
            subscriptions = await db.get_user_job_subscriptions(user_id)
            return subscriptions or []
        except Exception as e:
            logger.error(f"Failed to get subscriptions: {e}")
            return []

    async def update_subscription(self, 
                                subscription_id: str,
                                user_id: str,
                                updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update job subscription"""
        try:
            success = await db.update_job_subscription(subscription_id, user_id, updates)
            if success:
                return {'status': 'success', 'message': 'Подписка обновлена'}
            else:
                return {'status': 'error', 'message': 'Подписка не найдена'}
        except Exception as e:
            logger.error(f"Failed to update subscription: {e}")
            return {'status': 'error', 'message': str(e)}

    async def delete_subscription(self, subscription_id: str, user_id: str) -> Dict[str, Any]:
        """Delete job subscription"""
        try:
            success = await db.delete_job_subscription(subscription_id, user_id)
            if success:
                return {'status': 'success', 'message': 'Подписка удалена'}
            else:
                return {'status': 'error', 'message': 'Подписка не найдена'}
        except Exception as e:
            logger.error(f"Failed to delete subscription: {e}")
            return {'status': 'error', 'message': str(e)}

    def estimate_salary_range(self, job: Dict[str, Any]) -> Dict[str, Any]:
        """
        💰 Estimate salary range based on job details
        """
        title = job.get('title', '').lower()
        location = job.get('location', '').lower()
        
        # Base salary ranges by role (EUR per year)
        salary_ranges = {
            'junior developer': {'min': 35000, 'max': 50000},
            'senior developer': {'min': 55000, 'max': 80000},
            'data scientist': {'min': 50000, 'max': 75000},
            'marketing manager': {'min': 45000, 'max': 65000},
            'product manager': {'min': 60000, 'max': 90000},
            'default': {'min': 40000, 'max': 60000}
        }
        
        # Find matching role
        estimated_range = salary_ranges['default']
        for role, range_data in salary_ranges.items():
            if role in title:
                estimated_range = range_data
                break
        
        # Location adjustments
        if 'munich' in location or 'münchen' in location:
            estimated_range = {k: int(v * 1.15) for k, v in estimated_range.items()}
        elif 'berlin' in location:
            estimated_range = {k: int(v * 1.05) for k, v in estimated_range.items()}
        elif 'frankfurt' in location:
            estimated_range = {k: int(v * 1.20) for k, v in estimated_range.items()}
        
        return {
            'min_salary': estimated_range['min'],
            'max_salary': estimated_range['max'],
            'currency': 'EUR',
            'period': 'yearly',
            'location_factor': location,
            'confidence': 'medium'
        }

# Create a global instance
job_search_service = JobSearchService()
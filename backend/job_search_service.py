"""
🔍 Job Search Service - Enhanced Integration with Bundesagentur für Arbeit API
Интеграция с официальным API Bundesagentur für Arbeit с геолокацией и радиусом поиска
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
        # Enhanced Bundesagentur für Arbeit API
        self.base_url = "https://rest.arbeitsagentur.de/jobboerse/jobsuche-service"
        self.api_key = "jobboerse-jobsuche"  # Official API key for Bundesagentur
        self.session = None
        
        # Enhanced language level mappings for German proficiency
        self.language_levels = {
            'A1': {'min_score': 0, 'max_score': 20, 'description': 'Anfänger - Basic everyday expressions'},
            'A2': {'min_score': 21, 'max_score': 35, 'description': 'Grundlagen - Simple routine matters'},
            'B1': {'min_score': 36, 'max_score': 50, 'description': 'Mittelstufe - Work and study topics'},
            'B2': {'min_score': 51, 'max_score': 65, 'description': 'Gehobene Mittelstufe - Complex texts'},
            'C1': {'min_score': 66, 'max_score': 80, 'description': 'Fortgeschritten - Professional fluency'},
            'C2': {'min_score': 81, 'max_score': 100, 'description': 'Muttersprachlich - Native-like proficiency'}
        }
        
        # Enhanced job categories with German terms
        self.job_categories = {
            'tech': ['software', 'developer', 'engineer', 'programmer', 'data', 'it', 'tech', 'informatik', 'entwickler'],
            'marketing': ['marketing', 'seo', 'content', 'social media', 'advertising', 'werbung'],
            'finance': ['finance', 'accounting', 'controller', 'analyst', 'banking', 'finanzen', 'buchhaltung'],
            'sales': ['sales', 'account manager', 'business development', 'customer', 'verkauf', 'vertrieb'],
            'design': ['design', 'ui', 'ux', 'graphic', 'creative', 'gestaltung'],
            'management': ['manager', 'director', 'lead', 'head', 'chief', 'leitung', 'führung'],
            'healthcare': ['medical', 'nurse', 'doctor', 'healthcare', 'pharma', 'krankenpflege', 'medizin', 'pflege'],
            'education': ['teacher', 'education', 'training', 'instructor', 'lehrer', 'bildung', 'erzieher'],
            'gastronomy': ['restaurant', 'hotel', 'gastronomy', 'koch', 'kellner', 'hotelfach', 'gastronomie'],
            'construction': ['construction', 'bau', 'handwerk', 'bauleiter', 'elektriker', 'installateur'],
            'logistics': ['logistics', 'transport', 'lagerwirtschaft', 'spedition', 'fahrzeugführung'],
            'retail': ['retail', 'einzelhandel', 'verkauf', 'handel', 'verkäufer'],
            'other': []
        }
        
        # Radius options for location search (in kilometers)
        self.radius_options = [5, 10, 25, 50, 100, 200]
        
        # Work time filters
        self.work_time_filters = {
            'vz': {'name': 'Vollzeit', 'description': 'Full-time positions'},
            'tz': {'name': 'Teilzeit', 'description': 'Part-time positions'},
            'ho': {'name': 'Homeoffice', 'description': 'Remote/home office work'},
            'mj': {'name': 'Minijob', 'description': 'Mini jobs (450€ basis)'},
            'snw': {'name': 'Schicht/Nacht/Wochenende', 'description': 'Shift, night or weekend work'}
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
                         radius: int = 50,
                         remote: bool = None,
                         visa_sponsorship: bool = None,
                         language_level: str = None,
                         category: str = None,
                         work_time: str = None,
                         published_since: int = None,
                         contract_type: str = None,
                         limit: int = 50,
                         page: int = 1,
                         user_coordinates: Dict[str, float] = None) -> Dict[str, Any]:
        """
        🔍 Enhanced job search using Bundesagentur für Arbeit API with geolocation
        
        Args:
            search_query: Job title or description search
            location: Location name (city, postal code)
            radius: Search radius in kilometers (5, 10, 25, 50, 100, 200)
            remote: Filter for remote jobs
            visa_sponsorship: Filter for visa sponsorship
            language_level: German language level (A1-C2)
            category: Job category filter
            work_time: Work time filter (vz, tz, ho, mj, snw)
            published_since: Days since publication (0-100)
            contract_type: Contract type (1=limited, 2=unlimited)
            limit: Number of results per page
            page: Page number
            user_coordinates: User's current coordinates {'lat': float, 'lon': float}
        """
        try:
            session = await self._get_session()
            
            # Build enhanced query parameters
            params = {
                'page': page,
                'size': min(limit, 100),  # API allows max 100 per page
            }
            
            # Enhanced parameter mapping
            if search_query:
                params['was'] = search_query
                
            if location:
                params['wo'] = location
                
            # Enhanced radius support
            if radius and radius in self.radius_options:
                params['umkreis'] = radius
            else:
                params['umkreis'] = 50  # Default radius
            
            # Work time filter
            if work_time and work_time in self.work_time_filters:
                params['arbeitszeit'] = work_time
                
            # Published since filter
            if published_since and 0 <= published_since <= 100:
                params['veroeffentlichtseit'] = published_since
                
            # Contract type filter
            if contract_type in ['1', '2']:
                params['befristung'] = contract_type
            
            # Headers for API request
            headers = {
                'X-API-Key': self.api_key,
                'Accept': 'application/json',
                'User-Agent': 'German-Telegram-Mini-App/2.0'
            }
            
            logger.info(f"🔍 Enhanced job search with params: {params}")
            
            url = f"{self.base_url}/pc/v4/jobs"
            logger.info(f"🌐 Making request to: {url}")
            
            async with session.get(url, params=params, headers=headers) as response:
                logger.info(f"🌐 API Response status: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    jobs_raw = data.get('stellenangebote', [])
                    
                    logger.info(f"✅ Found {len(jobs_raw)} jobs from enhanced API")
                    
                    # Convert and enhance job data
                    jobs = self._convert_enhanced_jobs(jobs_raw, user_coordinates)
                    logger.info(f"✅ Converted {len(jobs)} jobs successfully")
                    
                    # Apply enhanced filters
                    filtered_jobs = self._apply_enhanced_filters(
                        jobs=jobs,
                        remote=remote,
                        language_level=language_level,
                        category=category,
                        visa_sponsorship=visa_sponsorship
                    )
                    
                    # Categorize and analyze jobs
                    analysis = self._analyze_jobs(filtered_jobs)
                    
                    logger.info(f"📊 Returning {len(filtered_jobs)} filtered jobs with analysis")
                    
                    return {
                        'status': 'success',
                        'total_found': len(filtered_jobs),
                        'total_available': data.get('maxErgebnisse', 0),
                        'jobs': filtered_jobs,
                        'analysis': analysis,
                        'facets': self._process_facets(data.get('facetten', {})),
                        'search_metadata': {
                            'search_query': search_query,
                            'location': location,
                            'radius_km': radius,
                            'work_time': work_time,
                            'language_level': language_level,
                            'published_since_days': published_since,
                            'contract_type': contract_type,
                            'user_location': user_coordinates,
                            'search_center': data.get('woOutput', {})
                        },
                        'pagination': {
                            'page': page,
                            'size': params.get('size', 25),
                            'total': data.get('maxErgebnisse', 0),
                            'has_next': len(filtered_jobs) >= params.get('size', 25)
                        },
                        'recommendations': self._generate_enhanced_recommendations(
                            search_query, filtered_jobs, analysis
                        ),
                        'api_info': {
                            'source': 'bundesagentur.de',
                            'name': 'Bundesagentur für Arbeit - Official German Job Board',
                            'version': 'v4',
                            'enhanced_features': ['geolocation', 'radius_search', 'advanced_filters']
                        }
                    }
                else:
                    logger.error(f"❌ API request failed with status: {response.status}")
                    error_text = await response.text()
                    logger.error(f"❌ Error response: {error_text}")
                    logger.error(f"❌ Request URL was: {url}")
                    logger.error(f"❌ Request params were: {params}")
                    logger.error(f"❌ Request headers were: {headers}")
                    return await self._get_enhanced_fallback_jobs()
                    
        except Exception as e:
            logger.error(f"❌ Enhanced job search failed: {e}")
            import traceback
            logger.error(f"❌ Full traceback: {traceback.format_exc()}")
            return await self._get_enhanced_fallback_jobs()

    def _convert_enhanced_jobs(self, jobs_raw: List[Dict], user_coordinates: Dict[str, float] = None) -> List[Dict]:
        """Convert API format to enhanced format with distance calculations"""
        converted_jobs = []
        
        for job in jobs_raw:
            try:
                arbeitsort = job.get('arbeitsort', {})
                job_coords = arbeitsort.get('koordinaten', {})
                
                # Calculate distance if user coordinates provided
                distance_km = None
                if user_coordinates and job_coords.get('lat') and job_coords.get('lon'):
                    distance_km = self._calculate_distance(
                        user_coordinates['lat'], user_coordinates['lon'],
                        job_coords['lat'], job_coords['lon']
                    )
                
                converted_job = {
                    'id': job.get('refnr', ''),
                    'title': job.get('titel', ''),
                    'profession': job.get('beruf', ''),
                    'company_name': job.get('arbeitgeber', ''),
                    'location': {
                        'city': arbeitsort.get('ort', ''),
                        'state': arbeitsort.get('region', ''),
                        'country': arbeitsort.get('land', 'Deutschland'),
                        'postal_code': arbeitsort.get('plz', ''),
                        'street': arbeitsort.get('strasse'),
                        'coordinates': job_coords,
                        'distance_km': distance_km or arbeitsort.get('entfernung')
                    },
                    'location_string': f"{arbeitsort.get('ort', '')}, {arbeitsort.get('region', '')}",
                    'dates': {
                        'published': job.get('aktuelleVeroeffentlichungsdatum', ''),
                        'start_date': job.get('eintrittsdatum', ''),
                        'modified': job.get('modifikationsTimestamp', '')
                    },
                    'external_url': job.get('externeUrl'),
                    'reference_number': job.get('refnr', ''),
                    'employer_hash': job.get('kundennummerHash', ''),
                    'job_type': self._determine_job_type(job),
                    'work_time': self._extract_work_time(job),
                    'remote_possible': self._check_remote_possibility(job),
                    'visa_sponsorship': False,  # Usually not specified in German job ads
                    'tags': self._extract_job_tags(job),
                    'salary_info': self._extract_salary_info(job),
                    'description': self._build_job_description(job),
                    'requirements': self._extract_requirements(job),
                    'benefits': self._extract_benefits(job),
                    'source': 'bundesagentur.de',
                    'language_requirement': self._estimate_language_requirement_enhanced(job),
                    'created_at': datetime.now().isoformat(),
                    'match_score': self._calculate_match_score(job)
                }
                
                converted_jobs.append(converted_job)
                
            except Exception as e:
                logger.warning(f"⚠️ Failed to convert job {job.get('refnr', 'unknown')}: {e}")
                continue
        
        return converted_jobs

    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two coordinates in kilometers"""
        import math
        
        # Convert to radians
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)
        
        # Haversine formula
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        # Earth radius in kilometers
        earth_radius = 6371
        return round(earth_radius * c, 1)
    
    def _determine_job_type(self, job: Dict) -> str:
        """Determine job type from job data"""
        # Most German jobs default to full-time
        return 'full-time'
    
    def _extract_work_time(self, job: Dict) -> str:
        """Extract work time information"""
        # This would need to be determined from job description or other fields
        return 'full-time'
    
    def _check_remote_possibility(self, job: Dict) -> bool:
        """Check if remote work is possible"""
        title = job.get('titel', '').lower()
        profession = job.get('beruf', '').lower()
        
        remote_keywords = ['home', 'remote', 'telearbeit', 'homeoffice']
        return any(keyword in title or keyword in profession for keyword in remote_keywords)
    
    def _extract_job_tags(self, job: Dict) -> List[str]:
        """Extract relevant tags from job data"""
        tags = []
        
        if job.get('beruf'):
            tags.append(job['beruf'])
        
        # Add location tag
        arbeitsort = job.get('arbeitsort', {})
        if arbeitsort.get('ort'):
            tags.append(arbeitsort['ort'])
            
        return tags
    
    def _extract_salary_info(self, job: Dict) -> Dict[str, Any]:
        """Extract salary information if available"""
        return {
            'available': False,
            'range': None,
            'currency': 'EUR',
            'period': 'monthly',
            'note': 'Salary information not provided in job listing'
        }
    
    def _build_job_description(self, job: Dict) -> str:
        """Build comprehensive job description"""
        parts = []
        
        if job.get('titel'):
            parts.append(f"Position: {job['titel']}")
        
        if job.get('beruf'):
            parts.append(f"Profession: {job['beruf']}")
            
        if job.get('arbeitgeber'):
            parts.append(f"Employer: {job['arbeitgeber']}")
            
        arbeitsort = job.get('arbeitsort', {})
        if arbeitsort.get('ort'):
            location_str = arbeitsort['ort']
            if arbeitsort.get('region'):
                location_str += f", {arbeitsort['region']}"
            parts.append(f"Location: {location_str}")
            
        return "\n".join(parts)
    
    def _extract_requirements(self, job: Dict) -> List[str]:
        """Extract job requirements"""
        requirements = []
        
        # Basic German requirement for most jobs
        requirements.append("German language skills required")
        
        # Add profession-specific requirements
        profession = job.get('beruf', '').lower()
        if 'software' in profession or 'entwickler' in profession:
            requirements.append("Programming experience")
        elif 'pflege' in profession:
            requirements.append("Healthcare/nursing qualification")
        elif 'verkauf' in profession:
            requirements.append("Sales experience")
            
        return requirements
    
    def _extract_benefits(self, job: Dict) -> List[str]:
        """Extract job benefits"""
        benefits = []
        
        # Standard German employment benefits
        benefits.append("German employment protection laws")
        benefits.append("Statutory health insurance")
        
        # Location-based benefits
        arbeitsort = job.get('arbeitsort', {})
        if arbeitsort.get('ort') in ['Berlin', 'München', 'Hamburg']:
            benefits.append("Major city location")
            
        return benefits
    
    def _calculate_match_score(self, job: Dict) -> int:
        """Calculate job match score (0-100)"""
        score = 50  # Base score
        
        # Add points for complete information
        if job.get('externeUrl'):
            score += 10
        if job.get('arbeitgeber'):
            score += 10
        if job.get('arbeitsort', {}).get('koordinaten'):
            score += 10
        
        # Add points for location details
        arbeitsort = job.get('arbeitsort', {})
        if arbeitsort.get('ort'):
            score += 5
        if arbeitsort.get('plz'):
            score += 5
            
        # Add points for recent publication
        if job.get('aktuelleVeroeffentlichungsdatum'):
            score += 5
            
        return min(100, max(0, score))  # Keep score between 0-100
            
    async def get_user_location_info(self, coordinates: Dict[str, float]) -> Dict[str, Any]:
        """
        🌍 Get location information from coordinates
        """
        try:
            lat = coordinates.get('lat')
            lon = coordinates.get('lon')
            
            if not lat or not lon:
                return {'status': 'error', 'message': 'Invalid coordinates'}
            
            # Simple reverse geocoding (in production, you'd use a real service)
            # For now, we'll return the coordinates and suggest German cities
            german_cities = [
                {'name': 'Berlin', 'lat': 52.5200, 'lon': 13.4050, 'distance': self._calculate_distance(lat, lon, 52.5200, 13.4050)},
                {'name': 'München', 'lat': 48.1351, 'lon': 11.5820, 'distance': self._calculate_distance(lat, lon, 48.1351, 11.5820)},
                {'name': 'Hamburg', 'lat': 53.5511, 'lon': 9.9937, 'distance': self._calculate_distance(lat, lon, 53.5511, 9.9937)},
                {'name': 'Köln', 'lat': 50.9375, 'lon': 6.9603, 'distance': self._calculate_distance(lat, lon, 50.9375, 6.9603)},
                {'name': 'Frankfurt am Main', 'lat': 50.1109, 'lon': 8.6821, 'distance': self._calculate_distance(lat, lon, 50.1109, 8.6821)},
                {'name': 'Stuttgart', 'lat': 48.7758, 'lon': 9.1829, 'distance': self._calculate_distance(lat, lon, 48.7758, 9.1829)},
                {'name': 'Düsseldorf', 'lat': 51.2277, 'lon': 6.7735, 'distance': self._calculate_distance(lat, lon, 51.2277, 6.7735)},
                {'name': 'Dresden', 'lat': 51.0504, 'lon': 13.7373, 'distance': self._calculate_distance(lat, lon, 51.0504, 13.7373)}
            ]
            
            # Find nearest cities
            nearest_cities = sorted(german_cities, key=lambda x: x['distance'])[:5]
            
            return {
                'status': 'success',
                'user_coordinates': {'lat': lat, 'lon': lon},
                'nearest_cities': nearest_cities,
                'recommended_radius': [25, 50, 100, 200],
                'location_detected': nearest_cities[0]['name'] if nearest_cities[0]['distance'] < 50 else 'Unknown',
                'country': 'Germany' if nearest_cities[0]['distance'] < 500 else 'Unknown'
            }
            
        except Exception as e:
            logger.error(f"❌ Location info failed: {e}")
            return {
                'status': 'error',
                'message': f'Location processing failed: {str(e)}'
            }

    async def get_search_radius_options(self) -> Dict[str, Any]:
        """
        📍 Get available search radius options with descriptions
        """
        return {
            'status': 'success',
            'radius_options': [
                {'value': 5, 'label': '5 km', 'description': 'Sehr nah - zu Fuß oder mit dem Fahrrad erreichbar'},
                {'value': 10, 'label': '10 km', 'description': 'Nah - kurze Fahrt mit öffentlichen Verkehrsmitteln'},
                {'value': 25, 'label': '25 km', 'description': 'Mittel - ca. 30 Minuten Fahrtzeit'},
                {'value': 50, 'label': '50 km', 'description': 'Erweitert - ca. 1 Stunde Fahrtzeit'},
                {'value': 100, 'label': '100 km', 'description': 'Weit - größere Region abdecken'},
                {'value': 200, 'label': '200 km', 'description': 'Sehr weit - mehrere Bundesländer'}
            ],
            'default_radius': 50,
            'recommendation': 'Wir empfehlen 50 km für eine gute Balance zwischen Auswahl und Erreichbarkeit'
        }

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
        
    def _apply_enhanced_filters(self, 
                               jobs: List[Dict],
                               remote: bool = None,
                               language_level: str = None,
                               category: str = None,
                               visa_sponsorship: bool = None) -> List[Dict]:
        """Apply enhanced filters to job listings"""
        
        filtered = jobs.copy()
        
        # Remote filter
        if remote is not None:
            filtered = [job for job in filtered if job.get('remote_possible', False) == remote]
        
        # Language level filter (enhanced AI-based estimation)
        if language_level and language_level in self.language_levels:
            max_score = self.language_levels[language_level]['max_score']
            filtered = [job for job in filtered if 
                       job.get('language_requirement', {}).get('score', 50) <= max_score]
        
        # Category filter (enhanced with German terms)
        if category and category in self.job_categories:
            category_keywords = self.job_categories[category]
            filtered = [job for job in filtered if 
                       any(keyword.lower() in job.get('title', '').lower() or 
                           keyword.lower() in job.get('profession', '').lower()
                           for keyword in category_keywords)]
        
        # Visa sponsorship filter
        if visa_sponsorship is not None:
            filtered = [job for job in filtered if job.get('visa_sponsorship', False) == visa_sponsorship]
        
        return filtered

    def _estimate_language_requirement_enhanced(self, job: Dict) -> Dict[str, Any]:
        """Enhanced AI-based estimation of German language requirement"""
        title = job.get('titel', '').lower()
        profession = job.get('beruf', '').lower()
        company = job.get('arbeitgeber', '').lower()
        
        score = 40  # Base score (B1 level)
        
        # Keywords indicating higher German requirement
        high_german_keywords = [
            'kundenkontakt', 'kundenbetreuung', 'vertrieb', 'verkauf', 'beratung',
            'kommunikation', 'präsentation', 'führung', 'management', 'teamleitung',
            'öffentlicher dienst', 'behörde', 'verwaltung', 'sozial', 'pflege',
            'erziehung', 'lehrer', 'ausbildung', 'recht', 'jura'
        ]
        
        # Keywords indicating lower German requirement  
        low_german_keywords = [
            'english', 'international', 'startup', 'tech', 'developer', 'software',
            'programmer', 'data scientist', 'remote', 'freelance', 'it', 'informatik',
            'entwickler', 'programmierer'
        ]
        
        # Check for high German requirement indicators
        for keyword in high_german_keywords:
            if keyword in title or keyword in profession or keyword in company:
                score += 15
        
        # Check for low German requirement indicators
        for keyword in low_german_keywords:
            if keyword in title or keyword in profession or keyword in company:
                score -= 10
        
        # Location factor (international cities have lower requirements)
        arbeitsort = job.get('arbeitsort', {})
        location = arbeitsort.get('ort', '').lower()
        if location in ['berlin', 'münchen', 'hamburg', 'frankfurt']:
            score -= 5
        
        # Company factor (international companies)
        if any(term in company for term in ['gmbh & co', 'international', 'global', 'europe']):
            score -= 5
        
        score = max(20, min(90, score))  # Keep score between A2-C1 range
        
        # Determine level
        level = 'B1'
        for lvl, data in self.language_levels.items():
            if data['min_score'] <= score <= data['max_score']:
                level = lvl
                break
        
        return {
            'level': level,
            'score': score,
            'description': self.language_levels[level]['description'],
            'confidence': 'medium'
        }

    def _analyze_jobs(self, jobs: List[Dict]) -> Dict[str, Any]:
        """Comprehensive analysis of job listings"""
        if not jobs:
            return {'categories': {}, 'locations': {}, 'companies': {}, 'insights': []}
        
        # Category analysis
        categories = {}
        for category, keywords in self.job_categories.items():
            matching_jobs = [job for job in jobs if 
                           any(keyword.lower() in job.get('title', '').lower() or
                               keyword.lower() in job.get('profession', '').lower()
                               for keyword in keywords)]
            if matching_jobs:
                categories[category] = {
                    'count': len(matching_jobs),
                    'percentage': round((len(matching_jobs) / len(jobs)) * 100, 1),
                    'average_match_score': round(sum((job.get('match_score') or 50) for job in matching_jobs) / len(matching_jobs), 1)
                }
        
        # Location analysis
        locations = {}
        for job in jobs:
            location = job.get('location', {}).get('city', 'Unknown')
            if location not in locations:
                locations[location] = {'count': 0, 'jobs': []}
            locations[location]['count'] += 1
            locations[location]['jobs'].append(job['id'])
        
        # Company analysis
        companies = {}
        for job in jobs:
            company = job.get('company_name', 'Unknown')
            if company not in companies:
                companies[company] = {'count': 0, 'jobs': []}
            companies[company]['count'] += 1
            companies[company]['jobs'].append(job['id'])
        
        # Generate insights
        insights = []
        
        # Top category insight
        if categories:
            top_category = max(categories.keys(), key=lambda k: categories[k]['count'])
            insights.append(f"Meiste Stellenangebote in Kategorie: {top_category} ({categories[top_category]['count']} Jobs)")
        
        # Top location insight
        if locations:
            top_location = max(locations.keys(), key=lambda k: locations[k]['count'])
            insights.append(f"Meiste Jobs in: {top_location} ({locations[top_location]['count']} Angebote)")
        
        # Remote work insight
        remote_jobs = [job for job in jobs if job.get('remote_possible', False)]
        if remote_jobs:
            insights.append(f"{len(remote_jobs)} Jobs bieten Homeoffice-Möglichkeiten")
        
        # Language level insight
        language_levels_dist = {}
        for job in jobs:
            level = job.get('language_requirement', {}).get('level', 'B1')
            language_levels_dist[level] = language_levels_dist.get(level, 0) + 1
        
        if language_levels_dist:
            most_common_level = max(language_levels_dist.keys(), key=lambda k: language_levels_dist[k])
            insights.append(f"Häufigster Sprachlevel: {most_common_level} ({language_levels_dist[most_common_level]} Jobs)")
        
        return {
            'categories': categories,
            'locations': dict(sorted(locations.items(), key=lambda x: x[1]['count'], reverse=True)[:10]),
            'companies': dict(sorted(companies.items(), key=lambda x: x[1]['count'], reverse=True)[:10]),
            'language_distribution': language_levels_dist,
            'remote_jobs_count': len(remote_jobs),
            'insights': insights
        }

    def _process_facets(self, facets: Dict) -> Dict[str, Any]:
        """Process API facets into user-friendly format"""
        processed = {}
        
        # Process work time facets
        if 'arbeitszeit' in facets:
            processed['work_time'] = {}
            for key, count in facets['arbeitszeit'].get('counts', {}).items():
                if key in self.work_time_filters:
                    processed['work_time'][key] = {
                        'name': self.work_time_filters[key]['name'],
                        'count': count,
                        'description': self.work_time_filters[key]['description']
                    }
        
        # Process location facets
        if 'arbeitsort' in facets:
            processed['locations'] = facets['arbeitsort'].get('counts', {})
        
        # Process employer facets
        if 'arbeitgeber' in facets:
            processed['employers'] = facets['arbeitgeber'].get('counts', {})
        
        # Process profession facets
        if 'beruf' in facets:
            processed['professions'] = facets['beruf'].get('counts', {})
        
        return processed

    def _generate_enhanced_recommendations(self, search_query: str, jobs: List[Dict], analysis: Dict) -> List[str]:
        """Generate enhanced AI-powered search recommendations"""
        recommendations = []
        
        if not jobs:
            recommendations.append("🔍 Versuchen Sie einen breiteren Suchbegriff oder vergrößern Sie den Suchradius")
            recommendations.append("📍 Erwägen Sie Homeoffice-Jobs für mehr Flexibilität")
            recommendations.append("🌍 Suchen Sie in mehreren deutschen Städten gleichzeitig")
            return recommendations
        
        # Category-based recommendations
        categories = analysis.get('categories', {})
        if categories:
            top_category = max(categories.keys(), key=lambda k: categories[k]['count'])
            recommendations.append(f"💼 Besonders viele {top_category.title()}-Jobs verfügbar")
        
        # Location-based recommendations  
        locations = analysis.get('locations', {})
        if len(locations) > 1:
            top_locations = list(locations.keys())[:3]
            recommendations.append(f"📍 Top Standorte: {', '.join(top_locations)}")
        
        # Remote work recommendation
        remote_count = analysis.get('remote_jobs_count', 0)
        if remote_count > 0:
            recommendations.append(f"🏠 {remote_count} Jobs bieten Homeoffice-Möglichkeiten")
        
        # Language level recommendation
        lang_dist = analysis.get('language_distribution', {})
        if lang_dist:
            common_levels = sorted(lang_dist.items(), key=lambda x: x[1], reverse=True)[:2]
            recommendations.append(f"🗣️ Empfohlene Sprachlevel: {', '.join([level for level, count in common_levels])}")
        
        # Search query specific recommendations
        if search_query:
            query_lower = search_query.lower()
            if 'developer' in query_lower or 'entwickler' in query_lower:
                recommendations.append("💻 Auch suchen: Software Engineer, Programmierer, IT-Spezialist")
            elif 'marketing' in query_lower:
                recommendations.append("📈 Auch suchen: Digital Marketing, Social Media, Content Manager")
            elif 'sales' in query_lower or 'vertrieb' in query_lower:
                recommendations.append("💰 Auch suchen: Account Manager, Business Development, Kundenberater")
        
        return recommendations[:5]  # Limit to 5 recommendations

    def _filter_jobs(self, 
                     jobs: List[Dict],
                     search_query: str = None,
                     location: str = None,
                     remote: bool = None,
                     language_level: str = None,
                     category: str = None) -> List[Dict]:
        """Legacy filter method for backward compatibility"""
        return self._apply_enhanced_filters(
            jobs=jobs,
            remote=remote,
            language_level=language_level,
            category=category
        )

    def _estimate_language_requirement(self, job: Dict) -> int:
        """Legacy method for backward compatibility"""
        enhanced_result = self._estimate_language_requirement_enhanced(job)
        return enhanced_result.get('score', 50)

    def _categorize_jobs(self, jobs: List[Dict]) -> Dict[str, Any]:
        """Legacy categorization method for backward compatibility"""
        categorized = {category: [] for category in self.job_categories.keys()}
        
        for job in jobs:
            title = job.get('title', '').lower()
            profession = job.get('profession', '').lower()
            assigned = False
            
            for category, keywords in self.job_categories.items():
                if category != 'other' and any(keyword.lower() in title or keyword.lower() in profession 
                                              for keyword in keywords):
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
        """Legacy recommendations method for backward compatibility"""
        analysis = self._analyze_jobs(jobs)
        return self._generate_enhanced_recommendations(search_query, jobs, analysis)

    async def _get_enhanced_fallback_jobs(self) -> Dict[str, Any]:
        """Return enhanced demo jobs when API is unavailable"""
        demo_jobs = [
            {
                'id': 'demo_2025_1',
                'title': 'Senior Software Developer - React & Node.js',
                'profession': 'Softwareentwickler/in',
                'company_name': 'TechBerlin GmbH',
                'location': {
                    'city': 'Berlin',
                    'state': 'Berlin', 
                    'country': 'Deutschland',
                    'postal_code': '10117',
                    'coordinates': {'lat': 52.5200, 'lon': 13.4050},
                    'distance_km': 5.2
                },
                'location_string': 'Berlin, Berlin',
                'dates': {
                    'published': '2025-01-20',
                    'start_date': '2025-02-01',
                    'modified': '2025-01-20T10:00:00Z'
                },
                'external_url': 'https://example.com/job/demo_1',
                'reference_number': 'DEMO-2025-001',
                'job_type': 'full-time',
                'work_time': 'vz',
                'remote_possible': True,
                'visa_sponsorship': True,
                'tags': ['Software Development', 'Berlin', 'React', 'Node.js'],
                'salary_info': {
                    'available': True,
                    'range': '65000-85000',
                    'currency': 'EUR',
                    'period': 'yearly'
                },
                'description': 'Entwicklung moderner Web-Anwendungen mit React und Node.js in internationalem Team.',
                'requirements': ['3+ Jahre Erfahrung', 'React & Node.js', 'Deutsch B1', 'Englisch fließend'],
                'benefits': ['Homeoffice möglich', 'Weiterbildungsbudget', '30 Tage Urlaub'],
                'language_requirement': {'level': 'B1', 'score': 35, 'confidence': 'high'},
                'match_score': 85
            },
            {
                'id': 'demo_2025_2',
                'title': 'Pflegefachkraft (m/w/d) - Vollzeit',
                'profession': 'Pflegefachmann/-frau',
                'company_name': 'Klinikum München',
                'location': {
                    'city': 'München',
                    'state': 'Bayern',
                    'country': 'Deutschland', 
                    'postal_code': '80331',
                    'coordinates': {'lat': 48.1351, 'lon': 11.5820},
                    'distance_km': 12.8
                },
                'location_string': 'München, Bayern',
                'dates': {
                    'published': '2025-01-19',
                    'start_date': '2025-02-15', 
                    'modified': '2025-01-19T14:30:00Z'
                },
                'external_url': 'https://example.com/job/demo_2',
                'reference_number': 'DEMO-2025-002',
                'job_type': 'full-time',
                'work_time': 'vz',
                'remote_possible': False,
                'visa_sponsorship': False,
                'tags': ['Krankenpflege', 'München', 'Vollzeit'],
                'salary_info': {
                    'available': True,
                    'range': '3200-3800',
                    'currency': 'EUR',
                    'period': 'monthly'
                },
                'description': 'Qualifizierte Pflegefachkraft für Intensivstation gesucht.',
                'requirements': ['Pflegeexamen', 'Deutsch C1', 'Schichtdienst möglich'],
                'benefits': ['Tarifvertrag', 'Betriebsrente', 'Fort- und Weiterbildung'],
                'language_requirement': {'level': 'C1', 'score': 75, 'confidence': 'high'},
                'match_score': 92
            },
            {
                'id': 'demo_2025_3',
                'title': 'Marketing Manager - Digital & E-Commerce',
                'profession': 'Marketing Manager/in',
                'company_name': 'StartupHamburg AG',
                'location': {
                    'city': 'Hamburg',
                    'state': 'Hamburg',
                    'country': 'Deutschland',
                    'postal_code': '20095',
                    'coordinates': {'lat': 53.5511, 'lon': 9.9937},
                    'distance_km': 8.1
                },
                'location_string': 'Hamburg, Hamburg',
                'dates': {
                    'published': '2025-01-18',
                    'start_date': '2025-03-01',
                    'modified': '2025-01-18T09:15:00Z'
                },
                'external_url': 'https://example.com/job/demo_3',
                'reference_number': 'DEMO-2025-003',
                'job_type': 'full-time',
                'work_time': 'vz',
                'remote_possible': True,
                'visa_sponsorship': True,
                'tags': ['Marketing', 'Hamburg', 'Digital', 'E-Commerce'],
                'salary_info': {
                    'available': True,
                    'range': '55000-70000', 
                    'currency': 'EUR',
                    'period': 'yearly'
                },
                'description': 'Strategische Planung und Umsetzung digitaler Marketing-Kampagnen.',
                'requirements': ['Marketing Studium', 'Digital Marketing Erfahrung', 'Deutsch B2'],
                'benefits': ['Flexible Arbeitszeiten', 'Homeoffice', 'Team Events'],
                'language_requirement': {'level': 'B2', 'score': 55, 'confidence': 'medium'},
                'match_score': 78
            }
        ]
        
        # Simulate analysis
        analysis = self._analyze_jobs(demo_jobs)
        
        return {
            'status': 'demo',
            'total_found': len(demo_jobs),
            'total_available': len(demo_jobs),
            'jobs': demo_jobs,
            'analysis': analysis,
            'facets': {
                'work_time': {
                    'vz': {'name': 'Vollzeit', 'count': 3, 'description': 'Full-time positions'}
                },
                'locations': {'Berlin': 1, 'München': 1, 'Hamburg': 1},
                'professions': {'Software': 1, 'Pflege': 1, 'Marketing': 1}
            },
            'search_metadata': {
                'search_mode': 'demo',
                'radius_km': 50,
                'language_levels_available': list(self.language_levels.keys())
            },
            'pagination': {
                'page': 1,
                'size': 25,
                'total': len(demo_jobs),
                'has_next': False
            },
            'recommendations': [
                '🔧 Demo-Modus aktiv - Echte Daten nach API-Konfiguration verfügbar',
                '🌟 Verschiedene Branchen und Standorte verfügbar',
                '📍 Nutzen Sie die Geolocation-Funktion für präzise Suche',
                '🗣️ Sprachfilter für alle Level A1-C2 verfügbar'
            ],
            'api_info': {
                'source': 'demo_mode',
                'name': 'Demo Job Search - Enhanced Features Preview',
                'version': 'v2.0',
                'enhanced_features': ['geolocation', 'radius_search', 'advanced_filters', 'language_estimation']
            }
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
        # Handle location as dict or string
        location_data = job.get('location', {})
        if isinstance(location_data, dict):
            location = location_data.get('city', '').lower()
        else:
            location = str(location_data).lower()
        
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
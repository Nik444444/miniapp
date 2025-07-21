"""
🏙️ German Cities Service - Service for city search and suggestions
Сервис для поиска и предложений городов Германии
"""

import logging
from typing import List, Dict, Any, Optional
import json

logger = logging.getLogger(__name__)

class GermanCitiesService:
    def __init__(self):
        # Major German cities with population and federal state
        self.cities = [
            # Major cities (>500k population)
            {"name": "Berlin", "state": "Berlin", "population": 3669491, "type": "major"},
            {"name": "Hamburg", "state": "Hamburg", "population": 1899160, "type": "major"},
            {"name": "München", "state": "Bayern", "population": 1484226, "type": "major", "aliases": ["Munich"]},
            {"name": "Köln", "state": "Nordrhein-Westfalen", "population": 1087863, "type": "major", "aliases": ["Cologne"]},
            {"name": "Frankfurt am Main", "state": "Hessen", "population": 758847, "type": "major", "aliases": ["Frankfurt"]},
            {"name": "Stuttgart", "state": "Baden-Württemberg", "population": 626275, "type": "major"},
            {"name": "Düsseldorf", "state": "Nordrhein-Westfalen", "population": 619477, "type": "major"},
            {"name": "Leipzig", "state": "Sachsen", "population": 597493, "type": "major"},
            {"name": "Dortmund", "state": "Nordrhein-Westfalen", "population": 588250, "type": "major"},
            {"name": "Essen", "state": "Nordrhein-Westfalen", "population": 579432, "type": "major"},
            {"name": "Bremen", "state": "Bremen", "population": 567559, "type": "major"},
            {"name": "Dresden", "state": "Sachsen", "population": 556780, "type": "major"},
            {"name": "Hannover", "state": "Niedersachsen", "population": 538068, "type": "major"},
            
            # Large cities (200k-500k population)
            {"name": "Nürnberg", "state": "Bayern", "population": 518365, "type": "large", "aliases": ["Nuremberg"]},
            {"name": "Duisburg", "state": "Nordrhein-Westfalen", "population": 498590, "type": "large"},
            {"name": "Bochum", "state": "Nordrhein-Westfalen", "population": 364454, "type": "large"},
            {"name": "Wuppertal", "state": "Nordrhein-Westfalen", "population": 354572, "type": "large"},
            {"name": "Bielefeld", "state": "Nordrhein-Westfalen", "population": 334002, "type": "large"},
            {"name": "Bonn", "state": "Nordrhein-Westfalen", "population": 327258, "type": "large"},
            {"name": "Münster", "state": "Nordrhein-Westfalen", "population": 315293, "type": "large"},
            {"name": "Karlsruhe", "state": "Baden-Württemberg", "population": 308436, "type": "large"},
            {"name": "Mannheim", "state": "Baden-Württemberg", "population": 307960, "type": "large"},
            {"name": "Augsburg", "state": "Bayern", "population": 296582, "type": "large"},
            {"name": "Wiesbaden", "state": "Hessen", "population": 278342, "type": "large"},
            {"name": "Gelsenkirchen", "state": "Nordrhein-Westfalen", "population": 260654, "type": "large"},
            {"name": "Mönchengladbach", "state": "Nordrhein-Westfalen", "population": 259996, "type": "large"},
            {"name": "Braunschweig", "state": "Niedersachsen", "population": 248292, "type": "large"},
            {"name": "Chemnitz", "state": "Sachsen", "population": 243521, "type": "large"},
            {"name": "Kiel", "state": "Schleswig-Holstein", "population": 240832, "type": "large"},
            {"name": "Aachen", "state": "Nordrhein-Westfalen", "population": 238942, "type": "large"},
            {"name": "Halle (Saale)", "state": "Sachsen-Anhalt", "population": 237865, "type": "large", "aliases": ["Halle"]},
            {"name": "Magdeburg", "state": "Sachsen-Anhalt", "population": 229826, "type": "large"},
            {"name": "Freiburg im Breisgau", "state": "Baden-Württemberg", "population": 228596, "type": "large", "aliases": ["Freiburg"]},
            {"name": "Krefeld", "state": "Nordrhein-Westfalen", "population": 226387, "type": "large"},
            {"name": "Lübeck", "state": "Schleswig-Holstein", "population": 217198, "type": "large"},
            {"name": "Oberhausen", "state": "Nordrhein-Westfalen", "population": 208752, "type": "large"},
            {"name": "Erfurt", "state": "Thüringen", "population": 208400, "type": "large"},
            {"name": "Mainz", "state": "Rheinland-Pfalz", "population": 206628, "type": "large"},
            {"name": "Rostock", "state": "Mecklenburg-Vorpommern", "population": 206628, "type": "large"},
            
            # Medium cities (100k-200k population) - most job relevant
            {"name": "Kassel", "state": "Hessen", "population": 197597, "type": "medium"},
            {"name": "Hagen", "state": "Nordrhein-Westfalen", "population": 188686, "type": "medium"},
            {"name": "Hamm", "state": "Nordrhein-Westfalen", "population": 178967, "type": "medium"},
            {"name": "Saarbrücken", "state": "Saarland", "population": 178151, "type": "medium"},
            {"name": "Mülheim an der Ruhr", "state": "Nordrhein-Westfalen", "population": 170632, "type": "medium", "aliases": ["Mülheim"]},
            {"name": "Potsdam", "state": "Brandenburg", "population": 170106, "type": "medium"},
            {"name": "Ludwigshafen am Rhein", "state": "Rheinland-Pfalz", "population": 164733, "type": "medium", "aliases": ["Ludwigshafen"]},
            {"name": "Oldenburg", "state": "Niedersachsen", "population": 162173, "type": "medium"},
            {"name": "Leverkusen", "state": "Nordrhein-Westfalen", "population": 160919, "type": "medium"},
            {"name": "Osnabrück", "state": "Niedersachsen", "population": 157998, "type": "medium"},
            {"name": "Solingen", "state": "Nordrhein-Westfalen", "population": 156693, "type": "medium"},
            {"name": "Heidelberg", "state": "Baden-Württemberg", "population": 154715, "type": "medium"},
            {"name": "Herne", "state": "Nordrhein-Westfalen", "population": 154600, "type": "medium"},
            {"name": "Neuss", "state": "Nordrhein-Westfalen", "population": 150707, "type": "medium"},
            {"name": "Darmstadt", "state": "Hessen", "population": 150100, "type": "medium"},
            {"name": "Paderborn", "state": "Nordrhein-Westfalen", "population": 149727, "type": "medium"},
            {"name": "Regensburg", "state": "Bayern", "population": 148379, "type": "medium"},
            {"name": "Ingolstadt", "state": "Bayern", "population": 136981, "type": "medium"},
            {"name": "Würzburg", "state": "Bayern", "population": 126933, "type": "medium"},
            {"name": "Fürth", "state": "Bayern", "population": 126892, "type": "medium"},
            {"name": "Wolfsburg", "state": "Niedersachsen", "population": 123064, "type": "medium"},
            {"name": "Offenbach am Main", "state": "Hessen", "population": 122415, "type": "medium", "aliases": ["Offenbach"]},
            {"name": "Ulm", "state": "Baden-Württemberg", "population": 120451, "type": "medium"},
            {"name": "Heilbronn", "state": "Baden-Württemberg", "population": 120468, "type": "medium"},
            {"name": "Pforzheim", "state": "Baden-Württemberg", "population": 119313, "type": "medium"},
            {"name": "Göttingen", "state": "Niedersachsen", "population": 116845, "type": "medium"},
            {"name": "Bottrop", "state": "Nordrhein-Westfalen", "population": 116441, "type": "medium"},
            {"name": "Trier", "state": "Rheinland-Pfalz", "population": 110570, "type": "medium"},
            {"name": "Recklinghausen", "state": "Nordrhein-Westfalen", "population": 108440, "type": "medium"},
            {"name": "Bremerhaven", "state": "Bremen", "population": 108440, "type": "medium"},
            {"name": "Koblenz", "state": "Rheinland-Pfalz", "population": 106341, "type": "medium"},
            {"name": "Bergisch Gladbach", "state": "Nordrhein-Westfalen", "population": 105696, "type": "medium"},
            {"name": "Jena", "state": "Thüringen", "population": 105129, "type": "medium"},
            {"name": "Remscheid", "state": "Nordrhein-Westfalen", "population": 109499, "type": "medium"},
            {"name": "Erlangen", "state": "Bayern", "population": 108336, "type": "medium"},
            {"name": "Moers", "state": "Nordrhein-Westfalen", "population": 103725, "type": "medium"},
            {"name": "Siegen", "state": "Nordrhein-Westfalen", "population": 100325, "type": "medium"},
            
            # Popular job locations (smaller cities but important for jobs)
            {"name": "Konstanz", "state": "Baden-Württemberg", "population": 83793, "type": "small"},
            {"name": "Bamberg", "state": "Bayern", "population": 75025, "type": "small"},
            {"name": "Bayreuth", "state": "Bayern", "population": 72148, "type": "small"},
            {"name": "Passau", "state": "Bayern", "population": 52415, "type": "small"}
        ]
        
        # Create search index for faster lookups
        self.search_index = self._build_search_index()
        
    def _build_search_index(self) -> Dict[str, List[Dict]]:
        """Build search index for faster city lookups"""
        index = {}
        
        for city in self.cities:
            # Index by city name
            name_lower = city['name'].lower()
            if name_lower not in index:
                index[name_lower] = []
            index[name_lower].append(city)
            
            # Index by aliases
            if 'aliases' in city:
                for alias in city['aliases']:
                    alias_lower = alias.lower()
                    if alias_lower not in index:
                        index[alias_lower] = []
                    index[alias_lower].append(city)
            
            # Index by partial matches (for autocomplete)
            for i in range(2, len(name_lower) + 1):
                partial = name_lower[:i]
                if partial not in index:
                    index[partial] = []
                if city not in index[partial]:
                    index[partial].append(city)
                    
        return index
    
    def search_cities(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        🔍 Search for German cities by name
        """
        if not query or len(query) < 2:
            # Return top major cities if no query
            return [city for city in self.cities if city['type'] == 'major'][:limit]
        
        query_lower = query.lower().strip()
        matches = []
        seen_cities = set()
        
        # Exact match first
        if query_lower in self.search_index:
            for city in self.search_index[query_lower]:
                if city['name'] not in seen_cities:
                    matches.append({
                        **city,
                        'match_type': 'exact',
                        'relevance': 100
                    })
                    seen_cities.add(city['name'])
        
        # Partial matches
        for indexed_term, cities in self.search_index.items():
            if query_lower in indexed_term and indexed_term != query_lower:
                for city in cities:
                    if city['name'] not in seen_cities:
                        # Calculate relevance based on match position and city type
                        relevance = 50
                        if indexed_term.startswith(query_lower):
                            relevance += 30
                        if city['type'] == 'major':
                            relevance += 20
                        elif city['type'] == 'large':
                            relevance += 10
                        
                        matches.append({
                            **city,
                            'match_type': 'partial',
                            'relevance': relevance
                        })
                        seen_cities.add(city['name'])
        
        # Sort by relevance and city importance
        matches.sort(key=lambda x: (
            -x['relevance'],  # Higher relevance first
            -x['population'],  # Larger cities first
            x['name']  # Alphabetical order
        ))
        
        return matches[:limit]
    
    def get_popular_cities(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most popular cities for job search"""
        return [
            {**city, 'reason': 'major_job_market'} 
            for city in self.cities 
            if city['type'] in ['major', 'large']
        ][:limit]
    
    def get_cities_by_state(self, state: str) -> List[Dict[str, Any]]:
        """Get cities by federal state"""
        return [
            city for city in self.cities 
            if city['state'].lower() == state.lower()
        ]
    
    def get_city_info(self, city_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific city"""
        city_lower = city_name.lower()
        
        # Direct name match
        for city in self.cities:
            if city['name'].lower() == city_lower:
                return {
                    **city,
                    'job_market_info': self._get_job_market_info(city)
                }
        
        # Alias match
        for city in self.cities:
            if 'aliases' in city:
                for alias in city['aliases']:
                    if alias.lower() == city_lower:
                        return {
                            **city,
                            'job_market_info': self._get_job_market_info(city)
                        }
        
        return None
    
    def _get_job_market_info(self, city: Dict[str, Any]) -> Dict[str, Any]:
        """Get job market information for a city"""
        # Job market insights based on city characteristics
        job_market = {
            'market_size': 'unknown',
            'main_industries': [],
            'avg_salary_range': {'min': 35000, 'max': 60000, 'currency': 'EUR'},
            'job_opportunities': 'medium'
        }
        
        city_name = city['name'].lower()
        
        # Major tech/financial hubs
        if city_name in ['berlin', 'münchen', 'munich', 'hamburg', 'frankfurt am main', 'frankfurt']:
            job_market.update({
                'market_size': 'very_large',
                'main_industries': ['technology', 'finance', 'startups', 'consulting'],
                'avg_salary_range': {'min': 45000, 'max': 80000, 'currency': 'EUR'},
                'job_opportunities': 'excellent'
            })
        
        # Industrial centers
        elif city_name in ['stuttgart', 'düsseldorf', 'köln', 'cologne', 'dortmund', 'essen']:
            job_market.update({
                'market_size': 'large',
                'main_industries': ['automotive', 'manufacturing', 'logistics', 'media'],
                'avg_salary_range': {'min': 40000, 'max': 70000, 'currency': 'EUR'},
                'job_opportunities': 'good'
            })
        
        # University/research cities
        elif city_name in ['heidelberg', 'göttingen', 'erlangen', 'jena', 'konstanz']:
            job_market.update({
                'market_size': 'medium',
                'main_industries': ['research', 'biotechnology', 'education', 'pharma'],
                'avg_salary_range': {'min': 38000, 'max': 65000, 'currency': 'EUR'},
                'job_opportunities': 'good'
            })
        
        return job_market

# Global instance
german_cities_service = GermanCitiesService()
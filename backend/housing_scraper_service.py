"""
🏠 GERMAN HOUSING SCRAPER SERVICE
Веб-скрапинг популярных немецких сайтов недвижимости для поиска аренды
"""

import requests
from bs4 import BeautifulSoup
import re
import logging
from typing import List, Dict, Any, Optional
import time
import random
from urllib.parse import quote, urljoin
import json

logger = logging.getLogger(__name__)

class GermanHousingScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'de-DE,de;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        # Rate limiting
        self.last_request_time = 0
        self.min_delay = 2  # seconds between requests
        
    def _rate_limit(self):
        """Rate limiting between requests"""
        current_time = time.time()
        elapsed = current_time - self.last_request_time
        if elapsed < self.min_delay:
            sleep_time = self.min_delay - elapsed + random.uniform(0.5, 1.5)
            time.sleep(sleep_time)
        self.last_request_time = time.time()
        
    def _safe_request(self, url: str, retries: int = 3) -> Optional[requests.Response]:
        """Safe HTTP request with retries"""
        self._rate_limit()
        
        for attempt in range(retries):
            try:
                logger.info(f"Scraping URL: {url} (attempt {attempt + 1})")
                response = self.session.get(url, timeout=15)
                
                if response.status_code == 200:
                    return response
                elif response.status_code == 429:
                    # Rate limited, wait longer
                    sleep_time = (attempt + 1) * 10
                    logger.warning(f"Rate limited. Waiting {sleep_time}s...")
                    time.sleep(sleep_time)
                else:
                    logger.warning(f"HTTP {response.status_code} for {url}")
                    
            except Exception as e:
                logger.error(f"Request failed for {url}: {str(e)}")
                if attempt < retries - 1:
                    time.sleep((attempt + 1) * 2)
                    
        return None
        
    def _extract_price(self, text: str) -> Optional[float]:
        """Extract price from German text with improved error handling"""
        if not text or not isinstance(text, str):
            return None
            
        try:
            # Remove common German currency formatting safely
            # First, remove currency symbols and non-numeric characters except comma and period
            cleaned = re.sub(r'[^\d,.\s]', '', str(text))
            
            # Handle German number formatting (1.234,56 -> 1234.56)
            if ',' in cleaned and '.' in cleaned:
                # If both comma and period, assume German format
                cleaned = cleaned.replace('.', '').replace(',', '.')
            elif ',' in cleaned:
                # Only comma, could be decimal separator
                parts = cleaned.split(',')
                if len(parts) == 2 and len(parts[1]) <= 2:
                    # Likely decimal separator
                    cleaned = cleaned.replace(',', '.')
                else:
                    # Likely thousands separator
                    cleaned = cleaned.replace(',', '')
            
            # Extract first number from the cleaned string
            number_match = re.search(r'\d+\.?\d*', cleaned)
            if number_match:
                return float(number_match.group())
                
            return None
        except (ValueError, AttributeError, re.error) as e:
            logger.debug(f"Price extraction failed for '{text}': {e}")
            return None
            
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text with better error handling"""
        if not text or not isinstance(text, str):
            return ""
        try:
            # Remove extra whitespace and normalize
            cleaned = re.sub(r'\s+', ' ', str(text).strip())
            # Remove any problematic characters that could cause pattern matching issues
            cleaned = re.sub(r'[^\w\s\-.,äöüÄÖÜß€$]', '', cleaned)
            return cleaned
        except (re.error, AttributeError) as e:
            logger.debug(f"Text cleaning failed for '{text}': {e}")
            return str(text).strip() if text else ""

    def scrape_immoscout24(self, city: str, max_price: int = None, property_type: str = "wohnung") -> List[Dict[str, Any]]:
        """Scrape ImmoScout24.de with improved error handling"""
        logger.info(f"🏠 Scraping ImmoScout24 for {city}")
        
        try:
            # Sanitize city name to prevent pattern matching issues
            safe_city = re.sub(r'[^\w\säöüÄÖÜß\-]', '', city.strip()) if city else ""
            if not safe_city:
                logger.warning(f"Invalid city name: {city}")
                return []
            
            # Build search URL
            base_url = "https://www.immobilienscout24.de/Suche/de/mieten/wohnung"
            params = f"/{quote(safe_city.lower())}"
            
            if max_price and isinstance(max_price, (int, float)) and max_price > 0:
                params += f"?price=-{int(max_price)}"
                
            url = base_url + params
            
            response = self._safe_request(url)
            if not response:
                logger.warning(f"No response from ImmoScout24 for {city}")
                return []
                
            soup = BeautifulSoup(response.content, 'html.parser')
            listings = []
            
            # Find property listings with safer regex patterns
            try:
                property_items = soup.find_all(['article', 'div'], {'data-item': True}) or soup.find_all('div', class_=lambda x: x and 'result' in str(x).lower())
            except Exception as e:
                logger.error(f"Error finding property items: {e}")
                property_items = []
            
            for item in property_items[:10]:  # Limit to 10 results
                try:
                    # Extract data with safer patterns
                    title_elem = None
                    try:
                        title_elem = item.find(['h3', 'h4', 'h5', 'a'], class_=lambda x: x and any(word in str(x).lower() for word in ['title', 'headline']))
                    except Exception:
                        title_elem = item.find(['h3', 'h4', 'h5', 'a'])
                    
                    title = self._clean_text(title_elem.get_text()) if title_elem else "Immobilie"
                    
                    price_elem = None
                    try:
                        price_elem = item.find(['span', 'div'], class_=lambda x: x and any(word in str(x).lower() for word in ['price', 'kaltmiete']))
                    except Exception:
                        price_elem = item.find(['span', 'div'], string=lambda text: text and '€' in str(text))
                    
                    price_text = price_elem.get_text() if price_elem else ""
                    price = self._extract_price(price_text)
                    
                    area_elem = None
                    try:
                        area_elem = item.find(['span', 'div'], class_=lambda x: x and any(word in str(x).lower() for word in ['area', 'flaeche', 'qm', 'm²']))
                    except Exception:
                        area_elem = item.find(['span', 'div'], string=lambda text: text and ('m²' in str(text) or 'qm' in str(text)))
                    
                    area_text = area_elem.get_text() if area_elem else ""
                    area = self._extract_price(area_text)  # Same extraction logic
                    
                    location_elem = None
                    try:
                        location_elem = item.find(['span', 'div'], class_=lambda x: x and any(word in str(x).lower() for word in ['location', 'address', 'ort']))
                    except Exception:
                        location_elem = item.find(['span', 'div'])
                    
                    location = self._clean_text(location_elem.get_text()) if location_elem else safe_city
                    
                    link_elem = item.find('a', href=True)
                    link = urljoin("https://www.immobilienscout24.de", link_elem['href']) if link_elem else None
                    
                    listing = {
                        'source': 'ImmoScout24',
                        'title': title,
                        'price': price,
                        'area': area,
                        'location': location,
                        'city': safe_city,
                        'link': link,
                        'currency': 'EUR',
                        'property_type': property_type,
                        'scraped_at': time.time()
                    }
                    
                    if price and title != "Immobilie":
                        listings.append(listing)
                        
                except Exception as e:
                    logger.debug(f"Error processing ImmoScout24 item: {e}")
                    continue
            
            logger.info(f"✅ ImmoScout24: Found {len(listings)} listings")
            return listings
            
        except Exception as e:
            logger.error(f"ImmoScout24 scraping failed for {city}: {str(e)}")
            return []

    def scrape_immobilien_de(self, city: str, max_price: int = None) -> List[Dict[str, Any]]:
        """Scrape Immobilien.de"""
        logger.info(f"🏠 Scraping Immobilien.de for {city}")
        
        try:
            base_url = f"https://www.immobilien.de/mieten/{quote(city.lower())}"
            response = self._safe_request(base_url)
            
            if not response:
                return []
                
            soup = BeautifulSoup(response.content, 'html.parser')
            listings = []
            
            # Find property listings
            property_items = soup.find_all(['div', 'article'], class_=re.compile(r'property|listing|result'))
            
            for item in property_items[:8]:  # Limit results
                try:
                    title_elem = item.find(['h2', 'h3', 'a'], class_=re.compile(r'title|headline'))
                    title = self._clean_text(title_elem.get_text()) if title_elem else "Immobilie"
                    
                    price_elem = item.find(['span', 'div'], class_=re.compile(r'price|miete'))
                    price = self._extract_price(price_elem.get_text()) if price_elem else None
                    
                    area_elem = item.find(['span', 'div'], string=re.compile(r'm²|qm'))
                    area = self._extract_price(area_elem.get_text()) if area_elem else None
                    
                    link_elem = item.find('a', href=True)
                    link = urljoin("https://www.immobilien.de", link_elem['href']) if link_elem else None
                    
                    listing = {
                        'source': 'Immobilien.de',
                        'title': title,
                        'price': price,
                        'area': area,
                        'location': city,
                        'city': city,
                        'link': link,
                        'currency': 'EUR',
                        'property_type': 'wohnung',
                        'scraped_at': time.time()
                    }
                    
                    if price and title != "Immobilie":
                        listings.append(listing)
                        
                except Exception as e:
                    logger.error(f"Error parsing Immobilien.de item: {str(e)}")
                    continue
                    
            logger.info(f"✅ Immobilien.de: Found {len(listings)} listings")
            return listings
            
        except Exception as e:
            logger.error(f"Immobilien.de scraping failed: {str(e)}")
            return []

    def scrape_wg_gesucht(self, city: str, max_price: int = None) -> List[Dict[str, Any]]:
        """Scrape WG-Gesucht.de"""
        logger.info(f"🏠 Scraping WG-Gesucht for {city}")
        
        try:
            base_url = f"https://www.wg-gesucht.de/wg-zimmer-in-{quote(city.lower())}.html"
            response = self._safe_request(base_url)
            
            if not response:
                return []
                
            soup = BeautifulSoup(response.content, 'html.parser')
            listings = []
            
            # Find WG listings
            wg_items = soup.find_all(['div'], class_=re.compile(r'wgg_card|listing'))
            
            for item in wg_items[:8]:  # Limit results
                try:
                    title_elem = item.find(['h3', 'a'], class_=re.compile(r'headline|title'))
                    title = self._clean_text(title_elem.get_text()) if title_elem else "WG-Zimmer"
                    
                    price_elem = item.find(['span', 'div'], class_=re.compile(r'price|miete'))
                    price = self._extract_price(price_elem.get_text()) if price_elem else None
                    
                    area_elem = item.find(['span'], class_=re.compile(r'size|groesse'))
                    area = self._extract_price(area_elem.get_text()) if area_elem else None
                    
                    location_elem = item.find(['span'], class_=re.compile(r'location|stadtteil'))
                    location = self._clean_text(location_elem.get_text()) if location_elem else city
                    
                    link_elem = item.find('a', href=True)
                    link = urljoin("https://www.wg-gesucht.de", link_elem['href']) if link_elem else None
                    
                    listing = {
                        'source': 'WG-Gesucht',
                        'title': title,
                        'price': price,
                        'area': area,
                        'location': location,
                        'city': city,
                        'link': link,
                        'currency': 'EUR',
                        'property_type': 'zimmer',
                        'scraped_at': time.time()
                    }
                    
                    if price and title != "WG-Zimmer":
                        listings.append(listing)
                        
                except Exception as e:
                    logger.error(f"Error parsing WG-Gesucht item: {str(e)}")
                    continue
                    
            logger.info(f"✅ WG-Gesucht: Found {len(listings)} listings")
            return listings
            
        except Exception as e:
            logger.error(f"WG-Gesucht scraping failed: {str(e)}")
            return []

    def scrape_ebay_kleinanzeigen(self, city: str, max_price: int = None) -> List[Dict[str, Any]]:
        """Scrape eBay Kleinanzeigen"""
        logger.info(f"🏠 Scraping eBay Kleinanzeigen for {city}")
        
        try:
            base_url = f"https://www.kleinanzeigen.de/s-mietwohnung/{quote(city)}/c203"
            if max_price:
                base_url += f"?priceType=FIXED&minPrice=&maxPrice={max_price}"
                
            response = self._safe_request(base_url)
            
            if not response:
                return []
                
            soup = BeautifulSoup(response.content, 'html.parser')
            listings = []
            
            # Find property listings
            ads = soup.find_all(['article', 'div'], class_=re.compile(r'ad-listitem|aditem'))
            
            for ad in ads[:8]:  # Limit results
                try:
                    title_elem = ad.find(['h2', 'a'], class_=re.compile(r'title|ellipsis'))
                    title = self._clean_text(title_elem.get_text()) if title_elem else "Wohnung"
                    
                    price_elem = ad.find(['strong', 'span'], class_=re.compile(r'price'))
                    price = self._extract_price(price_elem.get_text()) if price_elem else None
                    
                    link_elem = ad.find('a', href=True)
                    link = urljoin("https://www.kleinanzeigen.de", link_elem['href']) if link_elem else None
                    
                    location_elem = ad.find(['div', 'span'], class_=re.compile(r'aditem-addon'))
                    location = self._clean_text(location_elem.get_text()) if location_elem else city
                    
                    listing = {
                        'source': 'eBay Kleinanzeigen',
                        'title': title,
                        'price': price,
                        'area': None,
                        'location': location,
                        'city': city,
                        'link': link,
                        'currency': 'EUR',
                        'property_type': 'wohnung',
                        'scraped_at': time.time()
                    }
                    
                    if price and title != "Wohnung":
                        listings.append(listing)
                        
                except Exception as e:
                    logger.error(f"Error parsing eBay Kleinanzeigen item: {str(e)}")
                    continue
                    
            logger.info(f"✅ eBay Kleinanzeigen: Found {len(listings)} listings")
            return listings
            
        except Exception as e:
            logger.error(f"eBay Kleinanzeigen scraping failed: {str(e)}")
            return []

    def search_all_sources(self, city: str, max_price: int = None, property_type: str = "wohnung") -> List[Dict[str, Any]]:
        """Search all sources and combine results"""
        logger.info(f"🔍 Starting comprehensive search for {city}, max price: {max_price}, type: {property_type}")
        
        all_listings = []
        
        # Scrape all sources
        sources = [
            self.scrape_immoscout24,
            self.scrape_immobilien_de,
            self.scrape_wg_gesucht,
            self.scrape_ebay_kleinanzeigen
        ]
        
        for scraper_func in sources:
            try:
                if scraper_func == self.scrape_immoscout24:
                    listings = scraper_func(city, max_price, property_type)
                else:
                    listings = scraper_func(city, max_price)
                all_listings.extend(listings)
                
                # Small delay between sources
                time.sleep(random.uniform(1, 3))
                
            except Exception as e:
                logger.error(f"Error in {scraper_func.__name__}: {str(e)}")
                continue
        
        # Filter by max_price if specified
        if max_price:
            all_listings = [listing for listing in all_listings 
                          if listing.get('price') and listing['price'] <= max_price]
        
        # Sort by price (ascending)
        all_listings.sort(key=lambda x: x.get('price', float('inf')))
        
        logger.info(f"🎉 Total found: {len(all_listings)} listings from all sources")
        
        return all_listings

# Initialize global scraper instance
housing_scraper = GermanHousingScraper()
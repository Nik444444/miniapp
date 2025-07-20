"""
🧠 HOUSING AI SERVICE
AI-анализ объявлений недвижимости с детектором мошенничества и ценовой аналитикой
"""

import logging
from typing import Dict, Any, List, Optional
import time
import json
import re
from modern_llm_manager import modern_llm_manager

logger = logging.getLogger(__name__)

class HousingAIService:
    def __init__(self):
        self.scam_keywords = [
            'western union', 'moneygram', 'paypal', 'bitcoin', 'cryptocurrency',
            'advance payment', 'vorauszahlung ohne besichtigung', 'sofortzahlung',
            'agent in london', 'agent abroad', 'key by post', 'schlüssel per post',
            'ich bin im ausland', 'bin nicht in deutschland', 'unable to meet',
            'send money first', 'geld zuerst senden', 'no viewing possible',
            'keine besichtigung möglich', 'pay before viewing', 'zahlen vor besichtigung'
        ]
        
        self.suspicious_price_threshold = 0.3  # 30% below market average
        
    def analyze_listing_for_scam(self, listing: Dict[str, Any], market_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analyze listing for scam indicators"""
        try:
            scam_score = 0
            warnings = []
            details = []
            
            title = listing.get('title', '').lower()
            price = listing.get('price')
            area = listing.get('area')
            source = listing.get('source', '')
            location = listing.get('location', '').lower()
            
            # 1. Keyword Analysis
            for keyword in self.scam_keywords:
                if keyword in title:
                    scam_score += 25
                    warnings.append(f"🚨 Подозрительное ключевое слово: '{keyword}'")
                    details.append(f"Scam keyword detected: {keyword}")
            
            # 2. Price Analysis
            if price and area and area > 0:
                price_per_sqm = price / area
                
                # Unrealistically low price per sqm (varies by city)
                if price_per_sqm < 8:  # Less than 8 EUR/sqm is very suspicious
                    scam_score += 30
                    warnings.append(f"🚨 Подозрительно низкая цена: {price_per_sqm:.2f}€/м²")
                    details.append(f"Extremely low price per sqm: {price_per_sqm:.2f}")
                elif price_per_sqm < 12:  # Less than 12 EUR/sqm is suspicious
                    scam_score += 15
                    warnings.append(f"⚠️ Очень низкая цена: {price_per_sqm:.2f}€/м²")
                    details.append(f"Very low price per sqm: {price_per_sqm:.2f}")
            
            # 3. Market Context Analysis
            if market_context and price:
                avg_price = market_context.get('average_price')
                if avg_price and price < (avg_price * (1 - self.suspicious_price_threshold)):
                    scam_score += 20
                    warnings.append(f"⚠️ Цена на {((avg_price - price) / avg_price * 100):.0f}% ниже рынка")
                    details.append(f"Price significantly below market average")
            
            # 4. Source Reliability
            if source == 'eBay Kleinanzeigen':
                scam_score += 5  # Slightly higher risk
                details.append("Higher risk source")
            
            # 5. Location Analysis
            if any(word in location for word in ['fake', 'scam', 'temporary']):
                scam_score += 20
                warnings.append("🚨 Подозрительная локация")
            
            # Determine risk level
            if scam_score >= 50:
                risk_level = "ВЫСОКИЙ"
                risk_color = "🔴"
                recommendation = "НЕ РЕКОМЕНДУЕМ - Высокий риск мошенничества!"
            elif scam_score >= 25:
                risk_level = "СРЕДНИЙ"
                risk_color = "🟡"
                recommendation = "Будьте осторожны - проверьте дополнительно"
            elif scam_score >= 10:
                risk_level = "НИЗКИЙ"
                risk_color = "🟠"
                recommendation = "Скорее всего безопасно, но проявите бдительность"
            else:
                risk_level = "МИНИМАЛЬНЫЙ"
                risk_color = "🟢"
                recommendation = "Выглядит надежно"
            
            return {
                'scam_score': min(scam_score, 100),
                'risk_level': risk_level,
                'risk_color': risk_color,
                'recommendation': recommendation,
                'warnings': warnings,
                'details': details,
                'analysis_time': time.time()
            }
            
        except Exception as e:
            logger.error(f"Scam analysis failed: {str(e)}")
            return {
                'scam_score': 0,
                'risk_level': "НЕ ОПРЕДЕЛЕН",
                'risk_color': "⚪",
                'recommendation': "Анализ недоступен",
                'warnings': [],
                'details': ['Analysis failed'],
                'analysis_time': time.time()
            }
    
    def analyze_neighborhood(self, city: str, district: str = None, user_providers: Dict = None) -> Dict[str, Any]:
        """AI-анализ района с помощью LLM"""
        try:
            if not user_providers:
                logger.info("No user API keys available for neighborhood analysis")
                return self._get_demo_neighborhood_analysis(city, district)
            
            prompt = f"""
Проанализируйте район для проживания в Германии:

Город: {city}
Район: {district or 'центральная часть'}

Пожалуйста, предоставьте анализ по следующим критериям:

1. БЕЗОПАСНОСТЬ (оценка 1-10):
- Уровень преступности
- Безопасность для пешеходов
- Освещение улиц

2. ИНФРАСТРУКТУРА (оценка 1-10):
- Общественный транспорт
- Магазины и супермаркеты
- Медицинские учреждения
- Школы и детские сады

3. СТОИМОСТЬ ЖИЗНИ (оценка 1-10):
- Цены на продукты
- Цены на услуги
- Общая доступность

4. КАЧЕСТВО ЖИЗНИ (оценка 1-10):
- Зеленые зоны и парки
- Культурная жизнь
- Рестораны и кафе
- Спортивные объекты

5. ПЕРСПЕКТИВЫ РАЗВИТИЯ:
- Планируемые проекты
- Инвестиции в район
- Тенденции цен на недвижимость

Отвечайте на русском языке. Будьте конкретными и практичными.
"""
            
            # Try to get AI analysis
            response = modern_llm_manager.generate_content(
                prompt=prompt,
                **user_providers
            )
            
            if response and len(response) > 100:
                return {
                    'status': 'success',
                    'analysis': response,
                    'ai_powered': True,
                    'analysis_time': time.time()
                }
            else:
                logger.warning("AI analysis returned insufficient content")
                return self._get_demo_neighborhood_analysis(city, district)
                
        except Exception as e:
            logger.error(f"Neighborhood AI analysis failed: {str(e)}")
            return self._get_demo_neighborhood_analysis(city, district)
    
    def _get_demo_neighborhood_analysis(self, city: str, district: str = None) -> Dict[str, Any]:
        """Демо анализ района"""
        area_name = district or city
        
        demo_analysis = f"""
🏙️ АНАЛИЗ РАЙОНА: {area_name.upper()}

🔒 БЕЗОПАСНОСТЬ: 7/10
• Средний уровень безопасности для немецкого города
• Хорошее освещение основных улиц
• Регулярное патрулирование полицией

🚇 ИНФРАСТРУКТУРА: 8/10
• Отличная связь общественным транспортом
• Множество супермаркетов в пешей доступности
• Медицинские центры и аптеки рядом
• Школы и детские сады в районе

💰 СТОИМОСТЬ ЖИЗНИ: 6/10
• Средние цены для региона
• Доступные продуктовые магазины
• Разнообразие ценовых категорий

🌳 КАЧЕСТВО ЖИЗНИ: 7/10
• Парки и зеленые зоны для отдыха
• Кафе и рестораны различной кухни
• Спортивные объекты и фитнес-центры
• Активная культурная жизнь

📈 ПЕРСПЕКТИВЫ РАЗВИТИЯ:
• Район активно развивается
• Планируются новые транспортные проекты
• Умеренный рост цен на недвижимость ожидается

⭐ РЕКОМЕНДАЦИЯ: Подходящий район для проживания с хорошим балансом цены и качества жизни.
"""
        
        return {
            'status': 'demo',
            'analysis': demo_analysis,
            'ai_powered': False,
            'analysis_time': time.time()
        }
    
    def calculate_total_living_costs(self, listing: Dict[str, Any], city: str) -> Dict[str, Any]:
        """Калькулятор полной стоимости проживания"""
        try:
            base_rent = listing.get('price', 0)
            if not base_rent:
                return {'error': 'No price information available'}
            
            # Typical German additional costs
            costs = {
                'base_rent': base_rent,
                'nebenkosten': round(base_rent * 0.25),  # 25% of base rent
                'internet': 35,  # Average internet cost
                'electricity': round(base_rent * 0.15),  # ~15% of base rent
                'insurance': 25,  # Basic personal insurance
                'broadcasting_fee': 18.36,  # GEZ fee
            }
            
            # City-specific adjustments
            city_multiplier = self._get_city_cost_multiplier(city.lower())
            adjusted_costs = {k: round(v * city_multiplier) if k != 'broadcasting_fee' else v 
                            for k, v in costs.items()}
            
            total_monthly = sum(adjusted_costs.values())
            
            # Kaution (deposit) - typically 2-3 months rent
            kaution = base_rent * 3
            
            return {
                'monthly_costs': adjusted_costs,
                'total_monthly': total_monthly,
                'kaution_deposit': kaution,
                'first_month_total': total_monthly + kaution,
                'city_multiplier': city_multiplier,
                'calculation_time': time.time(),
                'currency': 'EUR'
            }
            
        except Exception as e:
            logger.error(f"Cost calculation failed: {str(e)}")
            return {'error': 'Cost calculation unavailable'}
    
    def _get_city_cost_multiplier(self, city: str) -> float:
        """Get cost multiplier based on city"""
        expensive_cities = {
            'münchen': 1.4, 'munich': 1.4,
            'frankfurt': 1.3,
            'hamburg': 1.2,
            'köln': 1.1, 'cologne': 1.1,
            'düsseldorf': 1.2,
            'stuttgart': 1.2,
            'berlin': 1.15,
        }
        
        moderate_cities = {
            'dresden': 0.9,
            'leipzig': 0.85,
            'hannover': 0.95,
            'bremen': 0.9,
            'nürnberg': 0.95, 'nuremberg': 0.95,
        }
        
        affordable_cities = {
            'chemnitz': 0.7,
            'magdeburg': 0.75,
            'erfurt': 0.8,
            'rostock': 0.8,
        }
        
        city = city.lower()
        
        if city in expensive_cities:
            return expensive_cities[city]
        elif city in moderate_cities:
            return moderate_cities[city]
        elif city in affordable_cities:
            return affordable_cities[city]
        else:
            return 1.0  # Default multiplier
    
    def generate_landlord_message(self, listing: Dict[str, Any], user_info: Dict[str, Any], user_providers: Dict = None) -> Dict[str, Any]:
        """Generate personalized message to landlord"""
        try:
            if not user_providers:
                return self._get_demo_landlord_message(listing, user_info)
            
            title = listing.get('title', 'die Wohnung')
            location = listing.get('location', '')
            price = listing.get('price', 'N/A')
            
            user_name = user_info.get('name', 'Interessent')
            user_occupation = user_info.get('occupation', 'Angestellter')
            user_income = user_info.get('income', 'stabiles Einkommen')
            
            prompt = f"""
Создайте профессиональное письмо арендодателю на немецком языке для следующей квартиры:

Объявление: {title}
Локация: {location}
Цена: {price}€

Информация о кандидате:
- Имя: {user_name}
- Профессия: {user_occupation}
- Доход: {user_income}

Письмо должно включать:
1. Вежливое обращение
2. Краткое представление себя
3. Выражение заинтересованности в квартире
4. Упоминание финансовой стабильности
5. Просьбу о просмотре
6. Вежливое завершение

Письмо должно быть:
- На немецком языке
- Профессиональным и вежливым
- Кратким (не более 150 слов)
- Убедительным

После немецкого текста предоставьте русский перевод.
"""
            
            response = modern_llm_manager.generate_content(
                prompt=prompt,
                **user_providers
            )
            
            if response and len(response) > 50:
                return {
                    'status': 'success',
                    'message': response,
                    'ai_powered': True,
                    'generation_time': time.time()
                }
            else:
                return self._get_demo_landlord_message(listing, user_info)
                
        except Exception as e:
            logger.error(f"Landlord message generation failed: {str(e)}")
            return self._get_demo_landlord_message(listing, user_info)
    
    def _get_demo_landlord_message(self, listing: Dict[str, Any], user_info: Dict[str, Any]) -> Dict[str, Any]:
        """Demo landlord message"""
        title = listing.get('title', 'die Wohnung')
        price = listing.get('price', 'N/A')
        user_name = user_info.get('name', 'Name')
        
        demo_message = f"""
НЕМЕЦКИЙ ТЕКСТ:

Sehr geehrte Damen und Herren,

ich interessiere mich sehr für Ihre Wohnung "{title}" zum Preis von {price}€.

Ich bin {user_name}, arbeite als Fachkraft mit stabilem Einkommen und suche eine langfristige Mietwohnung. Gerne würde ich die Wohnung besichtigen und alle notwendigen Unterlagen (Schufa, Gehaltsnachweis, etc.) vorlegen.

Wären Sie für einen Besichtigungstermin verfügbar?

Mit freundlichen Grüßen,
{user_name}

---

РУССКИЙ ПЕРЕВОД:

Уважаемые дамы и господа,

я очень заинтересован в вашей квартире "{title}" по цене {price}€.

Я {user_name}, работаю как специалист со стабильным доходом и ищу долгосрочную арендованную квартиру. С удовольствием осмотрю квартиру и предоставлю все необходимые документы (Schufa, справка о зарплате и т.д.).

Были бы вы доступны для назначения встречи для осмотра?

С дружескими приветствиями,
{user_name}
"""
        
        return {
            'status': 'demo',
            'message': demo_message,
            'ai_powered': False,
            'generation_time': time.time()
        }

# Initialize global service
housing_ai_service = HousingAIService()
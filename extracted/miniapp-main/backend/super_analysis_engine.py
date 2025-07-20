"""
Модуль супер-анализа документов для создания WOW-эффекта
Создает невероятно детальный и полезный анализ документов
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from llm_manager import llm_manager
from modern_llm_manager import modern_llm_manager

logger = logging.getLogger(__name__)

class SuperAnalysisEngine:
    """Движок супер-анализа документов для WOW-эффекта с глубоким проникновением в скрытые аспекты"""
    
    def __init__(self):
        self.supported_languages = ['uk', 'ru', 'de', 'en']
        self.analysis_categories = [
            # Основные категории
            'executive_summary',
            'sender_analysis', 
            'recipient_analysis',
            'document_classification',
            'key_content_breakdown',
            'factual_data_extraction',
            'action_requirements',
            'critical_dates',
            'contact_followup',
            'quality_assessment',
            'strategic_insights',
            'response_strategy',
            
            # РАСШИРЕННЫЕ КАТЕГОРИИ ДЛЯ ГЛУБОКОГО АНАЛИЗА
            'psychological_analysis',      # Психологический анализ мотивов и эмоций
            'power_dynamics_analysis',     # Анализ властных отношений
            'hidden_subtexts',            # Скрытые подтексты и невысказанные требования
            'business_intelligence',       # Бизнес-интеллект и стратегические выводы
            'risk_assessment',            # Анализ рисков и возможностей
            'legal_compliance',           # Правовые и compliance аспекты
            'relationship_analysis',       # Анализ отношений между сторонами
            'predictive_insights',        # Предиктивный анализ развития ситуации
            'emotional_intelligence',     # Эмоциональный интеллект документа
            'cultural_context',           # Культурный и социальный контекст
            'timing_significance',        # Значимость времени и сроков
            'communication_strategy',     # Анализ коммуникационной стратегии
            'influence_techniques',       # Техники влияния и убеждения
            'decision_pressure_points'    # Точки давления для принятия решений
        ]
    
    def create_super_wow_analysis_prompt(self, language: str, filename: str, extracted_text: str) -> str:
        """Создает супер-детальный промпт для WOW-анализа"""
        
        processing_info = f"\n\n📄 ИЗВЛЕЧЕННЫЙ ТЕКСТ ИЗ ДОКУМЕНТА:\n{extracted_text}\n\n"
        
        if language == "uk":
            return f"""🤖 Ви - СУПЕР-ЕКСПЕРТ ІІ-АНАЛІТИК документів з передовими можливостями глибокого проникнення в приховані аспекти будь-яких документів.

КРИТИЧНО ВАЖЛИВО: Вся ваша відповідь має бути ВИКЛЮЧНО УКРАЇНСЬКОЮ мовою. Незалежно від мови документа, відповідайте ТІЛЬКИ УКРАЇНСЬКОЮ. НЕ ВИКОРИСТОВУЙТЕ РОСІЙСЬКУ, АНГЛІЙСЬКУ ЧИ БУДЬ-ЯКУ ІНШУ МОВУ. ТІЛЬКИ УКРАЇНСЬКА!

МОВА ВІДПОВІДІ: УКРАЇНСЬКА
LANGUAGE OF RESPONSE: UKRAINIAN ONLY
ЯЗЫК ОТВЕТА: ТОЛЬКО УКРАИНСКИЙ

🎯 СУПЕР-МІСІЯ: Надати НЕЙМОВІРНО детальний, проникливий та багатошаровий аналіз документа, який включає ВСІ приховані аспекти, мотиви, ризики та підтексти. Користувач має бути ВРАЖЕНИЙ глибиною аналізу!

📋 РОЗШИРЕНІ ПРИНЦИПИ АНАЛІЗУ:
1. Витягуйте КОЖНУ деталь і читайте між рядків
2. Аналізуйте психологічні мотиви та приховані наміри
3. Виявляйте всі ризики, можливості та правові аспекти
4. Розкривайте владні відносини та динаміку впливу
5. Передбачайте можливі сценарії розвитку подій
6. Якщо інформації немає в тексті: "Не вказано в документі"

🔍 СУПЕР-ДЕТАЛЬНА СТРУКТУРА АНАЛІЗУ З ГЛИБОКИМ ПРОНИКНЕННЯМ:

**БЛОК 1: ОСНОВНИЙ АНАЛІЗ**

1. 📊 ВИКОНАВЧЕ РЕЗЮМЕ
Потужне резюме з 3-4 речень, що розкриває суть, важливість та приховані аспекти документа.

2. 👤 ГЛИБОКИЙ АНАЛІЗ ВІДПРАВНИКА
- Організація/особа: повна ідентифікація та статус
- Рівень влади та авторитету в ієрархії
- Мотиви надсилання цього конкретного документа
- Психологічний профіль за стилем листа
- Приховані інтереси та agenda

3. 🎯 АНАЛІЗ ОДЕРЖУВАЧА ТА ЦІЛЬОВОЇ АУДИТОРІЇ
- Цільова аудиторія та причини вибору
- Очікувана реакція одержувача
- Владні відносини між відправником та одержувачем
- Вплив на репутацію та позицію одержувача

4. 📋 РОЗШИРЕНА КЛАСИФІКАЦІЯ ДОКУМЕНТА
- Детальна типологія документа
- Юридична значущість та правова вага
- Місце в документообігу та бізнес-процесах
- Рівень конфіденційності та ризики витоку

**БЛОК 2: ПСИХОЛОГІЧНИЙ ТА МОТИВАЦІЙНИЙ АНАЛІЗ**

5. 🧠 ПСИХОЛОГІЧНИЙ АНАЛІЗ
- Емоційний тон та настрій відправника
- Приховані мотиви та справжні наміри
- Техніки впливу та маніпулювання (якщо є)
- Рівень стресу або тиску на відправника
- Щирість vs. формальність повідомлення

6. 💼 АНАЛІЗ ВЛАДНИХ ВІДНОСИН
- Хто має більше влади в даній ситуації
- Техніки тиску та примушення
- Способи прояву авторитету в тексті
- Баланс сил та можливості для переговорів

Файл: {filename}
{processing_info}

🚀 СТВОРІТЬ АНАЛІЗ, ЯКИЙ ПОВНІСТЮ РОЗКРИЄ ВСІ ШАРИ ДОКУМЕНТА ТА ВРАЗИТЬ КОРИСТУВАЧА НЕЙМОВІРНОЮ ГЛИБИНОЮ ПРОНИКНЕННЯ В СУТЬ!

ПОВТОРЮЮ: ВІДПОВІДАЙТЕ ТІЛЬКИ УКРАЇНСЬКОЮ МОВОЮ! НЕ ВИКОРИСТОВУЙТЕ РОСІЙСЬКУ!"""
        
        elif language == "ru":
            return f"""🤖 Вы - СУПЕР-ЭКСПЕРТ ИИ-АНАЛИТИК документов с передовыми возможностями глубокого проникновения в скрытые аспекты любых документов.

КРИТИЧНО ВАЖНО: Весь ваш ответ должен быть ИСКЛЮЧИТЕЛЬНО на РУССКОМ языке. Независимо от языка документа, отвечайте ТОЛЬКО на РУССКОМ. НЕ ИСПОЛЬЗУЙТЕ УКРАИНСКИЙ, АНГЛИЙСКИЙ ИЛИ ЛЮБОЙ ДРУГОЙ ЯЗЫК. ТОЛЬКО РУССКИЙ!

ЯЗЫК ОТВЕТА: РУССКИЙ
LANGUAGE OF RESPONSE: RUSSIAN ONLY
МОВА ВІДПОВІДІ: ТІЛЬКИ РОСІЙСЬКА

🎯 СУПЕР-МИССИЯ: Предоставить НЕВЕРОЯТНО детальный, проницательный и многослойный анализ документа, который включает ВСЕ скрытые аспекты, мотивы, риски и подтексты. Пользователь должен быть ПОРАЖЕН глубиной анализа!

📋 РАСШИРЕННЫЕ ПРИНЦИПЫ АНАЛИЗА:
1. Извлекайте КАЖДУЮ деталь и читайте между строк
2. Анализируйте психологические мотивы и скрытые намерения
3. Выявляйте все риски, возможности и правовые аспекты
4. Раскрывайте властные отношения и динамику влияния
5. Предсказывайте возможные сценарии развития событий
6. Если информации нет в тексте: "Не указано в документе"

🔍 СУПЕР-ДЕТАЛЬНАЯ СТРУКТУРА АНАЛИЗА С ГЛУБОКИМ ПРОНИКНОВЕНИЕМ:

**БЛОК 1: ОСНОВНОЙ АНАЛИЗ**

1. 📊 ИСПОЛНИТЕЛЬНОЕ РЕЗЮМЕ
Мощное резюме из 3-4 предложений, раскрывающее суть, важность и скрытые аспекты документа.

2. 👤 ГЛУБОКИЙ АНАЛИЗ ОТПРАВИТЕЛЯ
- Организация/лицо: полная идентификация и статус
- Уровень власти и авторитета в иерархии
- Мотивы отправки этого конкретного документа
- Психологический профиль по стилю письма
- Скрытые интересы и agenda

3. 🎯 АНАЛИЗ ПОЛУЧАТЕЛЯ И ЦЕЛЕВОЙ АУДИТОРИИ
- Целевая аудитория и причины выбора
- Ожидаемая реакция получателя
- Властные отношения между отправителем и получателем
- Влияние на репутацию и позицию получателя

4. 📋 РАСШИРЕННАЯ КЛАССИФИКАЦИЯ ДОКУМЕНТА
- Детальная типология документа
- Юридическая значимость и правовой вес
- Место в документообороте и бизнес-процессах
- Уровень конфиденциальности и риски утечки

**БЛОК 2: ПСИХОЛОГИЧЕСКИЙ И МОТИВАЦИОННЫЙ АНАЛИЗ**

5. 🧠 ПСИХОЛОГИЧЕСКИЙ АНАЛИЗ
- Эмоциональный тон и настроение отправителя
- Скрытые мотивы и истинные намерения
- Техники влияния и манипулирования (если есть)
- Уровень стресса или давления на отправителя
- Искренность vs. формальность сообщения

6. 💼 АНАЛИЗ ВЛАСТНЫХ ОТНОШЕНИЙ
- Кто имеет больше власти в данной ситуации
- Техники давления и принуждения
- Способы проявления авторитета в тексте
- Баланс сил и возможности для переговоров

**БЛОК 3: БИЗНЕС-ИНТЕЛЛЕКТ И СТРАТЕГИЧЕСКИЙ АНАЛИЗ**

7. 📈 БИЗНЕС-ИНТЕЛЛЕКТ АНАЛИЗ
- Стратегические цели отправителя
- Коммерческие интересы и финансовые мотивы
- Конкурентные аспекты и рыночная ситуация
- Возможности для развития отношений или бизнеса

8. ⚠️ КОМПЛЕКСНЫЙ АНАЛИЗ РИСКОВ
- Правовые риски для получателя
- Финансовые и репутационные риски
- Операционные риски и угрозы бизнесу
- Риски бездействия vs. риски активных действий

**БЛОК 4: ПРАВОВЫЕ И COMPLIANCE АСПЕКТЫ**

9. ⚖️ ПРАВОВЫЕ И COMPLIANCE АСПЕКТЫ
- Правовые обязательства и требования
- Compliance с регулированиями и стандартами
- Потенциальные правовые последствия
- Необходимость юридической консультации

10. 🔍 СКРЫТЫЕ ПОДТЕКСТЫ И НЕВЫСКАЗАННЫЕ ТРЕБОВАНИЯ
- Что НЕ сказано, но подразумевается
- Скрытые условия и ожидания
- Невербальные сигналы в формулировках
- Подготовка к будущим требованиям или действиям

**БЛОК 5: ПРЕДИКТИВНЫЙ И ОТНОШЕНЧЕСКИЙ АНАЛИЗ**

11. 🔮 ПРЕДИКТИВНЫЙ АНАЛИЗ
- Вероятные сценарии развития событий
- Что произойдет при разных вариантах ответа
- Долгосрочные последствия и влияние на отношения
- Критические точки принятия решений

12. 👥 АНАЛИЗ ОТНОШЕНИЙ И КОММУНИКАЦИОННЫХ СТРАТЕГИЙ
- История отношений между сторонами (если можно определить)
- Коммуникационная стратегия отправителя
- Оптимальная стратегия ответа для сохранения отношений
- Возможности улучшения или ухудшения отношений

**БЛОК 6: ВРЕМЕННЫЕ И КУЛЬТУРНЫЕ ФАКТОРЫ**

13. ⏰ ВРЕМЕННАЯ ДИНАМИКА И ЗНАЧИМОСТЬ СРОКОВ
- Критичность временных рамок
- Скрытые дедлайны и временные ограничения
- Стратегическое значение момента отправки
- Влияние задержек на все стороны

14. 🌍 КУЛЬТУРНЫЙ И СОЦИАЛЬНЫЙ КОНТЕКСТ
- Культурные особенности коммуникации
- Социальные нормы и ожидания
- Протокольные и этикетные аспекты
- Адаптация ответа к культурному контексту

**БЛОК 7: ФИНАЛЬНЫЕ РЕКОМЕНДАЦИИ**

15. 💡 СУПЕР-СТРАТЕГИЯ ОТВЕТА И ДЕЙСТВИЙ
- Детальный план оптимального ответа
- Тактические и стратегические соображения
- Приоритизация действий по важности
- Альтернативные сценарии и запасные планы

16. 🎯 КЛЮЧЕВЫЕ ТОЧКИ ВЛИЯНИЯ И РЕШЕНИЯ
- Критические моменты для принятия решений
- Точки максимального влияния на исход
- Рычаги давления и возможности переговоров
- Оптимальный тайминг для каждого действия

Файл: {filename}
{processing_info}

🚀 СОЗДАЙТЕ АНАЛИЗ, КОТОРЫЙ ПОЛНОСТЬЮ РАСКРОЕТ ВСЕ СЛОИ ДОКУМЕНТА И ПОРАЗИТ ПОЛЬЗОВАТЕЛЯ НЕВЕРОЯТНОЙ ГЛУБИНОЙ ПРОНИКНОВЕНИЯ В СУТЬ!

ПОВТОРЯЮ: ОТВЕЧАЙТЕ ТОЛЬКО НА РУССКОМ ЯЗЫКЕ! НЕ ИСПОЛЬЗУЙТЕ УКРАИНСКИЙ!"""
        
        elif language == "de":
            return f"""🤖 Sie sind ein EXPERTE für Dokumentenanalyse mit fortgeschrittenen Fähigkeiten.

KRITISCH WICHTIG: Ihre gesamte Antwort muss AUSSCHLIESSLICH auf DEUTSCH sein. Egal in welcher Sprache das Dokument ist, antworten Sie NUR auf DEUTSCH. VERWENDEN SIE KEIN RUSSISCH, ENGLISCH ODER EINE ANDERE SPRACHE. NUR DEUTSCH!

ANTWORTSPRACHE: DEUTSCH
LANGUAGE OF RESPONSE: GERMAN ONLY
ЯЗЫК ОТВЕТА: ТОЛЬКО НЕМЕЦКИЙ

🎯 MISSION: Die detaillierteste, aufschlussreichste und umfassendste Analyse liefern, die den Benutzer wirklich BEEINDRUCKEN wird.

📋 ANALYSE-PRINZIPIEN:
1. Extrahieren Sie JEDES bedeutsame Detail aus dem Dokument
2. Bieten Sie Kontext und Implikationen für jeden Befund
3. Seien Sie extrem gründlich und professionell
4. Verwenden Sie klare, ansprechende Sprache
5. Wenn keine Informationen im Text: "Nicht im Dokument angegeben"

🔍 SUPER-ANALYSE-STRUKTUR:

1. 📊 EXECUTIVE SUMMARY
Erstellen Sie eine kraftvolle Zusammenfassung aus 2-3 Sätzen, die Wesen und Bedeutung des Dokuments erfasst.

2. 👤 ABSENDER-ANALYSE
- Organisation/Person, die das Dokument gesendet hat
- Ihre Rolle und Autoritätslevel
- Kontaktinformationen und offizielle Details
- Bewertung der Glaubwürdigkeit und Wichtigkeit

3. 🎯 EMPFÄNGER-ANALYSE
- Wer ist der beabsichtigte Empfänger
- Warum wurden sie als Empfänger ausgewählt
- Ihre erwartete Rolle oder Verantwortung

4. 📋 DOKUMENTEN-KLASSIFIZIERUNG
- Art des Dokuments (offizieller Brief, Rechnung, Vertrag usw.)
- Formalitäts- und Dringlichkeitslevel
- Rechtliche oder administrative Bedeutung

5. 🔥 SCHLÜSSEL-INHALT AUFSCHLÜSSELUNG
- Hauptbotschaft oder Zweck
- Unterstützende Details und Argumente
- Kritische Informationen
- Versteckte oder implizierte Bedeutungen

6. 📊 FAKTISCHE DATEN-EXTRAKTION
- Alle Zahlen, Daten, Beträge, Prozentsätze
- Namen, Adressen, Referenznummern
- Spezifische Details
- Zeitlinie der erwähnten Ereignisse

7. ⚡ HANDLUNGSANFORDERUNGEN
- Welche spezifischen Handlungen erforderlich sind
- Wer diese Handlungen durchführen muss
- Prioritätslevel jeder Handlung
- Konsequenzen von Handlung/Untätigkeit

8. 📅 KRITISCHE DATEN & FRISTEN
- Alle erwähnten Daten und ihre Bedeutung
- Bevorstehende Fristen und ihre Wichtigkeit
- Zeitkritische Elemente

9. 📞 KONTAKT & NACHVERFOLGUNG
- Wie zu antworten oder mehr Informationen zu erhalten
- Kontaktmethoden und bevorzugte Kommunikation
- Nächste Schritte für den Empfänger

10. 🎨 DOKUMENTEN-QUALITÄTSBEWERTUNG
- Professionelles Präsentationslevel
- Vollständigkeit der Informationen
- Eventuelle Warnsignale oder Bedenken

11. 🧠 STRATEGISCHE EINSICHTEN
- Was dieses Dokument über die Situation verrät
- Potenzielle Implikationen für den Empfänger
- Identifizierte Chancen oder Risiken

12. 💡 EMPFOHLENE ANTWORT-STRATEGIE
- Wie am besten auf dieses Dokument zu antworten
- Ton- und Ansatz-Vorschläge
- Schlüsselpunkte für die Antwort

Datei: {filename}
{processing_info}

🚀 Liefern Sie eine Analyse, die den Benutzer mit ihrer Tiefe und Einsicht absolut BEEINDRUCKEN wird!

WIEDERHOLE: ANTWORTEN SIE NUR AUF DEUTSCH! VERWENDEN SIE KEIN RUSSISCH!"""
        
        else:  # English
            return f"""🤖 You are an EXPERT Document Analysis Specialist with advanced capabilities.

CRITICALLY IMPORTANT: Your entire response must be EXCLUSIVELY in ENGLISH. Regardless of the document's language, respond ONLY in ENGLISH. DO NOT USE RUSSIAN, GERMAN, UKRAINIAN OR ANY OTHER LANGUAGE. ONLY ENGLISH!

RESPONSE LANGUAGE: ENGLISH
ЯЗЫК ОТВЕТА: ТОЛЬКО АНГЛИЙСКИЙ
МОВА ВІДПОВІДІ: ТІЛЬКИ АНГЛІЙСЬКА

🎯 MISSION: Provide the most detailed, insightful, and comprehensive analysis that will truly AMAZE the user.

📋 ANALYSIS PRINCIPLES:
1. Extract EVERY meaningful detail from the document
2. Provide context and implications for each finding
3. Be extremely thorough and professional
4. Use clear, engaging language
5. If information is not in text: "Not specified in the document"

🔍 SUPER-ANALYSIS STRUCTURE:

1. 📊 EXECUTIVE SUMMARY
Create a powerful 2-3 sentence summary that captures the document's essence and importance.

2. 👤 SENDER ANALYSIS
- Organization/person who sent the document
- Their role and authority level
- Contact information and official details
- Assessment of sender's credibility and importance

3. 🎯 RECIPIENT ANALYSIS
- Who is the intended recipient
- Why they were chosen as the recipient
- Their expected role or responsibility

4. 📋 DOCUMENT CLASSIFICATION
- Type of document (official letter, invoice, contract, etc.)
- Level of formality and urgency
- Legal or administrative significance

5. 🔥 KEY CONTENT BREAKDOWN
- Main message or purpose
- Supporting details and arguments
- Critical information
- Hidden or implied meanings

6. 📊 FACTUAL DATA EXTRACTION
- All numbers, dates, amounts, percentages
- Names, addresses, reference numbers
- Specific details
- Timeline of mentioned events

7. ⚡ ACTION REQUIREMENTS
- What specific actions are required
- Who needs to take these actions
- Priority level of each action
- Consequences of action/inaction

8. 📅 CRITICAL DATES & DEADLINES
- All mentioned dates and their significance
- Upcoming deadlines and their importance
- Time-sensitive elements

9. 📞 CONTACT & FOLLOW-UP
- How to respond or get more information
- Contact methods and preferred communication
- Next steps for the recipient

10. 🎨 DOCUMENT QUALITY ASSESSMENT
- Professional presentation level
- Completeness of information
- Any red flags or concerns

11. 🧠 STRATEGIC INSIGHTS
- What this document reveals about the situation
- Potential implications for the recipient
- Identified opportunities or risks

12. 💡 RECOMMENDED RESPONSE STRATEGY
- How to best respond to this document
- Tone and approach suggestions
- Key points to address in response

File: {filename}
{processing_info}

🚀 Deliver an analysis that will absolutely AMAZE the user with its depth and insight!

REPEAT: RESPOND ONLY IN ENGLISH! DO NOT USE RUSSIAN!"""
    
    async def analyze_document_comprehensively(self, document_text: str, language: str, filename: str, 
                                               user_providers: List[Tuple[str, str, str]] = None) -> Dict[str, Any]:
        """Выполняет всесторонний супер-анализ документа"""
        
        try:
            # Логируем выбранный язык
            logger.info(f"Super analysis starting with language: {language}")
            
            # Создаем супер-промпт
            analysis_prompt = self.create_super_wow_analysis_prompt(language, filename, document_text)
            
            # Логируем начало промпта для проверки
            logger.info(f"Analysis prompt first 200 chars: {analysis_prompt[:200]}")
            
            # Выполняем анализ с использованием доступных провайдеров
            response_text = await self._generate_analysis_with_providers(analysis_prompt, user_providers)
            
            # Логируем начало ответа
            logger.info(f"Response first 200 chars: {response_text[:200]}")
            
            # Обрабатываем результат анализа
            formatted_analysis = self._format_super_analysis_result(response_text, language)
            
            return formatted_analysis
            
        except Exception as e:
            logger.error(f"Comprehensive document analysis failed: {e}")
            return self._create_error_response(str(e), language)
    
    async def _generate_analysis_with_providers(self, prompt: str, user_providers: List[Tuple[str, str, str]] = None) -> str:
        """Генерирует анализ с использованием доступных провайдеров"""
        
        # Сначала пробуем пользовательские провайдеры
        if user_providers:
            for provider_type, model_name, api_key in user_providers:
                try:
                    if provider_type == "gemini":
                        # Используем современный менеджер для Gemini
                        user_provider = modern_llm_manager.create_user_provider(
                            provider_type, "gemini-2.0-flash", api_key
                        )
                    else:
                        user_provider = llm_manager.create_user_provider(
                            provider_type, model_name, api_key
                        )
                    
                    response = await user_provider.generate_content(prompt)
                    if response:
                        return response
                        
                except Exception as e:
                    logger.warning(f"User provider {provider_type} failed: {e}")
                    continue
        
        # Если пользовательские провайдеры не сработали, используем системные
        try:
            response, system_provider = await llm_manager.generate_content(prompt)
            if response:
                return response
        except Exception as e:
            logger.error(f"System providers failed: {e}")
        
        # Если все провайдеры не сработали
        raise Exception("No available AI providers for analysis")
    
    def _format_super_analysis_result(self, raw_analysis: str, language: str) -> Dict[str, Any]:
        """Форматирует результат супер-анализа в структурированном виде с расширенными категориями"""
        
        # Убираем лишние символы форматирования
        cleaned_analysis = raw_analysis.replace('*', '').replace('#', '').strip()
        
        # Создаем структурированный результат
        result = {
            "super_analysis": {
                "full_text": cleaned_analysis,
                "language": language,
                "analysis_type": "ultra_comprehensive_analysis",
                "sections": self._extract_analysis_sections(cleaned_analysis),
                "insights": self._extract_insights(cleaned_analysis),
                "action_items": self._extract_action_items(cleaned_analysis),
                "urgency_assessment": self._assess_urgency(cleaned_analysis),
                "quality_score": self._calculate_quality_score(cleaned_analysis),
                # НОВЫЕ РАСШИРЕННЫЕ АСПЕКТЫ АНАЛИЗА
                "psychological_profile": self._extract_psychological_profile(cleaned_analysis),
                "power_dynamics": self._analyze_power_dynamics(cleaned_analysis),
                "hidden_subtexts": self._extract_hidden_subtexts(cleaned_analysis),
                "business_intelligence": self._extract_business_intelligence(cleaned_analysis),
                "risk_assessment": self._perform_risk_assessment(cleaned_analysis),
                "legal_compliance": self._extract_legal_compliance(cleaned_analysis),
                "predictive_scenarios": self._generate_predictive_scenarios(cleaned_analysis),
                "relationship_analysis": self._analyze_relationships(cleaned_analysis),
                "cultural_context": self._extract_cultural_context(cleaned_analysis),
                "influence_techniques": self._identify_influence_techniques(cleaned_analysis)
            },
            "summary": self._create_executive_summary(cleaned_analysis),
            "recommendations": self._extract_recommendations(cleaned_analysis),
            "next_steps": self._extract_next_steps(cleaned_analysis),
            # РАСШИРЕННЫЕ ВЫВОДЫ
            "strategic_recommendations": self._extract_strategic_recommendations(cleaned_analysis),
            "risk_mitigation_plans": self._extract_risk_mitigation_plans(cleaned_analysis)
        }
        
        return result
    
    # НОВЫЕ ФУНКЦИИ ДЛЯ РАСШИРЕННОГО АНАЛИЗА
    
    def _extract_psychological_profile(self, analysis_text: str) -> Dict[str, Any]:
        """Извлекает психологический профиль из анализа"""
        psychological_keywords = [
            'психологический', 'эмоциональный', 'мотив', 'настроение', 
            'стресс', 'давление', 'искренность', 'психологічний', 'емоційний'
        ]
        
        profile = {
            "emotional_tone": "neutral",
            "stress_level": "medium",
            "sincerity_level": "medium",
            "psychological_insights": []
        }
        
        lines = analysis_text.lower().split('\n')
        current_psychological_section = False
        
        for i, line in enumerate(lines):
            if any(keyword in line for keyword in psychological_keywords):
                current_psychological_section = True
                # Собираем следующие строки
                for j in range(i, min(i+10, len(lines))):
                    if lines[j].strip():
                        profile["psychological_insights"].append(lines[j].strip())
                break
                
        # Анализируем эмоциональный тон
        if any(word in analysis_text.lower() for word in ['агрессив', 'злост', 'раздражен', 'недовол']):
            profile["emotional_tone"] = "negative"
        elif any(word in analysis_text.lower() for word in ['дружелюбн', 'позитив', 'оптимист', 'радост']):
            profile["emotional_tone"] = "positive"
            
        return profile
    
    def _analyze_power_dynamics(self, analysis_text: str) -> Dict[str, Any]:
        """Анализирует властные отношения в документе"""
        power_keywords = [
            'власт', 'авторитет', 'иерархия', 'давление', 'принуждение', 
            'влияние', 'контроль', 'доминирование', 'влада', 'тиск'
        ]
        
        dynamics = {
            "power_balance": "equal",
            "authority_level": "medium",
            "pressure_techniques": [],
            "dominance_indicators": []
        }
        
        text_lower = analysis_text.lower()
        
        # Определяем баланс власти
        if any(word in text_lower for word in ['высокий авторитет', 'строгие требования', 'обязательно']):
            dynamics["power_balance"] = "sender_dominant"
        elif any(word in text_lower for word in ['просьба', 'пожалуйста', 'если возможно']):
            dynamics["power_balance"] = "recipient_dominant"
            
        return dynamics
    
    def _extract_hidden_subtexts(self, analysis_text: str) -> List[str]:
        """Извлекает скрытые подтексты из анализа"""
        subtext_keywords = [
            'скрыт', 'подразумевается', 'между строк', 'невысказанн', 
            'подтекст', 'имплицитн', 'прихован', 'підтекст'
        ]
        
        subtexts = []
        lines = analysis_text.split('\n')
        
        for i, line in enumerate(lines):
            if any(keyword in line.lower() for keyword in subtext_keywords):
                # Собираем контекст вокруг найденного подтекста
                context_start = max(0, i-2)
                context_end = min(len(lines), i+3)
                context_lines = lines[context_start:context_end]
                subtexts.append(' '.join(l.strip() for l in context_lines if l.strip()))
                
        return subtexts[:5]  # Ограничиваем количество
    
    def _extract_business_intelligence(self, analysis_text: str) -> Dict[str, Any]:
        """Извлекает бизнес-интеллект из анализа"""
        business_keywords = [
            'стратегическ', 'коммерческ', 'финансов', 'прибыл', 'убыток', 
            'конкурент', 'рынок', 'бізнес', 'стратегічн'
        ]
        
        intelligence = {
            "strategic_implications": [],
            "financial_aspects": [],
            "competitive_elements": [],
            "business_opportunities": []
        }
        
        lines = analysis_text.split('\n')
        
        for i, line in enumerate(lines):
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in business_keywords):
                if 'стратег' in line_lower or 'strategic' in line_lower:
                    intelligence["strategic_implications"].append(line.strip())
                elif any(word in line_lower for word in ['финанс', 'деньги', 'стоимост', 'цена']):
                    intelligence["financial_aspects"].append(line.strip())
                elif 'конкурент' in line_lower or 'competition' in line_lower:
                    intelligence["competitive_elements"].append(line.strip())
                    
        return intelligence
    
    def _perform_risk_assessment(self, analysis_text: str) -> Dict[str, Any]:
        """Выполняет оценку рисков"""
        risk_keywords = [
            'риск', 'опасност', 'угроз', 'последств', 'штраф', 'санкц', 
            'нарушение', 'ризик', 'небезпек'
        ]
        
        assessment = {
            "risk_level": "medium",
            "identified_risks": [],
            "mitigation_strategies": [],
            "consequences_of_inaction": []
        }
        
        text_lower = analysis_text.lower()
        lines = analysis_text.split('\n')
        
        risk_count = sum(1 for keyword in risk_keywords if keyword in text_lower)
        
        if risk_count > 5:
            assessment["risk_level"] = "high"
        elif risk_count < 2:
            assessment["risk_level"] = "low"
            
        for line in lines:
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in risk_keywords):
                assessment["identified_risks"].append(line.strip())
                
        return assessment
    
    def _extract_legal_compliance(self, analysis_text: str) -> Dict[str, Any]:
        """Извлекает правовые и compliance аспекты"""
        legal_keywords = [
            'правов', 'закон', 'юридическ', 'compliance', 'регулирование', 
            'нормативн', 'обязательств', 'legal', 'правил'
        ]
        
        compliance = {
            "legal_requirements": [],
            "compliance_issues": [],
            "regulatory_aspects": [],
            "legal_risks": []
        }
        
        lines = analysis_text.split('\n')
        
        for line in lines:
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in legal_keywords):
                if 'требован' in line_lower or 'обязательств' in line_lower:
                    compliance["legal_requirements"].append(line.strip())
                elif 'риск' in line_lower:
                    compliance["legal_risks"].append(line.strip())
                else:
                    compliance["compliance_issues"].append(line.strip())
                    
        return compliance
    
    def _generate_predictive_scenarios(self, analysis_text: str) -> List[Dict[str, Any]]:
        """Генерирует предиктивные сценарии"""
        predictive_keywords = [
            'если', 'вероятн', 'возможн', 'сценар', 'прогноз', 
            'будущ', 'ожидается', 'якщо', 'ймовірн'
        ]
        
        scenarios = []
        lines = analysis_text.split('\n')
        
        for i, line in enumerate(lines):
            if any(keyword in line.lower() for keyword in predictive_keywords):
                scenario = {
                    "scenario": line.strip(),
                    "probability": "medium",
                    "impact": "medium"
                }
                
                # Определяем вероятность по ключевым словам
                if any(word in line.lower() for word in ['скорее всего', 'вероятно', 'ожидается']):
                    scenario["probability"] = "high"
                elif any(word in line.lower() for word in ['маловероятно', 'возможно']):
                    scenario["probability"] = "low"
                    
                scenarios.append(scenario)
                
        return scenarios[:5]  # Ограничиваем количество
    
    def _analyze_relationships(self, analysis_text: str) -> Dict[str, Any]:
        """Анализирует отношения между сторонами"""
        relationship_keywords = [
            'отношен', 'связ', 'партнер', 'сотрудничеств', 'конфликт', 
            'дружб', 'враждебн', 'відносин', 'співпрац'
        ]
        
        analysis = {
            "relationship_type": "professional",
            "relationship_quality": "neutral",
            "communication_style": "formal",
            "relationship_history": []
        }
        
        text_lower = analysis_text.lower()
        
        if any(word in text_lower for word in ['дружеск', 'теплые отношения', 'партнер']):
            analysis["relationship_quality"] = "positive"
        elif any(word in text_lower for word in ['конфликт', 'напряжен', 'враждебн']):
            analysis["relationship_quality"] = "negative"
            
        return analysis
    
    def _extract_cultural_context(self, analysis_text: str) -> Dict[str, Any]:
        """Извлекает культурный контекст"""
        cultural_keywords = [
            'культур', 'традиц', 'этикет', 'протокол', 'обычай', 
            'норм', 'социальн', 'культурн'
        ]
        
        context = {
            "cultural_elements": [],
            "social_norms": [],
            "communication_style": "standard",
            "protocol_requirements": []
        }
        
        lines = analysis_text.split('\n')
        
        for line in lines:
            if any(keyword in line.lower() for keyword in cultural_keywords):
                context["cultural_elements"].append(line.strip())
                
        return context
    
    def _identify_influence_techniques(self, analysis_text: str) -> List[str]:
        """Идентифицирует техники влияния в тексте"""
        influence_keywords = [
            'влияни', 'убеждени', 'давлени', 'манипуляц', 'принуждени', 
            'мотивац', 'стимул', 'вплив', 'переконанн'
        ]
        
        techniques = []
        lines = analysis_text.split('\n')
        
        for line in lines:
            if any(keyword in line.lower() for keyword in influence_keywords):
                techniques.append(line.strip())
                
        return techniques[:5]
    
    def _extract_strategic_recommendations(self, analysis_text: str) -> List[str]:
        """Извлекает стратегические рекомендации"""
        strategic_keywords = [
            'стратегическ', 'долгосрочн', 'планирование', 'развитие', 
            'оптимизац', 'улучшени', 'стратегічн'
        ]
        
        recommendations = []
        lines = analysis_text.split('\n')
        
        for line in lines:
            if any(keyword in line.lower() for keyword in strategic_keywords):
                recommendations.append(line.strip())
                
        return recommendations[:5]
    
    def _extract_risk_mitigation_plans(self, analysis_text: str) -> List[Dict[str, Any]]:
        """Извлекает планы снижения рисков"""
        mitigation_keywords = [
            'снижени', 'предотвращени', 'минимизац', 'защит', 'страховк', 
            'резерв', 'зниженн', 'запобіганн'
        ]
        
        plans = []
        lines = analysis_text.split('\n')
        
        for line in lines:
            if any(keyword in line.lower() for keyword in mitigation_keywords):
                plan = {
                    "strategy": line.strip(),
                    "priority": "medium",
                    "complexity": "medium"
                }
                plans.append(plan)
                
        return plans[:3]
    
    def _extract_analysis_sections(self, analysis_text: str) -> List[Dict[str, Any]]:
        """Извлекает секции из анализа"""
        sections = []
        lines = analysis_text.split('\n')
        current_section = None
        current_content = []
        
        section_icons = {
            'резюме': '📊', 'summary': '📊', 'executive': '📊',
            'отправитель': '👤', 'sender': '👤', 'absender': '👤',
            'получатель': '🎯', 'recipient': '🎯', 'empfänger': '🎯',
            'классификация': '📋', 'classification': '📋', 'klassifizierung': '📋',
            'содержание': '🔥', 'content': '🔥', 'inhalt': '🔥',
            'данные': '📊', 'data': '📊', 'daten': '📊',
            'действия': '⚡', 'actions': '⚡', 'handlungen': '⚡',
            'даты': '📅', 'dates': '📅', 'daten': '📅',
            'контакт': '📞', 'contact': '📞', 'kontakt': '📞',
            'качество': '🎨', 'quality': '🎨', 'qualität': '🎨',
            'инсайты': '🧠', 'insights': '🧠', 'einsichten': '🧠',
            'стратегия': '💡', 'strategy': '💡', 'strategie': '💡'
        }
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Проверяем, является ли строка заголовком секции
            is_section_header = False
            for keyword, icon in section_icons.items():
                if keyword in line.lower() and len(line) < 100:
                    # Сохраняем предыдущую секцию
                    if current_section and current_content:
                        sections.append({
                            "title": current_section,
                            "content": '\n'.join(current_content),
                            "icon": section_icons.get(current_section.lower().split()[0], '📄')
                        })
                    
                    current_section = line
                    current_content = []
                    is_section_header = True
                    break
            
            if not is_section_header:
                current_content.append(line)
        
        # Добавляем последнюю секцию
        if current_section and current_content:
            sections.append({
                "title": current_section,
                "content": '\n'.join(current_content),
                "icon": section_icons.get(current_section.lower().split()[0], '📄')
            })
        
        return sections
    
    def _extract_insights(self, analysis_text: str) -> List[str]:
        """Извлекает ключевые инсайты из анализа"""
        insights = []
        
        # Ищем секции с инсайтами
        insight_keywords = ['инсайты', 'insights', 'einsichten', 'стратегические', 'strategic']
        lines = analysis_text.split('\n')
        
        for i, line in enumerate(lines):
            if any(keyword in line.lower() for keyword in insight_keywords):
                # Собираем следующие несколько строк как инсайты
                for j in range(i+1, min(i+10, len(lines))):
                    if lines[j].strip() and not lines[j].startswith(('1.', '2.', '3.', '4.', '5.')):
                        insights.append(lines[j].strip())
                    elif lines[j].strip() and lines[j].startswith(('1.', '2.', '3.', '4.', '5.')):
                        break
        
        return insights[:5]  # Ограничиваем количество инсайтов
    
    def _extract_action_items(self, analysis_text: str) -> List[Dict[str, Any]]:
        """Извлекает элементы действий из анализа"""
        action_items = []
        
        action_keywords = ['действия', 'actions', 'handlungen', 'требования', 'requirements']
        lines = analysis_text.split('\n')
        
        for i, line in enumerate(lines):
            if any(keyword in line.lower() for keyword in action_keywords):
                # Собираем действия из следующих строк
                for j in range(i+1, min(i+15, len(lines))):
                    if lines[j].strip():
                        action_items.append({
                            "action": lines[j].strip(),
                            "priority": self._assess_action_priority(lines[j]),
                            "deadline": self._extract_deadline(lines[j])
                        })
        
        return action_items[:10]  # Ограничиваем количество действий
    
    def _assess_urgency(self, analysis_text: str) -> str:
        """Оценивает уровень срочности документа"""
        urgency_indicators = {
            'high': ['срочно', 'критично', 'немедленно', 'urgent', 'critical', 'sofort', 'dringend'],
            'medium': ['важно', 'скоро', 'important', 'soon', 'wichtig', 'bald'],
            'low': ['когда удобно', 'не спешит', 'convenient', 'no rush', 'bequem', 'keine eile']
        }
        
        text_lower = analysis_text.lower()
        
        for level, indicators in urgency_indicators.items():
            if any(indicator in text_lower for indicator in indicators):
                return level
        
        return 'medium'  # По умолчанию средняя срочность
    
    def _calculate_quality_score(self, analysis_text: str) -> float:
        """Рассчитывает оценку качества анализа"""
        # Простая оценка на основе длины и содержания
        base_score = min(len(analysis_text) / 1000, 1.0)  # Базовая оценка на основе длины
        
        # Бонусы за структурированность
        if '📊' in analysis_text:
            base_score += 0.1
        if '👤' in analysis_text:
            base_score += 0.1
        if '💡' in analysis_text:
            base_score += 0.1
        
        return min(base_score, 1.0)
    
    def _create_executive_summary(self, analysis_text: str) -> str:
        """Создает краткое резюме анализа"""
        lines = analysis_text.split('\n')
        
        # Ищем секцию с резюме
        for i, line in enumerate(lines):
            if 'резюме' in line.lower() or 'summary' in line.lower():
                # Возвращаем следующие несколько строк
                summary_lines = []
                for j in range(i+1, min(i+5, len(lines))):
                    if lines[j].strip():
                        summary_lines.append(lines[j].strip())
                return ' '.join(summary_lines)
        
        # Если нет специальной секции резюме, берем первые строки
        first_lines = []
        for line in lines[:10]:
            if line.strip() and not line.startswith('🤖'):
                first_lines.append(line.strip())
                if len(first_lines) >= 3:
                    break
        
        return ' '.join(first_lines)
    
    def _extract_recommendations(self, analysis_text: str) -> List[str]:
        """Извлекает рекомендации из анализа"""
        recommendations = []
        
        rec_keywords = ['рекомендации', 'recommendations', 'empfehlungen', 'стратегия', 'strategy']
        lines = analysis_text.split('\n')
        
        for i, line in enumerate(lines):
            if any(keyword in line.lower() for keyword in rec_keywords):
                # Собираем рекомендации из следующих строк
                for j in range(i+1, min(i+10, len(lines))):
                    if lines[j].strip():
                        recommendations.append(lines[j].strip())
        
        return recommendations[:5]  # Ограничиваем количество рекомендаций
    
    def _extract_next_steps(self, analysis_text: str) -> List[str]:
        """Извлекает следующие шаги из анализа"""
        next_steps = []
        
        step_keywords = ['следующие шаги', 'next steps', 'nächste schritte', 'дальнейшие действия']
        lines = analysis_text.split('\n')
        
        for i, line in enumerate(lines):
            if any(keyword in line.lower() for keyword in step_keywords):
                # Собираем шаги из следующих строк
                for j in range(i+1, min(i+8, len(lines))):
                    if lines[j].strip():
                        next_steps.append(lines[j].strip())
        
        return next_steps[:5]  # Ограничиваем количество шагов
    
    def _assess_action_priority(self, action_text: str) -> str:
        """Оценивает приоритет действия"""
        high_priority = ['срочно', 'немедленно', 'критично', 'urgent', 'critical', 'sofort']
        medium_priority = ['важно', 'скоро', 'important', 'soon', 'wichtig']
        
        text_lower = action_text.lower()
        
        if any(hp in text_lower for hp in high_priority):
            return 'high'
        elif any(mp in text_lower for mp in medium_priority):
            return 'medium'
        else:
            return 'low'
    
    def _extract_deadline(self, text: str) -> Optional[str]:
        """Извлекает дедлайн из текста"""
        # Простой поиск дат в тексте
        import re
        
        date_patterns = [
            r'\d{1,2}\.\d{1,2}\.\d{4}',  # DD.MM.YYYY
            r'\d{1,2}\/\d{1,2}\/\d{4}',  # MM/DD/YYYY
            r'\d{4}-\d{1,2}-\d{1,2}',    # YYYY-MM-DD
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, text)
            if matches:
                return matches[0]
        
        return None
    
    def _create_error_response(self, error_message: str, language: str) -> Dict[str, Any]:
        """Создает ответ об ошибке"""
        error_messages = {
            'uk': f"Помилка при аналізі документа: {error_message}",
            'ru': f"Ошибка при анализе документа: {error_message}",
            'de': f"Fehler bei der Dokumentenanalyse: {error_message}",
            'en': f"Error analyzing document: {error_message}"
        }
        
        return {
            "super_analysis": {
                "full_text": error_messages.get(language, error_messages['en']),
                "language": language,
                "analysis_type": "error",
                "sections": [],
                "insights": [],
                "action_items": [],
                "urgency_assessment": "unknown",
                "quality_score": 0.0
            },
            "summary": error_messages.get(language, error_messages['en']),
            "recommendations": [],
            "next_steps": []
        }

# Глобальный экземпляр супер-анализатора
super_analysis_engine = SuperAnalysisEngine()
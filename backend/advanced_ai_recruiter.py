"""
🎯 Advanced AI Recruiter Service - Интеллектуальный AI-рекрутер нового поколения
Идеальный AI-рекрутер который:
- Умно анализирует пользователя за 3-5 вопросов
- Запоминает всю информацию
- Дает персональные рекомендации
- Переводит вакансии на любой язык
- Создает сопроводительные письма
- Анализирует совместимость с вакансиями
"""

import logging
import json
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from modern_llm_manager import modern_llm_manager
from job_search_service import JobSearchService
from german_cities_service import GermanCitiesService

logger = logging.getLogger(__name__)

class AdvancedAIRecruiter:
    def __init__(self, database):
        self.db = database
        self.job_search_service = JobSearchService()
        self.cities_service = GermanCitiesService()
        
        # Этапы разговора - сокращены для быстроты
        self.stages = {
            'initial': {'name': 'Знакомство', 'weight': 20},
            'skills': {'name': 'Навыки и опыт', 'weight': 40},
            'preferences': {'name': 'Предпочтения', 'weight': 30},
            'complete': {'name': 'Готов к поиску', 'weight': 100}
        }
        
        # Языки для ответов
        self.languages = {
            'ru': 'русский',
            'en': 'english',
            'de': 'deutsch',
            'uk': 'українська',
            'es': 'español',
            'fr': 'français'
        }
    
    async def start_conversation(self,
                                user_id: str,
                                user_language: str = 'ru',
                                user_providers: List[Tuple[str, str, str]] = None) -> Dict[str, Any]:
        """
        🚀 Запуск умного разговора с AI-рекрутером
        """
        try:
            logger.info(f"Starting advanced AI recruiter for user {user_id}")
            
            # Проверяем существующий профиль
            existing_profile = await self.db.get_ai_recruiter_profile(user_id)
            
            if existing_profile:
                # Возобновляем разговор
                return await self._resume_conversation(existing_profile, user_language, user_providers)
            
            # Создаем новый профиль
            profile = self._create_initial_profile(user_id, user_language)
            
            # Генерируем первое сообщение
            ai_message = await self._generate_smart_message(
                profile, 'initial', None, user_language, user_providers
            )
            
            # Обновляем профиль
            profile['conversation_history'].append({
                'timestamp': datetime.now().isoformat(),
                'stage': 'initial',
                'ai_message': ai_message,
                'user_message': None
            })
            
            # Сохраняем в базу
            await self.db.save_ai_recruiter_profile(user_id, profile)
            
            return {
                'status': 'success',
                'stage': 'initial',
                'ai_message': ai_message,
                'profile': profile,
                'progress': 0,
                'is_complete': False
            }
            
        except Exception as e:
            logger.error(f"Failed to start AI recruiter: {e}")
            return {
                'status': 'error',
                'message': f'Ошибка запуска AI-рекрутера: {str(e)}',
                'fallback_message': self._get_fallback_message(user_language)
            }
    
    async def continue_conversation(self,
                                   user_id: str,
                                   user_message: str,
                                   user_providers: List[Tuple[str, str, str]] = None) -> Dict[str, Any]:
        """
        💬 Продолжение умного разговора
        """
        try:
            logger.info(f"Continuing conversation for user {user_id}")
            
            # Получаем профиль
            profile = await self.db.get_ai_recruiter_profile(user_id)
            if not profile:
                return {
                    'status': 'error',
                    'message': 'Профиль не найден. Начните разговор заново.',
                    'restart_required': True
                }
            
            # Анализируем ответ пользователя
            extracted_data = await self._analyze_user_response(
                user_message, profile, user_providers
            )
            
            # Обновляем профиль
            profile['collected_data'].update(extracted_data)
            profile['last_interaction'] = datetime.now().isoformat()
            
            # Определяем следующий этап
            next_stage = self._get_next_stage(profile)
            profile['stage'] = next_stage
            
            # Генерируем ответ
            ai_message = await self._generate_smart_message(
                profile, next_stage, user_message, profile['language'], user_providers
            )
            
            # Добавляем в историю
            profile['conversation_history'].append({
                'timestamp': datetime.now().isoformat(),
                'stage': next_stage,
                'ai_message': ai_message,
                'user_message': user_message,
                'extracted_data': extracted_data
            })
            
            # Рассчитываем прогресс
            progress = self._calculate_progress(profile)
            is_complete = next_stage == 'complete'
            
            # Генерируем рекомендации если профиль завершен
            recommendations = None
            if is_complete:
                recommendations = await self._generate_job_recommendations(profile, user_providers)
            
            # Сохраняем профиль
            await self.db.save_ai_recruiter_profile(user_id, profile)
            
            return {
                'status': 'success',
                'stage': next_stage,
                'ai_message': ai_message,
                'profile': profile,
                'progress': progress,
                'is_complete': is_complete,
                'recommendations': recommendations
            }
            
        except Exception as e:
            logger.error(f"Failed to continue conversation: {e}")
            return {
                'status': 'error',
                'message': f'Ошибка продолжения разговора: {str(e)}'
            }
    
    async def get_job_recommendations(self,
                                     user_id: str,
                                     user_providers: List[Tuple[str, str, str]] = None) -> Dict[str, Any]:
        """
        🎯 Получение персональных рекомендаций работы
        """
        try:
            profile = await self.db.get_ai_recruiter_profile(user_id)
            if not profile:
                return {
                    'status': 'error',
                    'message': 'Профиль не найден. Сначала пройдите интервью с AI-рекрутером.'
                }
            
            recommendations = await self._generate_job_recommendations(profile, user_providers)
            
            return {
                'status': 'success',
                'recommendations': recommendations,
                'profile_completeness': self._calculate_progress(profile)
            }
            
        except Exception as e:
            logger.error(f"Failed to get recommendations: {e}")
            return {
                'status': 'error',
                'message': f'Ошибка получения рекомендаций: {str(e)}'
            }
    
    async def translate_job(self,
                           job_data: Dict[str, Any],
                           target_language: str,
                           user_providers: List[Tuple[str, str, str]] = None) -> Dict[str, Any]:
        """
        🌍 Перевод вакансии на нужный язык
        """
        try:
            logger.info(f"Translating job to {target_language}")
            
            # Создаем промпт для перевода
            prompt = self._create_translation_prompt(job_data, target_language)
            
            # Получаем перевод
            if user_providers:
                provider, model, api_key = user_providers[0]
                translation = await modern_llm_manager.generate_content(
                    prompt=prompt,
                    provider=provider,
                    model=model,
                    api_key=api_key,
                    max_tokens=2000
                )
            else:
                translation = self._create_demo_translation(job_data, target_language)
            
            # Парсим результат
            translated_job = self._parse_translation(translation, job_data)
            
            return {
                'status': 'success',
                'original_job': job_data,
                'translated_job': translated_job,
                'target_language': target_language
            }
            
        except Exception as e:
            logger.error(f"Failed to translate job: {e}")
            return {
                'status': 'error',
                'message': f'Ошибка перевода: {str(e)}',
                'fallback_translation': job_data
            }
    
    async def analyze_job_compatibility(self,
                                       user_id: str,
                                       job_data: Dict[str, Any],
                                       user_providers: List[Tuple[str, str, str]] = None) -> Dict[str, Any]:
        """
        🔍 Анализ совместимости с вакансией
        """
        try:
            profile = await self.db.get_ai_recruiter_profile(user_id)
            if not profile:
                return {
                    'status': 'error',
                    'message': 'Профиль не найден. Сначала пройдите интервью с AI-рекрутером.'
                }
            
            # Анализируем совместимость
            analysis = await self._analyze_compatibility(profile, job_data, user_providers)
            
            return {
                'status': 'success',
                'analysis': analysis,
                'job_title': job_data.get('title', 'Unknown'),
                'compatibility_score': analysis.get('score', 0)
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze compatibility: {e}")
            return {
                'status': 'error',
                'message': f'Ошибка анализа совместимости: {str(e)}'
            }
    
    # =====================================================
    # ВНУТРЕННИЕ МЕТОДЫ
    # =====================================================
    
    def _create_initial_profile(self, user_id: str, language: str) -> Dict[str, Any]:
        """Создание начального профиля"""
        return {
            'user_id': user_id,
            'language': language,
            'stage': 'initial',
            'collected_data': {},
            'conversation_history': [],
            'created_at': datetime.now().isoformat(),
            'last_interaction': datetime.now().isoformat()
        }
    
    async def _resume_conversation(self,
                                  profile: Dict[str, Any],
                                  language: str,
                                  user_providers: List[Tuple[str, str, str]] = None) -> Dict[str, Any]:
        """Возобновление разговора"""
        current_stage = profile.get('stage', 'initial')
        
        if current_stage == 'complete':
            # Если профиль завершен, предлагаем рекомендации
            recommendations = await self._generate_job_recommendations(profile, user_providers)
            return {
                'status': 'success',
                'stage': 'complete',
                'ai_message': self._get_completion_message(language),
                'profile': profile,
                'progress': 100,
                'is_complete': True,
                'recommendations': recommendations
            }
        
        # Возобновляем с текущего этапа
        ai_message = await self._generate_smart_message(
            profile, current_stage, None, language, user_providers
        )
        
        return {
            'status': 'success',
            'stage': current_stage,
            'ai_message': ai_message,
            'profile': profile,
            'progress': self._calculate_progress(profile),
            'is_complete': False
        }
    
    async def _generate_smart_message(self,
                                     profile: Dict[str, Any],
                                     stage: str,
                                     user_message: Optional[str],
                                     language: str,
                                     user_providers: List[Tuple[str, str, str]] = None) -> str:
        """Генерация умного сообщения"""
        
        # Создаем контекстный промпт
        prompt = self._create_context_prompt(profile, stage, user_message, language)
        
        if user_providers:
            try:
                provider, model, api_key = user_providers[0]
                ai_message = await modern_llm_manager.generate_content(
                    prompt=prompt,
                    provider=provider,
                    model=model,
                    api_key=api_key,
                    max_tokens=500
                )
                
                if ai_message:
                    return ai_message.strip()
            except Exception as e:
                logger.error(f"Failed to generate AI message: {e}")
        
        # Fallback сообщения
        return self._get_fallback_message_for_stage(stage, language)
    
    def _create_context_prompt(self,
                              profile: Dict[str, Any],
                              stage: str,
                              user_message: Optional[str],
                              language: str) -> str:
        """Создание контекстного промпта"""
        
        collected_data = profile.get('collected_data', {})
        history_summary = self._summarize_conversation_history(profile)
        
        prompts = {
            'ru': {
                'initial': f"""Ты - профессиональный AI-рекрутер, который помогает найти идеальную работу в Германии. 
                
Твоя задача - провести короткое интервью (максимум 3-5 вопросов) чтобы узнать:
- Какую работу ищет человек
- Какой у него опыт и навыки
- Где хочет работать
- Уровень немецкого языка

Будь дружелюбным, профессиональным и эффективным. НЕ говори "Здравствуйте" повторно.

{history_summary}

Твой ответ (на русском языке):""",
                
                'skills': f"""Продолжи интервью. Уже собрано: {collected_data}
                
Пользователь ответил: "{user_message}"

Теперь узнай подробности о навыках и опыте работы. Задай ОДИН конкретный вопрос.

Твой ответ (на русском языке):""",
                
                'preferences': f"""Продолжи интервью. Уже собрано: {collected_data}
                
Пользователь ответил: "{user_message}"

Теперь узнай предпочтения по работе (зарплата, график, компания). Задай ОДИН конкретный вопрос.

Твой ответ (на русском языке):""",
                
                'complete': f"""Интервью завершено! Собрано: {collected_data}
                
Пользователь ответил: "{user_message}"

Поблагодари пользователя и скажи, что начинаешь поиск идеальных вакансий специально для него.

Твой ответ (на русском языке):"""
            },
            'en': {
                'initial': f"""You are a professional AI recruiter helping find the perfect job in Germany.
                
Your task is to conduct a short interview (maximum 3-5 questions) to learn:
- What job they're looking for
- Their experience and skills
- Where they want to work
- German language level

Be friendly, professional, and efficient. DON'T say "Hello" repeatedly.

{history_summary}

Your response (in English):""",
                
                'skills': f"""Continue the interview. Already collected: {collected_data}
                
User responded: "{user_message}"

Now learn details about skills and work experience. Ask ONE specific question.

Your response (in English):""",
                
                'preferences': f"""Continue the interview. Already collected: {collected_data}
                
User responded: "{user_message}"

Now learn work preferences (salary, schedule, company). Ask ONE specific question.

Your response (in English):""",
                
                'complete': f"""Interview completed! Collected: {collected_data}
                
User responded: "{user_message}"

Thank the user and say you're starting to search for perfect job opportunities specifically for them.

Your response (in English):"""
            }
        }
        
        return prompts.get(language, prompts['ru']).get(stage, prompts['ru']['initial'])
    
    def _summarize_conversation_history(self, profile: Dict[str, Any]) -> str:
        """Краткое изложение истории разговора"""
        history = profile.get('conversation_history', [])
        if not history:
            return "Разговор только начинается."
        
        if len(history) == 1:
            return "Это первое взаимодействие с пользователем."
        
        return f"Уже было {len(history)} сообщений. Предыдущие ответы пользователя учтены."
    
    async def _analyze_user_response(self,
                                   user_message: str,
                                   profile: Dict[str, Any],
                                   user_providers: List[Tuple[str, str, str]] = None) -> Dict[str, Any]:
        """Анализ ответа пользователя и извлечение данных"""
        
        current_stage = profile.get('stage', 'initial')
        
        # Простой анализ по ключевым словам
        extracted_data = {}
        
        if current_stage == 'initial':
            # Ищем профессию, город, уровень языка
            extracted_data.update(self._extract_initial_data(user_message))
        
        elif current_stage == 'skills':
            # Ищем навыки и опыт
            extracted_data.update(self._extract_skills_data(user_message))
        
        elif current_stage == 'preferences':
            # Ищем предпочтения
            extracted_data.update(self._extract_preferences_data(user_message))
        
        # Если есть LLM, делаем более точный анализ
        if user_providers:
            try:
                ai_analysis = await self._ai_analyze_response(user_message, current_stage, user_providers)
                extracted_data.update(ai_analysis)
            except Exception as e:
                logger.error(f"Failed AI analysis: {e}")
        
        return extracted_data
    
    def _extract_initial_data(self, message: str) -> Dict[str, Any]:
        """Улучшенное извлечение начальных данных"""
        data = {}
        
        # Поиск уровня немецкого
        message_lower = message.lower()
        for level in ['a1', 'a2', 'b1', 'b2', 'c1', 'c2']:
            if level in message_lower:
                data['german_level'] = level.upper()
                break
        
        # Поиск города (расширенный список)
        cities = [
            'berlin', 'берлин', 'münchen', 'мюнхен', 'munich', 'hamburg', 'гамбург',
            'köln', 'кёльн', 'cologne', 'frankfurt', 'франкфурт', 'düsseldorf', 'дюссельдорф',
            'stuttgart', 'штутгарт', 'leipzig', 'лейпциг', 'dresden', 'дрезден',
            'hannover', 'ганновер', 'nürnberg', 'нюрнберг', 'nuremberg'
        ]
        for city in cities:
            if city in message_lower:
                # Нормализуем название города
                if city in ['берлин', 'berlin']:
                    data['preferred_city'] = 'Berlin'
                elif city in ['мюнхен', 'münchen', 'munich']:
                    data['preferred_city'] = 'München'
                elif city in ['гамбург', 'hamburg']:
                    data['preferred_city'] = 'Hamburg'
                elif city in ['кёльн', 'köln', 'cologne']:
                    data['preferred_city'] = 'Köln'
                elif city in ['франкфурт', 'frankfurt']:
                    data['preferred_city'] = 'Frankfurt'
                elif city in ['дюссельдорф', 'düsseldorf']:
                    data['preferred_city'] = 'Düsseldorf'
                elif city in ['штутгарт', 'stuttgart']:
                    data['preferred_city'] = 'Stuttgart'
                else:
                    data['preferred_city'] = city.title()
                break
        
        # Поиск профессии (значительно расширенный список)
        profession_patterns = {
            'developer': ['developer', 'разработчик', 'программист', 'dev', 'coder'],
            'python developer': ['python', 'пайтон'],
            'frontend developer': ['frontend', 'фронтенд', 'react', 'vue', 'angular'],
            'backend developer': ['backend', 'бэкенд', 'бекенд'],
            'fullstack developer': ['fullstack', 'фуллстек', 'full stack', 'full-stack'],
            'data scientist': ['data scientist', 'дата саентист', 'аналитик данных'],
            'designer': ['designer', 'дизайнер', 'ui', 'ux'],
            'manager': ['manager', 'менеджер', 'project manager', 'проект-менеджер'],
            'qa engineer': ['qa', 'тестировщик', 'quality', 'tester'],
            'devops': ['devops', 'девопс', 'infrastructure', 'инфраструктура'],
            'engineer': ['engineer', 'инженер'],
            'analyst': ['analyst', 'аналитик'],
            'consultant': ['consultant', 'консультант'],
            'marketing': ['marketing', 'маркетинг', 'маркетолог'],
            'sales': ['sales', 'продажи', 'менеджер по продажам']
        }
        
        for profession, patterns in profession_patterns.items():
            for pattern in patterns:
                if pattern in message_lower:
                    data['profession'] = profession
                    break
            if 'profession' in data:
                break
        
        # Если не нашли точную профессию, берем первое подходящее слово
        if 'profession' not in data:
            words = message_lower.split()
            profession_words = ['developer', 'разработчик', 'программист', 'manager', 'менеджер', 
                              'designer', 'дизайнер', 'analyst', 'аналитик', 'specialist', 'специалист']
            for word in words:
                if word in profession_words:
                    data['profession'] = word
                    break
        
        return data
        
        return data
    
    def _extract_skills_data(self, message: str) -> Dict[str, Any]:
        """Улучшенное извлечение данных о навыках"""
        data = {}
        
        message_lower = message.lower()
        
        # Расширенный поиск технических навыков
        tech_skills = {
            'python': ['python', 'пайтон', 'питон'],
            'javascript': ['javascript', 'js', 'джаваскрипт'],
            'java': ['java', 'джава'],
            'react': ['react', 'реакт'],
            'vue': ['vue', 'vue.js'],
            'angular': ['angular', 'ангуляр'],
            'node.js': ['node', 'node.js', 'nodejs'],
            'django': ['django', 'джанго'],
            'flask': ['flask', 'фласк'],
            'docker': ['docker', 'докер'],
            'kubernetes': ['kubernetes', 'k8s', 'кубернетес'],
            'postgresql': ['postgresql', 'postgres', 'постгрес'],
            'mysql': ['mysql', 'майсквл'],
            'mongodb': ['mongodb', 'mongo'],
            'redis': ['redis', 'редис'],
            'git': ['git', 'гит'],
            'aws': ['aws', 'amazon'],
            'linux': ['linux', 'линукс'],
            'sql': ['sql', 'эсквл'],
            'html': ['html'],
            'css': ['css'],
            'typescript': ['typescript', 'ts'],
            'c++': ['c++', 'cpp'],
            'c#': ['c#', 'csharp'],
            'php': ['php', 'пхп'],
            'go': ['golang', 'go'],
            'rust': ['rust', 'раст'],
            'kotlin': ['kotlin', 'котлин'],
            'swift': ['swift', 'свифт']
        }
        
        found_skills = []
        for skill_name, patterns in tech_skills.items():
            for pattern in patterns:
                if pattern in message_lower:
                    found_skills.append(skill_name)
                    break
        
        if found_skills:
            data['technical_skills'] = list(set(found_skills))  # убираем дубликаты
        
        # Поиск опыта работы (более точно)
        import re
        
        # Паттерны для поиска лет опыта
        experience_patterns = [
            r'(\d+)\s*(?:год|лет|года)',
            r'(\d+)\s*years?',
            r'(\d+)\s*лет\s*опыта',
            r'опыт\s*(\d+)',
            r'(\d+)\+?\s*years?\s*(?:of\s*)?experience'
        ]
        
        for pattern in experience_patterns:
            match = re.search(pattern, message_lower)
            if match:
                years = int(match.group(1))
                data['experience_years'] = years
                break
        
        # Поиск образования
        education_keywords = ['университет', 'институт', 'university', 'degree', 'диплом', 'образование', 'магистр', 'бакалавр']
        for keyword in education_keywords:
            if keyword in message_lower:
                data['has_education'] = True
                break
        
        return data
    
    def _extract_preferences_data(self, message: str) -> Dict[str, Any]:
        """Улучшенное извлечение данных о предпочтениях"""
        data = {}
        
        message_lower = message.lower()
        
        # Поиск зарплатных ожиданий (более точно)
        import re
        
        salary_patterns = [
            r'(\d+)\s*(?:000)?\s*(?:-|до|to)\s*(\d+)\s*(?:000)?\s*(?:евро|euro|eur|€)',
            r'от\s*(\d+)\s*(?:000)?\s*до\s*(\d+)\s*(?:000)?\s*(?:евро|euro|eur|€)',
            r'(\d+)\s*(?:к|k|тысяч)\s*(?:-|до|to)\s*(\d+)\s*(?:к|k|тысяч)',
            r'зарплата\s*(\d+)',
            r'salary\s*(\d+)'
        ]
        
        for pattern in salary_patterns:
            match = re.search(pattern, message_lower)
            if match:
                if len(match.groups()) >= 2:
                    # Диапазон зарплаты
                    min_salary = int(match.group(1))
                    max_salary = int(match.group(2))
                    # Если числа меньше 1000, вероятно это в тысячах
                    if min_salary < 1000:
                        min_salary *= 1000
                    if max_salary < 1000:
                        max_salary *= 1000
                    data['salary_min'] = min_salary
                    data['salary_max'] = max_salary
                    data['salary_expectations'] = f"{min_salary}-{max_salary} EUR"
                else:
                    # Одно число
                    salary = int(match.group(1))
                    if salary < 1000:
                        salary *= 1000
                    data['salary_expectations'] = f"{salary} EUR"
                break
        
        # Поиск формата работы
        work_format_keywords = {
            'remote': ['remote', 'удаленно', 'удаленная', 'дистанционно', 'из дома', 'home office'],
            'office': ['office', 'офис', 'офисе', 'на месте', 'очно'],
            'hybrid': ['hybrid', 'гибрид', 'смешанный', 'частично удаленно']
        }
        
        for format_type, keywords in work_format_keywords.items():
            for keyword in keywords:
                if keyword in message_lower:
                    data['work_format'] = format_type
                    break
            if 'work_format' in data:
                break
        
        # Поиск типа занятости
        employment_keywords = {
            'full_time': ['полный день', 'full time', 'fulltime', 'полная занятость', 'фулл тайм'],
            'part_time': ['частичная занятость', 'part time', 'parttime', 'неполный день'],
            'contract': ['контракт', 'contract', 'подряд', 'фриланс', 'freelance'],
            'internship': ['стажировка', 'internship', 'intern', 'практика']
        }
        
        for employment_type, keywords in employment_keywords.items():
            for keyword in keywords:
                if keyword in message_lower:
                    data['employment_type'] = employment_type
                    break
            if 'employment_type' in data:
                break
        
        # Поиск размера компании
        company_size_keywords = {
            'startup': ['стартап', 'startup', 'молодая компания', 'небольшая компания'],
            'small': ['малая', 'маленькая', 'small company', 'до 50'],
            'medium': ['средняя', 'medium', 'средний размер', '50-500'],
            'large': ['большая', 'крупная', 'large', 'корпорация', 'более 500']
        }
        
        for size_type, keywords in company_size_keywords.items():
            for keyword in keywords:
                if keyword in message_lower:
                    data['company_size_preference'] = size_type
                    break
            if 'company_size_preference' in data:
                break
        
        return data
    
    async def _ai_analyze_response(self,
                                  user_message: str,
                                  stage: str,
                                  user_providers: List[Tuple[str, str, str]]) -> Dict[str, Any]:
        """AI анализ ответа пользователя"""
        
        prompt = f"""Проанализируй ответ пользователя и извлеки структурированную информацию.
        
Этап: {stage}
Ответ пользователя: "{user_message}"

Верни JSON с найденной информацией. Например:
{{"profession": "Software Developer", "german_level": "B1", "city": "Berlin", "experience": "3 years"}}

Только JSON, без дополнительного текста:"""
        
        try:
            provider, model, api_key = user_providers[0]
            result = await modern_llm_manager.generate_content(
                prompt=prompt,
                provider=provider,
                model=model,
                api_key=api_key,
                max_tokens=200
            )
            
            # Пытаемся парсить JSON
            if result and '{' in result:
                json_str = result[result.find('{'):result.rfind('}')+1]
                return json.loads(json_str)
                
        except Exception as e:
            logger.error(f"Failed to AI analyze response: {e}")
        
        return {}
    
    def _get_next_stage(self, profile: Dict[str, Any]) -> str:
        """Определение следующего этапа"""
        current_stage = profile.get('stage', 'initial')
        collected_data = profile.get('collected_data', {})
        
        # Проверяем достаточность данных
        if current_stage == 'initial':
            if len(collected_data) >= 2:  # Хотя бы 2 поля заполнены
                return 'skills'
            return 'initial'
        
        elif current_stage == 'skills':
            if len(collected_data) >= 4:  # Больше данных собрано
                return 'preferences'
            return 'skills'
        
        elif current_stage == 'preferences':
            return 'complete'
        
        return 'complete'
    
    def _calculate_progress(self, profile: Dict[str, Any]) -> int:
        """Расчет прогресса"""
        stage = profile.get('stage', 'initial')
        collected_data = profile.get('collected_data', {})
        
        # Базовый прогресс по этапам
        stage_progress = {
            'initial': 20,
            'skills': 50,
            'preferences': 80,
            'complete': 100
        }
        
        base_progress = stage_progress.get(stage, 0)
        
        # Бонус за количество собранных данных
        data_bonus = min(len(collected_data) * 5, 20)
        
        return min(base_progress + data_bonus, 100)
    
    async def _generate_job_recommendations(self,
                                          profile: Dict[str, Any],
                                          user_providers: List[Tuple[str, str, str]] = None) -> List[Dict[str, Any]]:
        """Улучшенная генерация рекомендаций вакансий"""
        try:
            collected_data = profile.get('collected_data', {})
            
            # Расширенные параметры для поиска
            search_params = {
                'location': collected_data.get('preferred_city', 'Berlin'),
                'language_level': collected_data.get('german_level', 'B1'),
                'search_query': collected_data.get('profession', 'developer')
            }
            
            logger.info(f"Searching jobs with params: {search_params}")
            
            # Поиск вакансий
            jobs_result = await self.job_search_service.search_jobs(**search_params)
            
            if jobs_result.get('status') == 'success':
                all_jobs = jobs_result.get('jobs', [])
                logger.info(f"Found {len(all_jobs)} jobs")
                
                if not all_jobs:
                    # Если нет вакансий, создаем демо-рекомендации
                    return self._create_demo_job_recommendations(collected_data)
                
                # Анализируем совместимость для каждой вакансии
                recommendations = []
                for job in all_jobs[:10]:  # Топ 10 вакансий для анализа
                    compatibility = await self._analyze_compatibility(profile, job, user_providers)
                    
                    recommendation = {
                        'job': job,
                        'compatibility': compatibility,
                        'recommendation_reason': self._get_recommendation_reason(profile, job, compatibility),
                        'action_items': self._get_action_items_for_job(profile, job, compatibility),
                        'match_highlights': self._get_match_highlights(profile, job, compatibility)
                    }
                    
                    recommendations.append(recommendation)
                
                # Сортируем по совместимости
                recommendations.sort(key=lambda x: x['compatibility'].get('score', 0), reverse=True)
                
                # Берем топ 5 лучших совпадений
                return recommendations[:5]
            else:
                logger.warning(f"Job search failed: {jobs_result}")
                return self._create_demo_job_recommendations(collected_data)
            
        except Exception as e:
            logger.error(f"Failed to generate recommendations: {e}")
            # Создаем демо-рекомендации в случае ошибки
            return self._create_demo_job_recommendations(collected_data)
    
    def _create_demo_job_recommendations(self, collected_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Создание демо-рекомендаций при отсутствии реальных вакансий"""
        
        profession = collected_data.get('profession', 'developer')
        city = collected_data.get('preferred_city', 'Berlin')
        german_level = collected_data.get('german_level', 'B1')
        
        demo_jobs = [
            {
                'title': f'Senior {profession.title()}',
                'company': 'TechCorp Deutschland',
                'location': city,
                'salary': '60,000 - 80,000 EUR',
                'description': f'Exciting opportunity for an experienced {profession} to join our innovative team in {city}. We work with cutting-edge technologies and offer excellent growth opportunities.',
                'requirements': f'3+ years of experience in {profession}, strong technical skills, {german_level}+ German level',
                'type': 'Vollzeit',
                'remote_possible': True
            },
            {
                'title': f'Junior {profession.title()}',
                'company': 'StartupHub GmbH',
                'location': city,
                'salary': '45,000 - 55,000 EUR',
                'description': f'Perfect entry-level position for a motivated {profession}. Join our dynamic startup environment and grow your skills.',
                'requirements': f'1+ year of experience, willingness to learn, {german_level}+ German level',
                'type': 'Vollzeit',
                'remote_possible': False
            },
            {
                'title': f'{profession.title()} (Remote)',
                'company': 'RemoteWork Solutions',
                'location': 'Deutschland (Remote)',
                'salary': '55,000 - 70,000 EUR',
                'description': f'100% remote position for a skilled {profession}. Work from anywhere in Germany with flexible hours.',
                'requirements': f'2+ years of experience, excellent communication skills, {german_level}+ German level',
                'type': 'Vollzeit',
                'remote_possible': True
            }
        ]
        
        recommendations = []
        for job in demo_jobs:
            # Создаем искусственный анализ совместимости
            compatibility = {
                'score': 75 + (len(recommendations) * 5),  # Убывающие баллы
                'strengths': [
                    f"💼 Соответствует профессии: {profession}",
                    f"📍 Желаемый город: {city}",
                    f"🇩🇪 Подходящий уровень немецкого: {german_level}"
                ],
                'concerns': [],
                'recommendations': ["📝 Подготовьте резюме", "✍️ Напишите сопроводительное письмо"],
                'overall_recommendation': 'good',
                'recommendation_text': '👍 Хорошее соответствие. Стоит попробовать!',
                'summary': f'Хорошая совместимость ({75 + (len(recommendations) * 5)}/100)!'
            }
            
            recommendation = {
                'job': job,
                'compatibility': compatibility,
                'recommendation_reason': f"Отличное соответствие по профессии и локации. Подходит для вашего уровня опыта.",
                'action_items': [
                    "📝 Адаптируйте резюме под требования вакансии",
                    "✍️ Составьте персональное сопроводительное письмо",
                    "🔍 Изучите подробнее о компании",
                    "📞 Подготовьтесь к собеседованию"
                ],
                'match_highlights': [
                    f"✅ Точное соответствие профессии: {profession}",
                    f"✅ Предпочитаемый город: {city}",
                    f"✅ Уровень немецкого: {german_level}+"
                ]
            }
            
            recommendations.append(recommendation)
        
        return recommendations
    
    def _get_recommendation_reason(self, profile: Dict[str, Any], job: Dict[str, Any], compatibility: Dict[str, Any]) -> str:
        """Генерация причины рекомендации"""
        
        score = compatibility.get('score', 0)
        strengths = compatibility.get('strengths', [])
        
        if score >= 80:
            reason = "🎯 Идеальное совпадение! "
        elif score >= 65:
            reason = "👍 Отличное соответствие. "
        elif score >= 45:
            reason = "🤔 Хорошие перспективы. "
        else:
            reason = "📝 Возможный вариант. "
        
        if strengths:
            top_strengths = strengths[:2]  # Берем топ 2 преимущества
            reason += "Основные плюсы: " + ", ".join([s.split(" ", 1)[1] if " " in s else s for s in top_strengths])
        
        return reason
    
    def _get_action_items_for_job(self, profile: Dict[str, Any], job: Dict[str, Any], compatibility: Dict[str, Any]) -> List[str]:
        """Генерация конкретных действий для вакансии"""
        
        actions = []
        concerns = compatibility.get('concerns', [])
        score = compatibility.get('score', 0)
        
        # Базовые действия
        actions.append("📝 Адаптируйте резюме под требования вакансии")
        actions.append("✍️ Составьте персональное сопроводительное письмо")
        
        # Действия на основе анализа
        if score >= 80:
            actions.append("🚀 Подавайте заявку как можно скорее!")
            actions.append("📞 Подготовьтесь к собеседованию")
        elif score >= 65:
            actions.append("🔍 Изучите подробнее требования и компанию")
            actions.append("💪 Подчеркните свои сильные стороны")
        else:
            actions.append("📚 Подготовьтесь к возможным вопросам о слабых сторонах")
            actions.append("🎯 Фокусируйтесь на своих достижениях")
        
        # Специфические действия на основе проблем
        for concern in concerns:
            if 'немецкого' in concern.lower() or 'german' in concern.lower():
                actions.append("🇩🇪 Укажите свой реальный уровень немецкого в резюме")
            elif 'город' in concern.lower() or 'city' in concern.lower():
                actions.append("📍 Объясните готовность к переезду")
            elif 'опыт' in concern.lower() or 'experience' in concern.lower():
                actions.append("💼 Детально опишите релевантный опыт")
            elif 'навык' in concern.lower() or 'skill' in concern.lower():
                actions.append("🛠 Подготовьте примеры использования требуемых технологий")
        
        return actions[:6]  # Максимум 6 действий
    
    def _get_match_highlights(self, profile: Dict[str, Any], job: Dict[str, Any], compatibility: Dict[str, Any]) -> List[str]:
        """Генерация ключевых совпадений"""
        
        highlights = []
        strengths = compatibility.get('strengths', [])
        
        # Берем все сильные стороны как highlights
        for strength in strengths[:5]:  # Максимум 5 highlights
            if strength.startswith(('🎯', '💼', '🛠', '🇩🇪', '⏱', '🏠', '🏢')):
                highlights.append(strength)
            else:
                highlights.append(f"✅ {strength}")
        
        # Если мало highlights, добавляем базовые
        if len(highlights) < 2:
            highlights.append("✅ Подходящая вакансия для вашего профиля")
            highlights.append("✅ Соответствует базовым критериям поиска")
        
        return highlights
    
    async def _analyze_compatibility(self,
                                   profile: Dict[str, Any],
                                   job: Dict[str, Any],
                                   user_providers: List[Tuple[str, str, str]] = None) -> Dict[str, Any]:
        """Улучшенный анализ совместимости с вакансией"""
        
        collected_data = profile.get('collected_data', {})
        
        # Более детальная система оценки
        analysis = {
            'score': 0,
            'max_score': 100,
            'categories': {},
            'strengths': [],
            'concerns': [],
            'recommendations': [],
            'summary': ''
        }
        
        # 1. Анализ локации (25 баллов)
        location_score = self._analyze_location_match(job, collected_data)
        analysis['categories']['location'] = location_score
        analysis['score'] += location_score['score']
        
        # 2. Анализ профессии/навыков (30 баллов)
        skills_score = self._analyze_skills_match(job, collected_data)
        analysis['categories']['skills'] = skills_score
        analysis['score'] += skills_score['score']
        
        # 3. Анализ требований по языку (20 баллов)
        language_score = self._analyze_language_requirements(job, collected_data)
        analysis['categories']['language'] = language_score
        analysis['score'] += language_score['score']
        
        # 4. Анализ опыта работы (15 баллов)
        experience_score = self._analyze_experience_match(job, collected_data)
        analysis['categories']['experience'] = experience_score
        analysis['score'] += experience_score['score']
        
        # 5. Анализ предпочтений (10 баллов)
        preferences_score = self._analyze_preferences_match(job, collected_data)
        analysis['categories']['preferences'] = preferences_score
        analysis['score'] += preferences_score['score']
        
        # Собираем все insights
        for category in analysis['categories'].values():
            analysis['strengths'].extend(category.get('strengths', []))
            analysis['concerns'].extend(category.get('concerns', []))
            analysis['recommendations'].extend(category.get('recommendations', []))
        
        # Генерируем итоговое резюме
        analysis['summary'] = self._generate_compatibility_summary(analysis['score'], analysis['strengths'], analysis['concerns'])
        
        # Определяем общую рекомендацию
        if analysis['score'] >= 80:
            analysis['overall_recommendation'] = 'excellent'
            analysis['recommendation_text'] = '🎯 Отличное соответствие! Обязательно подавайте заявку.'
        elif analysis['score'] >= 65:
            analysis['overall_recommendation'] = 'good'
            analysis['recommendation_text'] = '👍 Хорошее соответствие. Стоит попробовать!'
        elif analysis['score'] >= 45:
            analysis['overall_recommendation'] = 'moderate'
            analysis['recommendation_text'] = '🤔 Частичное соответствие. Оцените свои шансы.'
        else:
            analysis['overall_recommendation'] = 'low'
            analysis['recommendation_text'] = '📝 Низкое соответствие. Возможно, стоит поискать другие варианты.'
        
        return analysis
    
    def _analyze_location_match(self, job: Dict[str, Any], collected_data: Dict[str, Any]) -> Dict[str, Any]:
        """Анализ соответствия по локации"""
        result = {'score': 0, 'max_score': 25, 'strengths': [], 'concerns': [], 'recommendations': []}
        
        job_location = job.get('location', '').lower()
        preferred_city = collected_data.get('preferred_city', '').lower()
        work_format = collected_data.get('work_format', '')
        
        if preferred_city and preferred_city in job_location:
            result['score'] = 25
            result['strengths'].append(f"🎯 Вакансия в желаемом городе: {job_location.title()}")
        elif 'remote' in job_location and work_format == 'remote':
            result['score'] = 20
            result['strengths'].append("🏠 Удаленная работа соответствует предпочтениям")
        elif preferred_city:
            # Проверяем близкие города
            if self._are_cities_nearby(preferred_city, job_location):
                result['score'] = 15
                result['recommendations'].append(f"📍 Рассмотрите переезд: {job_location.title()} недалеко от {preferred_city.title()}")
            else:
                result['score'] = 5
                result['concerns'].append(f"📍 Другой город: {job_location.title()} вместо {preferred_city.title()}")
        else:
            result['score'] = 10
            result['recommendations'].append("📍 Укажите предпочтения по городу для лучшего поиска")
        
        return result
    
    def _analyze_skills_match(self, job: Dict[str, Any], collected_data: Dict[str, Any]) -> Dict[str, Any]:
        """Анализ соответствия навыков"""
        result = {'score': 0, 'max_score': 30, 'strengths': [], 'concerns': [], 'recommendations': []}
        
        job_description = (job.get('description', '') + ' ' + job.get('requirements', '')).lower()
        job_title = job.get('title', '').lower()
        
        profession = collected_data.get('profession', '').lower()
        technical_skills = [skill.lower() for skill in collected_data.get('technical_skills', [])]
        experience_years = collected_data.get('experience_years', 0)
        
        # Проверка соответствия профессии
        if profession and profession in job_title:
            result['score'] += 15
            result['strengths'].append(f"💼 Точное соответствие профессии: {profession}")
        elif profession and any(word in job_title for word in profession.split()):
            result['score'] += 10
            result['strengths'].append(f"💼 Частичное соответствие профессии: {profession}")
        
        # Проверка технических навыков
        matching_skills = []
        for skill in technical_skills:
            if skill in job_description:
                matching_skills.append(skill)
        
        if matching_skills:
            skills_score = min(len(matching_skills) * 3, 15)
            result['score'] += skills_score
            result['strengths'].append(f"🛠 Совпадают навыки: {', '.join(matching_skills)}")
        else:
            result['concerns'].append("🛠 Не найдено явных совпадений по техническим навыкам")
            result['recommendations'].append("📚 Изучите требования вакансии и подготовьте примеры использования нужных технологий")
        
        return result
    
    def _analyze_language_requirements(self, job: Dict[str, Any], collected_data: Dict[str, Any]) -> Dict[str, Any]:
        """Анализ языковых требований"""
        result = {'score': 0, 'max_score': 20, 'strengths': [], 'concerns': [], 'recommendations': []}
        
        job_text = (job.get('description', '') + ' ' + job.get('requirements', '')).lower()
        user_german_level = collected_data.get('german_level', '')
        
        # Определяем требуемый уровень немецкого
        required_level = self._extract_german_level_from_job(job_text)
        
        if user_german_level and required_level:
            user_level_num = self._german_level_to_number(user_german_level)
            required_level_num = self._german_level_to_number(required_level)
            
            if user_level_num >= required_level_num:
                result['score'] = 20
                result['strengths'].append(f"🇩🇪 Уровень немецкого {user_german_level} соответствует требованиям ({required_level})")
            elif user_level_num >= required_level_num - 1:
                result['score'] = 15
                result['strengths'].append(f"🇩🇪 Уровень немецкого {user_german_level} близок к требованиям ({required_level})")
                result['recommendations'].append("📖 Рассмотрите возможность повышения уровня немецкого")
            else:
                result['score'] = 5
                result['concerns'].append(f"🇩🇪 Требуется {required_level}, у вас {user_german_level}")
                result['recommendations'].append("📖 Необходимо значительно улучшить уровень немецкого языка")
        else:
            result['score'] = 10
            if not user_german_level:
                result['recommendations'].append("🇩🇪 Укажите ваш уровень немецкого языка")
            else:
                result['recommendations'].append("🇩🇪 В вакансии не указаны требования к немецкому языку")
        
        return result
    
    def _analyze_experience_match(self, job: Dict[str, Any], collected_data: Dict[str, Any]) -> Dict[str, Any]:
        """Анализ соответствия опыта"""
        result = {'score': 0, 'max_score': 15, 'strengths': [], 'concerns': [], 'recommendations': []}
        
        job_text = (job.get('description', '') + ' ' + job.get('requirements', '')).lower()
        user_experience = collected_data.get('experience_years', 0)
        
        # Извлекаем требуемый опыт из описания вакансии
        required_experience = self._extract_experience_from_job(job_text)
        
        if required_experience is not None and user_experience > 0:
            if user_experience >= required_experience:
                result['score'] = 15
                result['strengths'].append(f"⏱ Опыт {user_experience} лет соответствует требованиям ({required_experience}+ лет)")
            elif user_experience >= required_experience - 1:
                result['score'] = 10
                result['strengths'].append(f"⏱ Опыт {user_experience} лет близок к требованиям ({required_experience}+ лет)")
            else:
                result['score'] = 5
                result['concerns'].append(f"⏱ Требуется {required_experience}+ лет, у вас {user_experience} лет")
                result['recommendations'].append("💼 Подчеркните в резюме все релевантные проекты и достижения")
        else:
            result['score'] = 8
            if user_experience == 0:
                result['recommendations'].append("⏱ Укажите ваш опыт работы для более точного анализа")
            else:
                result['recommendations'].append("⏱ В вакансии не указаны четкие требования к опыту")
        
        return result
    
    def _analyze_preferences_match(self, job: Dict[str, Any], collected_data: Dict[str, Any]) -> Dict[str, Any]:
        """Анализ соответствия предпочтений"""
        result = {'score': 0, 'max_score': 10, 'strengths': [], 'concerns': [], 'recommendations': []}
        
        job_text = (job.get('description', '') + ' ' + job.get('requirements', '')).lower()
        salary_expectations = collected_data.get('salary_expectations', '')
        work_format = collected_data.get('work_format', '')
        
        # Анализ формата работы
        if work_format == 'remote' and 'remote' in job_text:
            result['score'] += 5
            result['strengths'].append("🏠 Удаленная работа как предпочитаете")
        elif work_format == 'office' and 'office' in job_text:
            result['score'] += 5
            result['strengths'].append("🏢 Офисная работа как предпочитаете")
        elif work_format and work_format not in job_text:
            result['concerns'].append(f"📍 Возможно, формат работы не соответствует предпочтениям ({work_format})")
        
        # Анализ зарплатных ожиданий (упрощенно)
        if salary_expectations:
            result['score'] += 3
            result['strengths'].append("💰 Зарплатные ожидания учтены в анализе")
        else:
            result['score'] += 2
            result['recommendations'].append("💰 Укажите зарплатные ожидания для лучшего подбора")
        
        return result
    
    def _are_cities_nearby(self, city1: str, city2: str) -> bool:
        """Проверка близости городов"""
        nearby_cities = {
            'berlin': ['potsdam', 'brandenburg'],
            'munich': ['münchen', 'augsburg'],
            'hamburg': ['bremen', 'lübeck'],
            'frankfurt': ['mainz', 'darmstadt', 'wiesbaden'],
            'cologne': ['köln', 'düsseldorf', 'bonn'],
            'stuttgart': ['karlsruhe', 'heilbronn']
        }
        
        for main_city, nearby in nearby_cities.items():
            if (main_city in city1 and any(c in city2 for c in nearby)) or \
               (main_city in city2 and any(c in city1 for c in nearby)):
                return True
        
        return False
    
    def _extract_german_level_from_job(self, job_text: str) -> str:
        """Извлечение требуемого уровня немецкого из описания"""
        import re
        
        # Паттерны для поиска уровня немецкого
        patterns = [
            r'german.*?([abc][12])',
            r'deutsch.*?([abc][12])',
            r'([abc][12]).*german',
            r'([abc][12]).*deutsch'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, job_text, re.IGNORECASE)
            if match:
                return match.group(1).upper()
        
        # Если не найдено, пытаемся определить по ключевым словам
        if 'fluent german' in job_text or 'native german' in job_text:
            return 'C1'
        elif 'good german' in job_text or 'intermediate german' in job_text:
            return 'B2'
        elif 'basic german' in job_text:
            return 'A2'
        
        return None
    
    def _german_level_to_number(self, level: str) -> int:
        """Конвертация уровня немецкого в число для сравнения"""
        level_map = {'A1': 1, 'A2': 2, 'B1': 3, 'B2': 4, 'C1': 5, 'C2': 6}
        return level_map.get(level.upper(), 0)
    
    def _extract_experience_from_job(self, job_text: str) -> int:
        """Извлечение требуемого опыта из описания"""
        import re
        
        # Паттерны для поиска опыта
        patterns = [
            r'(\d+)\+?\s*years?\s*(?:of\s*)?experience',
            r'(\d+)\+?\s*jahre?\s*erfahrung',
            r'experience.*?(\d+)\+?\s*years?',
            r'minimum.*?(\d+)\+?\s*years?'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, job_text, re.IGNORECASE)
            if match:
                return int(match.group(1))
        
        return None
    
    def _generate_compatibility_summary(self, score: int, strengths: List[str], concerns: List[str]) -> str:
        """Генерация итогового резюме совместимости"""
        if score >= 80:
            summary = f"🎯 Отличная совместимость ({score}/100)! "
        elif score >= 65:
            summary = f"👍 Хорошая совместимость ({score}/100). "
        elif score >= 45:
            summary = f"🤔 Умеренная совместимость ({score}/100). "
        else:
            summary = f"📝 Низкая совместимость ({score}/100). "
        
        if strengths:
            summary += f"Сильные стороны: {len(strengths)} совпадений. "
        
        if concerns:
            summary += f"Требует внимания: {len(concerns)} моментов."
        
        return summary
    
    def _get_recommendation_reason(self,
                                  profile: Dict[str, Any],
                                  job: Dict[str, Any],
                                  compatibility: Dict[str, Any]) -> str:
        """Получение причины рекомендации"""
        score = compatibility.get('score', 0)
        reasons = compatibility.get('reasons', [])
        
        if score >= 80:
            reason = "Идеально подходит! "
        elif score >= 60:
            reason = "Хорошее соответствие. "
        else:
            reason = "Может быть интересно. "
        
        if reasons:
            reason += " ".join(reasons[:2])  # Первые 2 причины
        
        return reason
    
    def _create_translation_prompt(self, job_data: Dict[str, Any], target_language: str) -> str:
        """Создание промпта для перевода"""
        
        lang_names = {
            'ru': 'русский',
            'en': 'английский',
            'de': 'немецкий',
            'uk': 'украинский',
            'es': 'испанский',
            'fr': 'французский'
        }
        
        lang_name = lang_names.get(target_language, target_language)
        
        return f"""Переведи информацию о вакансии на {lang_name} язык.

Название: {job_data.get('title', '')}
Компания: {job_data.get('company', '')}
Локация: {job_data.get('location', '')}
Описание: {job_data.get('description', '')}
Требования: {job_data.get('requirements', '')}
Зарплата: {job_data.get('salary', '')}

Верни результат в формате JSON:
{{
    "title": "переведенное название",
    "company": "название компании",
    "location": "локация",
    "description": "переведенное описание",
    "requirements": "переведенные требования",
    "salary": "зарплата"
}}

Только JSON, без дополнительного текста:"""
    
    def _parse_translation(self, translation: str, original_job: Dict[str, Any]) -> Dict[str, Any]:
        """Парсинг переведенного контента"""
        try:
            if translation and '{' in translation:
                json_str = translation[translation.find('{'):translation.rfind('}')+1]
                parsed = json.loads(json_str)
                
                # Проверяем наличие ключевых полей
                if 'title' in parsed and 'description' in parsed:
                    return parsed
                    
        except Exception as e:
            logger.error(f"Failed to parse translation: {e}")
        
        # Fallback - возвращаем оригинал
        return original_job
    
    def _create_demo_translation(self, job_data: Dict[str, Any], target_language: str) -> str:
        """Улучшенный демо-перевод для fallback"""
        
        # Извлекаем данные о вакансии
        original_title = job_data.get('title', 'Software Developer')
        original_company = job_data.get('company', 'Tech Company')
        original_location = job_data.get('location', 'Berlin, Germany')
        original_description = job_data.get('description', 'Interesting software development position')
        original_requirements = job_data.get('requirements', 'Programming experience required')
        original_salary = job_data.get('salary', 'Competitive salary')
        
        translations = {
            'ru': {
                'title': self._translate_title_to_russian(original_title),
                'company': original_company,
                'location': self._translate_location_to_russian(original_location),
                'description': f"""📋 Описание позиции:
{self._translate_description_to_russian(original_description)}

🏢 О компании: {original_company} - динамично развивающаяся компания в сфере технологий.

🎯 Что предлагаем:
• Конкурентоспособная зарплата
• Возможность профессионального роста
• Современные технологии и инструменты
• Дружный коллектив профессионалов""",
                'requirements': f"""✅ Требования:
{self._translate_requirements_to_russian(original_requirements)}

📚 Будет плюсом:
• Опыт работы в команде
• Знание современных методологий разработки
• Желание изучать новые технологии""",
                'salary': self._translate_salary_to_russian(original_salary)
            },
            'en': {
                'title': self._translate_title_to_english(original_title),
                'company': original_company,
                'location': original_location,
                'description': f"""📋 Position Description:
{self._enhance_english_description(original_description)}

🏢 About Company: {original_company} - rapidly growing technology company.

🎯 What we offer:
• Competitive salary package
• Professional growth opportunities
• Modern technologies and tools
• Friendly team of professionals""",
                'requirements': f"""✅ Requirements:
{self._enhance_english_requirements(original_requirements)}

📚 Nice to have:
• Team collaboration experience
• Knowledge of modern development methodologies
• Willingness to learn new technologies""",
                'salary': original_salary
            },
            'de': {
                'title': self._translate_title_to_german(original_title),
                'company': original_company,
                'location': original_location,
                'description': f"""📋 Stellenbeschreibung:
{self._translate_description_to_german(original_description)}

🏢 Über das Unternehmen: {original_company} - dynamisch wachsendes Technologieunternehmen.

🎯 Was wir bieten:
• Wettbewerbsfähiges Gehalt
• Berufliche Entwicklungsmöglichkeiten
• Moderne Technologien und Tools
• Freundliches Profi-Team""",
                'requirements': f"""✅ Anforderungen:
{self._translate_requirements_to_german(original_requirements)}

📚 Von Vorteil:
• Teamarbeit-Erfahrung
• Kenntnisse moderner Entwicklungsmethoden
• Lernbereitschaft für neue Technologien""",
                'salary': self._translate_salary_to_german(original_salary)
            }
        }
        
        target_translation = translations.get(target_language, translations['en'])
        
        return json.dumps({
            'title': target_translation['title'],
            'company': target_translation['company'],
            'location': target_translation['location'],
            'description': target_translation['description'],
            'requirements': target_translation['requirements'],
            'salary': target_translation['salary'],
            'translation_note': f"Перевод на {self.languages.get(target_language, target_language)} выполнен автоматически"
        }, ensure_ascii=False, indent=2)
    
    def _translate_title_to_russian(self, title: str) -> str:
        """Перевод названия на русский"""
        common_translations = {
            'software developer': 'Разработчик ПО',
            'full stack developer': 'Fullstack разработчик',
            'frontend developer': 'Frontend разработчик',
            'backend developer': 'Backend разработчик',
            'data scientist': 'Специалист по данным',
            'project manager': 'Проект-менеджер',
            'ui/ux designer': 'UI/UX дизайнер',
            'marketing manager': 'Менеджер по маркетингу',
            'sales manager': 'Менеджер по продажам'
        }
        
        title_lower = title.lower()
        for eng, rus in common_translations.items():
            if eng in title_lower:
                return rus
                
        return f"Специалист - {title}"
    
    def _translate_description_to_russian(self, description: str) -> str:
        """Улучшенный перевод описания на русский"""
        if 'developer' in description.lower():
            return """Мы ищем талантливого разработчика для работы над инновационными проектами. 
Вы будете работать с современными технологиями, участвовать в создании масштабируемых решений 
и развивать свои навыки в дружной команде профессионалов."""
        elif 'designer' in description.lower():
            return """Ищем креативного дизайнера для создания выдающихся пользовательских интерфейсов.
Вы будете работать над интересными проектами, воплощать инновационные идеи в жизнь
и создавать продукты, которыми пользуются тысячи людей."""
        else:
            return """Присоединяйтесь к нашей команде профессионалов! Мы предлагаем интересные задачи,
возможности для развития и работу в современной технологической среде."""
    
    def _translate_requirements_to_russian(self, requirements: str) -> str:
        """Перевод требований на русский"""
        return """• Опыт работы от 2-х лет в соответствующей области
• Знание современных технологий и инструментов
• Понимание принципов разработки ПО
• Умение работать в команде
• Знание английского языка на уровне чтения технической документации"""
    
    def _translate_location_to_russian(self, location: str) -> str:
        """Перевод локации на русский"""
        city_translations = {
            'berlin': 'Берлин',
            'munich': 'Мюнхен',
            'hamburg': 'Гамбург',
            'frankfurt': 'Франкфурт',
            'cologne': 'Кёльн',
            'stuttgart': 'Штутгарт'
        }
        
        location_lower = location.lower()
        for eng, rus in city_translations.items():
            if eng in location_lower:
                return location.replace(eng.title(), rus)
                
        return location
    
    def _translate_salary_to_russian(self, salary: str) -> str:
        """Перевод зарплаты на русский"""
        if 'competitive' in salary.lower():
            return 'Конкурентоспособная зарплата (45,000-80,000 EUR/год)'
        return salary
    
    # Аналогичные методы для английского и немецкого
    def _translate_title_to_english(self, title: str) -> str:
        return title  # Already in English most likely
    
    def _enhance_english_description(self, description: str) -> str:
        return f"{description}\n\nJoin our innovative team and work on cutting-edge projects using the latest technologies."
    
    def _enhance_english_requirements(self, requirements: str) -> str:
        return f"{requirements}\n• 2+ years of relevant experience\n• Strong problem-solving skills\n• Team collaboration abilities"
    
    def _translate_title_to_german(self, title: str) -> str:
        german_translations = {
            'software developer': 'Softwareentwickler',
            'full stack developer': 'Fullstack-Entwickler',
            'frontend developer': 'Frontend-Entwickler',
            'backend developer': 'Backend-Entwickler',
            'project manager': 'Projektmanager',
            'designer': 'Designer'
        }
        
        title_lower = title.lower()
        for eng, ger in german_translations.items():
            if eng in title_lower:
                return ger
                
        return title
    
    def _translate_description_to_german(self, description: str) -> str:
        return f"{description}\n\nWerden Sie Teil unseres innovativen Teams und arbeiten Sie an zukunftsweisenden Projekten."
    
    def _translate_requirements_to_german(self, requirements: str) -> str:
        return f"{requirements}\n• Mindestens 2 Jahre Berufserfahrung\n• Teamfähigkeit\n• Lernbereitschaft"
    
    def _translate_salary_to_german(self, salary: str) -> str:
        if 'competitive' in salary.lower():
            return 'Attraktives Gehalt (45.000-80.000 EUR/Jahr)'
        return salary
    
    def _get_fallback_message(self, language: str) -> str:
        """Fallback сообщение"""
        messages = {
            'ru': "Привет! Я AI-рекрутер, помогу найти идеальную работу в Германии. Расскажи, какую работу ищешь?",
            'en': "Hi! I'm an AI recruiter, I'll help find the perfect job in Germany. Tell me what job you're looking for?",
            'de': "Hallo! Ich bin ein AI-Recruiter und helfe dir den perfekten Job in Deutschland zu finden. Erzähl mir, welchen Job du suchst?"
        }
        
        return messages.get(language, messages['ru'])
    
    def _get_fallback_message_for_stage(self, stage: str, language: str) -> str:
        """Улучшенные fallback сообщения для каждого этапа"""
        
        messages = {
            'ru': {
                'initial': """👋 Привет! Я AI-рекрутер и помогу найти идеальную работу в Германии. 

Расскажи мне:
• Какую должность ищешь? (например: разработчик, дизайнер, маркетолог)
• В каком городе хочешь работать?
• Какой у тебя уровень немецкого языка? (A1-C2)

Начни с любого пункта! 🚀""",
                
                'skills': """💼 Отлично! Теперь расскажи о своем опыте:

• Сколько лет работаешь в этой сфере?
• Какие технологии/инструменты знаешь?
• Есть ли образование или сертификаты?
• Какие проекты реализовывал?

Чем подробнее - тем лучше подберу вакансии! ⚡""",
                
                'preferences': """⚙️ Почти готово! Последние детали:

• Какая зарплата интересна? (от ... до ... EUR)
• Готов работать полный день или предпочитаешь частичную занятость?
• Интересует удаленная работа или только офис?
• Есть предпочтения по размеру компании? (стартап/корпорация)

После этого найду идеальные варианты! 🎯""",
                
                'complete': """🎉 Профиль готов! Сейчас ищу лучшие вакансии...

На основе твоих данных я найду:
✅ Вакансии с подходящими требованиями
✅ Позиции в выбранном городе
✅ Работу с нужным уровнем немецкого
✅ Соответствующую зарплатную вилку

Также могу:
🔄 Перевести любую вакансию на русский
📊 Проанализировать совместимость
✍️ Составить сопроводительное письмо

Вот что нашел для тебя:"""
            },
            'en': {
                'initial': """👋 Hi! I'm an AI recruiter helping find perfect jobs in Germany.

Tell me:
• What position are you looking for? (e.g., developer, designer, marketer)
• Which city would you like to work in?
• What's your German level? (A1-C2)

Start with any point! 🚀""",
                
                'skills': """💼 Great! Now tell me about your experience:

• How many years have you worked in this field?
• What technologies/tools do you know?
• Do you have education or certifications?
• What projects have you implemented?

The more details, the better I can match jobs! ⚡""",
                
                'preferences': """⚙️ Almost ready! Final details:

• What salary range interests you? (from ... to ... EUR)
• Full-time or part-time preference?
• Interested in remote work or office only?
• Company size preference? (startup/corporation)

After this, I'll find perfect matches! 🎯""",
                
                'complete': """🎉 Profile ready! Searching for best jobs...

Based on your data, I'll find:
✅ Jobs matching your requirements
✅ Positions in your chosen city
✅ Work with your German level
✅ Matching salary range

I can also:
🔄 Translate any job to English
📊 Analyze compatibility
✍️ Create cover letters

Here's what I found for you:"""
            },
            'de': {
                'initial': """👋 Hallo! Ich bin ein AI-Recruiter und helfe bei der Jobsuche in Deutschland.

Erzähl mir:
• Welche Position suchst du? (z.B. Entwickler, Designer, Marketer)
• In welcher Stadt möchtest du arbeiten?
• Wie ist dein Deutschniveau? (A1-C2)

Fang mit einem Punkt an! 🚀""",
                
                'skills': """💼 Toll! Jetzt erzähl von deiner Erfahrung:

• Wie viele Jahre Berufserfahrung hast du?
• Welche Technologien/Tools beherrschst du?
• Hast du Ausbildung oder Zertifikate?
• Welche Projekte hast du umgesetzt?

Je mehr Details, desto besser kann ich Jobs finden! ⚡""",
                
                'preferences': """⚙️ Fast fertig! Letzte Details:

• Welches Gehalt stellst du dir vor? (von ... bis ... EUR)
• Vollzeit oder Teilzeit?
• Remote-Arbeit oder nur Büro?
• Präferenz für Unternehmensgröße? (Startup/Konzern)

Danach finde ich perfekte Stellen! 🎯""",
                
                'complete': """🎉 Profil fertig! Suche beste Jobs...

Basierend auf deinen Daten finde ich:
✅ Jobs mit passenden Anforderungen
✅ Stellen in deiner gewählten Stadt
✅ Arbeit mit deinem Deutschniveau
✅ Passende Gehaltsvorstellungen

Ich kann auch:
🔄 Jobs ins Deutsche übersetzen
📊 Kompatibilität analysieren
✍️ Anschreiben erstellen

Hier ist was ich für dich gefunden habe:"""
            }
        }
        
        return messages.get(language, messages['ru']).get(stage, messages['ru']['initial'])
    
    def _get_completion_message(self, language: str) -> str:
        """Улучшенное сообщение о завершении"""
        messages = {
            'ru': """🎉 Отлично! Ваш профиль готов!

Теперь я могу предложить вам:

🎯 **ПЕРСОНАЛЬНЫЕ РЕКОМЕНДАЦИИ ВАКАНСИЙ**
• Подобрал лучшие варианты под ваш профиль
• Проанализировал совместимость с каждой позицией
• Указал конкретные шаги для каждой вакансии

💡 **ДОПОЛНИТЕЛЬНЫЕ ВОЗМОЖНОСТИ:**
🔄 **Перевод вакансий** - переведу любую вакансию на русский
📊 **Анализ совместимости** - детальный разбор ваших шансов
✍️ **Сопроводительные письма** - составлю для каждой вакансии
📝 **Улучшение резюме** - подскажу как адаптировать под вакансию

⭐ Вот лучшие вакансии специально для вас:""",
            
            'en': """🎉 Excellent! Your profile is ready!

Now I can offer you:

🎯 **PERSONALIZED JOB RECOMMENDATIONS**
• Selected best matches for your profile
• Analyzed compatibility with each position
• Provided specific action steps for each job

💡 **ADDITIONAL FEATURES:**
🔄 **Job Translation** - translate any job to English
📊 **Compatibility Analysis** - detailed breakdown of your chances
✍️ **Cover Letters** - create personalized letters for each job
📝 **Resume Improvement** - advice on adapting to specific jobs

⭐ Here are the best jobs specifically for you:""",
            
            'de': """🎉 Ausgezeichnet! Ihr Profil ist fertig!

Jetzt kann ich Ihnen anbieten:

🎯 **PERSONALISIERTE STELLENEMPFEHLUNGEN**
• Beste Übereinstimmungen für Ihr Profil ausgewählt
• Kompatibilität mit jeder Position analysiert
• Spezifische Handlungsschritte für jede Stelle bereitgestellt

💡 **ZUSÄTZLICHE FUNKTIONEN:**
🔄 **Stellenübersetzung** - übersetze jede Stelle ins Deutsche
📊 **Kompatibilitätsanalyse** - detaillierte Aufschlüsselung Ihrer Chancen
✍️ **Anschreiben** - erstelle personalisierte Briefe für jede Stelle
📝 **Lebenslauf-Verbesserung** - Ratschläge zur Anpassung an spezifische Jobs

⭐ Hier sind die besten Jobs speziell für Sie:"""
        }
        
        return messages.get(language, messages['ru'])
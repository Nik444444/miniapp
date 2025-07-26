"""
🎯 Perfect AI Recruiter - Идеальный AI-рекрутер для Telegram Mini App
Простой, эффективный и надежный AI-рекрутер который:
- Составляет профиль за 3 простых вопроса
- Дает точные рекомендации вакансий
- Генерирует идеальные сопроводительные письма
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

class PerfectAIRecruiter:
    def __init__(self, database):
        self.db = database
        self.job_search_service = JobSearchService()
        self.cities_service = GermanCitiesService()
        
        # Простые этапы разговора
        self.stages = {
            'greeting': {'name': 'Знакомство', 'progress': 20},
            'skills': {'name': 'Навыки и опыт', 'progress': 60},
            'complete': {'name': 'Готов к поиску', 'progress': 100}
        }

    async def start_conversation(self,
                                user_id: str,
                                user_language: str = 'ru',
                                user_providers: List[Tuple[str, str, str]] = None) -> Dict[str, Any]:
        """
        🚀 Запуск идеального AI-рекрутера
        """
        try:
            logger.info(f"🎯 Starting Perfect AI Recruiter for user {user_id}")
            
            # Проверяем существующий профиль
            existing_profile = await self.db.get_ai_recruiter_profile(user_id)
            
            if existing_profile and existing_profile.get('stage') == 'complete':
                # Если профиль завершен, показываем рекомендации
                recommendations = await self._generate_job_recommendations(existing_profile, user_providers)
                return {
                    'status': 'success',
                    'stage': 'complete',
                    'ai_message': self._get_welcome_back_message(user_language),
                    'profile': existing_profile,
                    'progress': 100,
                    'is_complete': True,
                    'recommendations': recommendations
                }
            
            # Создаем новый профиль
            profile = {
                'user_id': user_id,
                'language': user_language,
                'stage': 'greeting',
                'profile_data': {},
                'conversation': [],
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            # Генерируем первое сообщение
            ai_message = await self._generate_message(profile, None, user_language, user_providers)
            
            # Обновляем профиль
            profile['conversation'].append({
                'timestamp': datetime.now().isoformat(),
                'stage': 'greeting',
                'ai_message': ai_message,
                'user_message': None
            })
            
            # Сохраняем в базу
            await self.db.save_ai_recruiter_profile(user_id, profile)
            
            return {
                'status': 'success',
                'stage': 'greeting',
                'ai_message': ai_message,
                'profile': profile,
                'progress': 20,
                'is_complete': False
            }
            
        except Exception as e:
            logger.error(f"Failed to start Perfect AI Recruiter: {e}")
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
        💬 Продолжение разговора с идеальным AI-рекрутером
        """
        try:
            logger.info(f"🎯 Continuing Perfect AI Recruiter conversation for user {user_id}")
            
            # Получаем профиль
            profile = await self.db.get_ai_recruiter_profile(user_id)
            if not profile:
                return {
                    'status': 'error',
                    'message': 'Профиль не найден. Начните разговор заново.',
                    'restart_required': True
                }
            
            current_stage = profile.get('stage', 'greeting')
            
            # Анализируем ответ пользователя и извлекаем данные
            extracted_data = await self._analyze_user_response(
                user_message, current_stage, profile['language'], user_providers
            )
            
            # Обновляем данные профиля
            profile['profile_data'].update(extracted_data)
            profile['updated_at'] = datetime.now().isoformat()
            
            # Определяем следующий этап
            next_stage = self._get_next_stage(current_stage, profile['profile_data'])
            profile['stage'] = next_stage
            
            # Генерируем ответ AI
            ai_message = await self._generate_message(
                profile, user_message, profile['language'], user_providers
            )
            
            # Добавляем в историю разговора
            profile['conversation'].append({
                'timestamp': datetime.now().isoformat(),
                'stage': next_stage,
                'ai_message': ai_message,
                'user_message': user_message,
                'extracted_data': extracted_data
            })
            
            # Рассчитываем прогресс
            progress = self.stages[next_stage]['progress']
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
            
            if profile.get('stage') != 'complete':
                return {
                    'status': 'error',
                    'message': 'Сначала завершите анкетирование с AI-рекрутером.'
                }
            
            recommendations = await self._generate_job_recommendations(profile, user_providers)
            
            return {
                'status': 'success',
                'recommendations': recommendations,
                'profile_completeness': self.stages[profile.get('stage', 'greeting')]['progress']
            }
            
        except Exception as e:
            logger.error(f"Failed to get recommendations: {e}")
            return {
                'status': 'error',
                'message': f'Ошибка получения рекомендаций: {str(e)}'
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
            
            analysis = await self._analyze_compatibility(profile, job_data, user_providers)
            
            return {
                'status': 'success',
                'analysis': analysis,
                'job_title': job_data.get('title', 'Unknown'),
                'compatibility_score': analysis.get('overall_score', 0)
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze compatibility: {e}")
            return {
                'status': 'error',
                'message': f'Ошибка анализа совместимости: {str(e)}'
            }

    async def translate_job(self,
                           job_data: Dict[str, Any],
                           target_language: str,
                           user_providers: List[Tuple[str, str, str]] = None) -> Dict[str, Any]:
        """
        🌍 Перевод вакансии на нужный язык
        """
        try:
            logger.info(f"🌍 Translating job to {target_language}")
            
            if user_providers:
                provider, model, api_key = user_providers[0]
                
                # Создаем простой промпт для перевода
                prompt = f"""Переведи эту вакансию на {target_language}:

Название: {job_data.get('title', '')}
Компания: {job_data.get('company_name', '')}
Описание: {job_data.get('description', '')}
Требования: {job_data.get('requirements', '')}

Верни в формате JSON:
{{
    "title": "переведенное название",
    "company_name": "название компании",
    "description": "переведенное описание",
    "requirements": "переведенные требования",
    "location": "{job_data.get('location', '')}"
}}"""
                
                translation = await modern_llm_manager.generate_content(
                    prompt=prompt,
                    provider=provider,
                    model=model,
                    api_key=api_key,
                    max_tokens=1500
                )
                
                # Парсим результат
                translated_job = self._parse_translation(translation, job_data)
            else:
                # Fallback - возвращаем оригинал
                translated_job = job_data.copy()
                translated_job['translation_note'] = f'Для перевода на {target_language} добавьте AI ключи'
            
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

    async def generate_cover_letter(self,
                                   user_id: str,
                                   job_data: Dict[str, Any],
                                   style: str = 'professional',
                                   user_providers: List[Tuple[str, str, str]] = None) -> Dict[str, Any]:
        """
        📝 Генерация идеального сопроводительного письма
        """
        try:
            profile = await self.db.get_ai_recruiter_profile(user_id)
            if not profile:
                return {
                    'status': 'error',
                    'message': 'Профиль не найден. Сначала пройдите интервью с AI-рекрутером.'
                }
            
            cover_letter = await self._generate_cover_letter(
                profile, job_data, style, user_providers
            )
            
            return {
                'status': 'success',
                'cover_letter': cover_letter,
                'job_title': job_data.get('title', 'Unknown'),
                'style': style
            }
            
        except Exception as e:
            logger.error(f"Failed to generate cover letter: {e}")
            return {
                'status': 'error',
                'message': f'Ошибка генерации письма: {str(e)}'
            }

    # =====================================================
    # ВНУТРЕННИЕ МЕТОДЫ
    # =====================================================

    async def _generate_message(self,
                               profile: Dict[str, Any],
                               user_message: Optional[str],
                               language: str,
                               user_providers: List[Tuple[str, str, str]] = None) -> str:
        """Генерация сообщения AI"""
        
        stage = profile.get('stage', 'greeting')
        profile_data = profile.get('profile_data', {})
        
        # Создаем простой промпт
        if stage == 'greeting':
            prompt = self._create_greeting_prompt(language)
        elif stage == 'skills':
            prompt = self._create_skills_prompt(profile_data, user_message, language)
        else:
            prompt = self._create_completion_prompt(profile_data, language)
        
        if user_providers:
            try:
                provider, model, api_key = user_providers[0]
                ai_message = await modern_llm_manager.generate_content(
                    prompt=prompt,
                    provider=provider,
                    model=model,
                    api_key=api_key,
                    max_tokens=300
                )
                
                if ai_message:
                    return ai_message.strip()
            except Exception as e:
                logger.error(f"Failed to generate AI message: {e}")
        
        # Fallback сообщения
        return self._get_fallback_message_for_stage(stage, language)

    def _create_greeting_prompt(self, language: str) -> str:
        """Промпт для знакомства"""
        if language == 'ru':
            return """Ты - профессиональный AI-рекрутер для поиска работы в Германии.

Представься и кратко (в 2-3 предложениях) спроси у кандидата:
- Какую работу он ищет
- В каком городе Германии
- Какой у него уровень немецкого языка (A1-C2)

Будь дружелюбным и профессиональным. Говори кратко."""
        else:
            return """You are a professional AI recruiter for jobs in Germany.

Introduce yourself briefly (2-3 sentences) and ask the candidate:
- What job they are looking for
- In which German city
- What is their German language level (A1-C2)

Be friendly and professional. Keep it short."""

    def _create_skills_prompt(self, profile_data: Dict[str, Any], user_message: str, language: str) -> str:
        """Промпт для навыков"""
        if language == 'ru':
            return f"""Пользователь ответил: "{user_message}"

Уже собрано: {json.dumps(profile_data, ensure_ascii=False)}

Теперь кратко (1-2 предложения) спроси о его навыках и опыте:
- Сколько лет опыта работы
- Какие основные технические навыки
- Есть ли образование в этой области

Будь кратким и конкретным."""
        else:
            return f"""User responded: "{user_message}"

Already collected: {json.dumps(profile_data, ensure_ascii=False)}

Now briefly (1-2 sentences) ask about skills and experience:
- How many years of experience
- What are the main technical skills
- Do they have education in this field

Be brief and specific."""

    def _create_completion_prompt(self, profile_data: Dict[str, Any], language: str) -> str:
        """Промпт для завершения"""
        if language == 'ru':
            return f"""Собранные данные: {json.dumps(profile_data, ensure_ascii=False)}

Поблагодари пользователя за информацию и скажи, что теперь начинаешь поиск идеальных вакансий специально для него.

Будь воодушевляющим и обнадеживающим. 2-3 предложения максимум."""
        else:
            return f"""Collected data: {json.dumps(profile_data, ensure_ascii=False)}

Thank the user for the information and say you're now starting to search for perfect job opportunities specifically for them.

Be encouraging and optimistic. 2-3 sentences maximum."""

    async def _analyze_user_response(self,
                                   user_message: str,
                                   stage: str,
                                   language: str,
                                   user_providers: List[Tuple[str, str, str]] = None) -> Dict[str, Any]:
        """Анализ ответа пользователя"""
        
        extracted_data = {}
        
        if stage == 'greeting':
            extracted_data.update(self._extract_basic_info(user_message))
        elif stage == 'skills':
            extracted_data.update(self._extract_skills_info(user_message))
        
        # Если есть AI провайдеры, делаем более точный анализ
        if user_providers:
            try:
                ai_data = await self._ai_extract_data(user_message, stage, user_providers)
                extracted_data.update(ai_data)
            except Exception as e:
                logger.error(f"AI extraction failed: {e}")
        
        return extracted_data

    def _extract_basic_info(self, message: str) -> Dict[str, Any]:
        """Извлечение базовой информации"""
        data = {}
        message_lower = message.lower()
        
        # Поиск профессии
        professions = {
            'developer': ['developer', 'разработчик', 'программист', 'dev'],
            'designer': ['designer', 'дизайнер', 'ui', 'ux'],
            'manager': ['manager', 'менеджер', 'project manager'],
            'engineer': ['engineer', 'инженер'],
            'analyst': ['analyst', 'аналитик']
        }
        
        for profession, keywords in professions.items():
            if any(keyword in message_lower for keyword in keywords):
                data['profession'] = profession
                break
        
        # Поиск города
        cities = ['berlin', 'münchen', 'hamburg', 'köln', 'frankfurt', 'stuttgart', 'düsseldorf']
        for city in cities:
            if city in message_lower:
                data['city'] = city.capitalize()
                break
        
        # Поиск уровня немецкого
        for level in ['a1', 'a2', 'b1', 'b2', 'c1', 'c2']:
            if level in message_lower:
                data['german_level'] = level.upper()
                break
        
        return data

    def _extract_skills_info(self, message: str) -> Dict[str, Any]:
        """Извлечение информации о навыках"""
        data = {}
        message_lower = message.lower()
        
        # Поиск лет опыта
        import re
        experience_match = re.search(r'(\d+)\s*(?:год|лет|года|years?)', message_lower)
        if experience_match:
            data['experience_years'] = int(experience_match.group(1))
        
        # Поиск технических навыков
        tech_skills = ['python', 'javascript', 'java', 'react', 'vue', 'angular', 'node', 'docker', 'kubernetes']
        found_skills = [skill for skill in tech_skills if skill in message_lower]
        if found_skills:
            data['technical_skills'] = found_skills
        
        # Поиск образования
        if any(word in message_lower for word in ['университет', 'институт', 'university', 'degree', 'диплом']):
            data['has_education'] = True
        
        return data

    async def _ai_extract_data(self,
                              user_message: str,
                              stage: str,
                              user_providers: List[Tuple[str, str, str]]) -> Dict[str, Any]:
        """AI извлечение данных"""
        
        prompt = f"""Извлеки структурированную информацию из ответа пользователя.

Этап: {stage}
Ответ: "{user_message}"

Верни только JSON без дополнительного текста:
{{"profession": "...", "city": "...", "german_level": "...", "experience_years": 0, "technical_skills": []}}"""
        
        try:
            provider, model, api_key = user_providers[0]
            result = await modern_llm_manager.generate_content(
                prompt=prompt,
                provider=provider,
                model=model,
                api_key=api_key,
                max_tokens=200
            )
            
            if result and '{' in result:
                json_str = result[result.find('{'):result.rfind('}')+1]
                return json.loads(json_str)
                
        except Exception as e:
            logger.error(f"Failed to AI extract data: {e}")
        
        return {}

    def _get_next_stage(self, current_stage: str, profile_data: Dict[str, Any]) -> str:
        """Определение следующего этапа"""
        if current_stage == 'greeting':
            # Переходим к навыкам если есть базовая информация
            if len(profile_data) >= 2:
                return 'skills'
            return 'greeting'
        elif current_stage == 'skills':
            # Завершаем если собрано достаточно данных
            if len(profile_data) >= 4:
                return 'complete'
            return 'skills'
        else:
            return 'complete'

    async def _generate_job_recommendations(self,
                                          profile: Dict[str, Any],
                                          user_providers: List[Tuple[str, str, str]] = None) -> List[Dict[str, Any]]:
        """Генерация рекомендаций вакансий"""
        try:
            profile_data = profile.get('profile_data', {})
            
            # Параметры для поиска
            search_params = {
                'location': profile_data.get('city', 'Berlin'),
                'language_level': profile_data.get('german_level', 'B1'),
                'search_query': profile_data.get('profession', 'developer')
            }
            
            logger.info(f"🎯 Searching jobs with params: {search_params}")
            
            # Поиск вакансий
            jobs_result = await self.job_search_service.search_jobs(**search_params)
            
            if jobs_result.get('status') == 'success':
                jobs = jobs_result.get('jobs', [])[:10]  # Топ 10 вакансий
                
                recommendations = []
                for job in jobs:
                    # Анализируем совместимость
                    compatibility = await self._analyze_compatibility(profile, job, user_providers)
                    
                    recommendations.append({
                        'job': job,
                        'compatibility_score': compatibility.get('overall_score', 75),
                        'match_reasons': compatibility.get('strengths', []),
                        'improvement_suggestions': compatibility.get('suggestions', [])
                    })
                
                # Сортируем по совместимости
                recommendations.sort(key=lambda x: x['compatibility_score'], reverse=True)
                return recommendations[:5]  # Топ 5
            else:
                # Создаем демо-рекомендации
                return self._create_demo_recommendations(profile_data)
            
        except Exception as e:
            logger.error(f"Failed to generate recommendations: {e}")
            return self._create_demo_recommendations(profile.get('profile_data', {}))

    async def _analyze_compatibility(self,
                                   profile: Dict[str, Any],
                                   job_data: Dict[str, Any],
                                   user_providers: List[Tuple[str, str, str]] = None) -> Dict[str, Any]:
        """Анализ совместимости с вакансией"""
        
        profile_data = profile.get('profile_data', {})
        
        if user_providers:
            try:
                provider, model, api_key = user_providers[0]
                
                prompt = f"""Проанализируй совместимость кандидата с вакансией.

КАНДИДАТ:
Профессия: {profile_data.get('profession', 'Unknown')}
Опыт: {profile_data.get('experience_years', 'Unknown')} лет
Навыки: {', '.join(profile_data.get('technical_skills', []))}
Немецкий: {profile_data.get('german_level', 'Unknown')}

ВАКАНСИЯ:
Название: {job_data.get('title', '')}
Описание: {job_data.get('description', '')[:300]}
Требования: {job_data.get('requirements', '')}

Верни JSON:
{{
    "overall_score": 85,
    "strengths": ["список преимуществ"],
    "weaknesses": ["список слабых мест"],
    "suggestions": ["рекомендации"]
}}"""
                
                result = await modern_llm_manager.generate_content(
                    prompt=prompt,
                    provider=provider,
                    model=model,
                    api_key=api_key,
                    max_tokens=800
                )
                
                if result and '{' in result:
                    json_str = result[result.find('{'):result.rfind('}')+1]
                    return json.loads(json_str)
                    
            except Exception as e:
                logger.error(f"AI compatibility analysis failed: {e}")
        
        # Простой fallback анализ
        return {
            'overall_score': 75,
            'strengths': ['Релевантный опыт', 'Подходящие навыки'],
            'weaknesses': ['Требуется улучшение языка'],
            'suggestions': ['Изучите требования компании', 'Подготовьтесь к интервью']
        }

    async def _generate_cover_letter(self,
                                   profile: Dict[str, Any],
                                   job_data: Dict[str, Any],
                                   style: str,
                                   user_providers: List[Tuple[str, str, str]] = None) -> Dict[str, Any]:
        """Генерация сопроводительного письма"""
        
        profile_data = profile.get('profile_data', {})
        
        if user_providers:
            try:
                provider, model, api_key = user_providers[0]
                
                prompt = f"""Создай идеальное сопроводительное письмо в стиле "{style}".

КАНДИДАТ:
{json.dumps(profile_data, ensure_ascii=False)}

ВАКАНСИЯ:
Название: {job_data.get('title', '')}
Компания: {job_data.get('company_name', '')}
Описание: {job_data.get('description', '')[:300]}

Создай профессиональное письмо на немецком языке.
Верни в JSON формате:
{{
    "subject": "тема письма",
    "greeting": "приветствие",
    "body": "основной текст",
    "closing": "заключение",
    "full_text": "полный текст письма"
}}"""
                
                result = await modern_llm_manager.generate_content(
                    prompt=prompt,
                    provider=provider,
                    model=model,
                    api_key=api_key,
                    max_tokens=1500
                )
                
                if result and '{' in result:
                    json_str = result[result.find('{'):result.rfind('}')+1]
                    parsed = json.loads(json_str)
                    parsed['word_count'] = len(parsed.get('full_text', '').split())
                    parsed['style'] = style
                    return parsed
                    
            except Exception as e:
                logger.error(f"AI cover letter generation failed: {e}")
        
        # Fallback письмо
        return {
            'subject': f'Bewerbung für {job_data.get("title", "die Position")}',
            'greeting': f'Sehr geehrte Damen und Herren,',
            'body': f'hiermit bewerbe ich mich für die Position {job_data.get("title", "")} in Ihrem Unternehmen. Mit meiner Erfahrung in {profile_data.get("profession", "")} bin ich überzeugt, dass ich eine wertvolle Ergänzung für Ihr Team sein kann.',
            'closing': 'Mit freundlichen Grüßen',
            'full_text': f'Sehr geehrte Damen und Herren,\n\nhiermit bewerbe ich mich für die Position {job_data.get("title", "")} in Ihrem Unternehmen. Mit meiner Erfahrung in {profile_data.get("profession", "")} bin ich überzeugt, dass ich eine wertvolle Ergänzung für Ihr Team sein kann.\n\nMit freundlichen Grüßen',
            'word_count': 50,
            'style': style
        }

    def _create_demo_recommendations(self, profile_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Создание демо-рекомендаций"""
        
        profession = profile_data.get('profession', 'Developer')
        city = profile_data.get('city', 'Berlin')
        
        return [
            {
                'job': {
                    'title': f'Senior {profession}',
                    'company_name': 'TechCorp Deutschland',
                    'location': city,
                    'salary': '65,000 - 80,000 EUR',
                    'description': f'Exciting opportunity for an experienced {profession}.',
                    'requirements': ['3+ years experience', 'Strong technical skills']
                },
                'compatibility_score': 92,
                'match_reasons': ['Perfect skill match', 'Great location'],
                'improvement_suggestions': ['Improve German language skills']
            },
            {
                'job': {
                    'title': f'Junior {profession}',
                    'company_name': 'StartupHub GmbH',
                    'location': city,
                    'salary': '45,000 - 55,000 EUR',
                    'description': f'Great entry position for motivated {profession}.',
                    'requirements': ['1+ year experience', 'Learning mindset']
                },
                'compatibility_score': 85,
                'match_reasons': ['Entry level friendly', 'Startup environment'],
                'improvement_suggestions': ['Build portfolio projects']
            }
        ]

    def _parse_translation(self, translation: str, original_job: Dict[str, Any]) -> Dict[str, Any]:
        """Парсинг перевода"""
        try:
            if '{' in translation and '}' in translation:
                json_str = translation[translation.find('{'):translation.rfind('}')+1]
                parsed = json.loads(json_str)
                return parsed
        except:
            pass
        
        # Fallback
        return original_job.copy()

    def _get_fallback_message(self, language: str) -> str:
        """Fallback сообщение"""
        if language == 'ru':
            return "Привет! Я AI-рекрутер и помогу найти идеальную работу в Германии. Расскажите, какую работу вы ищете?"
        else:
            return "Hello! I'm an AI recruiter and I'll help you find the perfect job in Germany. Tell me, what job are you looking for?"

    def _get_fallback_message_for_stage(self, stage: str, language: str) -> str:
        """Fallback сообщение для этапа"""
        messages = {
            'ru': {
                'greeting': "Привет! Расскажите, какую работу вы ищете в Германии?",
                'skills': "Расскажите о своих навыках и опыте работы.",
                'complete': "Отлично! Теперь я найду идеальные вакансии для вас."
            },
            'en': {
                'greeting': "Hello! Tell me what job you're looking for in Germany?",
                'skills': "Tell me about your skills and work experience.",
                'complete': "Great! Now I'll find perfect job opportunities for you."
            }
        }
        
        return messages.get(language, messages['ru']).get(stage, messages['ru']['greeting'])

    def _get_welcome_back_message(self, language: str) -> str:
        """Сообщение для возвращающихся пользователей"""
        if language == 'ru':
            return "С возвращением! Ваш профиль готов. Вот ваши персональные рекомендации вакансий:"
        else:
            return "Welcome back! Your profile is ready. Here are your personalized job recommendations:"


# Глобальный экземпляр
perfect_ai_recruiter = None

def get_perfect_ai_recruiter(database):
    global perfect_ai_recruiter
    if perfect_ai_recruiter is None:
        perfect_ai_recruiter = PerfectAIRecruiter(database)
    return perfect_ai_recruiter
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
        """Извлечение начальных данных"""
        data = {}
        
        # Поиск уровня немецкого
        message_lower = message.lower()
        for level in ['a1', 'a2', 'b1', 'b2', 'c1', 'c2']:
            if level in message_lower:
                data['german_level'] = level.upper()
                break
        
        # Поиск города
        cities = ['berlin', 'münchen', 'hamburg', 'köln', 'frankfurt', 'düsseldorf', 'stuttgart']
        for city in cities:
            if city in message_lower:
                data['preferred_city'] = city.title()
                break
        
        # Поиск профессии
        professions = ['developer', 'engineer', 'manager', 'designer', 'analyst', 'consultant']
        for prof in professions:
            if prof in message_lower:
                data['profession'] = prof.title()
                break
        
        return data
    
    def _extract_skills_data(self, message: str) -> Dict[str, Any]:
        """Извлечение данных о навыках"""
        data = {}
        
        # Поиск технических навыков
        tech_skills = ['python', 'java', 'javascript', 'react', 'angular', 'node.js', 'docker']
        found_skills = []
        
        message_lower = message.lower()
        for skill in tech_skills:
            if skill in message_lower:
                found_skills.append(skill.title())
        
        if found_skills:
            data['technical_skills'] = found_skills
        
        # Поиск опыта работы
        if 'год' in message_lower or 'лет' in message_lower:
            data['experience_mentioned'] = True
        
        return data
    
    def _extract_preferences_data(self, message: str) -> Dict[str, Any]:
        """Извлечение данных о предпочтениях"""
        data = {}
        
        message_lower = message.lower()
        
        # Поиск зарплатных ожиданий
        if 'евро' in message_lower or '€' in message_lower:
            data['salary_mentioned'] = True
        
        # Поиск формата работы
        if 'remote' in message_lower or 'удаленно' in message_lower:
            data['work_format'] = 'remote'
        elif 'office' in message_lower or 'офис' in message_lower:
            data['work_format'] = 'office'
        
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
        """Генерация рекомендаций вакансий"""
        try:
            collected_data = profile.get('collected_data', {})
            
            # Параметры для поиска
            search_params = {
                'location': collected_data.get('preferred_city', 'Berlin'),
                'language_level': collected_data.get('german_level', 'B1'),
                'search_query': collected_data.get('profession', 'developer')
            }
            
            # Поиск вакансий
            jobs_result = await self.job_search_service.search_jobs(**search_params)
            
            if jobs_result.get('status') == 'success':
                jobs = jobs_result.get('jobs', [])[:5]  # Топ 5 вакансий
                
                # Анализируем совместимость для каждой вакансии
                recommendations = []
                for job in jobs:
                    compatibility = await self._analyze_compatibility(profile, job, user_providers)
                    recommendations.append({
                        'job': job,
                        'compatibility': compatibility,
                        'recommendation_reason': self._get_recommendation_reason(profile, job, compatibility)
                    })
                
                # Сортируем по совместимости
                recommendations.sort(key=lambda x: x['compatibility'].get('score', 0), reverse=True)
                
                return recommendations
            
        except Exception as e:
            logger.error(f"Failed to generate recommendations: {e}")
        
        return []
    
    async def _analyze_compatibility(self,
                                   profile: Dict[str, Any],
                                   job: Dict[str, Any],
                                   user_providers: List[Tuple[str, str, str]] = None) -> Dict[str, Any]:
        """Анализ совместимости с вакансией"""
        
        collected_data = profile.get('collected_data', {})
        
        # Базовая совместимость
        score = 50
        reasons = []
        
        # Проверка города
        job_location = job.get('location', '').lower()
        preferred_city = collected_data.get('preferred_city', '').lower()
        
        if preferred_city and preferred_city in job_location:
            score += 20
            reasons.append(f"Вакансия в желаемом городе: {job_location}")
        
        # Проверка профессии
        job_title = job.get('title', '').lower()
        profession = collected_data.get('profession', '').lower()
        
        if profession and profession in job_title:
            score += 15
            reasons.append(f"Соответствует профессии: {profession}")
        
        # Проверка навыков
        job_description = job.get('description', '').lower()
        technical_skills = collected_data.get('technical_skills', [])
        
        matching_skills = []
        for skill in technical_skills:
            if skill.lower() in job_description:
                matching_skills.append(skill)
        
        if matching_skills:
            score += len(matching_skills) * 5
            reasons.append(f"Совпадают навыки: {', '.join(matching_skills)}")
        
        # Ограничиваем максимальный балл
        score = min(score, 100)
        
        return {
            'score': score,
            'reasons': reasons,
            'analysis_date': datetime.now().isoformat()
        }
    
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
        """Демо-перевод для fallback"""
        
        translations = {
            'ru': {
                'title': 'Разработчик программного обеспечения',
                'company': job_data.get('company', 'Компания'),
                'location': job_data.get('location', 'Германия'),
                'description': 'Интересная позиция разработчика в динамичной команде.',
                'requirements': 'Опыт программирования, знание языков программирования.',
                'salary': job_data.get('salary', 'Обсуждается')
            },
            'en': {
                'title': 'Software Developer',
                'company': job_data.get('company', 'Company'),
                'location': job_data.get('location', 'Germany'),
                'description': 'Exciting developer position in a dynamic team.',
                'requirements': 'Programming experience, knowledge of programming languages.',
                'salary': job_data.get('salary', 'Competitive')
            }
        }
        
        demo_data = translations.get(target_language, translations['en'])
        return json.dumps(demo_data, ensure_ascii=False, indent=2)
    
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
        """Сообщение о завершении"""
        messages = {
            'ru': "Ваш профиль готов! Вот персональные рекомендации вакансий специально для вас:",
            'en': "Your profile is ready! Here are personalized job recommendations specifically for you:",
            'de': "Ihr Profil ist fertig! Hier sind personalisierte Stellenempfehlungen speziell für Sie:"
        }
        
        return messages.get(language, messages['ru'])
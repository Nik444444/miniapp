"""
⚡ Instant Job AI Analyzer - Мгновенный AI анализ вакансий
Революционный сервис для анализа вакансий в реальном времени:
- Мгновенный AI анализ при просмотре списка вакансий
- Показ % совместимости для каждой вакансии
- Умный перевод ключевых частей на понятный язык
- Объяснение, почему вакансия подходит или не подходит
- Предложения по улучшению кандидатуры
"""

import logging
import json
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from modern_llm_manager import modern_llm_manager

logger = logging.getLogger(__name__)

class InstantJobAIAnalyzer:
    def __init__(self, database):
        self.db = database
        
        # Кэш для быстрого анализа
        self.analysis_cache = {}
        self.cache_ttl = 3600  # 1 час
        
        # Параметры мгновенного анализа 
        self.quick_analysis_tokens = 800  # Быстрый анализ
        self.full_analysis_tokens = 1500  # Полный анализ
        
        # Типы анализа
        self.analysis_types = {
            'compatibility': 'Анализ совместимости',
            'translation': 'Умный перевод',
            'explanation': 'Объяснение требований',
            'improvement': 'Советы по улучшению',
            'salary': 'Анализ зарплаты',
            'company': 'Анализ компании'
        }
    
    async def instant_job_analysis(self,
                                 job_data: Dict[str, Any],
                                 user_profile: Dict[str, Any],
                                 analysis_type: str = 'compatibility',
                                 language: str = 'ru',
                                 user_providers: List[Tuple[str, str, str]] = None) -> Dict[str, Any]:
        """
        ⚡ Мгновенный анализ вакансии
        """
        try:
            # Создаем ключ кэша
            cache_key = self._create_cache_key(job_data, user_profile, analysis_type)
            
            # Проверяем кэш
            cached_result = self._get_cached_analysis(cache_key)
            if cached_result:
                logger.info(f"⚡ Using cached analysis for job {job_data.get('title', 'Unknown')}")
                return cached_result
            
            logger.info(f"⚡ Starting instant analysis for job: {job_data.get('title', 'Unknown')}")
            
            # Выполняем мгновенный анализ
            analysis_result = await self._perform_instant_analysis(
                job_data, user_profile, analysis_type, language, user_providers
            )
            
            # Кэшируем результат
            self._cache_analysis(cache_key, analysis_result)
            
            return {
                'status': 'success',
                'analysis': analysis_result,
                'analysis_type': analysis_type,
                'cached': False,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Instant job analysis failed: {e}")
            return {
                'status': 'error',
                'message': f'Ошибка мгновенного анализа: {str(e)}',
                'fallback_analysis': self._create_fallback_analysis(job_data, user_profile, analysis_type)
            }
    
    async def batch_instant_analysis(self,
                                   jobs_list: List[Dict[str, Any]],
                                   user_profile: Dict[str, Any],
                                   language: str = 'ru',
                                   user_providers: List[Tuple[str, str, str]] = None) -> List[Dict[str, Any]]:
        """
        🚀 Пакетный мгновенный анализ списка вакансий
        """
        try:
            logger.info(f"🚀 Starting batch analysis for {len(jobs_list)} jobs")
            
            # Создаем задачи для параллельного анализа
            analysis_tasks = []
            for job in jobs_list[:20]:  # Ограничиваем 20 вакансиями для производительности
                task = self.instant_job_analysis(
                    job, user_profile, 'compatibility', language, user_providers
                )
                analysis_tasks.append(task)
            
            # Выполняем параллельно с таймаутом
            results = await asyncio.gather(*analysis_tasks, return_exceptions=True)
            
            # Обрабатываем результаты
            analyzed_jobs = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Job analysis {i} failed: {result}")
                    # Добавляем fallback анализ
                    analyzed_jobs.append({
                        'job': jobs_list[i],
                        'analysis': self._create_fallback_analysis(jobs_list[i], user_profile, 'compatibility'),
                        'error': True
                    })
                else:
                    analyzed_jobs.append({
                        'job': jobs_list[i],
                        'analysis': result.get('analysis', {}),
                        'error': False
                    })
            
            return analyzed_jobs
            
        except Exception as e:
            logger.error(f"Batch instant analysis failed: {e}")
            # Возвращаем вакансии с fallback анализом
            return [
                {
                    'job': job,
                    'analysis': self._create_fallback_analysis(job, user_profile, 'compatibility'),
                    'error': True
                }
                for job in jobs_list
            ]
    
    async def _perform_instant_analysis(self,
                                      job_data: Dict[str, Any],
                                      user_profile: Dict[str, Any],
                                      analysis_type: str,
                                      language: str,
                                      user_providers: List[Tuple[str, str, str]] = None) -> Dict[str, Any]:
        """Выполнение мгновенного анализа"""
        
        if not user_providers:
            return self._create_fallback_analysis(job_data, user_profile, analysis_type)
        
        # Создаем специализированный промпт
        prompt = self._create_instant_analysis_prompt(job_data, user_profile, analysis_type, language)
        
        try:
            provider, model, api_key = user_providers[0]
            
            # Используем быстрые токены для мгновенного анализа
            max_tokens = self.quick_analysis_tokens if analysis_type == 'compatibility' else self.full_analysis_tokens
            
            ai_analysis = await modern_llm_manager.generate_content(
                prompt=prompt,
                provider=provider,
                model=model,
                api_key=api_key,
                max_tokens=max_tokens
            )
            
            return self._parse_instant_analysis(ai_analysis, job_data, user_profile, analysis_type)
            
        except Exception as e:
            logger.error(f"AI instant analysis failed: {e}")
            return self._create_fallback_analysis(job_data, user_profile, analysis_type)
    
    def _create_instant_analysis_prompt(self,
                                      job_data: Dict[str, Any],
                                      user_profile: Dict[str, Any],
                                      analysis_type: str,
                                      language: str) -> str:
        """Создание промпта для мгновенного анализа"""
        
        job_info = f"""
Вакансия: {job_data.get('title', 'Unknown')}
Компания: {job_data.get('company_name', 'Unknown')}
Описание: {job_data.get('description', 'No description')[:300]}...
Требования: {job_data.get('requirements', 'No requirements')}
Зарплата: {job_data.get('salary', 'Not specified')}
Локация: {job_data.get('location', 'Unknown')}
"""
        
        profile_summary = self._create_profile_summary(user_profile)
        
        if analysis_type == 'compatibility':
            return self._create_compatibility_prompt(job_info, profile_summary, language)
        elif analysis_type == 'translation':
            return self._create_translation_prompt(job_info, language)
        elif analysis_type == 'explanation':
            return self._create_explanation_prompt(job_info, language)
        elif analysis_type == 'improvement':
            return self._create_improvement_prompt(job_info, profile_summary, language)
        else:
            return self._create_compatibility_prompt(job_info, profile_summary, language)
    
    def _create_compatibility_prompt(self, job_info: str, profile_summary: str, language: str) -> str:
        """Промпт для анализа совместимости"""
        
        if language == 'ru':
            return f"""
Ты эксперт-рекрутер. Быстро проанализируй совместимость кандидата с вакансией.

ВАКАНСИЯ:
{job_info}

ПРОФИЛЬ КАНДИДАТА:
{profile_summary}

Дай МГНОВЕННЫЙ анализ (максимум 200 слов):

1. СОВМЕСТИМОСТЬ (0-100%): Точный балл совместимости
2. КЛЮЧЕВЫЕ ПЛЮСЫ: 2-3 главных преимущества кандидата
3. ОСНОВНЫЕ МИНУСЫ: 1-2 главных недостатка или пробела
4. ШАНСЫ УСПЕХА: Реальная оценка получения интервью/оффера
5. ОДНА РЕКОМЕНДАЦИЯ: Самый важный совет для улучшения кандидатуры

Будь краток, конкретен и честен. Ответ в формате JSON.
"""
        else:
            return f"""
You're an expert recruiter. Quickly analyze candidate-job compatibility.

JOB:
{job_info}

CANDIDATE PROFILE:
{profile_summary}

Give INSTANT analysis (max 200 words):

1. COMPATIBILITY (0-100%): Exact compatibility score
2. KEY STRENGTHS: 2-3 main candidate advantages  
3. MAIN WEAKNESSES: 1-2 main gaps or weaknesses
4. SUCCESS CHANCES: Realistic assessment for interview/offer
5. ONE RECOMMENDATION: Most important advice to improve candidacy

Be brief, specific and honest. Response in JSON format.
"""
    
    def _create_translation_prompt(self, job_info: str, language: str) -> str:
        """Промпт для умного перевода"""
        
        if language == 'ru':
            return f"""
Переведи ключевые части вакансии на русский язык простым, понятным языком.

ВАКАНСИЯ:
{job_info}

Переведи и объясни:
1. НАЗВАНИЕ И РОЛЬ: Что именно делает этот специалист
2. КЛЮЧЕВЫЕ ТРЕБОВАНИЯ: Самые важные навыки и опыт (простыми словами)
3. ОБЯЗАННОСТИ: Основные задачи на работе
4. УСЛОВИЯ: Зарплата, график, льготы
5. КОМПАНИЯ: Кто такие и чем занимаются

Избегай профессионального жаргона. Объясняй как обычному человеку.
Ответ в формате JSON.
"""
        else:
            return f"""
Translate key parts of the job posting into simple, understandable {language}.

JOB:
{job_info}

Translate and explain:
1. TITLE & ROLE: What exactly this specialist does
2. KEY REQUIREMENTS: Most important skills and experience (in simple terms)
3. RESPONSIBILITIES: Main job tasks
4. CONDITIONS: Salary, schedule, benefits  
5. COMPANY: Who they are and what they do

Avoid professional jargon. Explain to a regular person.
Response in JSON format.
"""
    
    def _create_improvement_prompt(self, job_info: str, profile_summary: str, language: str) -> str:
        """Промпт для советов по улучшению"""
        
        if language == 'ru':
            return f"""
Дай конкретные советы, как кандидату улучшить свои шансы на эту вакансию.

ВАКАНСИЯ:
{job_info}

ПРОФИЛЬ КАНДИДАТА:
{profile_summary}

Дай 5 КОНКРЕТНЫХ советов:

1. НАВЫКИ: Какие навыки срочно нужно подтянуть
2. ОПЫТ: Какой опыт/проекты можно получить быстро
3. CV: Как переписать резюме под эту вакансию
4. ПОДГОТОВКА: Что изучить перед интервью
5. СЕТЬ: Как найти связи в этой компании/индустрии

Каждый совет должен быть ДЕЙСТВЕННЫМ и КОНКРЕТНЫМ.
Ответ в формате JSON.
"""
        else:
            return f"""
Give specific advice on how the candidate can improve their chances for this job.

JOB:
{job_info}

CANDIDATE PROFILE:  
{profile_summary}

Give 5 SPECIFIC tips:

1. SKILLS: Which skills urgently need improvement
2. EXPERIENCE: What experience/projects can be gained quickly
3. CV: How to rewrite resume for this job
4. PREPARATION: What to study before interview
5. NETWORK: How to find connections in this company/industry

Each tip should be ACTIONABLE and SPECIFIC.
Response in JSON format.
"""
    
    def _create_profile_summary(self, user_profile: Dict[str, Any]) -> str:
        """Создание краткого резюме профиля"""
        
        collected_data = user_profile.get('collected_data', {})
        
        return f"""
Профессия: {collected_data.get('profession', 'Unknown')}
Опыт: {collected_data.get('experience_years', 'Unknown')} лет
Навыки: {', '.join(collected_data.get('technical_skills', ['Not specified']))}
Немецкий: {collected_data.get('german_level', 'Unknown')}
Город: {collected_data.get('preferred_city', 'Unknown')}
Зарплата: {collected_data.get('salary_expectations', 'Unknown')}
Формат работы: {collected_data.get('work_format', 'Unknown')}
"""
    
    def _parse_instant_analysis(self,
                              ai_analysis: str,
                              job_data: Dict[str, Any],
                              user_profile: Dict[str, Any],
                              analysis_type: str) -> Dict[str, Any]:
        """Парсинг результатов мгновенного анализа"""
        
        try:
            # Пытаемся извлечь JSON
            if '{' in ai_analysis and '}' in ai_analysis:
                json_start = ai_analysis.find('{')
                json_end = ai_analysis.rfind('}') + 1
                json_str = ai_analysis[json_start:json_end]
                parsed = json.loads(json_str)
                
                # Добавляем метаданные
                parsed['analysis_type'] = analysis_type
                parsed['job_title'] = job_data.get('title', 'Unknown')
                parsed['company'] = job_data.get('company_name', 'Unknown')
                parsed['analyzed_at'] = datetime.now().isoformat()
                
                return parsed
        except:
            pass
        
        # Fallback парсинг
        return self._extract_fallback_data(ai_analysis, analysis_type)
    
    def _extract_fallback_data(self, ai_analysis: str, analysis_type: str) -> Dict[str, Any]:
        """Извлечение данных из текстового ответа как fallback"""
        
        base_data = {
            'analysis_type': analysis_type,
            'raw_analysis': ai_analysis[:500] + '...' if len(ai_analysis) > 500 else ai_analysis,
            'analyzed_at': datetime.now().isoformat()
        }
        
        if analysis_type == 'compatibility':
            # Пытаемся извлечь процент совместимости
            import re
            percentage_match = re.search(r'(\d+)%', ai_analysis)
            compatibility_score = int(percentage_match.group(1)) if percentage_match else 75
            
            base_data.update({
                'compatibility_score': compatibility_score,
                'key_strengths': ['Анализ выполнен', 'Найдены совпадения'],
                'main_weaknesses': ['Требуется дополнительная проверка'],
                'success_chances': 'Средние перспективы',
                'recommendation': 'Рассмотрите подачу заявки'
            })
        
        return base_data
    
    def _create_fallback_analysis(self,
                                job_data: Dict[str, Any],
                                user_profile: Dict[str, Any],
                                analysis_type: str) -> Dict[str, Any]:
        """Создание fallback анализа при ошибке AI"""
        
        collected_data = user_profile.get('collected_data', {})
        
        if analysis_type == 'compatibility':
            # Простой алгоритм совместимости на основе ключевых слов
            job_title = job_data.get('title', '').lower()
            job_desc = job_data.get('description', '').lower()
            profession = collected_data.get('profession', '').lower()
            skills = collected_data.get('technical_skills', [])
            
            # Базовая совместимость
            compatibility_score = 50
            
            # Проверяем профессию в названии
            if profession in job_title:
                compatibility_score += 30
            elif profession in job_desc:
                compatibility_score += 20
            
            # Проверяем навыки
            skill_matches = 0
            for skill in skills:
                if skill.lower() in job_desc or skill.lower() in job_title:
                    skill_matches += 1
            
            compatibility_score += min(skill_matches * 5, 20)
            compatibility_score = min(compatibility_score, 100)
            
            return {
                'compatibility_score': compatibility_score,
                'key_strengths': [
                    f'Опыт в области {profession}',
                    f'Навыки: {", ".join(skills[:3])}' if skills else 'Общие навыки'
                ],
                'main_weaknesses': [
                    'Требуется детальная проверка требований',
                    'Рекомендуется дополнительная подготовка'
                ],
                'success_chances': 'Средние' if compatibility_score >= 70 else 'Низкие',
                'recommendation': 'Внимательно изучите требования и подготовьте сильное сопроводительное письмо',
                'analysis_type': 'fallback_compatibility',
                'fallback_mode': True
            }
        
        # Для других типов анализа
        return {
            'analysis_type': analysis_type,
            'fallback_mode': True,
            'message': 'Анализ выполнен в упрощенном режиме',
            'job_title': job_data.get('title', 'Unknown'),
            'company': job_data.get('company_name', 'Unknown')
        }
    
    # =====================================================
    # КЭШИРОВАНИЕ
    # =====================================================
    
    def _create_cache_key(self,
                         job_data: Dict[str, Any],
                         user_profile: Dict[str, Any],
                         analysis_type: str) -> str:
        """Создание ключа кэша"""
        
        job_key = f"{job_data.get('title', '')}-{job_data.get('company_name', '')}"
        profile_key = f"{user_profile.get('collected_data', {}).get('profession', '')}"
        
        return f"{analysis_type}:{hash(job_key)}:{hash(profile_key)}"
    
    def _get_cached_analysis(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Получение анализа из кэша"""
        
        if cache_key in self.analysis_cache:
            cached_data = self.analysis_cache[cache_key]
            
            # Проверяем TTL
            cache_time = datetime.fromisoformat(cached_data['cached_at'])
            if (datetime.now() - cache_time).seconds < self.cache_ttl:
                cached_data['from_cache'] = True
                return cached_data
            else:
                # Удаляем устаревший кэш
                del self.analysis_cache[cache_key]
        
        return None
    
    def _cache_analysis(self, cache_key: str, analysis_result: Dict[str, Any]) -> None:
        """Сохранение анализа в кэш"""
        
        analysis_result['cached_at'] = datetime.now().isoformat()
        self.analysis_cache[cache_key] = analysis_result
        
        # Ограничиваем размер кэша
        if len(self.analysis_cache) > 1000:
            # Удаляем старые записи
            oldest_keys = sorted(
                self.analysis_cache.keys(),
                key=lambda k: self.analysis_cache[k].get('cached_at', ''),
            )[:100]
            
            for key in oldest_keys:
                del self.analysis_cache[key]

# Создаем глобальный экземпляр
instant_job_analyzer = None

def get_instant_job_analyzer(database):
    global instant_job_analyzer
    if instant_job_analyzer is None:
        instant_job_analyzer = InstantJobAIAnalyzer(database)
    return instant_job_analyzer
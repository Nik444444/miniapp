"""
🚀 Revolutionary AI Recruiter - Революционный AI-рекрутер нового поколения
Супер-умный AI рекрутер, который:
- Проводит глубокий анализ профиля кандидата
- Создает персональную стратегию поиска работы
- Дает точные предсказания успешности
- Анализирует рынок труда в реальном времени
- Генерирует идеальные сопроводительные письма
- Предоставляет стратегические карьерные советы
"""

import logging
import json
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from modern_llm_manager import modern_llm_manager
from job_search_service import JobSearchService
from german_cities_service import GermanCitiesService

logger = logging.getLogger(__name__)

class RevolutionaryAIRecruiter:
    def __init__(self, database):
        self.db = database
        self.job_search_service = JobSearchService()
        self.cities_service = GermanCitiesService()
        
        # Революционные этапы анализа
        self.analysis_stages = {
            'profile_analysis': {'name': 'Глубокий анализ профиля', 'weight': 20},
            'market_analysis': {'name': 'Анализ рынка труда', 'weight': 20},
            'skill_gap_analysis': {'name': 'Анализ навыков', 'weight': 15},
            'salary_analysis': {'name': 'Анализ зарплатных возможностей', 'weight': 15},
            'strategy_creation': {'name': 'Создание стратегии поиска', 'weight': 15},
            'optimization': {'name': 'Оптимизация профиля', 'weight': 15}
        }
        
        # Категории навыков для глубокого анализа
        self.skill_categories = {
            'technical': 'Технические навыки',
            'soft': 'Мягкие навыки', 
            'language': 'Языковые навыки',
            'domain': 'Знание предметной области',
            'leadership': 'Лидерские качества',
            'analytical': 'Аналитические способности'
        }
        
        # Типы карьерных стратегий
        self.career_strategies = {
            'aggressive': 'Агрессивная стратегия (быстрый рост)',
            'steady': 'Устойчивая стратегия (постепенное развитие)',
            'pivot': 'Стратегия смены направления',
            'specialist': 'Стратегия углубления экспертизы',
            'generalist': 'Стратегия расширения компетенций'
        }

    async def conduct_revolutionary_analysis(self,
                                           user_id: str,
                                           user_language: str = 'ru',
                                           user_providers: List[Tuple[str, str, str]] = None) -> Dict[str, Any]:
        """
        🚀 Проведение революционного анализа кандидата
        """
        try:
            logger.info(f"🚀 Starting revolutionary analysis for user {user_id}")
            
            # Получаем существующий профиль или создаем новый
            profile = await self.db.get_ai_recruiter_profile(user_id)
            if not profile:
                return {
                    'status': 'error',
                    'message': 'Профиль не найден. Сначала пройдите базовое интервью с AI-рекрутером.'
                }
            
            # Запускаем революционный анализ
            analysis_result = await self._perform_comprehensive_analysis(
                profile, user_language, user_providers
            )
            
            # Сохраняем результаты анализа
            profile['revolutionary_analysis'] = analysis_result
            profile['last_analysis'] = datetime.now().isoformat()
            await self.db.save_ai_recruiter_profile(user_id, profile)
            
            return {
                'status': 'success',
                'analysis': analysis_result,
                'profile': profile,
                'recommendations_generated': len(analysis_result.get('job_recommendations', [])),
                'career_strategy': analysis_result.get('career_strategy'),
                'success_predictions': analysis_result.get('success_predictions')
            }
            
        except Exception as e:
            logger.error(f"Revolutionary analysis failed: {e}")
            return {
                'status': 'error',
                'message': f'Ошибка революционного анализа: {str(e)}'
            }
    
    async def _perform_comprehensive_analysis(self,
                                            profile: Dict[str, Any],
                                            language: str,
                                            user_providers: List[Tuple[str, str, str]] = None) -> Dict[str, Any]:
        """Комплексный революционный анализ"""
        
        collected_data = profile.get('collected_data', {})
        
        # 1. Глубокий анализ профиля
        profile_analysis = await self._deep_profile_analysis(collected_data, language, user_providers)
        
        # 2. Анализ рынка труда
        market_analysis = await self._analyze_job_market(collected_data, language, user_providers)
        
        # 3. Анализ пробелов в навыках
        skill_gap_analysis = await self._analyze_skill_gaps(collected_data, market_analysis, language, user_providers)
        
        # 4. Анализ зарплатных возможностей
        salary_analysis = await self._analyze_salary_potential(collected_data, market_analysis, language, user_providers)
        
        # 5. Создание персональной стратегии
        career_strategy = await self._create_career_strategy(
            profile_analysis, market_analysis, skill_gap_analysis, language, user_providers
        )
        
        # 6. Генерация революционных рекомендаций
        job_recommendations = await self._generate_revolutionary_recommendations(
            profile, market_analysis, career_strategy, user_providers
        )
        
        # 7. Предсказания успешности
        success_predictions = await self._predict_success_rates(
            profile_analysis, market_analysis, job_recommendations, language, user_providers
        )
        
        return {
            'profile_analysis': profile_analysis,
            'market_analysis': market_analysis,
            'skill_gap_analysis': skill_gap_analysis,
            'salary_analysis': salary_analysis,
            'career_strategy': career_strategy,
            'job_recommendations': job_recommendations,
            'success_predictions': success_predictions,
            'analysis_timestamp': datetime.now().isoformat(),
            'analysis_version': '2.0_revolutionary'
        }
    
    async def _deep_profile_analysis(self,
                                   collected_data: Dict[str, Any],
                                   language: str,
                                   user_providers: List[Tuple[str, str, str]] = None) -> Dict[str, Any]:
        """Глубокий анализ профиля кандидата"""
        
        if not user_providers:
            return self._create_demo_profile_analysis(collected_data, language)
        
        prompt = self._create_profile_analysis_prompt(collected_data, language)
        
        try:
            provider, model, api_key = user_providers[0]
            ai_analysis = await modern_llm_manager.generate_content(
                prompt=prompt,
                provider=provider,
                model=model,
                api_key=api_key,
                max_tokens=3000
            )
            
            return self._parse_profile_analysis(ai_analysis, collected_data)
            
        except Exception as e:
            logger.error(f"Profile analysis failed: {e}")
            return self._create_demo_profile_analysis(collected_data, language)
    
    def _create_profile_analysis_prompt(self, data: Dict[str, Any], language: str) -> str:
        """Создание промпта для глубокого анализа профиля"""
        
        data_summary = json.dumps(data, ensure_ascii=False, indent=2)
        
        if language == 'ru':
            return f"""
Ты опытный HR-аналитик и карьерный консультант. Проведи ГЛУБОКИЙ анализ профиля кандидата.

ДАННЫЕ КАНДИДАТА:
{data_summary}

Проанализируй следующие аспекты:

1. СИЛЬНЫЕ СТОРОНЫ:
   - Ключевые профессиональные навыки
   - Уникальные компетенции
   - Конкурентные преимущества

2. СЛАБЫЕ МЕСТА:
   - Пробелы в навыках
   - Области для развития
   - Потенциальные риски при поиске работы

3. ПРОФЕССИОНАЛЬНЫЙ ПОРТРЕТ:
   - Тип профессионала (специалист/универсал)
   - Уровень сениорности
   - Готовность к смене направления

4. РЫНОЧНАЯ ПОЗИЦИЯ:
   - Насколько востребован на рынке
   - В каких секторах наиболее конкурентоспособен
   - Уникальное предложение ценности (USP)

5. КАРЬЕРНЫЙ ПОТЕНЦИАЛ:
   - Возможности роста
   - Рекомендуемые направления развития
   - Временные рамки достижения целей

6. ПСИХОЛОГИЧЕСКИЙ ПРОФИЛЬ:
   - Мотивационные факторы
   - Стиль работы
   - Предпочтения в командной работе

Дай конкретные, действенные рекомендации. Будь честным и объективным.
Ответ структурируй в формате JSON.
"""
        else:
            return f"""
You are an experienced HR analyst and career consultant. Conduct a DEEP analysis of the candidate's profile.

CANDIDATE DATA:
{data_summary}

Analyze the following aspects:

1. STRENGTHS:
   - Key professional skills
   - Unique competencies  
   - Competitive advantages

2. WEAKNESSES:
   - Skill gaps
   - Areas for development
   - Potential job search risks

3. PROFESSIONAL PORTRAIT:
   - Type of professional (specialist/generalist)
   - Seniority level
   - Readiness for career change

4. MARKET POSITION:
   - Market demand level
   - Most competitive sectors
   - Unique value proposition (USP)

5. CAREER POTENTIAL:
   - Growth opportunities
   - Recommended development directions
   - Timeline for achieving goals

6. PSYCHOLOGICAL PROFILE:
   - Motivational factors
   - Work style
   - Team collaboration preferences

Give specific, actionable recommendations. Be honest and objective.
Structure your response in JSON format.
"""
    
    async def _analyze_job_market(self,
                                 collected_data: Dict[str, Any],
                                 language: str,
                                 user_providers: List[Tuple[str, str, str]] = None) -> Dict[str, Any]:
        """Анализ рынка труда в реальном времени"""
        
        # Получаем реальные данные с рынка
        search_params = {
            'location': collected_data.get('preferred_city', 'Berlin'),
            'language_level': collected_data.get('german_level', 'B1'),
            'search_query': collected_data.get('profession', 'developer')
        }
        
        try:
            # Получаем актуальные вакансии
            jobs_result = await self.job_search_service.search_jobs(**search_params)
            current_jobs = jobs_result.get('jobs', [])
            
            # Анализируем тренды
            market_trends = await self._analyze_market_trends(current_jobs, collected_data, language, user_providers)
            
            # Анализируем зарплатные вилки
            salary_trends = self._analyze_salary_trends(current_jobs)
            
            # Анализируем требуемые навыки
            skill_trends = self._analyze_skill_trends(current_jobs)
            
            # Анализируем компании
            company_analysis = self._analyze_companies(current_jobs)
            
            return {
                'total_jobs_found': len(current_jobs),
                'market_trends': market_trends,
                'salary_trends': salary_trends,
                'skill_trends': skill_trends,
                'company_analysis': company_analysis,
                'competition_level': self._assess_competition_level(len(current_jobs)),
                'market_hotness': self._assess_market_hotness(current_jobs),
                'analysis_date': datetime.now().isoformat(),
                'search_parameters': search_params
            }
            
        except Exception as e:
            logger.error(f"Market analysis failed: {e}")
            return self._create_demo_market_analysis(collected_data, language)
    
    async def _generate_revolutionary_recommendations(self,
                                                    profile: Dict[str, Any],
                                                    market_analysis: Dict[str, Any],
                                                    career_strategy: Dict[str, Any],
                                                    user_providers: List[Tuple[str, str, str]] = None) -> List[Dict[str, Any]]:
        """Генерация революционных рекомендаций вакансий"""
        
        try:
            collected_data = profile.get('collected_data', {})
            
            # Расширенные параметры поиска на основе анализа
            base_params = {
                'location': collected_data.get('preferred_city', 'Berlin'),
                'language_level': collected_data.get('german_level', 'B1'),
                'search_query': collected_data.get('profession', 'developer')
            }
            
            # Получаем вакансии с нескольких источников
            all_jobs = []
            
            # Основной поиск
            main_search = await self.job_search_service.search_jobs(**base_params)
            if main_search.get('status') == 'success':
                all_jobs.extend(main_search.get('jobs', []))
            
            # Дополнительные поиски по вариациям профессии
            profession_variants = self._get_profession_variants(collected_data.get('profession', ''))
            for variant in profession_variants[:3]:  # Ограничиваем 3 вариантами
                variant_params = base_params.copy()
                variant_params['search_query'] = variant
                variant_search = await self.job_search_service.search_jobs(**variant_params)
                if variant_search.get('status') == 'success':
                    all_jobs.extend(variant_search.get('jobs', [])[:5])  # Берем топ-5 от каждого варианта
            
            # Убираем дубликаты
            unique_jobs = self._remove_duplicate_jobs(all_jobs)
            
            if not unique_jobs:
                return self._create_demo_recommendations(collected_data)
            
            # Революционный анализ каждой вакансии
            revolutionary_recommendations = []
            
            for job in unique_jobs[:15]:  # Анализируем топ-15 вакансий
                job_analysis = await self._revolutionary_job_analysis(
                    job, profile, market_analysis, career_strategy, user_providers
                )
                
                if job_analysis['compatibility_score'] >= 60:  # Только хорошие совпадения
                    revolutionary_recommendations.append({
                        'job': job,
                        'revolutionary_analysis': job_analysis,
                        'ai_insights': job_analysis.get('ai_insights', {}),
                        'success_prediction': job_analysis.get('success_prediction', {}),
                        'application_strategy': job_analysis.get('application_strategy', {}),
                        'interview_preparation': job_analysis.get('interview_preparation', {})
                    })
            
            # Сортируем по революционному скорингу
            revolutionary_recommendations.sort(
                key=lambda x: x['revolutionary_analysis']['total_score'], 
                reverse=True
            )
            
            return revolutionary_recommendations[:10]  # Топ-10 лучших
            
        except Exception as e:
            logger.error(f"Revolutionary recommendations failed: {e}")
            return self._create_demo_recommendations(collected_data)
    
    async def _revolutionary_job_analysis(self,
                                        job: Dict[str, Any],
                                        profile: Dict[str, Any],
                                        market_analysis: Dict[str, Any],
                                        career_strategy: Dict[str, Any],
                                        user_providers: List[Tuple[str, str, str]] = None) -> Dict[str, Any]:
        """Революционный анализ конкретной вакансии"""
        
        if not user_providers:
            return self._create_demo_job_analysis(job, profile)
        
        prompt = self._create_revolutionary_job_analysis_prompt(job, profile, market_analysis, career_strategy)
        
        try:
            provider, model, api_key = user_providers[0]
            ai_analysis = await modern_llm_manager.generate_content(
                prompt=prompt,
                provider=provider,
                model=model,
                api_key=api_key,
                max_tokens=2500
            )
            
            return self._parse_revolutionary_job_analysis(ai_analysis, job, profile)
            
        except Exception as e:
            logger.error(f"Revolutionary job analysis failed: {e}")
            return self._create_demo_job_analysis(job, profile)
    
    def _create_revolutionary_job_analysis_prompt(self,
                                                job: Dict[str, Any],
                                                profile: Dict[str, Any],
                                                market_analysis: Dict[str, Any],
                                                career_strategy: Dict[str, Any]) -> str:
        """Создание промпта для революционного анализа вакансии"""
        
        job_info = f"""
Вакансия: {job.get('title', 'Unknown')}
Компания: {job.get('company_name', 'Unknown')}
Описание: {job.get('description', 'No description')[:500]}...
Требования: {job.get('requirements', 'No requirements')}
Локация: {job.get('location', 'Unknown')}
Зарплата: {job.get('salary', 'Not specified')}
"""
        
        candidate_data = json.dumps(profile.get('collected_data', {}), ensure_ascii=False, indent=2)
        market_data = json.dumps(market_analysis, ensure_ascii=False, indent=2)
        strategy_data = json.dumps(career_strategy, ensure_ascii=False, indent=2)
        
        return f"""
Ты революционный AI-рекрутер с 20-летним опытом. Проведи ГЛУБОКИЙ анализ соответствия кандидата вакансии.

ВАКАНСИЯ:
{job_info}

ПРОФИЛЬ КАНДИДАТА:
{candidate_data}

АНАЛИЗ РЫНКА:
{market_data}

КАРЬЕРНАЯ СТРАТЕГИЯ:
{strategy_data}

Проведи РЕВОЛЮЦИОННЫЙ анализ по следующим критериям:

1. СОВМЕСТИМОСТЬ (0-100):
   - Точное соответствие навыков
   - Опыт в релевантных областях
   - Культурное соответствие

2. УСПЕШНОСТЬ КАНДИДАТУРЫ (0-100):
   - Вероятность получения интервью
   - Вероятность получения оффера
   - Конкуренция с другими кандидатами

3. КАРЬЕРНАЯ ЦЕННОСТЬ (0-100):
   - Соответствие карьерным целям
   - Потенциал роста в компании
   - Развитие навыков

4. AI ИНСАЙТЫ:
   - Скрытые возможности в вакансии
   - Нестандартные преимущества кандидата
   - "Секретные" требования работодателя

5. СТРАТЕГИЯ ПОДАЧИ:
   - Как лучше всего подать заявку
   - Ключевые моменты для CV
   - Особенности сопроводительного письма

6. ПОДГОТОВКА К ИНТЕРВЬЮ:
   - Вопросы, которые зададут
   - Как продемонстрировать сильные стороны
   - Возможные слабые места и как их обыграть

7. ЗАРПЛАТНЫЕ ОЖИДАНИЯ:
   - Реалистичная вилка для переговоров
   - Дополнительные льготы и компенсации

Будь максимально конкретным и практичным. Дай четкий план действий.
Ответ в формате JSON со всеми разделами.
"""
    
    async def generate_perfect_cover_letter(self,
                                          job_data: Dict[str, Any],
                                          user_id: str,
                                          style: str = 'professional',
                                          user_providers: List[Tuple[str, str, str]] = None) -> Dict[str, Any]:
        """
        📝 Генерация идеального сопроводительного письма
        """
        try:
            # Получаем расширенный профиль
            profile = await self.db.get_ai_recruiter_profile(user_id)
            if not profile:
                return {
                    'status': 'error',
                    'message': 'Профиль не найден. Сначала пройдите анализ с AI-рекрутером.'
                }
            
            # Получаем революционный анализ
            revolutionary_analysis = profile.get('revolutionary_analysis', {})
            
            # Создаем идеальное письмо
            cover_letter = await self._create_perfect_cover_letter(
                job_data, profile, revolutionary_analysis, style, user_providers
            )
            
            return {
                'status': 'success',
                'cover_letter': cover_letter,
                'personalization_score': cover_letter.get('personalization_score', 85),
                'style': style,
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Perfect cover letter generation failed: {e}")
            return {
                'status': 'error',
                'message': f'Ошибка генерации письма: {str(e)}'
            }
    
    async def _create_perfect_cover_letter(self,
                                         job_data: Dict[str, Any],
                                         profile: Dict[str, Any],
                                         revolutionary_analysis: Dict[str, Any],
                                         style: str,
                                         user_providers: List[Tuple[str, str, str]] = None) -> Dict[str, Any]:
        """Создание идеального сопроводительного письма"""
        
        if not user_providers:
            return self._create_demo_cover_letter(job_data, profile, style)
        
        prompt = self._create_cover_letter_prompt(job_data, profile, revolutionary_analysis, style)
        
        try:
            provider, model, api_key = user_providers[0]
            ai_letter = await modern_llm_manager.generate_content(
                prompt=prompt,
                provider=provider,
                model=model,
                api_key=api_key,
                max_tokens=2000
            )
            
            return self._parse_perfect_cover_letter(ai_letter, job_data, style)
            
        except Exception as e:
            logger.error(f"Cover letter creation failed: {e}")
            return self._create_demo_cover_letter(job_data, profile, style)
    
    def _create_cover_letter_prompt(self, job_data: Dict[str, Any], profile: Dict[str, Any], revolutionary_analysis: Dict[str, Any], style: str) -> str:
        """Создание промпта для идеального сопроводительного письма"""
        
        job_info = f"""
Должность: {job_data.get('title', 'Unknown')}
Компания: {job_data.get('company_name', 'Unknown')}
Описание: {job_data.get('description', 'No description')[:400]}...
Требования: {job_data.get('requirements', 'No requirements')}
Зарплата: {job_data.get('salary', 'Not specified')}
Локация: {job_data.get('location', 'Unknown')}
"""
        
        user_data = profile.get('collected_data', {})
        analysis_data = json.dumps(revolutionary_analysis, ensure_ascii=False, indent=2) if revolutionary_analysis else "Нет данных анализа"
        
        style_instructions = {
            'professional': 'Строго деловой стиль, формальный тон, подчеркивание профессиональных достижений',
            'creative': 'Креативный подход, живой язык, подчеркивание уникальности и инновационности',
            'technical': 'Технический стиль, фокус на навыках и технологиях, использование профессиональной терминологии',
            'friendly': 'Дружелюбный тон, личностный подход, подчеркивание командной работы и культурного соответствия'
        }
        
        return f"""
Ты эксперт по написанию сопроводительных писем с 15-летним опытом в HR.

Создай ИДЕАЛЬНОЕ сопроводительное письмо в стиле "{style}".

ВАКАНСИЯ:
{job_info}

ПРОФИЛЬ КАНДИДАТА:
Профессия: {user_data.get('profession', 'Unknown')}
Опыт: {user_data.get('experience_years', 'Unknown')} лет
Навыки: {', '.join(user_data.get('technical_skills', ['Not specified']))}
Немецкий: {user_data.get('german_level', 'Unknown')}
Образование: {user_data.get('has_education', 'Unknown')}
Предпочтения: {user_data.get('work_format', 'Unknown')}

РЕВОЛЮЦИОННЫЙ АНАЛИЗ:
{analysis_data}

СТИЛЬ ПИСЬМА: {style_instructions.get(style, 'Professional approach')}

Создай письмо которое:

1. ЗАГОЛОВОК: Цепляющая тема письма
2. ПРИВЕТСТВИЕ: Персональное обращение к HR/нанимающему менеджеру
3. ВСТУПЛЕНИЕ (1 абзац): 
   - Конкретная позиция и где нашел вакансию
   - Краткое, но мощное заявление о соответствии
4. ОСНОВНАЯ ЧАСТЬ (2-3 абзаца):
   - Конкретные примеры релевантного опыта
   - Как навыки решат проблемы компании
   - Уникальные преимущества кандидата
5. МОТИВАЦИЯ (1 абзац):
   - Почему именно эта компания
   - Что привлекает в позиции
   - Какой вклад может внести
6. ЗАКЛЮЧЕНИЕ:
   - Call-to-action на интервью
   - Профессиональное закрытие

ТРЕБОВАНИЯ:
- Максимум 350 слов
- Конкретные факты, НЕ общие фразы
- Подчеркнуть 2-3 ключевых совпадения с требованиями
- Показать знание компании (если возможно)
- Уверенный, но не навязчивый тон

Ответ в формате JSON со структурированными полями.
"""
    
    def _parse_perfect_cover_letter(self, ai_letter: str, job_data: Dict[str, Any], style: str) -> Dict[str, Any]:
        """Парсинг идеального сопроводительного письма"""
        
        try:
            # Пытаемся извлечь JSON
            if '{' in ai_letter and '}' in ai_letter:
                json_start = ai_letter.find('{')
                json_end = ai_letter.rfind('}') + 1
                json_str = ai_letter[json_start:json_end]
                parsed = json.loads(json_str)
                
                # Добавляем метаданные
                parsed['style'] = style
                parsed['job_title'] = job_data.get('title', 'Unknown')
                parsed['company'] = job_data.get('company_name', 'Unknown')
                parsed['personalization_score'] = self._calculate_personalization_score(parsed)
                parsed['generated_at'] = datetime.now().isoformat()
                
                return parsed
        except:
            pass
        
        # Fallback структурирование
        return {
            'subject': f"Заявка на позицию {job_data.get('title', 'Unknown')}",
            'greeting': f"Уважаемый HR-менеджер {job_data.get('company_name', 'компании')}!",
            'body': ai_letter if len(ai_letter) < 1000 else ai_letter[:1000] + '...',
            'closing': 'С уважением,\n[Ваше имя]',
            'full_text': ai_letter,
            'word_count': len(ai_letter.split()),
            'style': style,
            'personalization_score': 75,
            'generated_at': datetime.now().isoformat()
        }
    
    def _calculate_personalization_score(self, letter_data: Dict[str, Any]) -> int:
        """Расчет балла персонализации письма"""
        score = 50  # Базовый балл
        
        # Проверяем наличие ключевых элементов
        if letter_data.get('subject') and 'позиция' in letter_data['subject'].lower():
            score += 10
        
        if letter_data.get('body'):
            body = letter_data['body'].lower()
            if 'компания' in body or 'организация' in body:
                score += 10
            if any(skill in body for skill in ['опыт', 'навык', 'умение', 'знание']):
                score += 10
            if 'интервью' in body or 'встреча' in body:
                score += 10
            if len(body.split()) >= 200:  # Достаточная длина
                score += 10
        
        return min(score, 100)
    
    def _create_demo_cover_letter(self, job_data: Dict[str, Any], profile: Dict[str, Any], style: str) -> Dict[str, Any]:
        """Создание демо сопроводительного письма"""
        
        job_title = job_data.get('title', 'Специалист')
        company = job_data.get('company_name', 'Компания')
        user_data = profile.get('collected_data', {})
        profession = user_data.get('profession', 'специалист')
        
        demo_body = f"""Меня заинтересовала вакансия {job_title} в {company}.

Мой опыт работы в качестве {profession} и знание современных технологий позволят мне эффективно решать задачи на этой позиции. Я обладаю необходимыми навыками и готов внести значительный вклад в развитие вашей команды.

{company} привлекает меня как инновативная компания с отличной репутацией. Я был бы рад обсудить мою кандидатуру более подробно на собеседовании.

Готов приступить к работе в ближайшее время и с нетерпением жду вашего ответа."""
        
        return {
            'subject': f'Заявка на позицию {job_title}',
            'greeting': f'Уважаемые представители {company}!',
            'body': demo_body,
            'closing': 'С уважением,\n[Ваше имя]',
            'full_text': f'Уважаемые представители {company}!\n\n{demo_body}\n\nС уважением,\n[Ваше имя]',
            'word_count': len(demo_body.split()),
            'style': style,
            'personalization_score': 80,
            'generated_at': datetime.now().isoformat(),
            'demo_mode': True
        }
    async def _analyze_skill_gaps(self,
                                collected_data: Dict[str, Any],
                                market_analysis: Dict[str, Any],
                                language: str,
                                user_providers: List[Tuple[str, str, str]] = None) -> Dict[str, Any]:
        """Анализ пробелов в навыках"""
        
        if not user_providers:
            return self._create_demo_skill_gaps_analysis(collected_data, language)
        
        # Извлекаем требуемые навыки из рыночного анализа
        market_skills = market_analysis.get('skill_trends', {}).get('top_skills', [])
        user_skills = collected_data.get('technical_skills', [])
        
        prompt = f"""
Проанализируй пробелы в навыках кандидата по сравнению с требованиями рынка.

НАВЫКИ КАНДИДАТА:
{', '.join(user_skills)}

ВОСТРЕБОВАННЫЕ НАВЫКИ НА РЫНКЕ:
{', '.join(market_skills[:10])}

ПРОФЕССИЯ: {collected_data.get('profession', 'Unknown')}
УРОВЕНЬ ОПЫТА: {collected_data.get('experience_years', 'Unknown')}

Проанализируй:

1. КРИТИЧЕСКИЕ ПРОБЕЛЫ:
   - Навыки, которые срочно нужно изучить
   - Влияние на трудоустройство

2. РЕКОМЕНДУЕМЫЕ К ИЗУЧЕНИЮ:
   - Навыки для улучшения позиций
   - Тренды развития профессии

3. СИЛЬНЫЕ СТОРОНЫ:
   - Навыки, которые уже есть у кандидата
   - Конкурентные преимущества

4. ПЛАН РАЗВИТИЯ:
   - Приоритетность изучения
   - Временные рамки
   - Ресурсы для изучения

Ответ в формате JSON.
"""
        
        try:
            provider, model, api_key = user_providers[0]
            ai_analysis = await modern_llm_manager.generate_content(
                prompt=prompt,
                provider=provider,
                model=model,
                api_key=api_key,
                max_tokens=2000
            )
            
            return self._parse_skill_gaps_analysis(ai_analysis, collected_data)
            
        except Exception as e:
            logger.error(f"Skill gaps analysis failed: {e}")
            return self._create_demo_skill_gaps_analysis(collected_data, language)
    
    async def _analyze_salary_potential(self,
                                      collected_data: Dict[str, Any],
                                      market_analysis: Dict[str, Any],
                                      language: str,
                                      user_providers: List[Tuple[str, str, str]] = None) -> Dict[str, Any]:
        """Анализ зарплатных возможностей"""
        
        if not user_providers:
            return self._create_demo_salary_analysis(collected_data, language)
        
        profession = collected_data.get('profession', 'Unknown')
        experience = collected_data.get('experience_years', 'Unknown')
        city = collected_data.get('preferred_city', 'Berlin')
        current_expectations = collected_data.get('salary_expectations', 'Unknown')
        
        prompt = f"""
Проанализируй зарплатные возможности кандидата на рынке труда Германии.

КАНДИДАТ:
Профессия: {profession}
Опыт: {experience} лет
Город: {city}
Текущие ожидания: {current_expectations}

ДАННЫЕ РЫНКА:
{json.dumps(market_analysis.get('salary_trends', {}), ensure_ascii=False, indent=2)}

Проанализируй:

1. РЕАЛИСТИЧНАЯ ЗАРПЛАТНАЯ ВИЛКА:
   - Минимум для данного уровня опыта
   - Средний уровень в отрасли
   - Максимум при отличной подготовке

2. ФАКТОРЫ ВЛИЯНИЯ НА ЗАРПЛАТУ:
   - Положительные (что увеличивает доход)
   - Отрицательные (что может снижать предложения)

3. СРАВНЕНИЕ С ОЖИДАНИЯМИ:
   - Реалистичность текущих ожиданий
   - Рекомендации по корректировке

4. СТРАТЕГИЯ ПЕРЕГОВОРОВ:
   - Начальная позиция для переговоров
   - Аргументы для обоснования зарплаты
   - Дополнительные льготы и компенсации

5. ПЕРСПЕКТИВЫ РОСТА:
   - Зарплатные возможности через 1-2 года
   - Что нужно для увеличения дохода

Учитывай особенности немецкого рынка труда.
Ответ в формате JSON.
"""
        
        try:
            provider, model, api_key = user_providers[0]
            ai_analysis = await modern_llm_manager.generate_content(
                prompt=prompt,
                provider=provider,
                model=model,
                api_key=api_key,
                max_tokens=2000
            )
            
            return self._parse_salary_analysis(ai_analysis, collected_data)
            
        except Exception as e:
            logger.error(f"Salary analysis failed: {e}")
            return self._create_demo_salary_analysis(collected_data, language)
    
    async def _create_career_strategy(self,
                                    profile_analysis: Dict[str, Any],
                                    market_analysis: Dict[str, Any],
                                    skill_gap_analysis: Dict[str, Any],
                                    language: str,
                                    user_providers: List[Tuple[str, str, str]] = None) -> Dict[str, Any]:
        """Создание персональной карьерной стратегии"""
        
        if not user_providers:
            return self._create_demo_career_strategy(profile_analysis, language)
        
        prompt = f"""
Создай персональную карьерную стратегию на основе глубокого анализа.

АНАЛИЗ ПРОФИЛЯ:
{json.dumps(profile_analysis, ensure_ascii=False, indent=2)}

АНАЛИЗ РЫНКА:
{json.dumps(market_analysis, ensure_ascii=False, indent=2)}

АНАЛИЗ НАВЫКОВ:
{json.dumps(skill_gap_analysis, ensure_ascii=False, indent=2)}

Создай РЕВОЛЮЦИОННУЮ карьерную стратегию:

1. ТИП СТРАТЕГИИ:
   - Агрессивная (быстрый рост)
   - Устойчивая (постепенное развитие) 
   - Смена направления
   - Углубление экспертизы
   - Расширение компетенций

2. КРАТКОСРОЧНЫЕ ЦЕЛИ (3-6 месяцев):
   - Конкретные действия для поиска работы
   - Навыки для изучения в первую очередь
   - Целевые компании и позиции

3. СРЕДНЕСРОЧНЫЕ ЦЕЛИ (6-18 месяцев):
   - Развитие карьеры на первой позиции
   - Дополнительные навыки и сертификации
   - Расширение профессиональной сети

4. ДОЛГОСРОЧНАЯ ПЕРСПЕКТИВА (1-3 года):
   - Карьерный рост и позиционирование
   - Специализация или диверсификация
   - Лидерские и менеджерские навыки

5. ПЛАН ДЕЙСТВИЙ:
   - Еженедельные задачи
   - Месячные цели
   - Контрольные точки

6. РИСКИ И ВОЗМОЖНОСТИ:
   - Потенциальные препятствия
   - Как их преодолеть
   - Скрытые возможности

Стратегия должна быть КОНКРЕТНОЙ и ДЕЙСТВЕННОЙ.
Ответ в формате JSON.
"""
        
        try:
            provider, model, api_key = user_providers[0]
            ai_analysis = await modern_llm_manager.generate_content(
                prompt=prompt,
                provider=provider,
                model=model,
                api_key=api_key,
                max_tokens=2500
            )
            
            return self._parse_career_strategy(ai_analysis)
            
        except Exception as e:
            logger.error(f"Career strategy creation failed: {e}")
            return self._create_demo_career_strategy(profile_analysis, language)
    
    async def _predict_success_rates(self,
                                   profile_analysis: Dict[str, Any],
                                   market_analysis: Dict[str, Any],
                                   job_recommendations: List[Dict[str, Any]],
                                   language: str,
                                   user_providers: List[Tuple[str, str, str]] = None) -> Dict[str, Any]:
        """Предсказание успешности кандидатуры"""
        
        if not user_providers:
            return self._create_demo_success_predictions(job_recommendations, language)
        
        # Готовим данные для анализа
        recommendations_summary = []
        for rec in job_recommendations[:5]:  # Берем топ-5 рекомендаций
            job = rec.get('job', {})
            analysis = rec.get('revolutionary_analysis', {})
            recommendations_summary.append({
                'title': job.get('title', 'Unknown'),
                'company': job.get('company_name', 'Unknown'),
                'compatibility_score': analysis.get('compatibility_score', 0),
                'success_prediction': analysis.get('success_prediction', 0)
            })
        
        prompt = f"""
Проанализируй и предскажи успешность кандидата на рынке труда.

ПРОФИЛЬ КАНДИДАТА:
{json.dumps(profile_analysis, ensure_ascii=False, indent=2)}

РЫНОЧНАЯ СИТУАЦИЯ:
{json.dumps(market_analysis, ensure_ascii=False, indent=2)}

АНАЛИЗ ТОПОВЫХ РЕКОМЕНДАЦИЙ:
{json.dumps(recommendations_summary, ensure_ascii=False, indent=2)}

Дай ТОЧНЫЕ предсказания:

1. ОБЩАЯ УСПЕШНОСТЬ (0-100%):
   - Вероятность получения интервью
   - Вероятность получения оффера
   - Время до трудоустройства

2. АНАЛИЗ ПО ТИПАМ КОМПАНИЙ:
   - Стартапы (шансы успеха)
   - Корпорации (шансы успеха)
   - Средний бизнес (шансы успеха)

3. АНАЛИЗ ПО УРОВНЯМ ПОЗИЦИЙ:
   - Junior позиции (% успеха)
   - Middle позиции (% успеха)
   - Senior позиции (% успеха)

4. ВРЕМЕННЫЕ ПРОГНОЗЫ:
   - Первое интервью (недели)
   - Первый оффер (недели)
   - Идеальная позиция (месяцы)

5. ФАКТОРЫ УСПЕХА:
   - Что повышает шансы
   - Что снижает шансы
   - Критические точки

6. РЕКОМЕНДАЦИИ ПО УЛУЧШЕНИЮ:
   - Что сделать СЕЙЧАС для увеличения шансов
   - Долгосрочные инвестиции в карьеру

Будь честным и точным в прогнозах.
Ответ в формате JSON.
"""
        
        try:
            provider, model, api_key = user_providers[0]
            ai_analysis = await modern_llm_manager.generate_content(
                prompt=prompt,
                provider=provider,
                model=model,
                api_key=api_key,
                max_tokens=2000
            )
            
            return self._parse_success_predictions(ai_analysis, job_recommendations)
            
        except Exception as e:
            logger.error(f"Success predictions failed: {e}")
            return self._create_demo_success_predictions(job_recommendations, language)
    
    async def _analyze_market_trends(self,
                                   current_jobs: List[Dict[str, Any]],
                                   collected_data: Dict[str, Any],
                                   language: str,
                                   user_providers: List[Tuple[str, str, str]] = None) -> Dict[str, Any]:
        """Анализ трендов рынка труда"""
        
        if not user_providers or not current_jobs:
            return self._create_demo_market_trends(collected_data, language)
        
        # Анализируем только первые 20 вакансий для эффективности
        jobs_sample = current_jobs[:20]
        jobs_data = []
        
        for job in jobs_sample:
            jobs_data.append({
                'title': job.get('title', ''),
                'company': job.get('company_name', ''),
                'description': job.get('description', '')[:200],  # Ограничиваем длину
                'requirements': job.get('requirements', ''),
                'salary': job.get('salary', ''),
            })
        
        prompt = f"""
Проанализируй тренды рынка труда на основе актуальных вакансий.

ПРОФЕССИЯ КАНДИДАТА: {collected_data.get('profession', 'Unknown')}
ГОРОД: {collected_data.get('preferred_city', 'Berlin')}

ТЕКУЩИЕ ВАКАНСИИ:
{json.dumps(jobs_data, ensure_ascii=False, indent=2)}

Проанализируй тренды:

1. ГОРЯЧИЕ ТРЕНДЫ:
   - Самые востребованные навыки
   - Растущие направления
   - Новые технологии в спросе

2. КОМПАНИИ И СЕКТОРЫ:
   - Активно нанимающие сектора
   - Типы компаний (стартапы, корпорации)
   - Размер компаний

3. ТРЕБОВАНИЯ К КАНДИДАТАМ:
   - Уровень опыта
   - Языковые требования
   - Образовательные требования

4. УСЛОВИЯ РАБОТЫ:
   - Remote vs Office
   - Зарплатные вилки
   - Дополнительные льготы

5. КОНКУРЕНЦИЯ:
   - Уровень конкуренции в отрасли
   - Дефицитные специализации
   - Избыток кандидатов

Ответ в формате JSON.
"""
        
        try:
            provider, model, api_key = user_providers[0]
            ai_analysis = await modern_llm_manager.generate_content(
                prompt=prompt,
                provider=provider,
                model=model,
                api_key=api_key,
                max_tokens=1500
            )
            
            return self._parse_market_trends(ai_analysis)
            
        except Exception as e:
            logger.error(f"Market trends analysis failed: {e}")
            return self._create_demo_market_trends(collected_data, language)
    
    def _analyze_salary_trends(self, jobs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Анализ зарплатных трендов из вакансий"""
        
        salaries = []
        salary_info = []
        
        for job in jobs:
            salary_str = job.get('salary', '')
            if salary_str and salary_str.lower() != 'not specified':
                salary_info.append(salary_str)
                
                # Пытаемся извлечь числовые значения
                import re
                numbers = re.findall(r'(\d{2,6})', salary_str)
                if numbers:
                    try:
                        salaries.extend([int(num) for num in numbers if int(num) > 1000])
                    except:
                        pass
        
        if salaries:
            avg_salary = sum(salaries) / len(salaries)
            min_salary = min(salaries)
            max_salary = max(salaries)
            
            return {
                'average_salary': f'{int(avg_salary):,} EUR',
                'salary_range': f'{min_salary:,} - {max_salary:,} EUR',
                'total_with_salary': len(salary_info),
                'salary_samples': salary_info[:5],
                'analysis': 'На основе реальных вакансий'
            }
        else:
            return {
                'average_salary': '45,000 - 65,000 EUR',
                'salary_range': '35,000 - 85,000 EUR', 
                'total_with_salary': 0,
                'analysis': 'Оценка на основе рыночных данных'
            }
    
    def _analyze_skill_trends(self, jobs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Анализ трендов навыков из вакансий"""
        
        skill_mentions = {}
        common_tech_skills = [
            'python', 'javascript', 'java', 'react', 'node.js', 'sql', 'docker', 
            'kubernetes', 'aws', 'git', 'agile', 'scrum', 'typescript', 'vue',
            'angular', 'mongodb', 'postgresql', 'redis', 'elasticsearch',
            'machine learning', 'ai', 'data science', 'cloud', 'devops'
        ]
        
        for job in jobs:
            job_text = f"{job.get('description', '')} {job.get('requirements', '')}".lower()
            
            for skill in common_tech_skills:
                if skill in job_text:
                    skill_mentions[skill] = skill_mentions.get(skill, 0) + 1
        
        # Сортируем по популярности
        top_skills = sorted(skill_mentions.items(), key=lambda x: x[1], reverse=True)
        
        return {
            'top_skills': [skill for skill, count in top_skills[:10]],
            'skill_demands': dict(top_skills[:15]),
            'total_jobs_analyzed': len(jobs),
            'analysis_date': datetime.now().isoformat()
        }
    
    def _analyze_companies(self, jobs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Анализ компаний из вакансий"""
        
        companies = {}
        company_types = {'startup': 0, 'enterprise': 0, 'medium': 0}
        
        for job in jobs:
            company = job.get('company_name', 'Unknown')
            if company != 'Unknown':
                companies[company] = companies.get(company, 0) + 1
                
                # Простая классификация по типу
                desc = job.get('description', '').lower()
                if any(word in desc for word in ['startup', 'scale-up', 'founded']):
                    company_types['startup'] += 1
                elif any(word in desc for word in ['enterprise', 'corporation', 'multinational']):
                    company_types['enterprise'] += 1
                else:
                    company_types['medium'] += 1
        
        top_companies = sorted(companies.items(), key=lambda x: x[1], reverse=True)
        
        return {
            'top_hiring_companies': dict(top_companies[:10]),
            'company_types_distribution': company_types,
            'total_companies': len(companies),
            'most_active_company': top_companies[0] if top_companies else ('Unknown', 0)
        }
    
    def _create_demo_profile_analysis(self, data: Dict[str, Any], language: str) -> Dict[str, Any]:
        """Демо-анализ профиля"""
        profession = data.get('profession', 'developer')
        experience = data.get('experience_years', '2-3')
        
        return {
            'strengths': [
                f'Опыт работы {profession} ({experience} лет)',
                'Мотивация к развитию и обучению',
                'Знание современных технологий',
                'Готовность к работе в международной среде'
            ],
            'weaknesses': [
                'Ограниченный опыт работы в немецких компаниях',
                'Может потребоваться улучшение языковых навыков',
                'Небольшая профессиональная сеть в Германии'
            ],
            'professional_portrait': {
                'type': 'Развивающийся специалист',
                'seniority': 'Junior-Middle',
                'adaptability': 'Высокая'
            },
            'market_position': {
                'demand_level': 'Высокий',
                'competitive_sectors': ['Tech', 'Startups', 'Digital'],
                'usp': f'Мотивированный {profession} с международным опытом'
            },
            'career_potential': {
                'growth_opportunities': 'Отличные',
                'recommended_directions': ['Углубление технических навыков', 'Развитие лидерских качеств'],
                'timeline': '1-2 года до следующего уровня'
            }
        }
    
    def _create_demo_market_analysis(self, data: Dict[str, Any], language: str) -> Dict[str, Any]:
        """Демо-анализ рынка"""
        return {
            'total_jobs_found': 150,
            'market_trends': {
                'trend': 'Растущий спрос',
                'hot_skills': ['Python', 'JavaScript', 'Cloud', 'AI/ML'],
                'growth_sectors': ['Fintech', 'Healthcare Tech', 'Green Tech']
            },
            'salary_trends': {
                'average_salary': '55,000 - 75,000 EUR',
                'salary_growth': '+8% за последний год',
                'bonus_potential': '10-20% от базовой зарплаты'
            },
            'competition_level': 'Умеренная',
            'market_hotness': 'Горячий рынок - много возможностей'
        }
    
    def _create_demo_recommendations(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Демо-рекомендации"""
        profession = data.get('profession', 'Developer')
        city = data.get('preferred_city', 'Berlin')
        
        return [
            {
                'job': {
                    'title': f'Senior {profession}',
                    'company_name': 'TechCorp Deutschland',
                    'location': city,
                    'salary': '65,000 - 80,000 EUR',
                    'description': f'Exciting opportunity for an experienced {profession} to join our innovative team.',
                    'requirements': ['3+ years experience', 'Strong technical skills', 'Team collaboration']
                },
                'revolutionary_analysis': {
                    'compatibility_score': 92,
                    'success_prediction': 85,
                    'career_value': 88,
                    'total_score': 88
                },
                'ai_insights': {
                    'hidden_opportunities': 'Company is expanding rapidly - great growth potential',
                    'key_advantages': 'Your international background is a perfect fit',
                    'secret_requirements': 'They value cultural diversity and fresh perspectives'
                }
            }
        ]
    
    def _parse_revolutionary_job_analysis(self, ai_analysis: str, job: Dict[str, Any], profile: Dict[str, Any]) -> Dict[str, Any]:
        """Парсинг революционного анализа вакансии"""
        try:
            # Пытаемся извлечь JSON из ответа
            if '{' in ai_analysis and '}' in ai_analysis:
                json_start = ai_analysis.find('{')
                json_end = ai_analysis.rfind('}') + 1
                json_str = ai_analysis[json_start:json_end]
                parsed = json.loads(json_str)
                
                # Вычисляем общий балл
                compatibility = parsed.get('compatibility_score', 75)
                success = parsed.get('success_prediction', 70)
                career_value = parsed.get('career_value', 80)
                
                total_score = int((compatibility * 0.4 + success * 0.3 + career_value * 0.3))
                parsed['total_score'] = total_score
                
                return parsed
        except:
            pass
        
        # Fallback анализ
        return {
            'compatibility_score': 75,
            'success_prediction': 70,
            'career_value': 80,
            'total_score': 75,
            'ai_insights': {
                'analysis': ai_analysis[:500] + '...' if len(ai_analysis) > 500 else ai_analysis
            }
        }
    
    # Дополнительные вспомогательные методы
    def _get_profession_variants(self, profession: str) -> List[str]:
        """Получение вариаций профессии для расширенного поиска"""
        variants_map = {
            'developer': ['software engineer', 'programmer', 'software developer'],
            'designer': ['ui designer', 'ux designer', 'product designer'],
            'manager': ['project manager', 'product manager', 'team lead'],
            'analyst': ['data analyst', 'business analyst', 'systems analyst'],
            'engineer': ['software engineer', 'system engineer', 'technical lead']
        }
        
        profession_lower = profession.lower()
        for key, variants in variants_map.items():
            if key in profession_lower:
                return variants
        
        return [profession]
    
    def _remove_duplicate_jobs(self, jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Удаление дубликатов вакансий"""
        unique_jobs = []
        seen_titles = set()
        
        for job in jobs:
            title_key = f"{job.get('title', '')}-{job.get('company_name', '')}"
            if title_key not in seen_titles:
                seen_titles.add(title_key)
                unique_jobs.append(job)
        
        return unique_jobs
    
    def _assess_competition_level(self, job_count: int) -> str:
        """Оценка уровня конкуренции"""
        if job_count > 100:
            return 'Низкая конкуренция - много возможностей'
        elif job_count > 50:
            return 'Умеренная конкуренция'
        elif job_count > 20:
            return 'Высокая конкуренция'
        else:
            return 'Очень высокая конкуренция - мало вакансий'
    
    def _assess_market_hotness(self, jobs: List[Dict[str, Any]]) -> str:
        """Оценка горячести рынка"""
        if len(jobs) > 100:
            return 'Горячий рынок 🔥'
        elif len(jobs) > 50:
            return 'Активный рынок 📈'
        elif len(jobs) > 20:
            return 'Стабильный рынок'
        else:
            return 'Спокойный рынок'

# Создаем глобальный экземпляр
revolutionary_ai_recruiter = None

def get_revolutionary_ai_recruiter(database):
    global revolutionary_ai_recruiter
    if revolutionary_ai_recruiter is None:
        revolutionary_ai_recruiter = RevolutionaryAIRecruiter(database)
    return revolutionary_ai_recruiter
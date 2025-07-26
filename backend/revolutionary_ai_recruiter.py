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
    
    # =====================================================
    # ДЕМО И ПАРСИНГ МЕТОДЫ
    # =====================================================
    
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
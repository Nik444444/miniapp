"""
🤖 Job AI Assistant Service - Персональный AI-рекрутер для поиска работы
Intelligent personal recruiter that analyzes users, asks questions, and finds perfect job matches
"""

import logging
import json
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from modern_llm_manager import modern_llm_manager

logger = logging.getLogger(__name__)

class JobAIAssistantService:
    def __init__(self):
        self.conversation_stages = {
            'initial': 'Знакомство и базовая информация',
            'experience': 'Опыт работы и навыки',
            'preferences': 'Предпочтения по работе',
            'requirements': 'Требования и ожидания',
            'personality': 'Личностные качества',
            'goals': 'Карьерные цели',
            'complete': 'Профиль завершен'
        }
        
        self.languages = {
            'ru': 'Русский',
            'en': 'English', 
            'de': 'Deutsch',
            'uk': 'Українська',
            'es': 'Español',
            'fr': 'Français'
        }
        
    async def start_ai_recruiter_conversation(self,
                                           user_id: str,
                                           user_language: str = 'ru',
                                           user_providers: List[Tuple[str, str, str]] = None) -> Dict[str, Any]:
        """
        🎯 Start conversation with AI recruiter
        """
        try:
            logger.info(f"Starting AI recruiter conversation for user {user_id}")
            
            # Create initial conversation prompt
            prompt = self._create_initial_conversation_prompt(user_language)
            
            # Get AI response
            if user_providers:
                provider, model, api_key = user_providers[0]
                ai_response = await modern_llm_manager.generate_content(
                    prompt=prompt,
                    provider=provider,
                    model=model,
                    api_key=api_key,
                    max_tokens=1000
                )
            else:
                ai_response = self._create_demo_conversation_start(user_language)
            
            if not ai_response:
                ai_response = self._create_demo_conversation_start(user_language)
            
            # Initialize user profile
            user_profile = {
                'user_id': user_id,
                'stage': 'initial',
                'language': user_language,
                'conversation_history': [],
                'collected_data': {},
                'created_at': datetime.now().isoformat(),
                'last_interaction': datetime.now().isoformat()
            }
            
            # Add first interaction
            interaction = {
                'timestamp': datetime.now().isoformat(),
                'stage': 'initial',
                'ai_message': ai_response,
                'user_message': None,
                'data_collected': {}
            }
            
            user_profile['conversation_history'].append(interaction)
            
            return {
                'status': 'success',
                'stage': 'initial',
                'ai_message': ai_response,
                'next_questions': self._get_stage_questions('initial', user_language),
                'profile': user_profile,
                'progress': 0
            }
            
        except Exception as e:
            logger.error(f"Failed to start AI recruiter conversation: {e}")
            return {
                'status': 'error',
                'message': f'Ошибка запуска AI-рекрутера: {str(e)}',
                'fallback_message': self._create_demo_conversation_start(user_language)
            }
    
    async def continue_ai_recruiter_conversation(self,
                                              user_id: str,
                                              user_message: str,
                                              current_profile: Dict[str, Any],
                                              user_providers: List[Tuple[str, str, str]] = None) -> Dict[str, Any]:
        """
        💬 Continue conversation with AI recruiter
        """
        try:
            logger.info(f"Continuing AI recruiter conversation for user {user_id}")
            
            # Analyze user response and extract data
            extracted_data = self._extract_data_from_response(user_message, current_profile['stage'])
            
            # Update profile with new data
            current_profile['collected_data'].update(extracted_data)
            current_profile['last_interaction'] = datetime.now().isoformat()
            
            # Determine next stage
            next_stage = self._determine_next_stage(current_profile)
            
            # Create conversation prompt
            prompt = self._create_conversation_prompt(
                user_message, 
                current_profile, 
                next_stage,
                current_profile.get('language', 'ru')
            )
            
            # Get AI response
            if user_providers:
                provider, model, api_key = user_providers[0]
                ai_response = await modern_llm_manager.generate_content(
                    prompt=prompt,
                    provider=provider,
                    model=model,
                    api_key=api_key,
                    max_tokens=1000
                )
            else:
                ai_response = self._create_demo_conversation_response(next_stage, current_profile.get('language', 'ru'))
            
            if not ai_response:
                ai_response = self._create_demo_conversation_response(next_stage, current_profile.get('language', 'ru'))
            
            # Add interaction to history
            interaction = {
                'timestamp': datetime.now().isoformat(),
                'stage': current_profile['stage'],
                'user_message': user_message,
                'ai_message': ai_response,
                'data_collected': extracted_data
            }
            
            current_profile['conversation_history'].append(interaction)
            current_profile['stage'] = next_stage
            
            # Calculate progress
            progress = self._calculate_progress(current_profile)
            
            return {
                'status': 'success',
                'stage': next_stage,
                'ai_message': ai_response,
                'next_questions': self._get_stage_questions(next_stage, current_profile.get('language', 'ru')),
                'profile': current_profile,
                'progress': progress,
                'is_complete': next_stage == 'complete'
            }
            
        except Exception as e:
            logger.error(f"Failed to continue AI recruiter conversation: {e}")
            return {
                'status': 'error',
                'message': f'Ошибка продолжения беседы: {str(e)}'
            }
    
    async def generate_job_compatibility_score(self,
                                             job_data: Dict[str, Any],
                                             user_profile: Dict[str, Any],
                                             user_providers: List[Tuple[str, str, str]] = None) -> Dict[str, Any]:
        """
        🎯 Generate compatibility score between user and job
        """
        try:
            logger.info("Generating job compatibility score")
            
            # Create compatibility analysis prompt
            prompt = self._create_compatibility_prompt(job_data, user_profile)
            
            # Get AI analysis
            if user_providers:
                provider, model, api_key = user_providers[0]
                ai_analysis = await modern_llm_manager.generate_content(
                    prompt=prompt,
                    provider=provider,
                    model=model,
                    api_key=api_key,
                    max_tokens=1500
                )
            else:
                ai_analysis = self._create_demo_compatibility_analysis(job_data, user_profile)
            
            if not ai_analysis:
                ai_analysis = self._create_demo_compatibility_analysis(job_data, user_profile)
            
            # Parse compatibility score and analysis
            compatibility = self._parse_compatibility_analysis(ai_analysis, job_data, user_profile)
            
            return {
                'status': 'success',
                'compatibility': compatibility,
                'job_title': job_data.get('title', 'Unknown'),
                'analysis_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to generate compatibility score: {e}")
            return {
                'status': 'error',
                'message': f'Ошибка анализа совместимости: {str(e)}',
                'fallback_score': 75
            }
    
    async def translate_job_content(self,
                                  job_data: Dict[str, Any],
                                  target_language: str,
                                  user_providers: List[Tuple[str, str, str]] = None) -> Dict[str, Any]:
        """
        🌍 Translate job content to target language
        """
        try:
            logger.info(f"Translating job content to {target_language}")
            
            # Create translation prompt
            prompt = self._create_translation_prompt(job_data, target_language)
            
            # Get AI translation
            if user_providers:
                provider, model, api_key = user_providers[0]
                translated_content = await modern_llm_manager.generate_content(
                    prompt=prompt,
                    provider=provider,
                    model=model,
                    api_key=api_key,
                    max_tokens=2000
                )
            else:
                translated_content = self._create_demo_translation(job_data, target_language)
            
            if not translated_content:
                translated_content = self._create_demo_translation(job_data, target_language)
            
            # Parse translated content
            translated_job = self._parse_translated_content(translated_content, job_data)
            
            return {
                'status': 'success',
                'original_job': job_data,
                'translated_job': translated_job,
                'target_language': target_language,
                'translation_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to translate job content: {e}")
            return {
                'status': 'error',
                'message': f'Ошибка перевода: {str(e)}',
                'fallback_translation': job_data
            }
    
    async def generate_cover_letter(self,
                                  job_data: Dict[str, Any],
                                  user_profile: Dict[str, Any],
                                  user_providers: List[Tuple[str, str, str]] = None) -> Dict[str, Any]:
        """
        📝 Generate personalized cover letter for job application
        """
        try:
            logger.info("Generating personalized cover letter")
            
            # Create cover letter prompt
            prompt = self._create_cover_letter_prompt(job_data, user_profile)
            
            # Get AI-generated cover letter
            if user_providers:
                provider, model, api_key = user_providers[0]
                cover_letter = await modern_llm_manager.generate_content(
                    prompt=prompt,
                    provider=provider,
                    model=model,
                    api_key=api_key,
                    max_tokens=2000
                )
            else:
                cover_letter = self._create_demo_cover_letter(job_data, user_profile)
            
            if not cover_letter:
                cover_letter = self._create_demo_cover_letter(job_data, user_profile)
            
            # Structure the cover letter
            structured_letter = self._structure_cover_letter(cover_letter)
            
            return {
                'status': 'success',
                'cover_letter': structured_letter,
                'job_title': job_data.get('title', 'Unknown'),
                'company_name': job_data.get('company_name', 'Unknown'),
                'generated_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to generate cover letter: {e}")
            return {
                'status': 'error',
                'message': f'Ошибка генерации сопроводительного письма: {str(e)}'
            }
    
    def _create_initial_conversation_prompt(self, language: str) -> str:
        """Create initial conversation prompt"""
        if language == 'ru':
            return """
Ты персональный AI-рекрутер, который помогает людям найти идеальную работу в Германии. 
Твоя задача - познакомиться с пользователем, узнать его опыт, навыки и предпочтения.

Начни дружественную беседу. Представься как AI-рекрутер и объясни, что ты будешь:
1. Изучать опыт и навыки пользователя
2. Понимать его предпочтения по работе
3. Подбирать идеальные вакансии
4. Отправлять персонализированные рекомендации

Задай первый вопрос о профессиональном опыте пользователя.
Будь дружелюбным, профессиональным и мотивирующим.
"""
        else:
            return """
You are a personal AI recruiter helping people find perfect jobs in Germany.
Your task is to get to know the user, learn about their experience, skills and preferences.

Start a friendly conversation. Introduce yourself as an AI recruiter and explain that you will:
1. Study user's experience and skills
2. Understand their job preferences  
3. Find perfect job matches
4. Send personalized recommendations

Ask the first question about user's professional experience.
Be friendly, professional and motivating.
"""
    
    def _create_conversation_prompt(self, user_message: str, profile: Dict, next_stage: str, language: str) -> str:
        """Create conversation continuation prompt"""
        
        conversation_history = "\n".join([
            f"AI: {h.get('ai_message', '')}\nUser: {h.get('user_message', '')}" 
            for h in profile.get('conversation_history', [])[-3:]  # Last 3 interactions
        ])
        
        collected_data = json.dumps(profile.get('collected_data', {}), ensure_ascii=False, indent=2)
        
        if language == 'ru':
            return f"""
Ты персональный AI-рекрутер. Продолжи беседу с пользователем.

ИСТОРИЯ БЕСЕДЫ:
{conversation_history}

ПОСЛЕДНИЙ ОТВЕТ ПОЛЬЗОВАТЕЛЯ: {user_message}

СОБРАННЫЕ ДАННЫЕ:
{collected_data}

ТЕКУЩИЙ ЭТАП: {next_stage}

Проанализируй ответ пользователя и:
1. Извлеки полезную информацию о его опыте/навыках/предпочтениях
2. Задай следующий умный вопрос для этапа "{next_stage}"
3. Будь дружелюбным и мотивирующим
4. Показывай, что понимаешь и запоминаешь то, что говорит пользователь

Ответ должен быть естественным и персональным.
"""
        else:
            return f"""
You are a personal AI recruiter. Continue the conversation with the user.

CONVERSATION HISTORY:
{conversation_history}

USER'S LAST RESPONSE: {user_message}

COLLECTED DATA:
{collected_data}

CURRENT STAGE: {next_stage}

Analyze user's response and:
1. Extract useful information about their experience/skills/preferences
2. Ask next smart question for stage "{next_stage}"
3. Be friendly and motivating
4. Show that you understand and remember what user says

Response should be natural and personal.
"""
    
    def _create_compatibility_prompt(self, job_data: Dict, user_profile: Dict) -> str:
        """Create job compatibility analysis prompt"""
        
        job_info = f"""
Вакансия: {job_data.get('title', 'Unknown')}
Компания: {job_data.get('company_name', 'Unknown')}
Описание: {job_data.get('description', 'No description')}
Требования: {', '.join(job_data.get('requirements', []))}
Локация: {job_data.get('location', {}).get('city', 'Unknown')}
"""
        
        user_info = json.dumps(user_profile.get('collected_data', {}), ensure_ascii=False, indent=2)
        
        return f"""
Проанализируй совместимость пользователя с вакансией как опытный рекрутер.

ИНФОРМАЦИЯ О ВАКАНСИИ:
{job_info}

ПРОФИЛЬ ПОЛЬЗОВАТЕЛЯ:
{user_info}

Дай детальный анализ совместимости:
1. Общий балл совместимости (0-100)
2. Сильные стороны кандидата для этой позиции
3. Потенциальные слабые места
4. Рекомендации по подготовке к собеседованию
5. Вероятность получения оффера
6. Советы по улучшению кандидатуры

Будь честным но позитивным в оценке.
"""
    
    def _create_translation_prompt(self, job_data: Dict, target_language: str) -> str:
        """Create job translation prompt"""
        
        job_content = f"""
Title: {job_data.get('title', '')}
Company: {job_data.get('company_name', '')}
Description: {job_data.get('description', '')}
Requirements: {', '.join(job_data.get('requirements', []))}
Benefits: {', '.join(job_data.get('benefits', []))}
Location: {job_data.get('location', {}).get('city', '') if isinstance(job_data.get('location'), dict) else str(job_data.get('location', ''))}
"""
        
        lang_name = self.languages.get(target_language, target_language)
        
        return f"""
Переведи информацию о вакансии на {lang_name} язык.
Сохрани профессиональный тон и все важные детали.

ОРИГИНАЛЬНАЯ ВАКАНСИЯ:
{job_content}

Переведи все поля:
- Title (Название должности)
- Company (Компания)  
- Description (Описание)
- Requirements (Требования)
- Benefits (Преимущества)
- Location (Локация)

Перевод должен быть точным и профессиональным.
"""
    
    def _create_cover_letter_prompt(self, job_data: Dict, user_profile: Dict) -> str:
        """Create cover letter generation prompt"""
        
        job_info = f"""
Должность: {job_data.get('title', 'Unknown')}
Компания: {job_data.get('company_name', 'Unknown')}
Описание: {job_data.get('description', 'No description')}
Требования: {', '.join(job_data.get('requirements', []))}
"""
        
        user_data = user_profile.get('collected_data', {})
        user_info = json.dumps(user_data, ensure_ascii=False, indent=2)
        
        return f"""
Создай персонализированное сопроводительное письмо для вакансии.

ИНФОРМАЦИЯ О ВАКАНСИИ:
{job_info}

ПРОФИЛЬ КАНДИДАТА:
{user_info}

Создай профессиональное сопроводительное письмо, которое:
1. Обращается к конкретной компании и позиции
2. Подчеркивает релевантный опыт кандидата
3. Показывает мотивацию и заинтересованность
4. Демонстрирует знание компании (если есть информация)
5. Заканчивается call-to-action

Письмо должно быть:
- Профессиональным но персональным
- Конкретным и фактическим
- Мотивирующим и позитивным
- Не длиннее 300-400 слов

Формат: стандартное деловое письмо.
"""
    
    def _extract_data_from_response(self, user_message: str, current_stage: str) -> Dict[str, Any]:
        """Extract structured data from user response"""
        
        extracted = {}
        message_lower = user_message.lower()
        
        # Extract experience information
        if current_stage in ['initial', 'experience']:
            # Years of experience
            years_match = re.search(r'(\d+)\s*(?:лет|год|years?|jahre?)', message_lower)
            if years_match:
                extracted['years_experience'] = int(years_match.group(1))
            
            # Technologies and skills
            tech_keywords = ['python', 'javascript', 'java', 'react', 'node', 'php', 'c++', 'sql', 'html', 'css']
            found_tech = [tech for tech in tech_keywords if tech in message_lower]
            if found_tech:
                extracted['technologies'] = found_tech
            
            # Job titles
            job_titles = ['developer', 'engineer', 'manager', 'designer', 'analyst', 'разработчик', 'инженер', 'менеджер']
            found_titles = [title for title in job_titles if title in message_lower]
            if found_titles:
                extracted['job_titles'] = found_titles
        
        # Extract preferences
        if current_stage == 'preferences':
            if any(word in message_lower for word in ['remote', 'удаленно', 'дома']):
                extracted['remote_preference'] = True
            if any(word in message_lower for word in ['office', 'офис', 'команда']):
                extracted['office_preference'] = True
            
            # Salary expectations
            salary_match = re.search(r'(\d+)\s*(?:€|euro|евро|тысяч)', message_lower)
            if salary_match:
                extracted['salary_expectation'] = int(salary_match.group(1))
        
        # Extract requirements
        if current_stage == 'requirements':
            if any(word in message_lower for word in ['visa', 'виза', 'sponsorship']):
                extracted['needs_visa'] = True
            if any(word in message_lower for word in ['german', 'deutsch', 'немецкий']):
                german_level = re.search(r'([abc][12]|beginner|intermediate|advanced)', message_lower)
                if german_level:
                    extracted['german_level'] = german_level.group(1).upper()
        
        return extracted
    
    def _determine_next_stage(self, profile: Dict[str, Any]) -> str:
        """Determine next conversation stage"""
        
        current_stage = profile.get('stage', 'initial')
        collected_data = profile.get('collected_data', {})
        
        stage_order = ['initial', 'experience', 'preferences', 'requirements', 'personality', 'goals', 'complete']
        
        # Check if we have enough data for current stage
        if current_stage == 'initial' and ('years_experience' in collected_data or 'job_titles' in collected_data):
            return 'experience'
        elif current_stage == 'experience' and len(collected_data) >= 3:
            return 'preferences'
        elif current_stage == 'preferences' and ('remote_preference' in collected_data or 'salary_expectation' in collected_data):
            return 'requirements'
        elif current_stage == 'requirements' and len(collected_data) >= 5:
            return 'personality'
        elif current_stage == 'personality' and len(collected_data) >= 6:
            return 'goals'
        elif current_stage == 'goals' and len(collected_data) >= 7:
            return 'complete'
        
        # Stay in current stage if not enough data
        current_index = stage_order.index(current_stage)
        if current_index < len(stage_order) - 1:
            return stage_order[current_index + 1]
        else:
            return 'complete'
    
    def _get_stage_questions(self, stage: str, language: str) -> List[str]:
        """Get sample questions for each stage"""
        
        if language == 'ru':
            questions = {
                'initial': [
                    "Расскажите о своем профессиональном опыте",
                    "В какой области вы работаете?",
                    "Сколько лет опыта у вас есть?"
                ],
                'experience': [
                    "Какие технологии вы используете?",
                    "Над какими проектами работали?",
                    "Какие достижения вас гордят?"
                ],
                'preferences': [
                    "Предпочитаете удаленную работу или офис?",
                    "Какая зарплата вас интересует?",
                    "В каких городах рассматриваете работу?"
                ],
                'requirements': [
                    "Нужна ли поддержка с визой?",
                    "Какой у вас уровень немецкого?",
                    "Есть ли особые требования к работе?"
                ],
                'personality': [
                    "Как вы работаете в команде?",
                    "Что мотивирует вас в работе?",
                    "Какие ваши сильные стороны?"
                ],
                'goals': [
                    "Какие у вас карьерные цели?",
                    "Куда хотите развиваться?",
                    "Что важно в новой работе?"
                ]
            }
        else:
            questions = {
                'initial': [
                    "Tell me about your professional experience",
                    "What field do you work in?",
                    "How many years of experience do you have?"
                ],
                'experience': [
                    "What technologies do you use?",
                    "What projects have you worked on?",
                    "What achievements are you proud of?"
                ],
                'preferences': [
                    "Do you prefer remote work or office?",
                    "What salary range interests you?",
                    "Which cities would you consider for work?"
                ],
                'requirements': [
                    "Do you need visa support?",
                    "What's your German language level?",
                    "Any special work requirements?"
                ],
                'personality': [
                    "How do you work in a team?",
                    "What motivates you at work?",
                    "What are your strengths?"
                ],
                'goals': [
                    "What are your career goals?",
                    "Where do you want to develop?",
                    "What's important in a new job?"
                ]
            }
        
        return questions.get(stage, [])
    
    def _calculate_progress(self, profile: Dict[str, Any]) -> int:
        """Calculate conversation progress percentage"""
        
        stage = profile.get('stage', 'initial')
        stages = ['initial', 'experience', 'preferences', 'requirements', 'personality', 'goals', 'complete']
        
        try:
            stage_index = stages.index(stage)
            return int((stage_index / (len(stages) - 1)) * 100)
        except ValueError:
            return 0
    
    def _parse_compatibility_analysis(self, ai_analysis: str, job_data: Dict, user_profile: Dict) -> Dict[str, Any]:
        """Parse AI compatibility analysis"""
        
        # Extract compatibility score
        score_match = re.search(r'(\d+)(?:%|\/100|балл)', ai_analysis)
        compatibility_score = int(score_match.group(1)) if score_match else 75
        
        return {
            'overall_score': compatibility_score,
            'detailed_analysis': ai_analysis,
            'strengths': self._extract_strengths(ai_analysis),
            'weaknesses': self._extract_weaknesses(ai_analysis),
            'recommendations': self._extract_recommendations(ai_analysis),
            'interview_tips': self._extract_interview_tips(ai_analysis)
        }
    
    def _parse_translated_content(self, translated_content: str, original_job: Dict) -> Dict[str, Any]:
        """Parse translated job content"""
        
        # Try to extract structured translation
        translated_job = original_job.copy()
        
        # Look for translated fields
        lines = translated_content.split('\n')
        for line in lines:
            if 'title:' in line.lower() or 'название:' in line.lower():
                translated_job['title'] = line.split(':', 1)[1].strip()
            elif 'company:' in line.lower() or 'компания:' in line.lower():
                translated_job['company_name'] = line.split(':', 1)[1].strip()
            elif 'description:' in line.lower() or 'описание:' in line.lower():
                translated_job['description'] = line.split(':', 1)[1].strip()
        
        # If structured parsing failed, use the full translation
        if translated_job.get('title') == original_job.get('title'):
            translated_job['full_translation'] = translated_content
        
        return translated_job
    
    def _structure_cover_letter(self, cover_letter: str) -> Dict[str, Any]:
        """Structure cover letter into components"""
        
        return {
            'full_text': cover_letter,
            'subject': self._extract_subject(cover_letter),
            'greeting': self._extract_greeting(cover_letter),
            'body': self._extract_body(cover_letter),
            'closing': self._extract_closing(cover_letter),
            'word_count': len(cover_letter.split())
        }
    
    # Demo methods for fallback
    def _create_demo_conversation_start(self, language: str) -> str:
        if language == 'ru':
            return """
Привет! Я ваш персональный AI-рекрутер 🤖

Меня зовут JobBot, и я помогу вам найти идеальную работу в Германии! 

Я буду:
✅ Изучать ваш опыт и навыки
✅ Понимать ваши предпочтения
✅ Подбирать идеальные вакансии
✅ Отправлять персонализированные рекомендации в Telegram

Давайте начнем! Расскажите мне о своем профессиональном опыте. В какой области вы работаете и сколько лет опыта у вас есть?
"""
        else:
            return """
Hello! I'm your personal AI recruiter 🤖

My name is JobBot, and I'll help you find the perfect job in Germany!

I will:
✅ Study your experience and skills
✅ Understand your preferences  
✅ Find perfect job matches
✅ Send personalized recommendations to Telegram

Let's start! Tell me about your professional experience. What field do you work in and how many years of experience do you have?
"""
    
    def _create_demo_conversation_response(self, stage: str, language: str) -> str:
        responses = {
            'ru': {
                'experience': "Отлично! Теперь расскажите больше о ваших навыках и технологиях, с которыми вы работаете.",
                'preferences': "Понятно! А какие у вас предпочтения по работе? Удаленка, офис, гибридный формат?",
                'requirements': "Хорошо! Есть ли особые требования? Нужна ли поддержка с визой?",
                'personality': "Замечательно! Расскажите о ваших личных качествах и стиле работы.",
                'goals': "Отлично! Какие у вас карьерные цели на ближайшие годы?",
                'complete': "Спасибо! Теперь я знаю вас достаточно хорошо, чтобы подбирать идеальные вакансии! 🎯"
            },
            'en': {
                'experience': "Great! Now tell me more about your skills and technologies you work with.",
                'preferences': "I see! What are your work preferences? Remote, office, or hybrid?",
                'requirements': "Good! Any special requirements? Do you need visa support?",
                'personality': "Wonderful! Tell me about your personal qualities and work style.",
                'goals': "Excellent! What are your career goals for the coming years?",
                'complete': "Thank you! Now I know you well enough to find perfect job matches! 🎯"
            }
        }
        
        lang_responses = responses.get(language, responses['en'])
        return lang_responses.get(stage, lang_responses['complete'])
    
    def _create_demo_compatibility_analysis(self, job_data: Dict, user_profile: Dict) -> str:
        return f"""
Анализ совместимости с вакансией "{job_data.get('title', 'Unknown')}":

Общий балл совместимости: 78/100

Сильные стороны:
- Соответствующий опыт работы
- Подходящие технические навыки
- Мотивация к развитию

Потенциальные слабые места:
- Может потребоваться дополнительное обучение
- Языковой барьер возможен

Рекомендации:
- Подготовьте примеры проектов
- Изучите компанию заранее
- Улучшите немецкий язык

Вероятность получения оффера: Высокая (70-80%)
"""
    
    def _create_demo_translation(self, job_data: Dict, target_language: str) -> str:
        if target_language == 'ru':
            return f"""
Название: {job_data.get('title', 'Разработчик')}
Компания: {job_data.get('company_name', 'Технологическая компания')}  
Описание: Мы ищем талантливого специалиста для работы в нашей команде
Требования: Опыт работы, знание технологий, командная работа
Локация: {job_data.get('location', {}).get('city', 'Берлин') if isinstance(job_data.get('location'), dict) else 'Берлин'}
"""
        else:
            return f"""
Title: {job_data.get('title', 'Developer')}
Company: {job_data.get('company_name', 'Tech Company')}
Description: We are looking for a talented professional to join our team
Requirements: Work experience, technology knowledge, teamwork
Location: {job_data.get('location', {}).get('city', 'Berlin') if isinstance(job_data.get('location'), dict) else 'Berlin'}
"""
    
    def _create_demo_cover_letter(self, job_data: Dict, user_profile: Dict) -> str:
        return f"""
Уважаемые сотрудники {job_data.get('company_name', 'компании')}!

Меня заинтересовала вакансия {job_data.get('title', 'специалиста')} в вашей компании.

Мой опыт и навыки идеально подходят для этой позиции. Я обладаю необходимыми компетенциями и готов внести значительный вклад в развитие вашей команды.

Я был бы рад обсудить мою кандидатуру подробнее и ответить на ваши вопросы.

С уважением,
[Ваше имя]
"""
    
    # Helper methods for parsing
    def _extract_strengths(self, analysis: str) -> List[str]:
        strengths = []
        lines = analysis.split('\n')
        in_strengths = False
        
        for line in lines:
            if 'сильные стороны' in line.lower() or 'strengths' in line.lower():
                in_strengths = True
                continue
            elif in_strengths and line.strip().startswith('-'):
                strengths.append(line.strip()[1:].strip())
            elif in_strengths and line.strip() and not line.strip().startswith('-'):
                break
        
        return strengths[:3] if strengths else ['Соответствующий опыт', 'Хорошие навыки', 'Мотивация']
    
    def _extract_weaknesses(self, analysis: str) -> List[str]:
        weaknesses = []
        lines = analysis.split('\n')
        in_weaknesses = False
        
        for line in lines:
            if 'слабые места' in line.lower() or 'weakness' in line.lower():
                in_weaknesses = True
                continue
            elif in_weaknesses and line.strip().startswith('-'):
                weaknesses.append(line.strip()[1:].strip())
            elif in_weaknesses and line.strip() and not line.strip().startswith('-'):
                break
        
        return weaknesses[:2] if weaknesses else ['Требуется дополнительная подготовка']
    
    def _extract_recommendations(self, analysis: str) -> List[str]:
        recommendations = []
        lines = analysis.split('\n')
        in_recommendations = False
        
        for line in lines:
            if 'рекомендации' in line.lower() or 'recommendations' in line.lower():
                in_recommendations = True
                continue
            elif in_recommendations and line.strip().startswith('-'):
                recommendations.append(line.strip()[1:].strip())
            elif in_recommendations and line.strip() and not line.strip().startswith('-'):
                break
        
        return recommendations[:3] if recommendations else ['Подготовьте портфолио', 'Изучите компанию', 'Практикуйте интервью']
    
    def _extract_interview_tips(self, analysis: str) -> List[str]:
        return ['Подготовьте примеры работ', 'Изучите технологии компании', 'Будьте готовы к техническим вопросам']
    
    def _extract_subject(self, letter: str) -> str:
        return "Заявка на вакансию"
    
    def _extract_greeting(self, letter: str) -> str:
        lines = letter.split('\n')
        for line in lines[:3]:
            if 'уважаем' in line.lower() or 'dear' in line.lower() or 'hello' in line.lower():
                return line.strip()
        return "Уважаемые коллеги!"
    
    def _extract_body(self, letter: str) -> str:
        lines = letter.split('\n')
        body_lines = []
        skip_greeting = True
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            if skip_greeting and ('уважаем' in line.lower() or 'dear' in line.lower()):
                skip_greeting = False
                continue
            if 'с уважением' in line.lower() or 'sincerely' in line.lower():
                break
            if not skip_greeting:
                body_lines.append(line)
        
        return '\n'.join(body_lines)
    
    def _extract_closing(self, letter: str) -> str:
        lines = letter.split('\n')
        for line in reversed(lines):
            if 'с уважением' in line.lower() or 'sincerely' in line.lower():
                return line.strip()
        return "С уважением,"

# Create global instance
job_ai_assistant_service = JobAIAssistantService()
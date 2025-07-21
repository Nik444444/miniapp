"""
🤖 Job AI Service - AI-powered resume analysis and interview coaching
ИИ сервис для анализа резюме и коучинга собеседований
"""

import logging
import json
import re
import base64
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from modern_llm_manager import modern_llm_manager

logger = logging.getLogger(__name__)

class JobAIService:
    def __init__(self):
        self.resume_sections = {
            'personal_info': ['name', 'email', 'phone', 'address', 'linkedin'],
            'summary': ['professional summary', 'career objective'],
            'experience': ['work experience', 'professional experience'],
            'education': ['education', 'academic background'],
            'skills': ['technical skills', 'soft skills', 'languages'],
            'certifications': ['certifications', 'licenses'],
            'projects': ['projects', 'portfolio'],
            'achievements': ['achievements', 'awards']
        }
        
        self.interview_types = {
            'technical': 'Техническое интервью',
            'behavioral': 'Поведенческое интервью', 
            'case_study': 'Кейс-интервью',
            'cultural_fit': 'Интервью на культурное соответствие',
            'phone_screening': 'Телефонный скрининг',
            'final_round': 'Финальное интервью'
        }

    async def analyze_resume(self, 
                           resume_text: str,
                           resume_file_data: str = None,
                           target_position: str = None,
                           user_providers: List[Tuple[str, str, str]] = None,
                           language: str = "ru") -> Dict[str, Any]:
        """
        📄 AI-powered resume analysis with improvement suggestions
        """
        try:
            logger.info(f"Starting resume analysis for target position: {target_position}")
            
            # Create analysis prompt
            analysis_prompt = self._create_resume_analysis_prompt(
                resume_text, target_position, language
            )
            
            # Get AI response
            if user_providers:
                provider, model, api_key = user_providers[0]
                ai_response = await modern_llm_manager.generate_content(
                    prompt=analysis_prompt,
                    provider=provider,
                    model=model,
                    api_key=api_key,
                    max_tokens=2000
                )
            else:
                ai_response = self._create_demo_resume_analysis(resume_text, target_position, language)
            
            if not ai_response:
                return self._create_demo_resume_analysis(resume_text, target_position, language)
            
            # Parse AI response and structure it
            structured_analysis = self._parse_resume_analysis(ai_response, resume_text)
            
            # Add technical metrics
            metrics = self._calculate_resume_metrics(resume_text)
            structured_analysis['metrics'] = metrics
            
            # Add improvement action items
            action_items = self._generate_resume_action_items(structured_analysis)
            structured_analysis['action_items'] = action_items
            
            logger.info("Resume analysis completed successfully")
            
            return {
                'status': 'success',
                'analysis': structured_analysis,
                'target_position': target_position,
                'language': language,
                'analysis_date': datetime.now().isoformat(),
                'message': 'Анализ резюме завершен успешно'
            }
            
        except Exception as e:
            logger.error(f"Resume analysis failed: {e}")
            return {
                'status': 'error',
                'message': f'Ошибка анализа резюме: {str(e)}',
                'fallback_analysis': self._create_demo_resume_analysis(resume_text, target_position, language)
            }

    def _create_resume_analysis_prompt(self, 
                                     resume_text: str, 
                                     target_position: str = None,
                                     language: str = "ru") -> str:
        """Create detailed prompt for resume analysis"""
        
        if language == "ru":
            prompt = f"""
Проанализируй резюме как эксперт HR и карьерный коуч. Дай детальную оценку и конкретные рекомендации для улучшения.

РЕЗЮМЕ:
{resume_text}

ЦЕЛЕВАЯ ПОЗИЦИЯ: {target_position or 'Не указана'}

ЗАДАЧА: Проведи всесторонний анализ резюме и предоставь:

1. ОБЩАЯ ОЦЕНКА (0-100 баллов)
- Оценка привлекательности для HR
- Соответствие целевой позиции
- Профессиональность оформления

2. АНАЛИЗ РАЗДЕЛОВ:
- Контактная информация
- Профессиональное резюме/цель
- Опыт работы
- Образование
- Навыки
- Достижения

3. СИЛЬНЫЕ СТОРОНЫ:
- Что делает кандидата привлекательным
- Конкурентные преимущества
- Уникальные качества

4. ОБЛАСТИ ДЛЛ УЛУЧШЕНИЯ:
- Конкретные недостатки
- Упущенные возможности
- Слабые формулировки

5. КОНКРЕТНЫЕ РЕКОМЕНДАЦИИ:
- Что добавить
- Что переписать
- Как лучше структурировать

6. КЛЮЧЕВЫЕ СЛОВА:
- Важные ключевые слова для ATS
- Индустриальная терминология
- Навыки для целевой позиции

Отвечай структурированно, конкретно и конструктивно. БЕЗ использования символов форматирования (* # и других).
"""
        else:
            prompt = f"""
Analyze this resume as an HR expert and career coach. Provide detailed assessment and specific improvement recommendations.

RESUME:
{resume_text}

TARGET POSITION: {target_position or 'Not specified'}

TASK: Conduct comprehensive resume analysis and provide:

1. OVERALL RATING (0-100 points)
- HR attractiveness rating
- Target position fit
- Professional presentation

2. SECTION ANALYSIS:
- Contact information
- Professional summary/objective
- Work experience
- Education
- Skills
- Achievements

3. STRENGTHS:
- What makes candidate attractive
- Competitive advantages
- Unique qualities

4. IMPROVEMENT AREAS:
- Specific weaknesses
- Missed opportunities
- Weak formulations

5. CONCRETE RECOMMENDATIONS:
- What to add
- What to rewrite
- How to better structure

6. KEYWORDS:
- Important ATS keywords
- Industry terminology
- Skills for target position

Respond structured, specific and constructive. WITHOUT using formatting symbols (* # and others).
"""
        
        return prompt

    def _parse_resume_analysis(self, ai_response: str, resume_text: str) -> Dict[str, Any]:
        """Parse and structure AI response"""
        
        # Extract overall score
        score_match = re.search(r'(\d+).*(?:баллов|points|score)', ai_response, re.IGNORECASE)
        overall_score = int(score_match.group(1)) if score_match else 75
        
        # Structure the response
        analysis = {
            'overall_score': overall_score,
            'score_breakdown': {
                'content_quality': min(100, overall_score + 5),
                'structure': min(100, overall_score - 5),
                'keywords': min(100, overall_score),
                'relevance': min(100, overall_score + 3)
            },
            'detailed_feedback': ai_response,
            'strengths': self._extract_section(ai_response, ['сильные стороны', 'strengths']),
            'improvements': self._extract_section(ai_response, ['улучшения', 'improvement', 'рекомендации']),
            'keywords_missing': self._extract_section(ai_response, ['ключевые слова', 'keywords']),
            'recommendations': self._extract_recommendations(ai_response)
        }
        
        return analysis

    def _extract_section(self, text: str, keywords: List[str]) -> List[str]:
        """Extract specific sections from AI response"""
        sections = []
        text_lower = text.lower()
        
        for keyword in keywords:
            if keyword in text_lower:
                # Find the section and extract points
                start_idx = text_lower.find(keyword)
                # Look for the next 500 characters after the keyword
                section_text = text[start_idx:start_idx + 500]
                
                # Extract bullet points or numbered items
                points = re.findall(r'[-•]\s*([^-•\n]+)', section_text)
                if not points:
                    points = re.findall(r'\d+\.\s*([^0-9\n]+)', section_text)
                
                sections.extend([point.strip() for point in points[:3]])  # Limit to 3 points
                break
        
        return sections[:5] if sections else ['Анализ проведен', 'Рекомендации подготовлены']

    def _extract_recommendations(self, text: str) -> List[Dict[str, str]]:
        """Extract actionable recommendations"""
        recommendations = []
        
        # Common recommendation patterns
        rec_patterns = [
            r'добавьте?\s+([^.!?\n]+)',
            r'улучшите?\s+([^.!?\n]+)',
            r'переписать?\s+([^.!?\n]+)',
            r'включите?\s+([^.!?\n]+)',
        ]
        
        for pattern in rec_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches[:2]:  # Limit per pattern
                recommendations.append({
                    'action': 'improve',
                    'description': match.strip(),
                    'priority': 'high' if 'важно' in match.lower() or 'critical' in match.lower() else 'medium'
                })
        
        if not recommendations:
            recommendations = [
                {'action': 'improve', 'description': 'Добавить больше измеримых достижений', 'priority': 'high'},
                {'action': 'improve', 'description': 'Улучшить профессиональное резюме', 'priority': 'medium'},
                {'action': 'improve', 'description': 'Оптимизировать ключевые слова', 'priority': 'medium'}
            ]
        
        return recommendations[:5]

    def _calculate_resume_metrics(self, resume_text: str) -> Dict[str, Any]:
        """Calculate technical metrics for resume"""
        
        word_count = len(resume_text.split())
        char_count = len(resume_text)
        
        # Check for common sections
        sections_found = 0
        for section_key, keywords in self.resume_sections.items():
            if any(keyword.lower() in resume_text.lower() for keyword in keywords):
                sections_found += 1
        
        # Check for contact info
        has_email = bool(re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', resume_text))
        has_phone = bool(re.search(r'[\+]?[1-9]?[0-9]{7,14}', resume_text))
        
        # Check for achievements (numbers, percentages)
        achievements_count = len(re.findall(r'\b\d+%|\b\d+\s*(?:million|thousand|k)\b|\b\d+\+', resume_text, re.IGNORECASE))
        
        return {
            'word_count': word_count,
            'character_count': char_count,
            'sections_found': sections_found,
            'total_sections': len(self.resume_sections),
            'completeness_score': min(100, (sections_found / len(self.resume_sections)) * 100),
            'has_contact_info': {
                'email': has_email,
                'phone': has_phone
            },
            'quantified_achievements': achievements_count,
            'readability_score': min(100, max(0, 100 - (word_count - 300) / 10)) if word_count > 0 else 0
        }

    def _generate_resume_action_items(self, analysis: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate specific action items for resume improvement"""
        
        action_items = []
        metrics = analysis.get('metrics', {})
        overall_score = analysis.get('overall_score', 75)
        
        # Based on completeness
        if metrics.get('completeness_score', 0) < 70:
            action_items.append({
                'action': 'add_sections',
                'title': 'Добавить недостающие разделы',
                'description': 'Резюме неполное. Добавьте разделы: навыки, образование, достижения',
                'priority': 'high',
                'estimated_time': '30 минут'
            })
        
        # Based on achievements
        if metrics.get('quantified_achievements', 0) < 3:
            action_items.append({
                'action': 'quantify_achievements',
                'title': 'Добавить измеримые достижения',
                'description': 'Включите конкретные цифры: увеличил продажи на 25%, управлял командой из 10 человек',
                'priority': 'high',
                'estimated_time': '20 минут'
            })
        
        # Based on overall score
        if overall_score < 60:
            action_items.append({
                'action': 'major_rewrite',
                'title': 'Кардинальная переработка',
                'description': 'Резюме требует значительного улучшения структуры и содержания',
                'priority': 'critical',
                'estimated_time': '2 часа'
            })
        elif overall_score < 80:
            action_items.append({
                'action': 'polish',
                'title': 'Полировка и улучшение',
                'description': 'Улучшить формулировки и добавить ключевые слова',
                'priority': 'medium',
                'estimated_time': '45 минут'
            })
        
        # Contact info check
        contact_info = metrics.get('has_contact_info', {})
        if not contact_info.get('email') or not contact_info.get('phone'):
            action_items.append({
                'action': 'fix_contact',
                'title': 'Исправить контактную информацию',
                'description': 'Убедитесь, что email и телефон указаны корректно',
                'priority': 'critical',
                'estimated_time': '5 минут'
            })
        
        return action_items[:4]  # Limit to 4 most important items

    async def generate_improved_resume(self,
                                     original_resume: str,
                                     analysis_results: Dict[str, Any],
                                     target_position: str = None,
                                     user_providers: List[Tuple[str, str, str]] = None,
                                     language: str = "ru") -> Dict[str, Any]:
        """
        ✨ Generate improved version of resume based on analysis
        """
        try:
            logger.info("Generating improved resume based on analysis")
            
            # Create improvement prompt
            improvement_prompt = self._create_resume_improvement_prompt(
                original_resume, analysis_results, target_position, language
            )
            
            # Get AI response
            if user_providers:
                provider, model, api_key = user_providers[0]
                improved_resume = await modern_llm_manager.generate_content(
                    prompt=improvement_prompt,
                    provider=provider,
                    model=model,
                    api_key=api_key,
                    max_tokens=2500
                )
            else:
                improved_resume = self._create_demo_improved_resume(original_resume, language)
            
            if not improved_resume:
                improved_resume = self._create_demo_improved_resume(original_resume, language)
            
            # Calculate improvement metrics
            improvement_metrics = self._calculate_improvement_metrics(
                original_resume, improved_resume, analysis_results
            )
            
            return {
                'status': 'success',
                'improved_resume': improved_resume,
                'improvement_metrics': improvement_metrics,
                'changes_summary': self._generate_changes_summary(analysis_results),
                'message': 'Улучшенное резюме готово!'
            }
            
        except Exception as e:
            logger.error(f"Resume improvement failed: {e}")
            return {
                'status': 'error',
                'message': f'Ошибка улучшения резюме: {str(e)}',
                'fallback_resume': self._create_demo_improved_resume(original_resume, language)
            }

    def _create_resume_improvement_prompt(self,
                                        original_resume: str,
                                        analysis_results: Dict[str, Any],
                                        target_position: str = None,
                                        language: str = "ru") -> str:
        """Create prompt for resume improvement"""
        
        recommendations = analysis_results.get('recommendations', [])
        improvements = analysis_results.get('improvements', [])
        
        if language == "ru":
            prompt = f"""
Ты эксперт по составлению резюме. Перепиши данное резюме, улучшив его на основе анализа.

ОРИГИНАЛЬНОЕ РЕЗЮМЕ:
{original_resume}

ЦЕЛЕВАЯ ПОЗИЦИЯ: {target_position or 'Не указана'}

РЕКОМЕНДАЦИИ ДЛЯ УЛУЧШЕНИЯ:
{' '.join([rec.get('description', '') for rec in recommendations])}

ОБЛАСТИ ДЛЯ УЛУЧШЕНИЯ:
{' '.join(improvements)}

ЗАДАЧА: Создай улучшенную версию резюме, которая:

1. ИСПРАВЛЯЕТ все выявленные недостатки
2. ДОБАВЛЯЕТ недостающие разделы и информацию
3. УЛУЧШАЕТ формулировки и структуру
4. ВКЛЮЧАЕТ релевантные ключевые слова
5. ДЕЛАЕТ достижения более конкретными и измеримыми
6. ОПТИМИЗИРУЕТ для ATS (системы отслеживания кандидатов)

СТРУКТУРА УЛУЧШЕННОГО РЕЗЮМЕ:
- Контактная информация
- Профессиональное резюме (2-3 предложения)
- Ключевые навыки
- Опыт работы (с измеримыми достижениями)
- Образование
- Дополнительная информация (сертификаты, проекты)

Создай профессиональное, привлекательное резюме БЕЗ символов форматирования.
"""
        else:
            prompt = f"""
You are a resume writing expert. Rewrite the given resume, improving it based on the analysis.

ORIGINAL RESUME:
{original_resume}

TARGET POSITION: {target_position or 'Not specified'}

IMPROVEMENT RECOMMENDATIONS:
{' '.join([rec.get('description', '') for rec in recommendations])}

IMPROVEMENT AREAS:
{' '.join(improvements)}

TASK: Create an improved resume version that:

1. FIXES all identified weaknesses
2. ADDS missing sections and information
3. IMPROVES wording and structure
4. INCLUDES relevant keywords
5. MAKES achievements more specific and measurable
6. OPTIMIZES for ATS (Applicant Tracking Systems)

IMPROVED RESUME STRUCTURE:
- Contact Information
- Professional Summary (2-3 sentences)
- Key Skills
- Work Experience (with measurable achievements)
- Education
- Additional Information (certificates, projects)

Create professional, attractive resume WITHOUT formatting symbols.
"""
        
        return prompt

    def _calculate_improvement_metrics(self,
                                     original_resume: str,
                                     improved_resume: str,
                                     analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate improvement metrics"""
        
        original_metrics = self._calculate_resume_metrics(original_resume)
        improved_metrics = self._calculate_resume_metrics(improved_resume)
        
        return {
            'score_improvement': improved_metrics['completeness_score'] - original_metrics['completeness_score'],
            'sections_added': improved_metrics['sections_found'] - original_metrics['sections_found'],
            'word_count_change': improved_metrics['word_count'] - original_metrics['word_count'],
            'achievements_added': improved_metrics['quantified_achievements'] - original_metrics['quantified_achievements'],
            'readability_improvement': improved_metrics['readability_score'] - original_metrics['readability_score'],
            'estimated_hr_appeal': min(100, analysis_results.get('overall_score', 75) + 15)
        }

    def _generate_changes_summary(self, analysis_results: Dict[str, Any]) -> List[str]:
        """Generate summary of what was changed"""
        
        changes = []
        action_items = analysis_results.get('action_items', [])
        
        for item in action_items:
            if item.get('action') == 'add_sections':
                changes.append("✅ Добавлены недостающие разделы")
            elif item.get('action') == 'quantify_achievements':
                changes.append("✅ Добавлены измеримые достижения")
            elif item.get('action') == 'fix_contact':
                changes.append("✅ Исправлена контактная информация")
            elif item.get('action') == 'polish':
                changes.append("✅ Улучшены формулировки")
        
        changes.extend([
            "✅ Оптимизированы ключевые слова для ATS",
            "✅ Улучшена общая структура резюме",
            "✅ Добавлены профессиональные формулировки"
        ])
        
        return changes[:5]

    async def prepare_for_interview(self,
                                  job_description: str,
                                  resume_text: str,
                                  interview_type: str = 'behavioral',
                                  user_providers: List[Tuple[str, str, str]] = None,
                                  language: str = "ru") -> Dict[str, Any]:
        """
        🎤 AI-powered interview preparation and coaching
        """
        try:
            logger.info(f"Preparing interview coaching for type: {interview_type}")
            
            # Create coaching prompt
            coaching_prompt = self._create_interview_coaching_prompt(
                job_description, resume_text, interview_type, language
            )
            
            # Get AI response
            if user_providers:
                provider, model, api_key = user_providers[0]
                coaching_response = await modern_llm_manager.generate_content(
                    prompt=coaching_prompt,
                    provider=provider,
                    model=model,
                    api_key=api_key,
                    max_tokens=2000
                )
            else:
                coaching_response = self._create_demo_interview_coaching(interview_type, language)
            
            if not coaching_response:
                coaching_response = self._create_demo_interview_coaching(interview_type, language)
            
            # Structure the coaching response
            structured_coaching = self._parse_interview_coaching(coaching_response, interview_type, language)
            
            return {
                'status': 'success',
                'interview_type': interview_type,
                'coaching': structured_coaching,
                'preparation_checklist': self._generate_preparation_checklist(interview_type, language),
                'message': 'Подготовка к собеседованию готова!'
            }
            
        except Exception as e:
            logger.error(f"Interview preparation failed: {e}")
            return {
                'status': 'error',
                'message': f'Ошибка подготовки к собеседованию: {str(e)}',
                'fallback_coaching': self._create_demo_interview_coaching(interview_type, language)
            }

    def _create_interview_coaching_prompt(self,
                                        job_description: str,
                                        resume_text: str,
                                        interview_type: str,
                                        language: str = "ru") -> str:
        """Create prompt for interview coaching"""
        
        if language == "ru":
            prompt = f"""
Ты эксперт по карьерному коучингу и подготовке к собеседованиям. Подготовь кандидата к собеседованию.

ОПИСАНИЕ ВАКАНСИИ:
{job_description}

РЕЗЮМЕ КАНДИДАТА:
{resume_text}

ТИП СОБЕСЕДОВАНИЯ: {self.interview_types.get(interview_type, interview_type)}

ЗАДАЧА: Подготовь детальный план подготовки к собеседованию, включающий:

1. ТИПИЧНЫЕ ВОПРОСЫ (5-7 вопросов):
- Конкретные вопросы для данной позиции
- Поведенческие вопросы
- Технические вопросы (если применимо)

2. РЕКОМЕНДУЕМЫЕ ОТВЕТЫ:
- Структура STAR для поведенческих вопросов
- Ключевые моменты для подчеркивания
- Примеры из опыта кандидата

3. ВОПРОСЫ ДЛЯ РАБОТОДАТЕЛЯ:
- Умные вопросы о компании
- Вопросы о развитии в роли
- Вопросы о команде и культуре

4. ПОДГОТОВКА К СЛАБЫМ МЕСТАМ:
- Как объяснить пробелы в резюме
- Как компенсировать недостаток опыта
- Как представить смену карьеры

5. ПРАКТИЧЕСКИЕ СОВЕТЫ:
- Что надеть
- Как вести себя
- Невербальная коммуникация

Ответы должны быть конкретными и персонализированными. БЕЗ символов форматирования.
"""
        else:
            prompt = f"""
You are a career coaching and interview preparation expert. Prepare candidate for the interview.

JOB DESCRIPTION:
{job_description}

CANDIDATE'S RESUME:
{resume_text}

INTERVIEW TYPE: {interview_type}

TASK: Prepare detailed interview preparation plan including:

1. TYPICAL QUESTIONS (5-7 questions):
- Specific questions for this position
- Behavioral questions
- Technical questions (if applicable)

2. RECOMMENDED ANSWERS:
- STAR structure for behavioral questions
- Key points to emphasize
- Examples from candidate's experience

3. QUESTIONS FOR EMPLOYER:
- Smart questions about company
- Questions about role development
- Questions about team and culture

4. WEAKNESS PREPARATION:
- How to explain resume gaps
- How to compensate for lack of experience
- How to present career change

5. PRACTICAL TIPS:
- What to wear
- How to behave
- Non-verbal communication

Answers should be specific and personalized. WITHOUT formatting symbols.
"""
        
        return prompt

    def _parse_interview_coaching(self,
                                coaching_response: str,
                                interview_type: str,
                                language: str = "ru") -> Dict[str, Any]:
        """Parse and structure interview coaching response"""
        
        coaching = {
            'interview_type': interview_type,
            'type_description': self.interview_types.get(interview_type, interview_type),
            'expected_questions': self._extract_questions(coaching_response),
            'answer_frameworks': self._extract_answer_frameworks(coaching_response, language),
            'questions_for_employer': self._extract_employer_questions(coaching_response),
            'preparation_tips': self._extract_preparation_tips(coaching_response),
            'weakness_handling': self._extract_weakness_handling(coaching_response),
            'full_coaching_text': coaching_response
        }
        
        return coaching

    def _extract_questions(self, text: str) -> List[Dict[str, str]]:
        """Extract interview questions from coaching text"""
        questions = []
        
        # Look for question patterns
        question_patterns = [
            r'(?:вопрос|question).*?:?\s*(.+?)\?',
            r'^\d+\.\s*(.+?\?)',
            r'[-•]\s*(.+?\?)'
        ]
        
        for pattern in question_patterns:
            matches = re.findall(pattern, text, re.MULTILINE | re.IGNORECASE)
            for match in matches:
                if len(match) > 10 and '?' in match:  # Valid question
                    questions.append({
                        'question': match.strip(),
                        'type': 'behavioral' if any(word in match.lower() for word in ['расскажите', 'опишите', 'tell me', 'describe']) else 'general',
                        'difficulty': 'medium'
                    })
        
        # Add fallback questions if none found
        if not questions:
            fallback_questions = [
                {'question': 'Расскажите о себе', 'type': 'general', 'difficulty': 'easy'},
                {'question': 'Почему вы хотите работать в нашей компании?', 'type': 'motivational', 'difficulty': 'medium'},
                {'question': 'Каковы ваши сильные и слабые стороны?', 'type': 'self-assessment', 'difficulty': 'medium'},
                {'question': 'Расскажите о вашем наибольшем профессиональном достижении', 'type': 'behavioral', 'difficulty': 'medium'},
                {'question': 'Где вы видите себя через 5 лет?', 'type': 'career-goals', 'difficulty': 'medium'}
            ]
            questions = fallback_questions
        
        return questions[:7]  # Limit to 7 questions

    def _extract_answer_frameworks(self, text: str, language: str) -> List[Dict[str, str]]:
        """Extract answer frameworks and templates"""
        frameworks = []
        
        if 'STAR' in text.upper() or 'СТАРТ' in text.upper():
            if language == "ru":
                frameworks.append({
                    'name': 'STAR метод',
                    'description': 'Ситуация, Задача, Действие, Результат',
                    'template': 'Ситуация: Опишите контекст\nЗадача: Что нужно было сделать\nДействие: Что вы предприняли\nРезультат: Каков был итог'
                })
            else:
                frameworks.append({
                    'name': 'STAR Method',
                    'description': 'Situation, Task, Action, Result',
                    'template': 'Situation: Describe context\nTask: What needed to be done\nAction: What you did\nResult: What was the outcome'
                })
        
        # Add common frameworks
        if language == "ru":
            frameworks.extend([
                {
                    'name': 'Структура ответа о себе',
                    'description': 'Настоящее → Прошлое → Будущее',
                    'template': 'Текущая роль и достижения → Релевантный опыт → Цели в новой роли'
                },
                {
                    'name': 'Ответ о слабостях',
                    'description': 'Честность + план развития',
                    'template': 'Признать слабость → Объяснить работу над ней → Показать прогресс'
                }
            ])
        
        return frameworks

    def _extract_employer_questions(self, text: str) -> List[str]:
        """Extract questions candidate should ask employer"""
        questions = []
        
        # Look for employer question sections
        lines = text.split('\n')
        in_employer_section = False
        
        for line in lines:
            line = line.strip()
            if any(phrase in line.lower() for phrase in ['вопросы для работодателя', 'questions for employer', 'вопросы компании']):
                in_employer_section = True
                continue
            
            if in_employer_section and line:
                if line.startswith(('-', '•', '1.', '2.', '3.')):
                    question = re.sub(r'^[-•\d.\s]+', '', line).strip()
                    if len(question) > 10:
                        questions.append(question)
                elif not line.isupper():  # Not a new section header
                    questions.append(line)
                else:
                    break
        
        # Add fallback questions
        if not questions:
            questions = [
                'Каковы основные вызовы в этой роли?',
                'Как выглядит типичный день в команде?',
                'Какие возможности для профессионального развития?',
                'Как измеряется успех в этой позиции?',
                'Расскажите о культуре команды'
            ]
        
        return questions[:5]

    def _extract_preparation_tips(self, text: str) -> List[str]:
        """Extract practical preparation tips"""
        tips = []
        
        # Look for tips sections
        tip_keywords = ['советы', 'tips', 'рекомендации', 'подготовка']
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if any(keyword in line.lower() for keyword in tip_keywords):
                continue
            if line.startswith(('-', '•')) and len(line) > 20:
                tip = re.sub(r'^[-•\s]+', '', line).strip()
                tips.append(tip)
        
        # Add fallback tips
        if not tips:
            tips = [
                'Изучите компанию и её продукты заранее',
                'Подготовьте конкретные примеры достижений',
                'Отрепетируйте ответы на основные вопросы',
                'Подготовьте вопросы для работодателя',
                'Приходите на 10-15 минут раньше'
            ]
        
        return tips[:6]

    def _extract_weakness_handling(self, text: str) -> List[Dict[str, str]]:
        """Extract advice for handling weaknesses"""
        weaknesses = []
        
        # Common weakness scenarios
        weakness_scenarios = [
            {
                'scenario': 'Недостаток опыта',
                'strategy': 'Подчеркните готовность к обучению и перенесите навыки из других областей'
            },
            {
                'scenario': 'Пробел в резюме',
                'strategy': 'Будьте честны и покажите, как использовали время для развития'
            },
            {
                'scenario': 'Смена карьеры',
                'strategy': 'Объясните мотивацию и покажите transferable skills'
            }
        ]
        
        return weakness_scenarios

    def _generate_preparation_checklist(self, interview_type: str, language: str) -> List[Dict[str, Any]]:
        """Generate interview preparation checklist"""
        
        if language == "ru":
            base_checklist = [
                {'task': 'Изучить компанию и её продукты', 'priority': 'high', 'time_needed': '1 час'},
                {'task': 'Подготовить примеры STAR для поведенческих вопросов', 'priority': 'high', 'time_needed': '45 минут'},
                {'task': 'Отрепетировать ответ "Расскажите о себе"', 'priority': 'high', 'time_needed': '20 минут'},
                {'task': 'Подготовить вопросы для работодателя (5-7 вопросов)', 'priority': 'medium', 'time_needed': '30 минут'},
                {'task': 'Выбрать подходящую одежду', 'priority': 'medium', 'time_needed': '15 минут'},
                {'task': 'Запланировать маршрут и время прибытия', 'priority': 'medium', 'time_needed': '10 минут'}
            ]
        else:
            base_checklist = [
                {'task': 'Research company and products', 'priority': 'high', 'time_needed': '1 hour'},
                {'task': 'Prepare STAR examples for behavioral questions', 'priority': 'high', 'time_needed': '45 minutes'},
                {'task': 'Practice "Tell me about yourself" answer', 'priority': 'high', 'time_needed': '20 minutes'},
                {'task': 'Prepare questions for employer (5-7 questions)', 'priority': 'medium', 'time_needed': '30 minutes'},
                {'task': 'Choose appropriate outfit', 'priority': 'medium', 'time_needed': '15 minutes'},
                {'task': 'Plan route and arrival time', 'priority': 'medium', 'time_needed': '10 minutes'}
            ]
        
        # Add type-specific items
        if interview_type == 'technical':
            if language == "ru":
                base_checklist.insert(2, {
                    'task': 'Повторить технические концепции и алгоритмы', 
                    'priority': 'high', 
                    'time_needed': '2 часа'
                })
            else:
                base_checklist.insert(2, {
                    'task': 'Review technical concepts and algorithms', 
                    'priority': 'high', 
                    'time_needed': '2 hours'
                })
        
        return base_checklist

    def _create_demo_resume_analysis(self, resume_text: str, target_position: str, language: str) -> Dict[str, Any]:
        """Create demo analysis when AI is unavailable"""
        
        metrics = self._calculate_resume_metrics(resume_text)
        
        if language == "ru":
            return {
                'status': 'demo',
                'analysis': {
                    'overall_score': 72,
                    'score_breakdown': {
                        'content_quality': 75,
                        'structure': 68,
                        'keywords': 70,
                        'relevance': 73
                    },
                    'detailed_feedback': 'Демо-анализ: Резюме имеет хорошую структуру, но требует добавления измеримых достижений и ключевых слов для целевой позиции.',
                    'strengths': [
                        'Четкая структура резюме',
                        'Хорошо описан опыт работы',
                        'Присутствует контактная информация'
                    ],
                    'improvements': [
                        'Добавить измеримые достижения с цифрами',
                        'Включить больше ключевых слов',
                        'Улучшить профессиональное резюме'
                    ],
                    'keywords_missing': [
                        'Отраслевые термины',
                        'Технические навыки',
                        'Soft skills'
                    ],
                    'recommendations': [
                        {'action': 'improve', 'description': 'Добавить количественные показатели достижений', 'priority': 'high'},
                        {'action': 'improve', 'description': 'Оптимизировать для ATS систем', 'priority': 'medium'}
                    ]
                },
                'metrics': metrics,
                'action_items': [
                    {
                        'action': 'quantify_achievements',
                        'title': 'Добавить измеримые достижения',
                        'description': 'Включите конкретные цифры и результаты',
                        'priority': 'high',
                        'estimated_time': '30 минут'
                    }
                ]
            }
        else:
            return {
                'status': 'demo',
                'analysis': {
                    'overall_score': 72,
                    'score_breakdown': {
                        'content_quality': 75,
                        'structure': 68,
                        'keywords': 70,
                        'relevance': 73
                    },
                    'detailed_feedback': 'Demo analysis: Resume has good structure but needs measurable achievements and keywords for target position.',
                    'strengths': [
                        'Clear resume structure',
                        'Well described work experience',
                        'Contact information present'
                    ],
                    'improvements': [
                        'Add measurable achievements with numbers',
                        'Include more keywords',
                        'Improve professional summary'
                    ],
                    'keywords_missing': [
                        'Industry terms',
                        'Technical skills',
                        'Soft skills'
                    ],
                    'recommendations': [
                        {'action': 'improve', 'description': 'Add quantitative achievement metrics', 'priority': 'high'},
                        {'action': 'improve', 'description': 'Optimize for ATS systems', 'priority': 'medium'}
                    ]
                },
                'metrics': metrics,
                'action_items': [
                    {
                        'action': 'quantify_achievements',
                        'title': 'Add measurable achievements',
                        'description': 'Include specific numbers and results',
                        'priority': 'high',
                        'estimated_time': '30 minutes'
                    }
                ]
            }

    def _create_demo_improved_resume(self, original_resume: str, language: str) -> str:
        """Create demo improved resume"""
        
        if language == "ru":
            return f"""
УЛУЧШЕННАЯ ВЕРСИЯ РЕЗЮМЕ

{original_resume[:200]}...

КЛЮЧЕВЫЕ УЛУЧШЕНИЯ:
- Добавлено профессиональное резюме с ключевыми достижениями
- Включены измеримые результаты (увеличение продаж на 25%, управление командой из 8 человек)
- Оптимизированы ключевые слова для ATS систем
- Улучшена структура и читаемость
- Добавлены релевантные технические и soft skills

Примечание: Это демо-версия. Для полного улучшения резюме требуется настройка API ключей.
"""
        else:
            return f"""
IMPROVED RESUME VERSION

{original_resume[:200]}...

KEY IMPROVEMENTS:
- Added professional summary with key achievements
- Included measurable results (25% sales increase, managed team of 8)
- Optimized keywords for ATS systems
- Improved structure and readability
- Added relevant technical and soft skills

Note: This is a demo version. Full resume improvement requires API key setup.
"""

    def _create_demo_interview_coaching(self, interview_type: str, language: str) -> str:
        """Create demo interview coaching"""
        
        if language == "ru":
            return f"""
ПОДГОТОВКА К СОБЕСЕДОВАНИЮ: {self.interview_types.get(interview_type, interview_type)}

ТИПИЧНЫЕ ВОПРОСЫ:
1. Расскажите о себе и своем опыте
2. Почему вы хотите работать в нашей компании?
3. Каковы ваши сильные и слабые стороны?
4. Расскажите о вашем наибольшем профессиональном достижении
5. Где вы видите себя через 5 лет?

РЕКОМЕНДУЕМЫЕ ОТВЕТЫ:
- Используйте STAR метод для поведенческих вопросов
- Подкрепляйте ответы конкретными примерами
- Показывайте энтузиазм и мотивацию

ВОПРОСЫ ДЛЯ РАБОТОДАТЕЛЯ:
1. Каковы основные вызовы в этой роли?
2. Как выглядит типичный день в команде?
3. Какие возможности для развития?

ПРАКТИЧЕСКИЕ СОВЕТЫ:
- Изучите компанию заранее
- Приходите на 10-15 минут раньше
- Поддерживайте зрительный контакт
- Подготовьте вопросы

Примечание: Это демо-версия коучинга. Для персонализированной подготовки настройте API ключи.
"""
        else:
            return f"""
INTERVIEW PREPARATION: {interview_type}

TYPICAL QUESTIONS:
1. Tell me about yourself and your experience
2. Why do you want to work at our company?
3. What are your strengths and weaknesses?
4. Tell me about your greatest professional achievement
5. Where do you see yourself in 5 years?

RECOMMENDED ANSWERS:
- Use STAR method for behavioral questions
- Support answers with specific examples
- Show enthusiasm and motivation

QUESTIONS FOR EMPLOYER:
1. What are the main challenges in this role?
2. What does a typical day look like for the team?
3. What development opportunities are available?

PRACTICAL TIPS:
- Research the company beforehand
- Arrive 10-15 minutes early
- Maintain eye contact
- Prepare questions

Note: This is a demo coaching version. For personalized preparation, set up API keys.
"""

# Create a global instance
job_ai_service = JobAIService()
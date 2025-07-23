"""
📱 Telegram Job Notification Service - Advanced job notifications for Telegram Mini App
Sends personalized job notifications directly to users via Telegram Bot
"""

import logging
import asyncio
import json
import aiohttp
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from job_ai_assistant_service import job_ai_assistant_service

logger = logging.getLogger(__name__)

class TelegramJobNotificationService:
    def __init__(self):
        self.bot_token = "8003539432:AAFJkAYdEhM6i77va_JFo5Z_OlCiDJX3BC4"
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        self.notification_types = {
            'job_match': '🎯 Идеальная вакансия найдена!',
            'new_jobs': '🆕 Новые вакансии по вашим критериям',
            'ai_recommendation': '🤖 AI-рекомендация от персонального рекрутера',
            'compatibility_alert': '📊 Высокая совместимость с вакансией',
            'deadline_reminder': '⏰ Не забудьте подать заявку!',
            'interview_prep': '🎤 Время готовиться к собеседованию'
        }
        
    async def send_job_match_notification(self,
                                        user_telegram_id: str,
                                        job_data: Dict[str, Any],
                                        compatibility_score: Optional[Dict[str, Any]] = None,
                                        user_language: str = 'ru') -> Dict[str, Any]:
        """
        🎯 Send personalized job match notification to user
        """
        try:
            logger.info(f"Sending job match notification to user {user_telegram_id}")
            
            # Format job notification message
            message = self._format_job_match_message(job_data, compatibility_score, user_language)
            
            # Create inline keyboard with actions
            keyboard = self._create_job_actions_keyboard(job_data, user_language)
            
            # Send notification
            result = await self._send_telegram_message(
                chat_id=user_telegram_id,
                text=message,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
            
            return {
                'status': 'success',
                'notification_sent': True,
                'job_title': job_data.get('title', 'Unknown'),
                'telegram_message_id': result.get('message_id')
            }
            
        except Exception as e:
            logger.error(f"Failed to send job match notification: {e}")
            return {
                'status': 'error',
                'message': f'Ошибка отправки уведомления: {str(e)}'
            }
    
    async def send_ai_recruiter_recommendation(self,
                                             user_telegram_id: str,
                                             jobs_list: List[Dict[str, Any]],
                                             ai_analysis: str,
                                             user_language: str = 'ru') -> Dict[str, Any]:
        """
        🤖 Send AI recruiter personalized recommendations
        """
        try:
            logger.info(f"Sending AI recruiter recommendation to user {user_telegram_id}")
            
            # Format AI recommendation message
            message = self._format_ai_recommendation_message(jobs_list, ai_analysis, user_language)
            
            # Create keyboard for job actions
            keyboard = self._create_recommendations_keyboard(jobs_list, user_language)
            
            # Send notification
            result = await self._send_telegram_message(
                chat_id=user_telegram_id,
                text=message,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
            
            return {
                'status': 'success',
                'notification_sent': True,
                'jobs_count': len(jobs_list),
                'telegram_message_id': result.get('message_id')
            }
            
        except Exception as e:
            logger.error(f"Failed to send AI recommendation: {e}")
            return {
                'status': 'error',
                'message': f'Ошибка отправки AI-рекомендации: {str(e)}'
            }
    
    async def send_new_jobs_digest(self,
                                 user_telegram_id: str,
                                 new_jobs: List[Dict[str, Any]],
                                 subscription_data: Dict[str, Any],
                                 user_language: str = 'ru') -> Dict[str, Any]:
        """
        📊 Send daily/weekly digest of new matching jobs
        """
        try:
            logger.info(f"Sending new jobs digest to user {user_telegram_id}")
            
            # Format digest message
            message = self._format_jobs_digest_message(new_jobs, subscription_data, user_language)
            
            # Create pagination keyboard if many jobs
            keyboard = self._create_digest_keyboard(new_jobs, user_language)
            
            # Send notification
            result = await self._send_telegram_message(
                chat_id=user_telegram_id,
                text=message,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
            
            return {
                'status': 'success',
                'notification_sent': True,
                'jobs_count': len(new_jobs),
                'telegram_message_id': result.get('message_id')
            }
            
        except Exception as e:
            logger.error(f"Failed to send jobs digest: {e}")
            return {
                'status': 'error',
                'message': f'Ошибка отправки дайджеста: {str(e)}'
            }
    
    async def send_compatibility_alert(self,
                                     user_telegram_id: str,
                                     job_data: Dict[str, Any],
                                     compatibility_analysis: Dict[str, Any],
                                     user_language: str = 'ru') -> Dict[str, Any]:
        """
        📈 Send high compatibility job alert
        """
        try:
            logger.info(f"Sending compatibility alert to user {user_telegram_id}")
            
            # Format compatibility alert message
            message = self._format_compatibility_alert_message(job_data, compatibility_analysis, user_language)
            
            # Create action keyboard
            keyboard = self._create_compatibility_actions_keyboard(job_data, compatibility_analysis, user_language)
            
            # Send notification
            result = await self._send_telegram_message(
                chat_id=user_telegram_id,
                text=message,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
            
            return {
                'status': 'success',
                'notification_sent': True,
                'compatibility_score': compatibility_analysis.get('overall_score', 0),
                'telegram_message_id': result.get('message_id')
            }
            
        except Exception as e:
            logger.error(f"Failed to send compatibility alert: {e}")
            return {
                'status': 'error',
                'message': f'Ошибка отправки уведомления о совместимости: {str(e)}'
            }
    
    async def send_interview_preparation_reminder(self,
                                                user_telegram_id: str,
                                                job_data: Dict[str, Any],
                                                interview_date: str,
                                                preparation_tips: List[str],
                                                user_language: str = 'ru') -> Dict[str, Any]:
        """
        🎤 Send interview preparation reminder
        """
        try:
            logger.info(f"Sending interview reminder to user {user_telegram_id}")
            
            # Format interview preparation message
            message = self._format_interview_reminder_message(job_data, interview_date, preparation_tips, user_language)
            
            # Create preparation keyboard
            keyboard = self._create_interview_prep_keyboard(job_data, user_language)
            
            # Send notification
            result = await self._send_telegram_message(
                chat_id=user_telegram_id,
                text=message,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
            
            return {
                'status': 'success',
                'notification_sent': True,
                'job_title': job_data.get('title', 'Unknown'),
                'telegram_message_id': result.get('message_id')
            }
            
        except Exception as e:
            logger.error(f"Failed to send interview reminder: {e}")
            return {
                'status': 'error',
                'message': f'Ошибка отправки напоминания: {str(e)}'
            }
    
    async def send_custom_notification(self,
                                     user_telegram_id: str,
                                     title: str,
                                     message: str,
                                     actions: Optional[List[Dict[str, str]]] = None,
                                     user_language: str = 'ru') -> Dict[str, Any]:
        """
        🔧 Send custom notification with optional actions
        """
        try:
            logger.info(f"Sending custom notification to user {user_telegram_id}")
            
            # Format custom message
            formatted_message = f"*{title}*\n\n{message}"
            
            # Create keyboard if actions provided
            keyboard = None
            if actions:
                keyboard = self._create_custom_actions_keyboard(actions, user_language)
            
            # Send notification
            result = await self._send_telegram_message(
                chat_id=user_telegram_id,
                text=formatted_message,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
            
            return {
                'status': 'success',
                'notification_sent': True,
                'telegram_message_id': result.get('message_id')
            }
            
        except Exception as e:
            logger.error(f"Failed to send custom notification: {e}")
            return {
                'status': 'error',
                'message': f'Ошибка отправки уведомления: {str(e)}'
            }
    
    async def _send_telegram_message(self,
                                   chat_id: str,
                                   text: str,
                                   reply_markup: Optional[Dict] = None,
                                   parse_mode: str = 'Markdown') -> Dict[str, Any]:
        """Send message via Telegram Bot API"""
        
        url = f"{self.base_url}/sendMessage"
        
        payload = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': parse_mode,
            'disable_web_page_preview': True
        }
        
        if reply_markup:
            payload['reply_markup'] = json.dumps(reply_markup)
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                result = await response.json()
                
                if response.status == 200 and result.get('ok'):
                    return result.get('result', {})
                else:
                    error_msg = result.get('description', 'Unknown error')
                    raise Exception(f"Telegram API error: {error_msg}")
    
    def _format_job_match_message(self,
                                job_data: Dict[str, Any],
                                compatibility_score: Optional[Dict[str, Any]],
                                language: str) -> str:
        """Format job match notification message"""
        
        if language == 'ru':
            message = f"🎯 *Идеальная вакансия найдена!*\n\n"
            message += f"*{job_data.get('title', 'Неизвестная должность')}*\n"
            message += f"🏢 {job_data.get('company_name', 'Неизвестная компания')}\n"
            
            # Location
            location = job_data.get('location', {})
            if isinstance(location, dict):
                city = location.get('city', 'Неизвестно')
            else:
                city = str(location) if location else 'Неизвестно'
            message += f"📍 {city}\n"
            
            # Compatibility score
            if compatibility_score and compatibility_score.get('overall_score'):
                score = compatibility_score['overall_score']
                message += f"📊 Совместимость: *{score}%*\n"
                
                if score >= 85:
                    message += "🔥 Очень высокая совместимость!\n"
                elif score >= 70:
                    message += "✅ Хорошая совместимость\n"
            
            # Salary info
            salary_info = job_data.get('salary_info', {})
            if salary_info and salary_info.get('available'):
                message += f"💰 {salary_info.get('range', 'Не указано')} {salary_info.get('currency', 'EUR')}\n"
            
            # Work type
            if job_data.get('remote_possible'):
                message += "🏠 Удаленная работа возможна\n"
            
            if job_data.get('visa_sponsorship'):
                message += "🛂 Поддержка визы\n"
            
            message += f"\n💡 *Описание:*\n{job_data.get('description', 'Описание недоступно')[:200]}..."
            
            # Requirements
            requirements = job_data.get('requirements', [])
            if requirements:
                message += f"\n📋 *Основные требования:*\n"
                for req in requirements[:3]:
                    message += f"• {req}\n"
                    
        else:  # English
            message = f"🎯 *Perfect Job Match Found!*\n\n"
            message += f"*{job_data.get('title', 'Unknown Position')}*\n"
            message += f"🏢 {job_data.get('company_name', 'Unknown Company')}\n"
            
            location = job_data.get('location', {})
            if isinstance(location, dict):
                city = location.get('city', 'Unknown')
            else:
                city = str(location) if location else 'Unknown'
            message += f"📍 {city}\n"
            
            if compatibility_score and compatibility_score.get('overall_score'):
                score = compatibility_score['overall_score']
                message += f"📊 Compatibility: *{score}%*\n"
                
                if score >= 85:
                    message += "🔥 Very high compatibility!\n"
                elif score >= 70:
                    message += "✅ Good compatibility\n"
            
            salary_info = job_data.get('salary_info', {})
            if salary_info and salary_info.get('available'):
                message += f"💰 {salary_info.get('range', 'Not specified')} {salary_info.get('currency', 'EUR')}\n"
            
            if job_data.get('remote_possible'):
                message += "🏠 Remote work possible\n"
            
            if job_data.get('visa_sponsorship'):
                message += "🛂 Visa support available\n"
            
            message += f"\n💡 *Description:*\n{job_data.get('description', 'No description')[:200]}..."
            
            requirements = job_data.get('requirements', [])
            if requirements:
                message += f"\n📋 *Key Requirements:*\n"
                for req in requirements[:3]:
                    message += f"• {req}\n"
        
        return message
    
    def _format_ai_recommendation_message(self,
                                        jobs_list: List[Dict[str, Any]],
                                        ai_analysis: str,
                                        language: str) -> str:
        """Format AI recruiter recommendation message"""
        
        if language == 'ru':
            message = f"🤖 *Персональные рекомендации от AI-рекрутера*\n\n"
            message += f"Привет! Я нашел для вас {len(jobs_list)} отличных вакансий:\n\n"
            
            for i, job in enumerate(jobs_list[:3], 1):
                message += f"*{i}. {job.get('title', 'Неизвестная должность')}*\n"
                message += f"🏢 {job.get('company_name', 'Неизвестная компания')}\n"
                
                location = job.get('location', {})
                if isinstance(location, dict):
                    city = location.get('city', 'Неизвестно')
                else:
                    city = str(location) if location else 'Неизвестно'
                message += f"📍 {city}\n\n"
            
            if len(jobs_list) > 3:
                message += f"И еще {len(jobs_list) - 3} вакансий!\n\n"
            
            message += f"💬 *Мой анализ:*\n{ai_analysis[:300]}...\n\n"
            message += "Хотите узнать больше о вакансиях? Нажмите кнопки ниже! 👇"
            
        else:  # English
            message = f"🤖 *Personal Recommendations from AI Recruiter*\n\n"
            message += f"Hello! I found {len(jobs_list)} great job opportunities for you:\n\n"
            
            for i, job in enumerate(jobs_list[:3], 1):
                message += f"*{i}. {job.get('title', 'Unknown Position')}*\n"
                message += f"🏢 {job.get('company_name', 'Unknown Company')}\n"
                
                location = job.get('location', {})
                if isinstance(location, dict):
                    city = location.get('city', 'Unknown')
                else:
                    city = str(location) if location else 'Unknown'
                message += f"📍 {city}\n\n"
            
            if len(jobs_list) > 3:
                message += f"And {len(jobs_list) - 3} more jobs!\n\n"
            
            message += f"💬 *My Analysis:*\n{ai_analysis[:300]}...\n\n"
            message += "Want to learn more about the jobs? Click the buttons below! 👇"
        
        return message
    
    def _format_jobs_digest_message(self,
                                  new_jobs: List[Dict[str, Any]],
                                  subscription_data: Dict[str, Any],
                                  language: str) -> str:
        """Format jobs digest message"""
        
        if language == 'ru':
            message = f"📊 *Дайджест новых вакансий*\n\n"
            message += f"За последние дни найдено *{len(new_jobs)} новых вакансий* по вашим критериям:\n\n"
            
            # Show search criteria
            if subscription_data.get('search_query'):
                message += f"🔍 Запрос: {subscription_data['search_query']}\n"
            if subscription_data.get('location'):
                message += f"📍 Место: {subscription_data['location']}\n"
            if subscription_data.get('language_level'):
                message += f"🗣️ Немецкий: {subscription_data['language_level']}\n"
            
            message += "\n*Топ вакансии:*\n"
            
            for i, job in enumerate(new_jobs[:5], 1):
                message += f"*{i}. {job.get('title', 'Неизвестная должность')}*\n"
                message += f"   🏢 {job.get('company_name', 'Неизвестная компания')}\n"
                
                location = job.get('location', {})
                if isinstance(location, dict):
                    city = location.get('city', 'Неизвестно')
                else:
                    city = str(location) if location else 'Неизвестно'
                message += f"   📍 {city}\n\n"
                
        else:  # English
            message = f"📊 *New Jobs Digest*\n\n"
            message += f"Found *{len(new_jobs)} new jobs* matching your criteria in recent days:\n\n"
            
            if subscription_data.get('search_query'):
                message += f"🔍 Query: {subscription_data['search_query']}\n"
            if subscription_data.get('location'):
                message += f"📍 Location: {subscription_data['location']}\n"
            if subscription_data.get('language_level'):
                message += f"🗣️ German: {subscription_data['language_level']}\n"
            
            message += "\n*Top Jobs:*\n"
            
            for i, job in enumerate(new_jobs[:5], 1):
                message += f"*{i}. {job.get('title', 'Unknown Position')}*\n"
                message += f"   🏢 {job.get('company_name', 'Unknown Company')}\n"
                
                location = job.get('location', {})
                if isinstance(location, dict):
                    city = location.get('city', 'Unknown')
                else:
                    city = str(location) if location else 'Unknown'
                message += f"   📍 {city}\n\n"
        
        return message
    
    def _format_compatibility_alert_message(self,
                                          job_data: Dict[str, Any],
                                          compatibility_analysis: Dict[str, Any],
                                          language: str) -> str:
        """Format compatibility alert message"""
        
        score = compatibility_analysis.get('overall_score', 0)
        
        if language == 'ru':
            message = f"📈 *Высокая совместимость обнаружена!*\n\n"
            message += f"*{job_data.get('title', 'Неизвестная должность')}*\n"
            message += f"🏢 {job_data.get('company_name', 'Неизвестная компания')}\n"
            message += f"📊 Совместимость: *{score}%*\n\n"
            
            if score >= 90:
                message += "🔥 *Идеальное совпадение!* Настоятельно рекомендую подать заявку!\n\n"
            elif score >= 80:
                message += "⭐ *Отличная совместимость!* Эта вакансия очень вам подходит!\n\n"
            
            # Add strengths
            strengths = compatibility_analysis.get('strengths', [])
            if strengths:
                message += "💪 *Ваши преимущества:*\n"
                for strength in strengths[:3]:
                    message += f"• {strength}\n"
                message += "\n"
            
            # Add recommendations
            recommendations = compatibility_analysis.get('recommendations', [])
            if recommendations:
                message += "💡 *Рекомендации:*\n"
                for rec in recommendations[:2]:
                    message += f"• {rec}\n"
                    
        else:  # English
            message = f"📈 *High Compatibility Detected!*\n\n"
            message += f"*{job_data.get('title', 'Unknown Position')}*\n"
            message += f"🏢 {job_data.get('company_name', 'Unknown Company')}\n"
            message += f"📊 Compatibility: *{score}%*\n\n"
            
            if score >= 90:
                message += "🔥 *Perfect match!* Highly recommend applying!\n\n"
            elif score >= 80:
                message += "⭐ *Excellent compatibility!* This job suits you very well!\n\n"
            
            strengths = compatibility_analysis.get('strengths', [])
            if strengths:
                message += "💪 *Your Strengths:*\n"
                for strength in strengths[:3]:
                    message += f"• {strength}\n"
                message += "\n"
            
            recommendations = compatibility_analysis.get('recommendations', [])
            if recommendations:
                message += "💡 *Recommendations:*\n"
                for rec in recommendations[:2]:
                    message += f"• {rec}\n"
        
        return message
    
    def _format_interview_reminder_message(self,
                                         job_data: Dict[str, Any],
                                         interview_date: str,
                                         preparation_tips: List[str],
                                         language: str) -> str:
        """Format interview preparation reminder"""
        
        if language == 'ru':
            message = f"🎤 *Подготовка к собеседованию*\n\n"
            message += f"*{job_data.get('title', 'Неизвестная должность')}*\n"
            message += f"🏢 {job_data.get('company_name', 'Неизвестная компания')}\n"
            message += f"📅 Дата: {interview_date}\n\n"
            
            message += "🎯 *Рекомендации по подготовке:*\n"
            for tip in preparation_tips[:4]:
                message += f"• {tip}\n"
            
            message += f"\n💪 Удачи на собеседовании! Вы отлично подготовлены!"
            
        else:  # English
            message = f"🎤 *Interview Preparation*\n\n"
            message += f"*{job_data.get('title', 'Unknown Position')}*\n"
            message += f"🏢 {job_data.get('company_name', 'Unknown Company')}\n"
            message += f"📅 Date: {interview_date}\n\n"
            
            message += "🎯 *Preparation Tips:*\n"
            for tip in preparation_tips[:4]:
                message += f"• {tip}\n"
            
            message += f"\n💪 Good luck with your interview! You're well prepared!"
        
        return message
    
    def _create_job_actions_keyboard(self, job_data: Dict[str, Any], language: str) -> Dict[str, Any]:
        """Create keyboard with job actions"""
        
        if language == 'ru':
            buttons = [
                [
                    {"text": "📋 Подробнее о вакансии", "url": job_data.get('external_url', '#')},
                    {"text": "📝 Создать сопроводительное письмо", "callback_data": f"cover_letter_{job_data.get('id', '')}"}
                ],
                [
                    {"text": "📊 Анализ совместимости", "callback_data": f"compatibility_{job_data.get('id', '')}"},
                    {"text": "🌍 Перевести на русский", "callback_data": f"translate_{job_data.get('id', '')}_ru"}
                ],
                [
                    {"text": "⭐ Сохранить вакансию", "callback_data": f"save_{job_data.get('id', '')}"},
                    {"text": "🚫 Не показывать больше", "callback_data": f"hide_{job_data.get('id', '')}"}
                ]
            ]
        else:
            buttons = [
                [
                    {"text": "📋 Job Details", "url": job_data.get('external_url', '#')},
                    {"text": "📝 Generate Cover Letter", "callback_data": f"cover_letter_{job_data.get('id', '')}"}
                ],
                [
                    {"text": "📊 Compatibility Analysis", "callback_data": f"compatibility_{job_data.get('id', '')}"},
                    {"text": "🌍 Translate to English", "callback_data": f"translate_{job_data.get('id', '')}_en"}
                ],
                [
                    {"text": "⭐ Save Job", "callback_data": f"save_{job_data.get('id', '')}"},
                    {"text": "🚫 Don't Show Again", "callback_data": f"hide_{job_data.get('id', '')}"}
                ]
            ]
        
        return {"inline_keyboard": buttons}
    
    def _create_recommendations_keyboard(self, jobs_list: List[Dict[str, Any]], language: str) -> Dict[str, Any]:
        """Create keyboard for AI recommendations"""
        
        if language == 'ru':
            buttons = [
                [{"text": f"📋 Вакансия #{i+1}", "callback_data": f"job_details_{job.get('id', i)}"} 
                 for i, job in enumerate(jobs_list[:3])]
            ]
            buttons.append([
                {"text": "🎯 Показать все вакансии", "callback_data": "show_all_jobs"},
                {"text": "🤖 Задать вопрос AI-рекрутеру", "callback_data": "ask_ai_recruiter"}
            ])
        else:
            buttons = [
                [{"text": f"📋 Job #{i+1}", "callback_data": f"job_details_{job.get('id', i)}"} 
                 for i, job in enumerate(jobs_list[:3])]
            ]
            buttons.append([
                {"text": "🎯 Show All Jobs", "callback_data": "show_all_jobs"},
                {"text": "🤖 Ask AI Recruiter", "callback_data": "ask_ai_recruiter"}
            ])
        
        return {"inline_keyboard": buttons}
    
    def _create_digest_keyboard(self, new_jobs: List[Dict[str, Any]], language: str) -> Dict[str, Any]:
        """Create keyboard for jobs digest"""
        
        if language == 'ru':
            buttons = [
                [
                    {"text": "🎯 Открыть поиск работы", "url": "https://germany-ai-mini-app.netlify.app/telegram"},
                    {"text": "⚙️ Настроить подписки", "callback_data": "manage_subscriptions"}
                ]
            ]
        else:
            buttons = [
                [
                    {"text": "🎯 Open Job Search", "url": "https://germany-ai-mini-app.netlify.app/telegram"},
                    {"text": "⚙️ Manage Subscriptions", "callback_data": "manage_subscriptions"}
                ]
            ]
        
        return {"inline_keyboard": buttons}
    
    def _create_compatibility_actions_keyboard(self, 
                                             job_data: Dict[str, Any], 
                                             compatibility_analysis: Dict[str, Any], 
                                             language: str) -> Dict[str, Any]:
        """Create keyboard for compatibility alerts"""
        
        if language == 'ru':
            buttons = [
                [
                    {"text": "📝 Подать заявку", "url": job_data.get('external_url', '#')},
                    {"text": "📄 Создать сопроводительное", "callback_data": f"cover_letter_{job_data.get('id', '')}"}
                ],
                [
                    {"text": "🎤 Подготовка к интервью", "callback_data": f"interview_prep_{job_data.get('id', '')}"},
                    {"text": "📊 Полный анализ", "callback_data": f"full_analysis_{job_data.get('id', '')}"}
                ]
            ]
        else:
            buttons = [
                [
                    {"text": "📝 Apply Now", "url": job_data.get('external_url', '#')},
                    {"text": "📄 Generate Cover Letter", "callback_data": f"cover_letter_{job_data.get('id', '')}"}
                ],
                [
                    {"text": "🎤 Interview Prep", "callback_data": f"interview_prep_{job_data.get('id', '')}"},
                    {"text": "📊 Full Analysis", "callback_data": f"full_analysis_{job_data.get('id', '')}"}
                ]
            ]
        
        return {"inline_keyboard": buttons}
    
    def _create_interview_prep_keyboard(self, job_data: Dict[str, Any], language: str) -> Dict[str, Any]:
        """Create keyboard for interview preparation"""
        
        if language == 'ru':
            buttons = [
                [
                    {"text": "📚 Материалы для подготовки", "callback_data": f"prep_materials_{job_data.get('id', '')}"},
                    {"text": "🎯 Вопросы для интервью", "callback_data": f"interview_questions_{job_data.get('id', '')}"}
                ],
                [
                    {"text": "💼 Что надеть", "callback_data": f"dress_code_{job_data.get('id', '')}"},
                    {"text": "⏰ Напомнить за час", "callback_data": f"remind_interview_{job_data.get('id', '')}"}
                ]
            ]
        else:
            buttons = [
                [
                    {"text": "📚 Preparation Materials", "callback_data": f"prep_materials_{job_data.get('id', '')}"},
                    {"text": "🎯 Interview Questions", "callback_data": f"interview_questions_{job_data.get('id', '')}"}
                ],
                [
                    {"text": "💼 What to Wear", "callback_data": f"dress_code_{job_data.get('id', '')}"},
                    {"text": "⏰ Remind in 1 Hour", "callback_data": f"remind_interview_{job_data.get('id', '')}"}
                ]
            ]
        
        return {"inline_keyboard": buttons}
    
    def _create_custom_actions_keyboard(self, actions: List[Dict[str, str]], language: str) -> Dict[str, Any]:
        """Create custom actions keyboard"""
        
        buttons = []
        for action in actions:
            button = {"text": action.get('text', 'Action')}
            
            if action.get('url'):
                button['url'] = action['url']
            elif action.get('callback_data'):
                button['callback_data'] = action['callback_data']
            
            buttons.append([button])
        
        return {"inline_keyboard": buttons}

# Create global instance
telegram_job_notification_service = TelegramJobNotificationService()
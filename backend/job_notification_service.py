"""
📬 Job Notification Service - Telegram notifications for job subscriptions
Сервис уведомлений о вакансиях через Telegram
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from database import db
from job_search_service import job_search_service
import os
from telegram_service import telegram_service

logger = logging.getLogger(__name__)

class JobNotificationService:
    def __init__(self):
        self.bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
        self.check_interval = 3600  # Check every hour
        self.max_notifications_per_check = 5  # Limit to avoid spam
        
    async def start_notification_worker(self):
        """Start the notification worker that checks for new jobs"""
        logger.info("Starting job notification worker")
        
        while True:
            try:
                await self.check_and_notify_subscribers()
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Error in notification worker: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes before retry

    async def check_and_notify_subscribers(self):
        """Check all active subscriptions and send notifications for new jobs"""
        try:
            # Get all active job subscriptions
            subscriptions = await db.get_all_active_job_subscriptions()
            logger.info(f"Checking {len(subscriptions)} active job subscriptions")
            
            for subscription in subscriptions:
                try:
                    await self.process_subscription(subscription)
                    await asyncio.sleep(1)  # Small delay between subscriptions
                except Exception as e:
                    logger.error(f"Error processing subscription {subscription.get('id')}: {e}")
                    
        except Exception as e:
            logger.error(f"Error checking subscriptions: {e}")

    async def process_subscription(self, subscription: Dict[str, Any]):
        """Process a single subscription and send notifications if new jobs found"""
        try:
            subscription_id = subscription['id']
            user_id = subscription['user_id']
            user_email = subscription.get('email', '')
            
            logger.info(f"Processing subscription {subscription_id} for user {user_email}")
            
            # Build search parameters from subscription
            search_params = {
                'search_query': subscription.get('search_query'),
                'location': subscription.get('location'),
                'remote': subscription.get('remote'),
                'visa_sponsorship': subscription.get('visa_sponsorship'),
                'language_level': subscription.get('language_level'),
                'category': subscription.get('category'),
                'limit': 10  # Limit to recent jobs
            }
            
            # Search for jobs
            results = await job_search_service.search_jobs(**search_params)
            
            if results.get('status') == 'success' and results.get('jobs'):
                new_jobs = results['jobs'][:self.max_notifications_per_check]
                
                # Filter out jobs we might have already sent (basic deduplication)
                last_check = subscription.get('last_check')
                if last_check:
                    # Simple filter - in production you'd want more sophisticated tracking
                    new_jobs = [job for job in new_jobs if self._is_recent_job(job, last_check)]
                
                if new_jobs:
                    # Send Telegram notification
                    await self.send_telegram_notification(subscription, new_jobs)
                    
                    # Update subscription last check
                    current_count = subscription.get('notification_count', 0)
                    await db.update_job_subscription_last_check(
                        subscription_id, 
                        current_count + len(new_jobs)
                    )
                    
                    logger.info(f"Sent {len(new_jobs)} job notifications for subscription {subscription_id}")
                else:
                    # Update last check even if no new jobs
                    await db.update_job_subscription_last_check(subscription_id)
            else:
                # Update last check even if search failed
                await db.update_job_subscription_last_check(subscription_id)
                
        except Exception as e:
            logger.error(f"Error processing subscription: {e}")

    def _is_recent_job(self, job: Dict[str, Any], last_check: str) -> bool:
        """Check if job is recent (simple implementation)"""
        try:
            job_date = job.get('published_at', '')
            if not job_date:
                return True  # If no date, assume it's new
                
            # Simple check - could be improved with proper date parsing
            return True  # For now, send all jobs
        except:
            return True

    async def send_telegram_notification(self, subscription: Dict[str, Any], jobs: List[Dict[str, Any]]):
        """Send Telegram notification about new jobs"""
        try:
            user_email = subscription.get('email', 'Unknown')
            
            # Create notification message
            if len(jobs) == 1:
                job = jobs[0]
                message = self._create_single_job_message(job, subscription)
            else:
                message = self._create_multiple_jobs_message(jobs, subscription)
            
            # Send via telegram_service (if configured)
            try:
                await telegram_service.send_notification_message(user_email, message)
                logger.info(f"Sent Telegram notification to {user_email}")
            except Exception as e:
                logger.warning(f"Could not send Telegram notification: {e}")
                # Fallback: log the notification
                logger.info(f"JOB NOTIFICATION for {user_email}: {message}")
                
        except Exception as e:
            logger.error(f"Error sending telegram notification: {e}")

    def _create_single_job_message(self, job: Dict[str, Any], subscription: Dict[str, Any]) -> str:
        """Create notification message for a single job"""
        
        message = "🎯 **Новая вакансия по вашей подписке!**\n\n"
        message += f"**{job.get('title', 'Unknown Position')}**\n"
        message += f"🏢 {job.get('company_name', 'Unknown Company')}\n"
        message += f"📍 {job.get('location', 'Unknown Location')}\n"
        
        if job.get('remote'):
            message += "🌐 Удаленная работа\n"
            
        if job.get('visa_sponsorship'):
            message += "🛂 Поддержка визы\n"
            
        if job.get('estimated_salary'):
            salary = job['estimated_salary']
            message += f"💰 {salary['min_salary']}k-{salary['max_salary']}k EUR/год\n"
        
        # Add subscription info
        if subscription.get('language_level'):
            message += f"🗣 Требуемый уровень: {subscription['language_level']}\n"
            
        message += f"\n📝 {job.get('description', '')[:200]}..."
        
        if job.get('url'):
            message += f"\n\n🔗 Подробнее: {job['url']}"
            
        message += "\n\n💼 Найдено через German AI Job Search"
        
        return message

    def _create_multiple_jobs_message(self, jobs: List[Dict[str, Any]], subscription: Dict[str, Any]) -> str:
        """Create notification message for multiple jobs"""
        
        message = f"🎯 **{len(jobs)} новых вакансий по вашей подписке!**\n\n"
        
        for i, job in enumerate(jobs, 1):
            message += f"**{i}. {job.get('title', 'Unknown Position')}**\n"
            message += f"🏢 {job.get('company_name', 'Unknown Company')} | "
            message += f"📍 {job.get('location', 'Unknown Location')}\n"
            
            highlights = []
            if job.get('remote'):
                highlights.append("🌐 Remote")
            if job.get('visa_sponsorship'):
                highlights.append("🛂 Visa")
            if job.get('estimated_salary'):
                salary = job['estimated_salary']
                highlights.append(f"💰 {salary['min_salary']}-{salary['max_salary']}k EUR")
                
            if highlights:
                message += " | ".join(highlights) + "\n"
                
            if job.get('url'):
                message += f"🔗 {job['url']}\n"
                
            message += "\n"
        
        # Add subscription info
        subscription_info = []
        if subscription.get('search_query'):
            subscription_info.append(f"Запрос: {subscription['search_query']}")
        if subscription.get('location'):
            subscription_info.append(f"Локация: {subscription['location']}")
        if subscription.get('language_level'):
            subscription_info.append(f"Уровень: {subscription['language_level']}")
            
        if subscription_info:
            message += f"🔍 Ваша подписка: {' | '.join(subscription_info)}\n\n"
            
        message += "💼 Найдено через German AI Job Search"
        
        return message

    async def send_test_notification(self, user_email: str) -> bool:
        """Send a test notification to check if everything works"""
        try:
            test_message = """
🎯 **Тест уведомлений Job Search**

✅ Ваши уведомления о вакансиях настроены правильно!

Теперь вы будете получать уведомления о новых вакансиях, которые соответствуют вашим подпискам.

💼 German AI Job Search - ваш ИИ-помощник для карьеры
"""
            
            await telegram_service.send_notification_message(user_email, test_message)
            return True
        except Exception as e:
            logger.error(f"Test notification failed: {e}")
            return False

    async def get_notification_stats(self) -> Dict[str, Any]:
        """Get notification statistics"""
        try:
            subscriptions = await db.get_all_active_job_subscriptions()
            
            total_subscriptions = len(subscriptions)
            total_notifications = sum(sub.get('notification_count', 0) for sub in subscriptions)
            
            # Group by subscription types
            by_category = {}
            by_language_level = {}
            
            for sub in subscriptions:
                category = sub.get('category', 'all')
                by_category[category] = by_category.get(category, 0) + 1
                
                level = sub.get('language_level', 'any')
                by_language_level[level] = by_language_level.get(level, 0) + 1
            
            return {
                'total_subscriptions': total_subscriptions,
                'total_notifications_sent': total_notifications,
                'subscriptions_by_category': by_category,
                'subscriptions_by_language_level': by_language_level,
                'last_check': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting notification stats: {e}")
            return {
                'total_subscriptions': 0,
                'total_notifications_sent': 0,
                'error': str(e)
            }

# Create global instance
job_notification_service = JobNotificationService()

# Background task function (to be called from main application)
async def start_job_notifications():
    """Start the background job notification service"""
    try:
        await job_notification_service.start_notification_worker()
    except Exception as e:
        logger.error(f"Job notification service failed to start: {e}")
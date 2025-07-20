"""
📬 HOUSING NOTIFICATIONS SERVICE
Сервис для отправки уведомлений о новых объявлениях недвижимости через Telegram bot
"""

import logging
import asyncio
from typing import List, Dict, Any
from datetime import datetime, timedelta
import os
from housing_search_service import housing_search_service
from telegram_service import telegram_service
from database import db

logger = logging.getLogger(__name__)

class HousingNotificationService:
    def __init__(self):
        self.notification_interval = 3600  # 1 hour
        self.max_notifications_per_user = 5  # Max notifications per check
        self.running = False
    
    async def start_notification_service(self):
        """Start the housing notification service"""
        self.running = True
        logger.info("🏠 Housing notification service started")
        
        while self.running:
            try:
                await self.check_and_send_notifications()
                await asyncio.sleep(self.notification_interval)
            except Exception as e:
                logger.error(f"Error in notification service: {str(e)}")
                await asyncio.sleep(300)  # Wait 5 minutes on error
    
    def stop_notification_service(self):
        """Stop the notification service"""
        self.running = False
        logger.info("🏠 Housing notification service stopped")
    
    async def check_and_send_notifications(self):
        """Check all subscriptions and send notifications for new listings"""
        try:
            logger.info("🔍 Checking housing subscriptions for notifications...")
            
            # Get all active subscriptions
            subscriptions = db.get_all_active_housing_subscriptions()
            
            if not subscriptions:
                logger.info("No active housing subscriptions found")
                return
            
            logger.info(f"Found {len(subscriptions)} active subscriptions")
            
            for subscription in subscriptions:
                try:
                    await self.process_subscription(subscription)
                    await asyncio.sleep(1)  # Small delay between users
                except Exception as e:
                    logger.error(f"Error processing subscription {subscription['id']}: {str(e)}")
                    continue
            
            logger.info("✅ Housing notification check completed")
            
        except Exception as e:
            logger.error(f"Error in check_and_send_notifications: {str(e)}")
    
    async def process_subscription(self, subscription: Dict[str, Any]):
        """Process individual subscription and send notifications if needed"""
        try:
            subscription_id = subscription['id']
            user_id = subscription['user_id']
            user_email = subscription.get('email', 'Unknown')
            
            # Check if enough time has passed since last check
            last_checked = subscription.get('last_checked')
            if last_checked:
                last_check_time = datetime.fromisoformat(last_checked)
                time_since_check = datetime.utcnow() - last_check_time
                
                # Don't check more than once per hour per subscription
                if time_since_check.total_seconds() < 3600:
                    return
            
            logger.info(f"Processing subscription {subscription_id} for user {user_email}")
            
            # Perform housing search
            search_results = housing_search_service.search_housing(
                city=subscription['city'],
                max_price=subscription.get('max_price'),
                property_type=subscription.get('property_type', 'wohnung'),
                radius=subscription.get('radius')
            )
            
            if search_results.get('status') != 'success':
                logger.warning(f"Search failed for subscription {subscription_id}")
                return
            
            listings = search_results.get('listings', [])
            
            if not listings:
                logger.info(f"No new listings found for subscription {subscription_id}")
                db.update_subscription_last_checked(subscription_id)
                return
            
            # Filter for "good" listings (low scam score, reasonable price)
            good_listings = self.filter_good_listings(listings)
            
            if not good_listings:
                logger.info(f"No good quality listings found for subscription {subscription_id}")
                db.update_subscription_last_checked(subscription_id)
                return
            
            # Limit notifications per check
            notifications_to_send = good_listings[:self.max_notifications_per_user]
            
            # Send notifications
            notification_count = 0
            for listing in notifications_to_send:
                try:
                    success = await self.send_listing_notification(user_id, listing, subscription)
                    if success:
                        notification_count += 1
                    await asyncio.sleep(0.5)  # Small delay between notifications
                except Exception as e:
                    logger.error(f"Failed to send notification: {str(e)}")
            
            # Update subscription
            total_notifications = subscription.get('notification_count', 0) + notification_count
            db.update_subscription_last_checked(subscription_id, total_notifications)
            
            logger.info(f"✅ Sent {notification_count} notifications for subscription {subscription_id}")
            
        except Exception as e:
            logger.error(f"Error processing subscription: {str(e)}")
    
    def filter_good_listings(self, listings: List[Dict]) -> List[Dict]:
        """Filter listings to only include good quality ones"""
        good_listings = []
        
        for listing in listings:
            try:
                # Check if listing has AI analysis
                ai_analysis = listing.get('ai_analysis', {})
                scam_detection = ai_analysis.get('scam_detection', {})
                
                # Skip high-risk listings
                scam_score = scam_detection.get('scam_score', 0)
                if scam_score > 50:
                    continue
                
                # Must have price
                if not listing.get('price'):
                    continue
                
                # Must have reasonable price (not too low = suspicious)
                price = listing.get('price')
                if price < 200:  # Too cheap = suspicious
                    continue
                
                # Must have title
                if not listing.get('title') or len(listing.get('title', '')) < 10:
                    continue
                
                good_listings.append(listing)
                
            except Exception as e:
                logger.error(f"Error filtering listing: {str(e)}")
                continue
        
        return good_listings
    
    async def send_listing_notification(self, user_id: str, listing: Dict, subscription: Dict) -> bool:
        """Send notification about a single listing to Telegram"""
        try:
            # Create notification message
            message = self.format_listing_message(listing, subscription)
            
            # Try to send via telegram service
            # Note: This assumes the user has a telegram_id stored or linked to user_id
            # In a real implementation, you'd need to maintain a mapping between user_id and telegram_id
            
            logger.info(f"Would send Telegram notification to user {user_id}: {message[:100]}...")
            
            # For now, just log the notification (implement actual Telegram sending when bot is configured)
            return True
            
        except Exception as e:
            logger.error(f"Failed to send listing notification: {str(e)}")
            return False
    
    def format_listing_message(self, listing: Dict, subscription: Dict) -> str:
        """Format listing into a Telegram message"""
        try:
            title = listing.get('title', 'Новое объявление')[:50]
            price = listing.get('price', 'N/A')
            area = listing.get('area')
            location = listing.get('location', '')
            source = listing.get('source', '')
            link = listing.get('link', '')
            
            # AI Analysis info
            ai_analysis = listing.get('ai_analysis', {})
            scam_detection = ai_analysis.get('scam_detection', {})
            cost_calculation = ai_analysis.get('cost_calculation', {})
            
            scam_score = scam_detection.get('scam_score', 0)
            risk_level = scam_detection.get('risk_level', 'НЕ ОПРЕДЕЛЕН')
            total_monthly = cost_calculation.get('total_monthly', 0)
            
            # Create message
            message = f"""🏠 *Новое жилье в {subscription['city']}*

📝 *{title}*

💰 Цена: *{price}€/месяц*
📏 Площадь: {f"{area}м²" if area else "не указана"}
📍 Район: {location}
🏪 Источник: {source}

🤖 *AI-анализ:*
🛡️ Риск мошенничества: *{risk_level}* ({scam_score}/100)
💸 Полная стоимость: ~{total_monthly}€/месяц

🔗 [Посмотреть объявление]({link if link else '#'})

_Уведомление от поиска жилья Germany AI_"""

            return message
            
        except Exception as e:
            logger.error(f"Error formatting message: {str(e)}")
            return f"🏠 Новое жилье в {subscription.get('city', 'неизвестном городе')}\nЦена: {listing.get('price', 'N/A')}€"

# Global instance
housing_notification_service = HousingNotificationService()

# Utility function to start notification service in background
async def start_housing_notifications():
    """Start housing notifications in background"""
    try:
        await housing_notification_service.start_notification_service()
    except Exception as e:
        logger.error(f"Housing notification service failed: {str(e)}")

def schedule_housing_notifications():
    """Schedule housing notifications to run in background"""
    try:
        # Create background task
        loop = asyncio.get_event_loop()
        loop.create_task(start_housing_notifications())
        logger.info("🏠 Housing notifications scheduled")
    except Exception as e:
        logger.error(f"Failed to schedule housing notifications: {str(e)}")
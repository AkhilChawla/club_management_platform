"""RabbitMQ consumers for the notification service."""

import os
import json
import logging
from typing import Dict, Any

import pika
from django.conf import settings

from .models import Notification

logger = logging.getLogger(__name__)


class NotificationConsumer:
    """Consumes messages from RabbitMQ and creates notifications."""
    
    def __init__(self):
        self.host = os.environ.get('RABBITMQ_HOST', 'localhost')
        self.user = os.environ.get('RABBITMQ_USER', 'guest')
        self.password = os.environ.get('RABBITMQ_PASS', 'guest')
        self.connection = None
        self.channel = None
    
    def connect(self):
        """Establish connection to RabbitMQ."""
        try:
            credentials = pika.PlainCredentials(self.user, self.password)
            self.connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=self.host, credentials=credentials)
            )
            self.channel = self.connection.channel()
            
            # Declare the events queue (same as other services use)
            self.channel.queue_declare(queue='events', durable=True)
            
            logger.info("Connected to RabbitMQ successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            return False
    
    def disconnect(self):
        """Close connection to RabbitMQ."""
        if self.connection and not self.connection.is_closed:
            self.connection.close()
            logger.info("Disconnected from RabbitMQ")
    
    def handle_message(self, channel, method, properties, body):
        """Handle incoming message from RabbitMQ."""
        try:
            # Parse the message
            message = json.loads(body.decode('utf-8'))
            event_type = message.get('type')
            event_data = message.get('data', {})
            
            logger.info(f"Received event: {event_type} with data: {event_data}")
            
            # Create notification based on event type
            notification = self.create_notification(event_type, event_data)
            
            if notification:
                logger.info(f"Created notification: {notification.id}")
                # Acknowledge the message
                channel.basic_ack(delivery_tag=method.delivery_tag)
            else:
                logger.warning(f"Failed to create notification for event: {event_type}")
                # Still acknowledge to avoid reprocessing
                channel.basic_ack(delivery_tag=method.delivery_tag)
                
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse message: {e}")
            # Acknowledge to avoid reprocessing invalid messages
            channel.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            # Acknowledge to avoid infinite reprocessing
            channel.basic_ack(delivery_tag=method.delivery_tag)
    
    def create_notification(self, event_type: str, event_data: Dict[str, Any]) -> Notification:
        """Create a notification based on event type and data."""
        try:
            # Determine source service based on event type
            source_service = self.get_source_service(event_type)
            
            # Generate notification content based on event type
            subject, message = self.generate_notification_content(event_type, event_data)
            
            # Extract user information from event data
            user_id = event_data.get('user_id')
            user_name = event_data.get('user_name')
            user_email = event_data.get('user_email')
            
            # Create the notification
            notification = Notification.objects.create(
                event_type=event_type,
                event_data=event_data,
                user_id=user_id,
                user_name=user_name,
                user_email=user_email,
                subject=subject,
                message=message,
                source_service=source_service,
                status='pending'
            )
            
            return notification
            
        except Exception as e:
            logger.error(f"Failed to create notification: {e}")
            return None
    
    def get_source_service(self, event_type: str) -> str:
        """Determine which service generated the event."""
        if event_type in ['club_created', 'club_approved', 'member_added']:
            return 'clubs_service'
        elif event_type in ['event_created', 'rsvp_created']:
            return 'events_service'
        elif event_type in ['order_created']:
            return 'payments_service'
        else:
            return 'unknown'
    
    def generate_notification_content(self, event_type: str, event_data: Dict[str, Any]) -> tuple[str, str]:
        """Generate subject and message based on event type."""
        
        if event_type == 'club_created':
            club_name = event_data.get('name', 'Unknown Club')
            return (
                "New Club Created",
                f"A new club '{club_name}' has been created and is pending approval."
            )
        
        elif event_type == 'club_approved':
            club_name = event_data.get('name', 'Unknown Club')
            return (
                "Club Approved!",
                f"Congratulations! Your club '{club_name}' has been approved and is now active."
            )
        
        elif event_type == 'member_added':
            club_id = event_data.get('club_id', 'Unknown')
            user_name = event_data.get('user_name', 'Unknown User')
            role = event_data.get('role', 'member')
            return (
                "New Club Member",
                f"{user_name} has joined the club as a {role}."
            )
        
        elif event_type == 'event_created':
            event_name = event_data.get('name', 'Unknown Event')
            club_id = event_data.get('club_id', 'Unknown')
            return (
                "New Event Created",
                f"A new event '{event_name}' has been created for your club."
            )
        
        elif event_type == 'rsvp_created':
            event_id = event_data.get('event_id', 'Unknown')
            user_name = event_data.get('user_name', 'Unknown User')
            return (
                "Event RSVP",
                f"{user_name} has RSVP'd for the event."
            )
        
        elif event_type == 'order_created':
            order_id = event_data.get('id', 'Unknown')
            user_id = event_data.get('user_id', 'Unknown User')
            return (
                "Ticket Purchase Confirmation",
                f"Your ticket purchase (Order #{order_id}) has been completed successfully."
            )
        
        else:
            return (
                "System Notification",
                f"An event of type '{event_type}' has occurred in the system."
            )
    
    def start_consuming(self):
        """Start consuming messages from RabbitMQ with retry logic."""
        max_retries = 5
        retry_delay = 5
        
        for attempt in range(max_retries):
            try:
                if self.connect():
                    logger.info("Successfully connected to RabbitMQ")
                    break
                else:
                    logger.warning(f"Connection attempt {attempt + 1} failed")
                    if attempt < max_retries - 1:
                        logger.info(f"Retrying in {retry_delay} seconds...")
                        import time
                        time.sleep(retry_delay)
                        retry_delay *= 2  # Exponential backoff
            except Exception as e:
                logger.error(f"Connection attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    import time
                    time.sleep(retry_delay)
                    retry_delay *= 2
        
        if not self.connection or self.connection.is_closed:
            logger.error("Failed to connect to RabbitMQ after all retries. Cannot start consuming.")
            return
        
        try:
            # Set up the consumer
            self.channel.basic_consume(
                queue='events',
                on_message_callback=self.handle_message,
                auto_ack=False  # We manually acknowledge messages
            )
            
            logger.info("Starting to consume messages from 'events' queue...")
            logger.info("Press Ctrl+C to stop consuming")
            
            # Start consuming
            self.channel.start_consuming()
            
        except KeyboardInterrupt:
            logger.info("Stopping consumer...")
            self.channel.stop_consuming()
        except Exception as e:
            logger.error(f"Error while consuming: {e}")
        finally:
            self.disconnect()


def start_notification_consumer():
    """Start the notification consumer."""
    consumer = NotificationConsumer()
    consumer.start_consuming()

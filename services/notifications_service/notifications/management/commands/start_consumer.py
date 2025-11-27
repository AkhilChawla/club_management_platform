"""Django management command to start the notification consumer."""

from django.core.management.base import BaseCommand
from notifications.consumers import start_notification_consumer


class Command(BaseCommand):
    help = 'Start the RabbitMQ notification consumer'

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Starting notification consumer...')
        )
        
        try:
            start_notification_consumer()
        except KeyboardInterrupt:
            self.stdout.write(
                self.style.SUCCESS('Notification consumer stopped.')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error running consumer: {e}')
            )

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from orders.models import Order

class Command(BaseCommand):
    help = 'Deletes pending and unpaid orders older than 24 hours'

    def handle(self, *args, **kwargs):
        cutoff_time = timezone.now() - timedelta(days=1)
        
        # Filter orders that are PENDING AND UNPAID and older than 24 hours
        orders_to_delete = Order.objects.filter(
            status='PENDING',
            payment_status='UNPAID',
            created_at__lt=cutoff_time
        )
        
        count = orders_to_delete.count()
        if count > 0:
            orders_to_delete.delete()
            self.stdout.write(self.style.SUCCESS(f'Successfully deleted {count} stale orders.'))
        else:
            self.stdout.write(self.style.SUCCESS('No stale orders found.'))

import os
import django
import sys

# Add project root to path
sys.path.append(os.getcwd())

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from orders.models import Order

try:
    o = Order.objects.get(pk=11)
    o.status = 'COMPLETED'
    o.payment_status = 'PAID' # Ensure payment is paid too
    o.save()
    print(f"SUCCESS: Order {o.id} updated to {o.status}")
except Exception as e:
    print(f"ERROR: {e}")

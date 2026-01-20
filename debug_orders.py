import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from orders.models import Order
from django.contrib.auth import get_user_model

User = get_user_model()

print("--- ALL ORDERS ---")
for order in Order.objects.all():
    has_review = hasattr(order, 'review')
    print(f"Order #{order.id}: Customer={order.customer.username}, TailorID={order.tailor.id} ({order.tailor.user.username}), Status={order.status}, HasReview={has_review}")

print("\n--- USERS ---")
for user in User.objects.all():
    print(f"User: {user.username} (ID: {user.id})")

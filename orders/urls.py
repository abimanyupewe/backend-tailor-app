from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet, CleanupOrdersView

router = DefaultRouter()
router.register(r'', OrderViewSet, basename='order')

from .webhook import PaymentNotificationView

urlpatterns = [
    path('payment-notification/', PaymentNotificationView.as_view(), name='payment-notification'),
    path('cleanup/', CleanupOrdersView.as_view(), name='order-cleanup'),
    path('', include(router.urls)),
]

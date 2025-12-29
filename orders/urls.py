from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet

router = DefaultRouter()
router.register(r'', OrderViewSet, basename='order')

from .webhook import PaymentNotificationView

urlpatterns = [
    path('payment-notification/', PaymentNotificationView.as_view(), name='payment-notification'),
    path('', include(router.urls)),
]

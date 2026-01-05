from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ChatRoomViewSet, MessageViewSet

router = DefaultRouter()
router.register(r'rooms', ChatRoomViewSet, basename='chat-rooms')
# We register messages separately. Usage: /api/chat/messages/?room_id=1
router.register(r'messages', MessageViewSet, basename='chat-messages')

urlpatterns = [
    path('', include(router.urls)),
]

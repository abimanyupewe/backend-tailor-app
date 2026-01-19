from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ChatRoomViewSet, MessageViewSet

# Standard router for flat endpoints if needed (like standard CRUD)
router = DefaultRouter()
router.register(r'rooms', ChatRoomViewSet, basename='chat-rooms')
# messages registered but we will override with specific path below for nested

urlpatterns = [
    # 1. Start Chat: POST /api/chat/start/{user_id}/
    path('start/<int:user_id>/', ChatRoomViewSet.as_view({'post': 'start_chat_by_user'}), name='chat-start'),

    # 2. List Chat Room: GET /api/chat/rooms/ (Covered by router)
    
    # 3. Get Messages: GET /api/chat/rooms/{room_id}/messages/
    # 4. Send Message: POST /api/chat/rooms/{room_id}/messages/
    path('rooms/<int:room_pk>/messages/', MessageViewSet.as_view({'get': 'list', 'post': 'create'}), name='chat-room-messages'),

    path('', include(router.urls)),
]

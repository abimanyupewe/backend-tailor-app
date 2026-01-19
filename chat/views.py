from rest_framework import viewsets, permissions, status, decorators
from rest_framework.response import Response
from django.db.models import Q
from .models import ChatRoom, Message
from .serializers import ChatRoomSerializer, MessageSerializer
from users.models import TailorProfile

class ChatRoomViewSet(viewsets.ModelViewSet):
    serializer_class = ChatRoomSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'TAILOR':
            return ChatRoom.objects.filter(tailor=user.tailor_profile).order_by('-updated_at')
        else:
            return ChatRoom.objects.filter(customer=user).order_by('-updated_at')

    def perform_create(self, serializer):
        # This is strictly not needed if we use 'start_chat' action, but good for generic CREATE
        pass

    @decorators.action(detail=False, methods=['post'], url_path='start/(?P<user_id>\d+)')
    def start_chat_by_user(self, request, user_id=None):
        """
        Start chat with a tailor (by User ID).
        URL: /api/chat/start/{user_id}/
        """
        try:
            # Assume user_id passed is the User ID of the Tailor
            # Find the TailorProfile associated with this User
            tailor_profile = TailorProfile.objects.get(user_id=user_id)
        except TailorProfile.DoesNotExist:
             return Response({"error": "Tailor not found or user is not a tailor"}, status=status.HTTP_404_NOT_FOUND)

        # Ensure user is not the same tailor
        if request.user.role == 'TAILOR' and request.user.tailor_profile == tailor_profile:
             return Response({"error": "Cannot chat with yourself"}, status=status.HTTP_400_BAD_REQUEST)

        # Get or Create Room
        room, created = ChatRoom.objects.get_or_create(
            customer=request.user,
            tailor=tailor_profile
        )
        
        serializer = self.get_serializer(room)
        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Support both query_param and URL kwarg (nested)
        room_id = self.kwargs.get('room_pk') or self.request.query_params.get('room_id')
        user = self.request.user
        
        if room_id:
            return Message.objects.filter(
                Q(room__customer=user) | Q(room__tailor__user=user),
                room_id=room_id
            ).order_by('created_at')
        return Message.objects.none()

    def perform_create(self, serializer):
        # Support both body param and URL kwarg
        room_id = self.kwargs.get('room_pk') or self.request.data.get('room')
        
        try:
            room = ChatRoom.objects.get(pk=room_id)
        except ChatRoom.DoesNotExist:
             raise serializers.ValidationError({"room": "Room not found"})
        
        # Verify user belongs to room
        if self.request.user != room.customer and (self.request.user.role != 'TAILOR' or self.request.user.tailor_profile != room.tailor):
             raise permissions.PermissionDenied("You are not part of this chat room")

        serializer.save(room=room, sender=self.request.user)
        
        # Update room timestamp
        room.save() # Updates updated_at auto_now

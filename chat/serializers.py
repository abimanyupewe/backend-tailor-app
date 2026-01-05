from rest_framework import serializers
from .models import ChatRoom, Message
from users.serializers import UserSerializer, TailorProfileSerializer

class MessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.username', read_only=True)
    is_me = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ['id', 'sender', 'sender_name', 'text', 'is_read', 'created_at', 'is_me']
        read_only_fields = ['sender', 'created_at', 'is_read']

    def get_is_me(self, obj):
        request = self.context.get('request')
        if request and request.user:
            return obj.sender == request.user
        return False

class ChatRoomSerializer(serializers.ModelSerializer):
    partner_name = serializers.SerializerMethodField()
    partner_avatar = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = ChatRoom
        fields = ['id', 'customer', 'tailor', 'created_at', 'partner_name', 'partner_avatar', 'last_message']

    def get_partner_name(self, obj):
        request = self.context.get('request')
        if not request or not request.user:
            return ""
        
        if request.user.role == 'TAILOR':
            return obj.customer.username
        else:
            return obj.tailor.shop_name # Or tailor.user.username

    def get_partner_avatar(self, obj):
        request = self.context.get('request')
        if not request or not request.user:
            return None
        
        if request.user.role == 'TAILOR':
            return obj.customer.avatar.url if obj.customer.avatar else None
        else:
            return obj.tailor.shop_image.url if obj.tailor.shop_image else None # Or user avatar

    def get_last_message(self, obj):
        last_msg = obj.messages.order_by('-created_at').first()
        if last_msg:
             return MessageSerializer(last_msg, context=self.context).data
        return None

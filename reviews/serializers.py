from rest_framework import serializers
from .models import Review
from orders.models import Order
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'avatar']

class ReviewSerializer(serializers.ModelSerializer):
    user = UserSerializer(source='order.customer', read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'order', 'user', 'rating', 'comment', 'created_at']
        read_only_fields = ['id', 'created_at', 'user']

    def validate_order(self, value):
        if value.customer != self.context['request'].user:
            raise serializers.ValidationError("You can only review your own orders.")
        if value.status != Order.Status.COMPLETED:
            raise serializers.ValidationError("You can only review completed orders.")
        return value

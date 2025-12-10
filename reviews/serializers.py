from rest_framework import serializers
from .models import Review
from orders.models import Order

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'order', 'rating', 'comment', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate_order(self, value):
        if value.customer != self.context['request'].user:
            raise serializers.ValidationError("You can only review your own orders.")
        if value.status != Order.Status.COMPLETED:
            raise serializers.ValidationError("You can only review completed orders.")
        return value

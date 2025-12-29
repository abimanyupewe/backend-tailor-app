from rest_framework import serializers
from .models import Order, OrderItem, OrderTracking
from tailor.serializers import TailorServiceSerializer
from users.serializers import UserSerializer, TailorProfileSerializer

class OrderItemSerializer(serializers.ModelSerializer):
    service_detail = TailorServiceSerializer(source='service', read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ['id', 'service', 'service_detail', 'quantity', 'notes', 'reference_image', 'price_at_order']
        read_only_fields = ['price_at_order']

class OrderTrackingSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderTracking
        fields = ['status', 'description', 'timestamp']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    customer = UserSerializer(read_only=True)
    tailor_detail = TailorProfileSerializer(source='tailor', read_only=True)
    tracking_history = OrderTrackingSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'customer', 'tailor', 'tailor_detail', 'status', 'total_price', 'created_at', 'updated_at', 'items', 'tracking_history', 'snap_token', 'payment_status']
        read_only_fields = ['customer', 'total_price', 'status', 'created_at', 'updated_at', 'snap_token', 'payment_status']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        user = self.context['request'].user
        
        # Calculate total price
        total_price = 0
        for item in items_data:
            service = item['service']
            total_price += service.base_price * item.get('quantity', 1)

        order = Order.objects.create(customer=user, total_price=total_price, **validated_data)

        for item_data in items_data:
            service = item_data['service']
            OrderItem.objects.create(
                order=order,
                price_at_order=service.base_price,
                **item_data
            )
        
        # Initial Tracking
        OrderTracking.objects.create(order=order, status=Order.Status.PENDING, description="Order placed")
        
        return order

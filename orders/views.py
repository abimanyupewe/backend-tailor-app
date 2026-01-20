from rest_framework import viewsets, permissions, status, decorators
from rest_framework.response import Response
from .models import Order, OrderTracking
from .serializers import OrderSerializer

from django.conf import settings
import midtransclient
import uuid

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        order = serializer.save(customer=self.request.user)
        
        # Initialize Snap client
        snap = midtransclient.Snap(
            is_production=settings.MIDTRANS_IS_PRODUCTION,
            server_key=settings.MIDTRANS_SERVER_KEY,
            client_key=settings.MIDTRANS_CLIENT_KEY
        )
        
        # Create transaction parameters
        transaction_details = {
            'order_id': f"ORDER-{order.id}-{uuid.uuid4().hex[:6]}", # Unique Order ID
            'gross_amount': int(order.total_price),
        }
        
        customer_details = {
            'first_name': order.customer.first_name,
            'last_name': order.customer.last_name,
            'email': order.customer.email,
            'phone': order.customer.phone_number,
        }
        
        transaction = {
            'transaction_details': transaction_details,
            'customer_details': customer_details,
            # You can add item_details here if needed
        }
        
        try:
            snap_response = snap.create_transaction(transaction)
            order.snap_token = snap_response['token']
            order.save()
        except Exception as e:
            # Re-raise exception so Frontend knows why it failed
            from rest_framework import serializers
            raise serializers.ValidationError({"midtrans_error": str(e)})

    def get_queryset(self):
        user = self.request.user
        if user.role == 'TAILOR':
            return Order.objects.filter(tailor__user=user).order_by('-created_at')
        return Order.objects.filter(customer=user).order_by('-created_at')

    @decorators.action(detail=True, methods=['post'])
    def status(self, request, pk=None):
        order = self.get_object()
        if order.tailor.user != request.user:
             return Response({"error": "Not authorized"}, status=status.HTTP_403_FORBIDDEN)

        new_status = request.data.get('status')
        description = request.data.get('description', '')

        if new_status not in Order.Status.values:
            return Response({"error": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST)

        order.status = new_status
        order.save()

        OrderTracking.objects.create(order=order, status=new_status, description=description)

        return Response({"status": "updated", "current_status": new_status})

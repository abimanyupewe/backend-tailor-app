from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Order
import midtransclient

class PaymentNotificationView(APIView):
    authentication_classes = [] # Disable CSRF check/Session Auth
    permission_classes = [] # Allow Midtrans to post without auth

    def post(self, request):
        snap = midtransclient.Snap(
            is_production=settings.MIDTRANS_IS_PRODUCTION,
            server_key=settings.MIDTRANS_SERVER_KEY,
            client_key=settings.MIDTRANS_CLIENT_KEY
        )
        
        try:
            notification_body = request.data
            print(f"Midtrans Notification Received: {notification_body}") # Debug Log
            # Verify notification functionality provided by library is better
            # But here we trust the payload if it matches our order format
            
            order_id_str = notification_body.get('order_id')
            transaction_status = notification_body.get('transaction_status')
            fraud_status = notification_body.get('fraud_status')
            
            # Extract ID from 'ORDER-{id}-{uuid}'
            # safer to store order_id in order model or just parse
            try:
                db_order_id = order_id_str.split('-')[1]
                order = Order.objects.get(id=db_order_id)
            except (IndexError, Order.DoesNotExist):
                return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

            if transaction_status == 'capture':
                if fraud_status == 'challenge':
                    order.payment_status = Order.PaymentStatus.UNPAID # or CHALLENGE
                else:
                    order.payment_status = Order.PaymentStatus.PAID
            elif transaction_status == 'settlement':
                order.payment_status = Order.PaymentStatus.PAID
            elif transaction_status == 'pending':
                order.payment_status = Order.PaymentStatus.UNPAID
            elif transaction_status in ['deny', 'expire', 'cancel']:
                order.payment_status = Order.PaymentStatus.CANCELLED  # or EXPIRED
            
            order.save()
            return Response({'status': 'OK'})
            
        except Exception as e:
            print(f"Notification Error: {e}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

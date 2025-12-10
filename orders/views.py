from rest_framework import viewsets, permissions, status, decorators
from rest_framework.response import Response
from .models import Order, OrderTracking
from .serializers import OrderSerializer

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'TAILOR':
            return Order.objects.filter(tailor__user=user).order_by('-created_at')
        return Order.objects.filter(customer=user).order_by('-created_at')

    @decorators.action(detail=True, methods=['post'])
    def status(self, request, pk=None):
        order = self.get_object()
        # Ensure only the assigned tailor can update status
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

from rest_framework import viewsets, permissions, filters, decorators
from rest_framework.response import Response
from django.db.models import F, FloatField, ExpressionWrapper
from django.db.models.functions import Cast
from django.db.models.expressions import RawSQL
from .models import TailorService, ShopLocation, TailorPost
from users.models import TailorProfile
from .serializers import TailorDetailSerializer, TailorServiceSerializer, ShopLocationSerializer, TailorPostSerializer

# 1. Total Revenue (Paid or Completed orders)
from orders.models import Order
from django.db.models import Sum, Count
from django.utils import timezone
import datetime

class TailorViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Public viewset to list and retrieve tailors.
    """
    queryset = TailorProfile.objects.filter(is_verified=True)
    serializer_class = TailorDetailSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter]
    search_fields = ['shop_name', 'services__name']

    def get_queryset(self):
        queryset = super().get_queryset()
        lat = self.request.query_params.get('lat')
        lon = self.request.query_params.get('lon')
        
        if lat and lon:
            # Haversine formula in raw SQL (PostgreSQL specific but works with simple floats)
            # Distance in kilometers
            sql = """
            6371 * acos(
                cos(radians(%s)) * cos(radians(location.latitude)) *
                cos(radians(location.longitude) - radians(%s)) +
                sin(radians(%s)) * sin(radians(location.latitude))
            )
            """
            
            # Annotate manually since we are traversing relationship (tailor -> location)
            # We fetch location latitude/longitude by joining tables
            queryset = queryset.select_related('location').annotate(
                distance=RawSQL(
                    # We need to map 'location.latitude' to the actual table column name
                    # Typically app_model.field. Let's assume tailor_shoplocation
                    f"""
                    6371 * acos(
                        cos(radians(%s)) * cos(radians(tailor_shoplocation.latitude)) *
                        cos(radians(tailor_shoplocation.longitude) - radians(%s)) +
                        sin(radians(%s)) * sin(radians(tailor_shoplocation.latitude))
                    )
                    """,
                    params=[lat, lon, lat]
                )
            )
            
            # Radius filtering (default 500m / 0.5km if 'nearby' param is sent)
            if self.request.query_params.get('radius'):
                try:
                    radius_km = float(self.request.query_params.get('radius'))
                    queryset = queryset.filter(distance__lte=radius_km)
                except ValueError:
                    pass
            
            # Default sorting by distance if coordinates are present
            queryset = queryset.order_by('distance')
            
        return queryset

class TailorServiceViewSet(viewsets.ModelViewSet):
    """
    Viewset for tailors to manage their services.
    """
    serializer_class = TailorServiceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return TailorService.objects.filter(tailor__user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(tailor=self.request.user.tailor_profile)

class ShopLocationViewSet(viewsets.ModelViewSet):
    """
    Viewset for tailors to manage their shop location.
    """
    serializer_class = ShopLocationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ShopLocation.objects.filter(tailor__user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(tailor=self.request.user.tailor_profile)

    @decorators.action(detail=False, methods=['get', 'put', 'patch'])
    def my_location(self, request):
        location, created = ShopLocation.objects.get_or_create(tailor=request.user.tailor_profile)
        if request.method == 'GET':
            serializer = self.get_serializer(location)
            return Response(serializer.data)
        
        serializer = self.get_serializer(location, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

class TailorPostViewSet(viewsets.ModelViewSet):
    """
    Viewset for tailors to manage their posts (portfolio).
    """
    serializer_class = TailorPostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return TailorPost.objects.filter(tailor__user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(tailor=self.request.user.tailor_profile)

class TailorDashboardViewSet(viewsets.ViewSet):
    """
    ViewSet for Tailor Admin Dashboard Analytics.
    """
    permission_classes = [permissions.IsAuthenticated]

    @decorators.action(detail=False, methods=['get'])
    def summary(self, request):
        user = request.user
        if user.role != 'TAILOR':
             return Response({"error": "Only tailors can access this dashboard"}, status=status.HTTP_403_FORBIDDEN)
        
        tailor_profile = user.tailor_profile
        
        # Get date range from query params, default to 7 days
        days_param = request.query_params.get('range', '7')
        try:
            days = int(days_param)
            if days not in [1, 3, 7, 30]: 
                 days = 7 # Fallback to default if invalid
        except ValueError:
            days = 7

        today = timezone.now().date()
        start_date = today - datetime.timedelta(days=days - 1) # Inclusive of today

        # 1. Total Revenue (Paid orders within range)
        total_revenue = Order.objects.filter(
            tailor=tailor_profile,
            payment_status='PAID',
            created_at__date__gte=start_date
        ).aggregate(total=Sum('total_price'))['total'] or 0

        # 2. Order Statistics (All time or within range? Usually dashboard stats match the range)
        # Let's filter stats by range too for consistency
        order_stats = Order.objects.filter(
            tailor=tailor_profile,
            created_at__date__gte=start_date
        ).values('status').annotate(count=Count('id'))
        
        stats_dict = {
            'PENDING': 0,
            'ACCEPTED': 0,
            'IN_PROGRESS': 0,
            'COMPLETED': 0,
            'CANCELLED': 0
        }
        for stat in order_stats:
            stats_dict[stat['status']] = stat['count']

        # 3. Chart Data (Daily breakdown)
        # Generate list of dates from start_date to today
        date_list = [(today - datetime.timedelta(days=i)) for i in range(days - 1, -1, -1)]
        
        chart_data = []
        for date in date_list:
            daily_orders = Order.objects.filter(
                tailor=tailor_profile,
                created_at__date=date
            )
            
            daily_revenue = daily_orders.filter(payment_status='PAID').aggregate(total=Sum('total_price'))['total'] or 0
            daily_count = daily_orders.count()
            
            chart_data.append({
                'date': date.strftime('%Y-%m-%d'),
                'revenue': daily_revenue,
                'orders': daily_count
            })

        return Response({
            'range': f"{days} days",
            'total_revenue': total_revenue,
            'order_stats': stats_dict,
            'chart_data': chart_data
        })

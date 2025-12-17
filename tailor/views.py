from rest_framework import viewsets, permissions, filters, decorators
from rest_framework.response import Response
from django.db.models import F, FloatField, ExpressionWrapper
from django.db.models.functions import Cast
from django.db.models.expressions import RawSQL
from .models import TailorService, ShopLocation, TailorPost
from users.models import TailorProfile
from .serializers import TailorDetailSerializer, TailorServiceSerializer, ShopLocationSerializer, TailorPostSerializer

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

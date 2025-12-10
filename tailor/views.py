from rest_framework import viewsets, permissions, filters, decorators
from rest_framework.response import Response
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
        # Geo-filtering logic would go here
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

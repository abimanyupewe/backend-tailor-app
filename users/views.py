from rest_framework import viewsets, permissions, status, decorators, filters
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
from .serializers import (
    RegisterSerializer, LoginSerializer, UserSerializer,
    CustomerProfileSerializer, TailorProfileSerializer,
    TailorRegisterSerializer
)


User = get_user_model()

class AuthViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]

    @decorators.action(detail=False, methods=['post'])
    def register(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'role': user.role
        }, status=status.HTTP_201_CREATED)

    @decorators.action(detail=False, methods=['post'], url_path='register-tailor')
    def register_tailor(self, request):
        serializer = TailorRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'role': user.role
        }, status=status.HTTP_201_CREATED)

    @decorators.action(detail=False, methods=['post'])
    def login(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'role': user.role
        })

class ProfileViewSet(viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.user.role == User.Role.TAILOR:
            return TailorProfileSerializer
        return CustomerProfileSerializer

    def get_object(self):
        if self.request.user.role == User.Role.TAILOR:
            return self.request.user.tailor_profile
        return self.request.user.customer_profile

    @decorators.action(detail=False, methods=['get', 'put', 'patch'])
    def me(self, request):
        instance = self.get_object()
        if request.method == 'GET':
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet to list all users (for debugging or admin purposes).
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny] # Changed to AllowAny for easier debugging as requested
    filter_backends = [filters.SearchFilter]
    search_fields = ['username', 'email']

    def get_queryset(self):
        queryset = User.objects.all()
        role = self.request.query_params.get('role')
        if role:
            queryset = queryset.filter(role=role)
        return queryset

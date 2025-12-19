from rest_framework import viewsets, permissions, status, decorators, filters
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
from .serializers import (
    RegisterSerializer, LoginSerializer, UserSerializer,
    CustomerProfileSerializer, TailorProfileSerializer,
    TailorRegisterSerializer, ChangePasswordSerializer,
    RequestPasswordResetSerializer, ResetPasswordSerializer
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
            'role': user.role,
            'role': user.role
        })

    @decorators.action(detail=False, methods=['post'], url_path='change-password', permission_classes=[permissions.IsAuthenticated])
    def change_password(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        if not user.check_password(serializer.data.get("old_password")):
            return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(serializer.data.get("new_password"))
        user.save()
        return Response({"status": "Password updated successfully"}, status=status.HTTP_200_OK)

    @decorators.action(detail=False, methods=['post'], url_path='request-password-reset')
    def request_password_reset(self, request):
        serializer = RequestPasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.data['email']
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # For security, don't reveal if user exists
            return Response({"status": "If an account exists, a reset email has been sent."}, status=status.HTTP_200_OK)

        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        
        # In a real app, this link points to a Frontend page (e.g., Flutter App Deep Link)
        # For this dev phase, we just show the token/uid in the email body
        reset_link = f"UID: {uid}\nToken: {token}"
        
        send_mail(
            subject="Password Reset Request",
            message=f"Use these credentials to reset your password:\n{reset_link}",
            from_email=settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@tailorapp.com',
            recipient_list=[email],
            fail_silently=False,
        )
        
        return Response({"status": "If an account exists, a reset email has been sent."}, status=status.HTTP_200_OK)

    @decorators.action(detail=False, methods=['post'], url_path='reset-password')
    def reset_password(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        uid = serializer.validated_data['uid']
        token = serializer.validated_data['token']
        new_password = serializer.validated_data['new_password']
        
        try:
            uid_decoded = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=uid_decoded)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({"error": "Invalid token or user"}, status=status.HTTP_400_BAD_REQUEST)
            
        if not default_token_generator.check_token(user, token):
             return Response({"error": "Invalid or expired token"}, status=status.HTTP_400_BAD_REQUEST)
             
        user.set_password(new_password)
        user.save()
        return Response({"status": "Password has been reset successfully"}, status=status.HTTP_200_OK)

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

from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from .models import CustomerProfile, TailorProfile

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'phone_number', 'avatar']
        read_only_fields = ['id']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'role', 'phone_number']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            role=validated_data.get('role', User.Role.CUSTOMER),
            phone_number=validated_data.get('phone_number', '')
        )
        if user.role == User.Role.CUSTOMER:
            CustomerProfile.objects.create(user=user)
        elif user.role == User.Role.TAILOR:
            TailorProfile.objects.create(user=user, shop_name=f"{user.username}'s Shop")
        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Incorrect Credentials")

class CustomerProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = CustomerProfile
        fields = ['user', 'address']

class TailorProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = TailorProfile
        fields = ['user', 'shop_name', 'bio', 'is_verified', 'experience_years']

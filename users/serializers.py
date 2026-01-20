from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from .models import CustomerProfile, TailorProfile

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'phone_number', 'avatar']
        read_only_fields = ['id']

class RegisterSerializer(serializers.ModelSerializer):
    # ... (unchanged) ...
    password = serializers.CharField(write_only=True)
    re_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'password', 're_password']

    def validate(self, data):
        if data['password'] != data['re_password']:
            raise serializers.ValidationError({"password": "Passwords must match."})
        return data

    def create(self, validated_data):
        validated_data.pop('re_password')
        user = User.objects.create_user(
            username=validated_data['username'],
            email='',
            password=validated_data['password'],
            role=User.Role.CUSTOMER,
            phone_number=''
        )
        CustomerProfile.objects.create(user=user)
        return user

class TailorRegisterSerializer(serializers.ModelSerializer):
    # ... (unchanged) ...
    password = serializers.CharField(write_only=True)
    re_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'password', 're_password']

    def validate(self, data):
        if data['password'] != data['re_password']:
            raise serializers.ValidationError({"password": "Passwords must match."})
        return data

    def create(self, validated_data):
        validated_data.pop('re_password')
        user = User.objects.create_user(
            username=validated_data['username'],
            email='',
            password=validated_data['password'],
            role=User.Role.TAILOR,
            phone_number=''
        )
        TailorProfile.objects.create(user=user, shop_name=f"{user.username}'s Shop", is_verified=True)
        return user

class LoginSerializer(serializers.Serializer):
    # ... (unchanged) ...
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Incorrect Credentials")

class ChangePasswordSerializer(serializers.Serializer):
    # ... (unchanged) ...
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    re_new_password = serializers.CharField(required=True)

    def validate(self, data):
        if data['new_password'] != data['re_new_password']:
            raise serializers.ValidationError({"new_password": "New passwords must match."})
        return data

class RequestPasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

class ResetPasswordSerializer(serializers.Serializer):
    # ... (unchanged) ...
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True)
    re_new_password = serializers.CharField(write_only=True)

    def validate(self, data):
        if data['new_password'] != data['re_new_password']:
            raise serializers.ValidationError({"new_password": "Passwords must match."})
        return data

class CustomerProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    # Writable fields for User update (Flat structure for Form-Data support)
    email = serializers.EmailField(write_only=True, required=False)
    username = serializers.CharField(write_only=True, required=False)
    first_name = serializers.CharField(write_only=True, required=False)
    last_name = serializers.CharField(write_only=True, required=False)
    phone_number = serializers.CharField(write_only=True, required=False)
    avatar = serializers.ImageField(write_only=True, required=False)

    class Meta:
        model = CustomerProfile
        fields = ['user', 'address', 'latitude', 'longitude', 'email', 'username', 'first_name', 'last_name', 'phone_number', 'avatar']

    def update(self, instance, validated_data):
        user = instance.user
        
        # Update User fields from flat data
        if 'email' in validated_data: user.email = validated_data.pop('email')
        if 'username' in validated_data: user.username = validated_data.pop('username')
        if 'first_name' in validated_data: user.first_name = validated_data.pop('first_name')
        if 'last_name' in validated_data: user.last_name = validated_data.pop('last_name')
        if 'phone_number' in validated_data: user.phone_number = validated_data.pop('phone_number')
        if 'avatar' in validated_data: user.avatar = validated_data.pop('avatar')
        user.save()

        # Update Profile fields
        return super().update(instance, validated_data)

class TailorProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    # Writable fields for User update (Flat structure for Form-Data support)
    email = serializers.EmailField(write_only=True, required=False)
    username = serializers.CharField(write_only=True, required=False)
    first_name = serializers.CharField(write_only=True, required=False)
    last_name = serializers.CharField(write_only=True, required=False)
    phone_number = serializers.CharField(write_only=True, required=False)
    avatar = serializers.ImageField(write_only=True, required=False)

    class Meta:
        model = TailorProfile
        fields = ['id', 'user', 'shop_name', 'bio', 'is_verified', 'experience_years', 'shop_image', 'email', 'username', 'first_name', 'last_name', 'phone_number', 'avatar']

    def update(self, instance, validated_data):
        user = instance.user
        
        # Update User fields from flat data
        if 'email' in validated_data: user.email = validated_data.pop('email')
        if 'username' in validated_data: user.username = validated_data.pop('username')
        if 'first_name' in validated_data: user.first_name = validated_data.pop('first_name')
        if 'last_name' in validated_data: user.last_name = validated_data.pop('last_name')
        if 'phone_number' in validated_data: user.phone_number = validated_data.pop('phone_number')
        if 'avatar' in validated_data: user.avatar = validated_data.pop('avatar')
        user.save()

        # Update Profile fields
        return super().update(instance, validated_data)

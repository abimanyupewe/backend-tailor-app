from rest_framework import serializers
from .models import TailorService, ShopLocation, TailorPost
from users.serializers import TailorProfileSerializer

class TailorServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = TailorService
        fields = ['id', 'name', 'description', 'base_price', 'estimated_duration_days', 'is_active']

class ShopLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShopLocation
        fields = ['address', 'latitude', 'longitude']

class TailorPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = TailorPost
        fields = ['id', 'image', 'caption', 'created_at']
        read_only_fields = ['created_at']

class TailorDetailSerializer(TailorProfileSerializer):
    services = TailorServiceSerializer(many=True, read_only=True)
    location = ShopLocationSerializer(read_only=True)

    posts = TailorPostSerializer(many=True, read_only=True)
    distance = serializers.FloatField(read_only=True, required=False)

    class Meta(TailorProfileSerializer.Meta):
        fields = TailorProfileSerializer.Meta.fields + ['shop_image', 'services', 'location', 'posts', 'distance']

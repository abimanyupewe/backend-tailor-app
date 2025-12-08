from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import TailorService, ShopLocation, TailorPost

@admin.register(TailorService)
class TailorServiceAdmin(ModelAdmin):
    list_display = ('name', 'tailor', 'base_price', 'estimated_duration_days', 'is_active')
    list_filter = ('is_active', 'tailor')
    search_fields = ('name', 'tailor__shop_name')

@admin.register(ShopLocation)
class ShopLocationAdmin(ModelAdmin):
    list_display = ('tailor', 'address', 'latitude', 'longitude')
    search_fields = ('tailor__shop_name', 'address')

@admin.register(TailorPost)
class TailorPostAdmin(ModelAdmin):
    list_display = ('tailor', 'created_at', 'caption')
    list_filter = ('created_at', 'tailor')

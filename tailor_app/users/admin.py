from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from unfold.admin import ModelAdmin
from .models import User, CustomerProfile, TailorProfile

@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    list_display = ('username', 'email', 'role', 'is_staff')
    search_fields = ('username', 'email')
    list_filter = ('role', 'is_staff', 'is_active')

@admin.register(CustomerProfile)
class CustomerProfileAdmin(ModelAdmin):
    list_display = ('user', 'address')
    search_fields = ('user__username', 'address')

@admin.register(TailorProfile)
class TailorProfileAdmin(ModelAdmin):
    list_display = ('user', 'shop_name', 'is_verified')
    list_filter = ('is_verified',)
    search_fields = ('user__username', 'shop_name')

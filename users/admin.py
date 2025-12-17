from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from unfold.admin import ModelAdmin
from .models import User, CustomerProfile, TailorProfile

@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    list_display = ('username', 'email', 'display_avatar', 'role', 'phone_number', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'phone_number')
    list_filter = ('role', 'is_staff', 'is_active', 'date_joined')
    
    def display_avatar(self, obj):
        if obj.avatar:
            return format_html('<img src="{}" style="width: 40px; height: 40px; object-fit: cover; border-radius: 50%;" />', obj.avatar.url)
        return "-"
    display_avatar.short_description = "Avatar"

@admin.register(CustomerProfile)
class CustomerProfileAdmin(ModelAdmin):
    list_display = ('display_user_avatar', 'user', 'user_email', 'user_phone', 'address', 'latitude', 'longitude')
    search_fields = ('user__username', 'address', 'user__email', 'user__phone_number')

    def display_user_avatar(self, obj):
        if obj.user.avatar:
             return format_html('<img src="{}" style="width: 40px; height: 40px; object-fit: cover; border-radius: 50%;" />', obj.user.avatar.url)
        return "-"
    display_user_avatar.short_description = "Avatar"

    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = "Email"

    def user_phone(self, obj):
        return obj.user.phone_number
    user_phone.short_description = "Phone"
    search_fields = ('user__username', 'address')

@admin.register(TailorProfile)
class TailorProfileAdmin(ModelAdmin):
    list_display = ('display_user_avatar', 'user', 'display_shop_image', 'shop_name', 'is_verified', 'rating_display', 'experience_years')
    list_filter = ('is_verified', 'experience_years')
    search_fields = ('user__username', 'shop_name')

    def display_user_avatar(self, obj):
        if obj.user.avatar:
             return format_html('<img src="{}" style="width: 40px; height: 40px; object-fit: cover; border-radius: 50%;" />', obj.user.avatar.url)
        return "-"
    display_user_avatar.short_description = "User Avatar"

    def display_shop_image(self, obj):
        if obj.shop_image:
             return format_html('<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 5px;" />', obj.shop_image.url)
        return "-"
    display_shop_image.short_description = "Shop"
    
    def rating_display(self, obj):
        # Placeholder if we have ratings later
        return "-"
    rating_display.short_description = "Rating"

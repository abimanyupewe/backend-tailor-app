from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Order, OrderItem, OrderTracking

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    # Unfold supports inlines too, standard django admin inline works but for styling ensure it matches.
    # Unfold creates its own look for standard inlines.

class OrderTrackingInline(admin.TabularInline):
    model = OrderTracking
    extra = 0
    readonly_fields = ('status', 'description', 'timestamp')

@admin.register(Order)
class OrderAdmin(ModelAdmin):
    list_display = ('id', 'customer', 'tailor', 'status', 'total_price', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('customer__username', 'tailor__shop_name', 'id')
    inlines = [OrderItemInline, OrderTrackingInline]

@admin.register(OrderItem)
class OrderItemAdmin(ModelAdmin):
    list_display = ('order', 'service', 'quantity', 'price_at_order')
    list_filter = ('order__created_at',)

@admin.register(OrderTracking)
class OrderTrackingAdmin(ModelAdmin):
    list_display = ('order', 'status', 'timestamp')
    list_filter = ('status', 'timestamp')

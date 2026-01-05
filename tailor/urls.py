from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TailorViewSet, TailorServiceViewSet, ShopLocationViewSet, TailorPostViewSet, TailorDashboardViewSet

router = DefaultRouter()
router.register(r'list', TailorViewSet, basename='tailor-list')
router.register(r'manage/services', TailorServiceViewSet, basename='manage-services')
router.register(r'manage/location', ShopLocationViewSet, basename='manage-location')
router.register(r'manage/posts', TailorPostViewSet, basename='manage-posts')
router.register(r'dashboard', TailorDashboardViewSet, basename='tailor-dashboard')

urlpatterns = [
    path('', include(router.urls)),
]

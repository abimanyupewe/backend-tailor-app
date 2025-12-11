from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AuthViewSet, ProfileViewSet, UserViewSet

router = DefaultRouter()
router.register(r'auth', AuthViewSet, basename='auth')
router.register(r'profile', ProfileViewSet, basename='profile')
router.register(r'list', UserViewSet, basename='user-list')

urlpatterns = [
    path('', include(router.urls)),
]

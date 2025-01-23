from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    NotificationViewSet, 
    send_message, 
    login_user, 
    refresh_token,
    register_user
)

router = DefaultRouter()
router.register(r'notifications', NotificationViewSet, basename='notification')

urlpatterns = [
    path('register/', register_user, name='register'),
    path('login/', login_user, name='login'),
    path('send-message/', send_message, name='send-message'),
    path('refresh-token/', refresh_token, name='refresh-token'),
    path('', include(router.urls)),
]
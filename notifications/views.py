import traceback
from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Notification
from .serializers import NotificationSerializer, RegisterSerializer
from django.contrib.auth import authenticate


class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    
    def get_queryset(self):
        # Users can only see their own notifications
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')
    
    def create(self, request, *args, **kwargs):
        try:
            # Create the notification object directly
            notification = Notification.objects.create(
                user=request.user,
                message=request.data.get('message', '')
            )

            # Serialize the created object
            serializer = self.get_serializer(notification)

            # Get channel layer
            channel_layer = get_channel_layer()

            # Broadcast to all connected users
            async_to_sync(channel_layer.group_send)(
                "notification_broadcast",
                {
                    "type": "send_notification",
                    "message": {
                        "id": notification.id,
                        "message": notification.message,
                        "user": request.user.username,
                        "created_at": notification.created_at.isoformat(),
                        "read": notification.read
                    }
                }
            )
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            traceback.print_exc()
            print("Error:", str(e))
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    def update(self, request, *args, **kwargs):
        try:
            # Get the existing notification
            instance = self.get_object()
            
            # Check permission
            if instance.user != request.user:
                return Response(
                    {"detail": "You don't have permission to update this notification."},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Update the notification object directly
            instance.message = request.data.get('message', instance.message)
            instance.read = request.data.get('read', instance.read)
            instance.save()
            
            # Serialize the updated object
            serializer = self.get_serializer(instance)
            
            # Send real-time update notification if needed
            if 'message' in request.data:
                send_notification(request.user, serializer.instance.message)
            
            return Response(serializer.data)
            
        except Exception as e:
            traceback.print_exc()
            print("Error:", str(e))
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        # Mark all notifications as read for the current user
        notifications = self.get_queryset().filter(read=False)
        notifications.update(read=True)
        return Response({"status": "All notifications marked as read"})
    
    @action(detail=False, methods=['get'])
    def unread(self, request):
        # Get only unread notifications
        notifications = self.get_queryset().filter(read=False)
        serializer = self.get_serializer(notifications, many=True)
        return Response(serializer.data)

def send_notification(user, message):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"user_{user.id}", 
        {
            "type": "send_notification",
            "message": message
        }
    )

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'message': 'User registered successfully',
            'user_id': user.id,
            'username': user.username,
            'email': user.email,
            'access_token': str(refresh.access_token),
            'refresh_token': str(refresh),
        })
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    username = request.data.get('username')
    password = request.data.get('password')
    
    user = authenticate(username=username, password=password)
    
    if user:
        refresh = RefreshToken.for_user(user)
        return Response({
            'access_token': str(refresh.access_token),
            'refresh_token': str(refresh),
            'user_id': user.id,
            'username': user.username
        })
    else:
        return Response(
            {"error": "Invalid credentials"}, 
            status=status.HTTP_401_UNAUTHORIZED
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_message(request):
    try:
        user_id = request.data.get('user_id')
        message = request.data.get('message')
        
        try:
            target_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {"error": "Target user not found"},
                status=status.HTTP_404_NOT_FOUND
            )
            
        notification = Notification.objects.create(
            user=target_user,
            message=message
        )

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"user_{user_id}",
            {
                "type": "send_notification",
                "message": message
            }
        )

        return Response({
            "status": "success",
            "message": "Notification sent successfully",
            "notification_id": notification.id
        })

    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_token(request):
    refresh_token = request.data.get('refresh_token')
    try:
        refresh = RefreshToken(refresh_token)
        return Response({
            'access_token': str(refresh.access_token)
        })
    except Exception as e:
        return Response(
            {"error": "Invalid refresh token"},
            status=status.HTTP_401_UNAUTHORIZED
        )

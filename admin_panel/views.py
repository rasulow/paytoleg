from django.http import JsonResponse
from django.shortcuts import render
from rest_framework import viewsets, permissions, views
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import APIEndpoint, TransactionLog, ServiceConfiguration, UserActivity, Plugin
from .serializers import (
    UserSerializer,
    APIEndpointSerializer,
    TransactionLogSerializer,
    ServiceConfigurationSerializer,
    UserActivitySerializer,
)


class IsAdminUserOrReadOnly(permissions.BasePermission):
    """
    Разрешает чтение всем пользователям, а изменение только администраторам.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff


def index(request):
    """Представление главной страницы"""
    return render(request, 'admin_panel/index.html')


@login_required
def plugins(request):
    """Представление страницы плагинов"""
    if request.method == 'POST':
        for plugin in Plugin.objects.all():
            is_active = request.POST.get(f'plugin_{plugin.id}') == 'on'
            if plugin.is_active != is_active: 
                plugin.is_active = is_active
                plugin.save()

    plugins = Plugin.objects.all()
    return render(request, 'admin_panel/plugins.html', {'plugins': plugins})

class PluginListAPIView(views.APIView):

    def get(self, request):
        plugins = Plugin.objects.all().values(
            'id', 'name', 'key', 'is_active', 'settings', 'created_at', 'updated_at'
        )
        return Response(
            {
                'data': list(plugins)
            }
        )



class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]


class APIEndpointViewSet(viewsets.ModelViewSet):
    queryset = APIEndpoint.objects.all()
    serializer_class = APIEndpointSerializer
    permission_classes = [IsAdminUserOrReadOnly]

    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        endpoint = self.get_object()
        endpoint.is_active = not endpoint.is_active
        endpoint.save()
        return Response({'status': 'success'})


class TransactionLogViewSet(viewsets.ModelViewSet):
    queryset = TransactionLog.objects.all()
    serializer_class = TransactionLogSerializer
    permission_classes = [IsAdminUserOrReadOnly]
    filterset_fields = ['status', 'currency', 'created_at']
    search_fields = ['transaction_id', 'sender', 'receiver']
    ordering_fields = ['created_at', 'amount']

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        total_transactions = self.get_queryset().count()
        successful_transactions = self.get_queryset().filter(status='success').count()
        failed_transactions = self.get_queryset().filter(status='failed').count()
        
        return Response({
            'total': total_transactions,
            'successful': successful_transactions,
            'failed': failed_transactions,
            'success_rate': (successful_transactions / total_transactions * 100) if total_transactions > 0 else 0
        })


class ServiceConfigurationViewSet(viewsets.ModelViewSet):
    queryset = ServiceConfiguration.objects.all()
    serializer_class = ServiceConfigurationSerializer
    permission_classes = [IsAdminUserOrReadOnly]

    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        config = self.get_object()
        config.is_active = not config.is_active
        config.save()
        return Response({'status': 'success'})


class UserActivityViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = UserActivity.objects.all()
    serializer_class = UserActivitySerializer
    permission_classes = [IsAdminUserOrReadOnly]
    filterset_fields = ['user', 'action', 'created_at']
    search_fields = ['user__username', 'action', 'details']
    ordering_fields = ['created_at']

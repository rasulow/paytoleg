from rest_framework import serializers
from django.contrib.auth.models import User
from .models import APIEndpoint, TransactionLog, ServiceConfiguration, UserActivity


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name')


class APIEndpointSerializer(serializers.ModelSerializer):
    class Meta:
        model = APIEndpoint
        fields = '__all__'


class TransactionLogSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = TransactionLog
        fields = '__all__'


class ServiceConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceConfiguration
        fields = '__all__'


class UserActivitySerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = UserActivity
        fields = '__all__' 
        
        

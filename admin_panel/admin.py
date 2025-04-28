from django.contrib import admin
from django.utils.html import format_html
from .models import APIEndpoint, TransactionLog, ServiceConfiguration, UserActivity, Plugin


@admin.register(APIEndpoint)
class APIEndpointAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'url', 'description')
    ordering = ('-created_at',)


@admin.register(TransactionLog)
class TransactionLogAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'sender', 'receiver', 'amount', 'currency',
                   'status_colored', 'created_at')
    list_filter = ('status', 'currency', 'created_at')
    search_fields = ('transaction_id', 'sender', 'receiver')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)

    def status_colored(self, obj):
        colors = {
            'pending': 'orange',
            'success': 'green',
            'failed': 'red',
        }
        return format_html(
            '<span style="color: {};">{}</span>',
            colors.get(obj.status, 'black'),
            obj.get_status_display()
        )
    status_colored.short_description = 'Статус'


@admin.register(ServiceConfiguration)
class ServiceConfigurationAdmin(admin.ModelAdmin):
    list_display = ('name', 'key', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'key', 'description')
    ordering = ('name',)


@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'ip_address', 'created_at')
    list_filter = ('user', 'action', 'created_at')
    search_fields = ('user__username', 'action', 'details', 'ip_address')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    
    
@admin.register(Plugin)
class PluginAdmin(admin.ModelAdmin):
    pass

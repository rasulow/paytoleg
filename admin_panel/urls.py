from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'endpoints', views.APIEndpointViewSet)
router.register(r'transactions', views.TransactionLogViewSet)
router.register(r'configurations', views.ServiceConfigurationViewSet)
router.register(r'activities', views.UserActivityViewSet)

urlpatterns = [
    path('', views.index, name='index'),
    path('plugins/', views.plugins, name='plugins'),
    path('api/plugins/', views.PluginListAPIView.as_view(), name='api-plugins'),
    path('api/', include(router.urls)),
] 
from django.db import models
from django.contrib.auth.models import User


class Plugin(models.Model):
    """Модель для управления плагинами"""
    name = models.CharField('Название', max_length=100)
    key = models.CharField('Ключ', max_length=100, unique=True)
    is_active = models.BooleanField('Активен', default=True)
    settings = models.JSONField('Настройки', default=dict, blank=True)
    created_at = models.DateTimeField('Создан', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлен', auto_now=True)

    class Meta:
        verbose_name = 'Плагин'
        verbose_name_plural = 'Плагины'
        ordering = ['name']

    def __str__(self):
        return self.name


class APIEndpoint(models.Model):
    """Модель для хранения конечных точек API микросервисов"""
    name = models.CharField('Название', max_length=100)
    url = models.URLField('URL')
    description = models.TextField('Описание', blank=True)
    is_active = models.BooleanField('Активен', default=True)
    created_at = models.DateTimeField('Создан', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлен', auto_now=True)

    class Meta:
        verbose_name = 'API Endpoint'
        verbose_name_plural = 'API Endpoints'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class TransactionLog(models.Model):
    """Модель для хранения логов транзакций"""
    STATUS_CHOICES = [
        ('pending', 'В обработке'),
        ('success', 'Успешно'),
        ('failed', 'Ошибка'),
    ]

    transaction_id = models.CharField('ID транзакции', max_length=100, unique=True)
    sender = models.CharField('Отправитель', max_length=100)
    receiver = models.CharField('Получатель', max_length=100)
    amount = models.DecimalField('Сумма', max_digits=10, decimal_places=2)
    currency = models.CharField('Валюта', max_length=3)
    status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES)
    created_at = models.DateTimeField('Создан', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлен', auto_now=True)
    error_message = models.TextField('Сообщение об ошибке', blank=True)

    class Meta:
        verbose_name = 'Лог транзакции'
        verbose_name_plural = 'Логи транзакций'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.transaction_id} - {self.status}'


class ServiceConfiguration(models.Model):
    """Модель для хранения конфигураций сервисов"""
    name = models.CharField('Название', max_length=100)
    key = models.CharField('Ключ', max_length=100, unique=True)
    value = models.TextField('Значение')
    description = models.TextField('Описание', blank=True)
    is_active = models.BooleanField('Активен', default=True)
    created_at = models.DateTimeField('Создан', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлен', auto_now=True)

    class Meta:
        verbose_name = 'Конфигурация сервиса'
        verbose_name_plural = 'Конфигурации сервисов'
        ordering = ['name']

    def __str__(self):
        return self.name


class UserActivity(models.Model):
    """Модель для отслеживания действий пользователей"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    action = models.CharField('Действие', max_length=100)
    details = models.TextField('Детали', blank=True)
    ip_address = models.GenericIPAddressField('IP адрес')
    created_at = models.DateTimeField('Создан', auto_now_add=True)

    class Meta:
        verbose_name = 'Активность пользователя'
        verbose_name_plural = 'Активность пользователей'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} - {self.action}'

from django.contrib.auth.models import BaseUserManager

class CustomUserManager(BaseUserManager):
    def create_user(self, email=None, phone_number=None, password=None, **extra_fields):
        # Обязательное условие: либо email, либо phone_number должны быть переданы
        if not email and not phone_number:
            raise ValueError("User must have either an email or phone number")
        
        # Если email передан, то нормализуем его
        if email:
            email = self.normalize_email(email)
            extra_fields['email'] = email

        # Проверяем, что phone_number обязательно передан, если email отсутствует
        if not phone_number:
            raise ValueError("Phone number is required if email is not provided.")

        # Создаем пользователя
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_email_verified', True)
        extra_fields.setdefault('is_phone_verified', True)
        return self.create_user(email=email, password=password, **extra_fields)

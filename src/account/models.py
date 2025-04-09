from django.db import models
from django.contrib.auth.models import PermissionsMixin, AbstractBaseUser
from account.managers import CustomUserManager
import random

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, null=True, blank=True)
    phone_number = models.CharField(max_length=20, unique=True, null=True, blank=True)
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)
    is_phone_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []
    
    def get_fullname(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return self.get_fullname()
    
    class Meta:
        db_table = 'user'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-id']
    
    
class PhoneVerification(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="phone_verifications")
    phone_number = models.CharField(max_length=20, unique=True)
    code = models.CharField(max_length=6)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'phone_verification'
        verbose_name = 'Phone Verification'
        verbose_name_plural = 'Phone Verifications'
        ordering = ['-id']

    def __str__(self):
        return f"{self.phone_number} - {'Verified' if self.is_verified else 'Not Verified'}"


    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.is_verified and not self.user.is_phone_verified:
            self.user.is_phone_verified = True
            self.user.save()

    @staticmethod
    def gen_code():
        return str(random.randint(100000, 999999))
from os import environ as env
from datetime import timedelta
from django.utils import timezone
from rest_framework import serializers
from dotenv import load_dotenv
from account import models, tasks, services

load_dotenv()


class UsersListSerializer(serializers.ModelSerializer):
    """Serializer for listing all users."""
    class Meta:
        model = models.CustomUser
        fields = ('id', 'email', 'phone_number', 'first_name', 'last_name', 'is_active', 'is_phone_verified')


class UserRegisterSerializer(serializers.Serializer):
    """Serializer for user registration."""
    email = serializers.EmailField(required=False, allow_blank=True)
    phone_number = serializers.CharField(required=False, allow_blank=True)
    password1 = serializers.CharField(
        label="Password",
        style={'input_type': 'password'},
        trim_whitespace=False,
        write_only=True,
    )
    password2 = serializers.CharField(
        label="Password confirmation",
        style={'input_type': 'password'},
        trim_whitespace=False,
        write_only=True,
    )
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)

    def validate(self, attrs):
        """Validate registration data before creating a user."""
        email = attrs.get('email')
        phone_number = attrs.get('phone_number')
        password1 = attrs.get('password1')
        password2 = attrs.get('password2')

        # Check if either email or phone_number is provided
        if not email and not phone_number:
            raise serializers.ValidationError(
                {'non_field_errors': 'Either email or phone number is required.'}
            )

        # Check if passwords match
        if password1 != password2:
            raise serializers.ValidationError({'password2': 'Passwords must match.'})

        # Check if email is unique
        if email and models.CustomUser.objects.filter(email=email).exists():
            raise serializers.ValidationError({'email': 'A user with this email already exists.'})

        # Check if phone number is unique
        if phone_number and models.CustomUser.objects.filter(phone_number=phone_number).exists():
            raise serializers.ValidationError(
                {'phone_number': 'A user with this phone number already exists.'}
            )

        return attrs

    def create(self, validated_data):
        """Create a user, generate a verification code, and send it via SMS."""
        try:
            user = models.CustomUser.objects.create_user(
                email=validated_data.get('email'),
                phone_number=validated_data.get('phone_number'),
                password=validated_data['password1'],
                first_name=validated_data['first_name'],
                last_name=validated_data['last_name'],
            )

            if validated_data.get('phone_number'):
                self._create_phone_verification(user, validated_data['phone_number'])

            return user
        except Exception as e:
            raise serializers.ValidationError({'non_field_errors': f'Error creating user: {str(e)}'})

    def _create_phone_verification(self, user, phone_number):
        """Helper method to create a phone verification instance."""
        verification_code = models.PhoneVerification.gen_code()
        phone_verification = models.PhoneVerification.objects.create(
            user=user,
            phone_number=phone_number,
            code=verification_code,
            is_verified=False
        )
        return services.send_sms(phone_number, verification_code)


class UserRegistrationVerifyPhoneSerializer(serializers.Serializer):
    """Serializer for verifying a phone number."""
    phone_number = serializers.CharField(required=True)
    code = serializers.CharField(required=True, max_length=6)

    def validate(self, attrs):
        """Validate phone number and verification code."""
        phone_number = attrs.get('phone_number')
        code = attrs.get('code')

        if not phone_number or not code:
            raise serializers.ValidationError({'non_field_errors': 'Phone number and code are required.'})

        try:
            phone_verification = models.PhoneVerification.objects.get(phone_number=phone_number, code=code)
        except models.PhoneVerification.DoesNotExist:
            raise serializers.ValidationError({'non_field_errors': 'Invalid phone number or code.'})

        if phone_verification.is_verified:
            raise serializers.ValidationError({'phone_number': 'This phone number is already verified.'})

        expiration_time = timezone.now() - timedelta(minutes=int(env.get('PHONE_NUMBER_VERIFICATION_CODE_EXPIRATION_MINUTES', 10)))
        if phone_verification.created_at < expiration_time:
            raise serializers.ValidationError({'code': 'The verification code has expired.'})

        attrs['phone_verification'] = phone_verification
        return attrs

    def create(self, validated_data):
        """Confirm phone number verification."""
        phone_verification = validated_data['phone_verification']
        phone_verification.is_verified = True
        phone_verification.save()
        return phone_verification


class UserRegistrationResendPhoneVerificationSerializer(serializers.Serializer):
    """Serializer for resending a phone verification code."""
    phone_number = serializers.CharField(required=True)

    def validate(self, attrs):
        """Validate phone number for resending verification code."""
        phone_number = attrs.get('phone_number')

        if not phone_number:
            raise serializers.ValidationError({'phone_number': 'Phone number is required.'})

        try:
            phone_verification = models.PhoneVerification.objects.get(phone_number=phone_number)
        except models.PhoneVerification.DoesNotExist:
            raise serializers.ValidationError({'phone_number': 'This phone number is not registered.'})

        if phone_verification.is_verified:
            raise serializers.ValidationError({'phone_number': 'This phone number is already verified.'})

        attrs['phone_verification'] = phone_verification
        return attrs

    def create(self, validated_data):
        """Resend a phone verification code."""
        phone_number = validated_data['phone_number']
        phone_verification = validated_data['phone_verification']
        phone_verification.delete()

        try:
            user = models.CustomUser.objects.get(phone_number=phone_number)
            verification_code = models.PhoneVerification.gen_code()
            new_phone_verification = models.PhoneVerification.objects.create(
                user=user,
                phone_number=phone_number,
                code=verification_code,
                is_verified=False
            )
            services.send_sms(phone_number, verification_code)
            return user
        except models.CustomUser.DoesNotExist:
            raise serializers.ValidationError({'phone_number': 'User with this phone number not found.'})
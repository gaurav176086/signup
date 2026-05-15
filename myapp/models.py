from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.hashers import make_password
from .managers import CustomUserManager
from django.utils.timezone import now
# Create your models here.

class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True,null=True)
    updated_at = models.DateTimeField(auto_now=True,null=True)

    class Meta:
        abstract = True
        
class User(BaseModel, AbstractBaseUser, PermissionsMixin):
    USER_TYPES = (
        (1, 'SuperAdmin'),
        (2, 'Admin'),
        (3, 'User'),
    )
    GENDER_CHOICES = ( 
        ("male", "Male"),
        ("female", "Female"),
        ("other", "Other"),
    )
    
    firstname = models.CharField(max_length=30)
    lastname = models.CharField(max_length=30)  
    email = models.EmailField(unique=True)
    user_type=models.IntegerField(choices=USER_TYPES, default=3)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    
    email_notification = models.BooleanField(default=False)
    push_notification = models.BooleanField(default=False)
    
    objects = CustomUserManager()
    USERNAME_FIELD = 'email'

    def __str__(self):
      return self.email or f"User {self.id}"
  
  
class OTP (models.Model):
    PURPOSE_CHOICES = (
        ("signup", "Signup"),
        ("reset_password", "Reset Password"))
    purpose = models.CharField(max_length=20, choices=PURPOSE_CHOICES)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    otp_verified = models.BooleanField(default=False)
    
    def __str__(self):
        return f"OTP for {self.user} - {self.otp_code}"
    
    
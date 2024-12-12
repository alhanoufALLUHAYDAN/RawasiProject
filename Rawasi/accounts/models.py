from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from datetime import date , datetime

# Create your models here.

class CustomUser(AbstractUser):
    full_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    email = models.EmailField(unique=True)
    phone_number = models.CharField(
        max_length=12, 
        blank=True, 
        null=True,
        unique=True, 
    )
    profile_picture = models.ImageField(
        upload_to='profile_pictures/', 
        blank=True, 
        null=True, 
        default='profile_pictures/default_profile_picture.jpg'  
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Leader(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='leader')  # link to CustomUser
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Leader: {self.user.first_name} {self.user.last_name}"

class Investor(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='investor')  # link to CustomUser
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Investor: {self.user.first_name} {self.user.last_name}, Balance: {self.balance}"

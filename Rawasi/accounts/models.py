from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from datetime import date , datetime

# Create your models here.

class CustomUser(AbstractUser):
    full_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    phone_number = models.CharField(
        max_length=12, 
        blank=True, 
        null=True,
        unique=True, 
    )

    def clean(self): 
        today = date.today()

        if isinstance(self.date_of_birth, str): 
            self.date_of_birth = datetime.strptime(self.date_of_birth, "%Y-%m-%d").date()

        if not self.date_of_birth:
            raise ValidationError("يجب إدخال تاريخ الميلاد.")
        
        age = today.year - self.date_of_birth.year
        if today.month < self.date_of_birth.month or (today.month == self.date_of_birth.month and today.day < self.date_of_birth.day):
            age -= 1
        
        if age < 18:
            raise ValidationError("يجب أن يكون عمرك 18 سنة أو أكبر للتسجيل.")
        
        if self.phone_number and CustomUser.objects.filter(phone_number=self.phone_number).exists():
            raise ValidationError("رقم الهاتف المدخل موجود بالفعل في النظام.")
            
    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Leader(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='leader')  # link to CustomUser
    #managed_fund = models.OneToOneField('InvestmentFund', on_delete=models.CASCADE, related_name='leader', null=True, blank=True)
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

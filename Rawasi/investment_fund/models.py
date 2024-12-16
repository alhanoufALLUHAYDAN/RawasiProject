from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model

User = get_user_model()
# Family Investment Fund
class InvestmentFund(models.Model):
    STATUS_CHOICES = [
    ('Active', 'نشط'),
    ('Inactive', 'غير نشط'),
]
    
    name = models.CharField(max_length=255)
    description = models.TextField(default='')
    total_balance = models.FloatField(default=0.0)
    leader = models.OneToOneField('accounts.Leader', on_delete=models.CASCADE, related_name="managed_fund")
    is_active = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default='Inactive'  # Default is 'Inactive'
    )
    status = models.CharField(
        max_length=50,
        choices=[('Open', 'Open'), ('Closed', 'Closed'), ('Pending', 'Pending')],
        default='Pending'
    )
    category = models.CharField(
        max_length=50,
        choices=[('Stocks', 'أسهم'), ('Real Estate', 'عقارات')],
        default='Stocks'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    join_code = models.CharField(max_length=10, unique=True, blank=True, null=True) 
    def __str__(self):
        return self.name

# Base Wallet Model
class Wallet(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="wallet")
    balance = models.FloatField(default=0.0)
    last_updated = models.DateTimeField(auto_now=True)  # Tracks the last modification date
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s Wallet"

class Transactions(models.Model):
    fund = models.ForeignKey('InvestmentFund', on_delete=models.CASCADE, related_name="transactions")
    wallet = models.ForeignKey('Wallet', null=True, blank=True, on_delete=models.SET_NULL, related_name="transactions")
    transaction_type = models.CharField(
        max_length=50,
        choices=[('Deposit', 'Deposit'), ('Withdrawal', 'Withdrawal'), ('Profit', 'Profit')]
    )
    amount = models.FloatField()
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.transaction_type} - {self.amount}"






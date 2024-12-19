from django.db import models
from accounts.models import CustomUser, Investor
from investment_fund.models import InvestmentFund
from datetime import datetime
from decimal import Decimal
# Create your models here.

class InvestorFund(models.Model):
    fund = models.ForeignKey(InvestmentFund, on_delete=models.CASCADE, related_name='fund_investments') 
    investor = models.ForeignKey(Investor, on_delete=models.CASCADE, related_name='investments')  
    amount_invested = models.DecimalField(max_digits=12, decimal_places=2)
    invested_at = models.DateTimeField(auto_now_add=True)  
    status = models.CharField(max_length=100, choices=[('Completed', 'Completed'), ('Pending', 'Pending')], default='Pending') 

    def calculate_profit(self):
        """Calculates profit based on associated opportunities and expected returns."""
        total_profit = Decimal(0.0)  # Use Decimal for precise calculations
        opportunities = self.fund.investment_opportunities.filter(status='Closed')  # Consider only closed opportunities
        
        for opportunity in opportunities:
            # Calculate the investment period (in days)
            invested_period_days = (opportunity.end_date - opportunity.start_date).days or 1
            # Calculate profit considering investment duration
            profit = self.amount_invested * (opportunity.expected_return / 100) * (invested_period_days / 365)  # Pro-rate the return over the investment duration
            total_profit += profit
        
        # Optionally update the status after calculating the profit
        if total_profit > 0:
            self.status = 'Completed'
            self.save()

        return round(total_profit, 2)  # Return profit rounded to 2 decimal places


class InvestmentOpportunity(models.Model):
    INVESTMENT_TYPE_CHOICES = [
        ('Stocks', 'Stocks'),
        ('Real Estate', 'Real Estate')
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    company_name = models.CharField(max_length=255)
    fund = models.ForeignKey(InvestmentFund, on_delete=models.CASCADE, related_name='investment_opportunities') 
    investment_type = models.CharField(max_length=100, choices=INVESTMENT_TYPE_CHOICES, blank=False, null=False)
    total_investment = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    expected_return = models.FloatField()
    status = models.CharField(max_length=100, choices=[('Open', 'Open'), ('Closed', 'Closed'), ('Completed', 'Completed')], default='Open')
    pdf_file = models.FileField(upload_to='investment_opportunities/pdf/', blank=True, null=True)
    image = models.ImageField(upload_to='investment_opportunities/images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self): 
        return self.title
    


class Voting(models.Model):
    APPROVAL_CHOICES = [
        ('Accepted', 'Accepted'), 
        ('Rejected', 'Rejected'),
        ('Pending', 'Pending') ,
    ]
    VOTE_TYPE_CHOICES = [
        ('Buy', 'Buy'),
        ('Sell', 'Sell'),
    ]
    opportunity = models.ForeignKey('InvestmentOpportunity', on_delete=models.CASCADE, related_name='votes')  
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE) 
    vote = models.CharField(max_length=10, choices=APPROVAL_CHOICES, default='Pending') 
    vote_type = models.CharField(max_length=4, choices=VOTE_TYPE_CHOICES, default='Buy')
    required_approval_percentage = models.FloatField(default=70.0)  
    voting_start_time = models.DateTimeField(default=datetime.now)
    voting_end_time = models.DateTimeField(default=datetime.now)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True) 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} voted {self.vote} on {self.opportunity.title}"

class BuySellTransaction(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ('Buy', 'Buy'),
        ('Sell', 'Sell'), 
    ]
    
    opportunity = models.ForeignKey(InvestmentOpportunity, on_delete=models.CASCADE, related_name='buy_sell_transactions') 
    transaction_type = models.CharField(max_length=4, choices=TRANSACTION_TYPE_CHOICES) 
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_date = models.DateTimeField(auto_now_add=True) 
    status = models.CharField(max_length=50, choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected')],default='Pending') 

    def __str__(self):
        return f"{self.get_transaction_type_display()} Transaction for {self.opportunity.title}"

    
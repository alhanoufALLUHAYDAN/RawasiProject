from django import forms
from .models import InvestmentFund

class InvestmentFundForm(forms.ModelForm):
    class Meta:
        model = InvestmentFund
        fields = ['name', 'description', 'total_balance', 'is_active', 'status', 'category']


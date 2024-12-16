from django import forms
from .models import InvestmentOpportunity

class InvestmentOpportunityForm(forms.ModelForm):
    class Meta:
        model = InvestmentOpportunity
        fields = ['title', 'description', 'investment_type', 'total_investment', 'start_date', 'end_date', 'image', 'pdf_file']

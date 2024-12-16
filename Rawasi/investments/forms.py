from django import forms
from .models import InvestmentOpportunity

class InvestmentOpportunityForm(forms.ModelForm):
    class Meta:
        model = InvestmentOpportunity
        fields = ['title', 'description', 'investment_type', 'total_investment', 'required_approval_percentage', 'start_date', 'end_date', 'image', 'pdf_file']

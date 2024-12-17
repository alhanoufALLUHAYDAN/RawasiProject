from django import forms
from .models import InvestmentOpportunity , Voting

class InvestmentOpportunityForm(forms.ModelForm):
    class Meta:
        model = InvestmentOpportunity
        fields = ['title', 'description', 'investment_type', 'total_investment', 'start_date', 'end_date', 'image', 'pdf_file']

class VotingForm(forms.ModelForm):
    voting_duration_days = forms.IntegerField(
        min_value=1, 
        label="Voting Duration (in days)", 
        widget=forms.NumberInput(attrs={'placeholder': 'Duration in days'})
    )
    
    required_approval_percentage = forms.FloatField(
        min_value=0, 
        max_value=100, 
        label="Required Approval Percentage",
        widget=forms.NumberInput(attrs={'placeholder': 'Approval percentage'})
    )

    vote_type = forms.ChoiceField(
        choices=Voting.VOTE_TYPE_CHOICES,  
        label="Vote Type",
        widget=forms.Select(attrs={'placeholder': 'Select Vote Type'})
    )

    class Meta:
        model = Voting
        fields = ['vote_type', 'required_approval_percentage', 'voting_duration_days']  

    

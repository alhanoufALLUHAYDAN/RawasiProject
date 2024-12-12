
from django import forms
from main.models import Contact

# Create the form class
class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = "__all__"
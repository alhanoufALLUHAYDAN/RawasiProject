from django import forms
from django.contrib.auth.models import User

class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField(label="البريد الإلكتروني", max_length=254)

    def clean_email(self):
        email = self.cleaned_data['email']
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise forms.ValidationError("البريد الإلكتروني غير مسجل لدينا.")
        return email

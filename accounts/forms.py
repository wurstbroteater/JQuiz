from django import forms
from django.contrib.auth.models import User


class UpdateEmailForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email']


class DeleteAccountForm(forms.Form):
    confirm = forms.BooleanField(required=True, label="Confirm deletion")

from django import forms
from django.contrib.auth.models import User

class SignUpForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        data = super().clean()
        if data['password'] != data['confirm_password']:
            raise forms.ValidationError("Passwords don't match")
    class Meta:
        model = User
        fields = ('username', 'password', 'confirm_password')
        help_texts = {
            'username': ''
        }


from django import forms
from django.contrib.auth.models import User

class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        data = super().clean()
        if data['password'] != data['confirm_password']:
            self.add_error("confirm_password", "Passwords don't match")
        if len(data['password']) < 8:
            self.add_error("password", "Password must be at least 8 characters")
    class Meta:
        model = User
        fields = ('username', 'password', 'confirm_password')
        help_texts = {
            'username': ''
        }

class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput())
    password = forms.CharField(widget=forms.PasswordInput)





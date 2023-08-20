from django import forms

from django.core.exceptions import ValidationError
from django.contrib.auth.models import User


class LoginForm(forms.Form):
    username = forms.CharField(min_length=2, max_length=50)
    password = forms.CharField(min_length=8, max_length=50, widget=forms.PasswordInput)
    error = ""


class RegisterForm(forms.Form):
    username = forms.CharField(min_length=2, max_length=50)
    password = forms.CharField(min_length=8, max_length=50, widget=forms.PasswordInput)
    error = ""

    def username_clean(self):
        username = self.cleaned_data['username'].lower()
        new = User.objects.filter(username=username)
        if new.count():
            raise ValidationError("User Already Exist", code="invalid")
        return username

    def save(self):
        user = User.objects.create_user(
            self.cleaned_data['username'],
            self.cleaned_data['password'],
        )

        return user
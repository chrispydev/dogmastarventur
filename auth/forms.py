from django import forms
from savings.models import Customer
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        labels = {
            'password1': 'Password',
            'password2': 'Confirm Password',
        }


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'next_of_kin', 'balance', 'customer_image']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter customer name',
            }),
            'next_of_kin': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter next of kin',
            }),
            'balance': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter balance',
            }),
            'customer_image': forms.FileInput(attrs={
                'class': 'form-control-file',
            }),
        }


class AdminRegisterForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 != password2:
            raise forms.ValidationError("Passwords do not match!")
        return cleaned_data

from django import forms
from .models import Collection


class CollectionForm(forms.ModelForm):
    class Meta:
        model = Collection
        fields = ['customer', 'amount']
        widgets = {
            'customer': forms.Select(attrs={
                'class': 'form-control',
                'placeholder': 'Select a customer',
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter collection amount',
            }),
        }
        labels = {
            'customer': 'Customer',
            'amount': 'Collection Amount',
        }

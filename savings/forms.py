from django import forms
from savings.models import Collection, Customer


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



class DeductionForm(forms.Form):
    customer = forms.ModelChoiceField(queryset=Customer.objects.all(), label="Select Customer")
    amount = forms.DecimalField(min_value=0.01, max_digits=10, decimal_places=2, label="Amount to Deduct")

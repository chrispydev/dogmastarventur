from django import forms
from savings.models import Collection, Customer, Deduction


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


class DeductionForm(forms.ModelForm):
    deduction_type = forms.ChoiceField(
        choices=Deduction.DEDUCTION_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    customer = forms.ModelChoiceField(
        queryset=Customer.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    amount = forms.DecimalField(
        min_value=0.01,
        max_digits=10,
        decimal_places=2,
        label="Amount to Deduct",
        widget=forms.NumberInput(
            attrs={'class': 'form-control', 'placeholder': 'Enter amount'})
    )

    class Meta:
        model = Deduction
        fields = ['deduction_type', 'customer', 'amount']

    def clean(self):
        cleaned_data = super().clean()
        deduction_type = cleaned_data.get("deduction_type")
        customer = cleaned_data.get("customer")

        if deduction_type == "customer" and not customer:
            raise forms.ValidationError(
                "Please select a customer for a customer deduction.")

        if deduction_type == "company" and customer:
            raise forms.ValidationError(
                "Do not select a customer when deducting from the company account.")

        return cleaned_data

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser ,Order, Product

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2', 'role']

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['product', 'quantity']
        widgets = {
            'quantity': forms.NumberInput(attrs={
                'min': 1,
                'class': 'form-control'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show products with stock available
        self.fields['product'].queryset = Product.objects.filter(stock_quantity__gt=0)
        self.fields['product'].widget.attrs.update({
            'class': 'form-control'
        })
        
        # Add empty choice at the beginning
        self.fields['product'].empty_label = "Select a product"

    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if quantity < 1:
            raise forms.ValidationError("Quantity must be at least 1")
        return quantity 

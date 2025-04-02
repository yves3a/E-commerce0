from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Order, Product

# Custom User Registration Form
class CustomUserCreationForm(UserCreationForm):
    """
    Form for user registration that extends Django's UserCreationForm.
    Includes additional fields for the custom user model.
    """
    class Meta:
        model = CustomUser
        # Specify fields to be included in the registration form
        fields = ['username', 'email', 'password1', 'password2', 'role']

# Order Creation Form
class OrderForm(forms.ModelForm):
    """
    Form for creating and managing product orders.
    Includes validation for quantity and filters available products.
    """
    class Meta:
        model = Order
        # Only show product and quantity fields in the form
        fields = ['product', 'quantity']
        # Custom widget for quantity input with minimum value and styling
        widgets = {
            'quantity': forms.NumberInput(attrs={
                'min': 1,
                'class': 'form-control'
            })
        }

    def __init__(self, *args, **kwargs):
        """
        Initialize the form with custom queryset and styling.
        Filters out products with zero stock and adds Bootstrap classes.
        """
        super().__init__(*args, **kwargs)
        # Only show products with stock available
        self.fields['product'].queryset = Product.objects.filter(stock_quantity__gt=0)
        # Add Bootstrap styling to product dropdown
        self.fields['product'].widget.attrs.update({
            'class': 'form-control'
        })
        
        # Add empty choice at the beginning of product dropdown
        self.fields['product'].empty_label = "Select a product"

    def clean_quantity(self):
        """
        Custom validation for quantity field.
        Ensures quantity is at least 1.
        """
        quantity = self.cleaned_data.get('quantity')
        if quantity < 1:
            raise forms.ValidationError("Quantity must be at least 1")
        return quantity 

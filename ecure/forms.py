from django import forms
from .models import PrescriptionOrder, Order
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
import re


class PrescriptionForm(forms.ModelForm):
    class Meta:
        model = PrescriptionOrder
        # We only ask the user for these 4 things. We hide the "Status" and "Price" from them!
        fields = ['patient_name', 'phone_number', 'delivery_address', 'prescription_file']

        widgets = {
            'patient_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Full Name'}),

            # LAYER 1: The HTML Bouncer (Keeps the form-input class, adds 10-digit limits)
            'phone_number': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Phone Number',
                'pattern': '[0-9]{10}',
                'title': 'Please enter exactly 10 digits',
                'maxlength': '10',
                'minlength': '10'
            }),

            'delivery_address': forms.Textarea(
                attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Full Delivery Address'}),
            'prescription_file': forms.FileInput(attrs={'class': 'form-input file-input'}),
        }

    # LAYER 2: The Django Vault (Backend Security)
    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')

        # Strip out any spaces, dashes, or brackets if the user copy-pasted them
        cleaned_phone = re.sub(r'\D', '', phone)

        # Check if the remaining numbers equal exactly 10
        if len(cleaned_phone) != 10:
            raise forms.ValidationError("Please enter a valid 10-digit phone number.")

        return cleaned_phone


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['full_name', 'email', 'phone', 'shipping_address']

        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'John Doe'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'john@example.com'}),
            'phone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '+1 (555) 000-0000'}),
            'shipping_address': forms.Textarea(
                attrs={'class': 'form-input', 'rows': 3, 'placeholder': '123 Health Street, City, Zip Code'}),
        }

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True) # Make email mandatory

    class Meta:
        model = User
        fields = ['username', 'email']

    # This neat little trick automatically applies your CSS class to every box!
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-input'
from backend.models import Address
from backend.models import STATE_CHOICES, COUNTRY_CHOICES
from django import forms


PAYMENT_CHOICES = [
    ('str', 'Card'),
    ('bks', 'bKash'),
    ('con', 'Cash On Delivery'),
]


class RefundForm(forms.Form):
    ref_code = forms.CharField(max_length=20, widget=forms.TextInput(attrs={
        'class': 'form-control mb-4',
        'placeholder': 'Reference code',
    }))
    message = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'form-control rounded-3',
        'rows': '5',
        'placeholder': 'Return reasons'
    }))


class CheckOutForm(forms.Form):
    shipping_address = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': '1/3 Block D, Lalmatia, Dhaka', 'class': 'form-control'}))
    shipping_address2 = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Apartment or suite', 'class': 'form-control'}))
    shipping_country = forms.ChoiceField(required=False, choices=COUNTRY_CHOICES, widget=forms.Select(attrs={'class': 'custom-select d-block w-100'}))
    shipping_state = forms.ChoiceField(required=False, choices=STATE_CHOICES, widget=forms.Select(attrs={'class': 'custom-select d-block w-100'}))
    shipping_zip_code = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    same_billing_address = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'custom-control-input', 'type': 'checkbox'}))
    set_default_shipping_address = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'custom-control-input', 'type': 'checkbox'}))
    use_default_shipping_address = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'custom-control-input', 'type': 'checkbox'}))

    billing_address = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': '1/3 Block D, Lalmatia, Dhaka', 'class': 'form-control'}))
    billing_address2 = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Apartment or suite', 'class': 'form-control'}))
    billing_country = forms.ChoiceField(required=False, choices=COUNTRY_CHOICES,widget=forms.Select(attrs={'class': 'custom-select d-block w-100'}))
    billing_state = forms.ChoiceField(required=False, choices=STATE_CHOICES, widget=forms.Select(attrs={'class': 'custom-select d-block w-100'}))
    billing_zip_code = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    set_default_billing_address = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'custom-control-input', 'type': 'checkbox'}))
    use_default_billing_address = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'custom-control-input', 'type': 'checkbox'}))

    payment_method = forms.ChoiceField(choices=PAYMENT_CHOICES, widget=forms.RadioSelect(attrs={
        'class': 'custom-control-input',
        'type': 'radio',
        'maxlength': '3',
    }))


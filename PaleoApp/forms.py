from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from .models import AccessionNumber, Collection, Locality, Storage


# -----------------------------
# Form: Generate Accession Number
# -----------------------------
class GenerateAccessionNumberForm(forms.ModelForm):
    locality = forms.ModelChoiceField(queryset=Locality.objects.all(), label='Locality')
    shelf_number = forms.CharField(
        max_length=100,
        required=False,
        label='Shelf Number',
        widget=forms.TextInput(attrs={'placeholder': 'Optional (N/A if not provided)'})
    )
    num_specimens = forms.IntegerField(
        min_value=1, 
        max_value=10,  # max_value here should prevent > 10 submissions
        label='Number of Specimens',
        error_messages={
            'max_value': 'You cannot specify more than 10 specimens at a time.'
        }
    )

    class Meta:
        model = AccessionNumber
        fields = ['user', 'collection', 'locality', 'shelf_number', 'num_specimens', 'type_status', 'comment']

    def __init__(self, *args, **kwargs):
        super(GenerateAccessionNumberForm, self).__init__(*args, **kwargs)
        self.fields['collection'].queryset = Collection.objects.all()

    def clean_num_specimens(self):
        shelf_number = self.cleaned_data.get('shelf_number')
        num_specimens = self.cleaned_data.get('num_specimens')
        if shelf_number and shelf_number.strip():
            if num_specimens != 1:
                raise forms.ValidationError("Number of specimens must be equal to 1 when a shelf number is provided.")
        elif num_specimens < 1 or num_specimens > 10:
            raise forms.ValidationError("Number of specimens must be between 1 and 10.")
        return num_specimens

    def clean_shelf_number(self):
        shelf_number = self.cleaned_data.get('shelf_number')
        return shelf_number if shelf_number else None



# -----------------------------
# Form: Custom User Registration
# -----------------------------
class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("Email is already in use.")
        return email

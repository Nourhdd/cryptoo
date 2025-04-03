from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import Usera, Doctor, Appointment

from django import forms
from django.contrib.auth.forms import AuthenticationForm

from django.contrib.auth.forms import AuthenticationForm

class LoginForm(AuthenticationForm):
    username = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={
            'autofocus': True,
            'class': 'form-control',
            'placeholder': 'Votre email'
        })
    )
    
    def clean(self):
        email = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        
        if email and password:
            try:
                user = Usera.objects.get(email=email)
                if not user.check_password(password):
                    raise forms.ValidationError("Mot de passe incorrect")
            except Usera.DoesNotExist:
                raise forms.ValidationError("Email non trouvé")
        
        return self.cleaned_data

class PatientRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = Usera
        fields = ['username', 'email']
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match")

class DoctorRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())
    license_number = forms.CharField(required=True)

    class Meta:
        model = Usera
        fields = ['username', 'email']

    def clean_license_number(self):
        license_number = self.cleaned_data.get('license_number')
        if not Doctor.objects.filter(license_number=license_number).exists():
            raise forms.ValidationError("Numéro de licence invalide")
        return license_number

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Les mots de passe ne correspondent pas")

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['doctor', 'date', 'notes']
        widgets = {
            'date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

from django import forms
from .models import MedicalRecord

class MedicalRecordForm(forms.ModelForm):
    class Meta:
        model = MedicalRecord
        fields = [
            'file', 'allergies', 'chronic_diseases', 'medications',
            'previous_surgeries', 'blood_type', 'emergency_contact', 'notes'
        ]
        widgets = {
            'allergies': forms.Textarea(attrs={'rows': 3}),
            'chronic_diseases': forms.Textarea(attrs={'rows': 3}),
            'medications': forms.Textarea(attrs={'rows': 3}),
            'previous_surgeries': forms.Textarea(attrs={'rows': 3}),
            'notes': forms.Textarea(attrs={'rows': 4}),
        }


from django import forms
from .models import Profile

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['phone_number', 'address', 'profile_picture']
        
        widgets = {
            'address': forms.Textarea(attrs={'rows': 4, 'cols': 50}),
        }

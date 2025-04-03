from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404
from .forms import LoginForm, PatientRegistrationForm, DoctorRegistrationForm, AppointmentForm
from .models import Usera, Profile, Doctor, Patient, Appointment
from django.shortcuts import render
from django.contrib.auth import logout

def home(request):
    return render(request, 'home.html')
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from .models import Usera  # Assurez-vous que c'est votre modèle User personnalisé



def logout_view(request):
    logout(request)
    return redirect('login')  # Redirige vers la vue 'login'


from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib import messages
from .models import Usera
from .forms import LoginForm

from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from .models import Usera

def login_view(request):
    if request.user.is_authenticated:
        return redirect_based_on_role(request.user)
    
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            
            try:
                user = Usera.objects.get(email=email)
                if user.check_password(password):
                    login(request, user)
                    return redirect_based_on_role(user)
                else:
                    messages.error(request, "Mot de passe incorrect")
            except Usera.DoesNotExist:
                messages.error(request, "Aucun compte associé à cet email")
        else:
            messages.error(request, "Formulaire invalide")
    else:
        form = LoginForm()
    
    return render(request, 'login.html', {'form': form})

def redirect_based_on_role(user):
    """Redirection basée sur le rôle de l'utilisateur"""
    if user.role == 'patient':
        return redirect('patient_home')
    elif user.role == 'doctor':
        return redirect('doctor_home')
    return redirect('home')  # Fallback



def register_choice(request):
    return render(request, 'register_choice.html')

def register_patient(request):
    if request.method == 'POST':
        form = PatientRegistrationForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    user = Usera.objects.create_user(
                        username=form.cleaned_data['username'],
                        email=form.cleaned_data['email'],
                        password=form.cleaned_data['password'],
                        role='patient'
                    )
                    profile = Profile.objects.create(user=user)
                    Patient.objects.create(
                        profile=profile,
                        date_of_birth=form.cleaned_data.get('date_of_birth')
                    )
                    messages.success(request, 'Patient account created successfully!')
                    return redirect('login')
            except Exception as e:
                messages.error(request, f"Error creating account: {str(e)}")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = PatientRegistrationForm()
    return render(request, 'register_patient.html', {'form': form})

def register_doctor(request):
    if request.method == 'POST':
        form = DoctorRegistrationForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    license_number = form.cleaned_data['license_number']
                    
                    # Vérifie si la licence existe MAIS n'a pas encore de profil
                    doctor = Doctor.objects.filter(license_number=license_number).first()
                    
                    if not doctor:
                        messages.error(request, "Numéro de licence invalide")
                        return redirect('register_doctor')
                    if doctor.profile is not None:
                        messages.error(request, "Ce médecin a déjà un compte")
                        return redirect('register_doctor')
                    if hasattr(doctor, 'profile'):
                          # Crée le user et le profile
                        user = Usera.objects.create_user(
                        username=form.cleaned_data['username'],
                        email=form.cleaned_data['email'],
                        password=form.cleaned_data['password'],
                        role='doctor'
                        )
                        profile = Profile.objects.create(user=user)
                    
                    # Lie le profile au docteur existant
                        doctor.profile = profile
                        doctor.save()
                    
                        messages.success(request, 'Compte médecin créé avec succès!')
                        return redirect('login')
                    
                  
                    
            except Exception as e:
                messages.error(request, f"Erreur: {str(e)}")
    else:
        form = DoctorRegistrationForm()
    
    return render(request, 'register_doctor.html', {'form': form})

@login_required
def create_appointment(request):
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    appointment = form.save(commit=False)
                    doctor = get_object_or_404(Doctor, id=form.cleaned_data['doctor'].id)
                    
                    # Get patient through profile
                    if hasattr(request.user, 'profile') and hasattr(request.user.profile, 'patient'):
                        appointment.patient = request.user.profile.patient
                    else:
                        messages.error(request, "User has no associated patient profile")
                        return redirect('create_appointment')
                    
                    appointment.doctor = doctor
                    appointment.save()
                    
                    messages.success(request, "Appointment created successfully!")
                    return redirect('appointment_list')
                    
            except Exception as e:
                messages.error(request, f"Error creating appointment: {str(e)}")
    else:
        form = AppointmentForm()
    
    return render(request, 'create_appointment.html', {'form': form})



@login_required
def patient_home(request):
    if not hasattr(request.user, 'patient'):
        messages.error(request, "Accès réservé aux patients")
        return redirect('home')
    
    # Récupère les médecins disponibles
    doctors = Doctor.objects.filter(profile__isnull=False)
    
    # Récupère les rendez-vous du patient
    appointments = Appointment.objects.filter(patient=request.user.patient)
    
    return render(request, 'patient_home.html', {
        'doctors': doctors,
        'appointments': appointments
    })

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Appointment

@login_required
def appointment_list(request):
    if hasattr(request.user, 'profile'):
        if hasattr(request.user.profile, 'patient'):
            appointments = Appointment.objects.filter(patient=request.user.profile.patient)
            username = request.user.profile.user.username
        elif hasattr(request.user.profile, 'doctor'):
            appointments = Appointment.objects.filter(doctor=request.user.profile.doctor)
            username = request.user.profile.user.username
        else:
            appointments = Appointment.objects.none()
            username = request.user.username  # Par défaut si aucun rôle n'est trouvé
    else:
        appointments = Appointment.objects.none()
        username = request.user.username  # Cas improbable où le user n'a pas de profil

    return render(request, 'appointment_list.html', {
        'appointments': appointments,
        'username': username  # Envoyer le username au template
    })




from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import MedicalRecord, Patient
from .forms import MedicalRecordForm

@login_required
def medical_record_view(request):
    try:
        patient = request.user.profile.patient
    except AttributeError:
        return render(request, 'error.html', {'message': "Vous devez être un patient pour accéder à cette page."})

    # Récupérer ou créer un dossier médical pour le patient
    medical_record, created = MedicalRecord.objects.get_or_create(patient=patient)

    if request.method == 'POST':
        form = MedicalRecordForm(request.POST, request.FILES, instance=medical_record)
        if form.is_valid():
            form.save()
            return redirect('medical_record')
    else:
        form = MedicalRecordForm(instance=medical_record)

    return render(request, 'medical_record.html', {'form': form, 'medical_record': medical_record})


from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Appointment

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Appointment, MedicalRecord

@login_required
def doctor_home(request):
    """ Afficher les rendez-vous du médecin connecté """
    if hasattr(request.user, 'profile') and hasattr(request.user.profile, 'doctor'):
        doctor = request.user.profile.doctor
        appointments = Appointment.objects.filter(doctor=doctor).order_by('-date')
    else:
        appointments = None  
    
    return render(request, 'doctor_home.html', {'appointments': appointments})

@login_required
def update_appointment_status(request, appointment_id, action):
    """ Le médecin peut accepter ou refuser un rendez-vous """
    appointment = get_object_or_404(Appointment, id=appointment_id)

    # Vérifier que l'utilisateur est bien le médecin concerné
    if not hasattr(request.user, 'profile') or not hasattr(request.user.profile, 'doctor'):
        return redirect('doctor_home')

    if request.user.profile.doctor != appointment.doctor:
        return redirect('doctor_home')

    if action == 'accept':
        appointment.accept()
    elif action == 'reject':
        appointment.reject()

    return redirect('doctor_home')

from django.shortcuts import render, get_object_or_404
from .models import Patient, MedicalRecord
from django.contrib.auth.decorators import login_required

@login_required
def view_medical_record(request, username):
    # Récupérer le patient via son `username`
    patient = get_object_or_404(Patient, profile__user__username=username)
    
    # Vérifier que l'utilisateur connecté est le médecin
    if not hasattr(request.user, 'profile') or not hasattr(request.user.profile, 'doctor'):
        return redirect('doctor_home')

    doctor = request.user.profile.doctor

    # Vérifier si ce médecin est associé à ce patient via un rendez-vous
    if doctor not in patient.appointments.values_list('doctor', flat=True):
        return redirect('doctor_home')

    # Récupérer le dossier médical du patient
    medical_record = MedicalRecord.objects.filter(patient=patient).first()  # S'assurer qu'il y a un dossier médical

    return render(request, 'view_medical_record.html', {
        'patient': patient,
        'medical_record': medical_record
    })



from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import ProfileForm
from django.contrib.auth.decorators import login_required

@login_required
def profile_view(request):
    # Récupérer le profil de l'utilisateur connecté
    profile = request.user.profile
    
    # Si la méthode est POST, cela signifie que l'utilisateur soumet un formulaire
    if request.method == 'POST':
        # Créer le formulaire avec les données envoyées
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        
        # Vérifier si le formulaire est valide
        if form.is_valid():
            form.save()  # Sauvegarder les nouvelles informations
            messages.success(request, 'Vos informations ont été mises à jour!')
            return redirect('profile')
    else:
        # Si la méthode est GET, on crée un formulaire avec les données actuelles
        form = ProfileForm(instance=profile)

    # Afficher le formulaire dans le template
    return render(request, 'profile.html', {'form': form, 'profile': profile})






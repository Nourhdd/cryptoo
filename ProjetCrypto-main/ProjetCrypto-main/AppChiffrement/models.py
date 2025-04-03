from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.exceptions import ValidationError
from django.db import transaction

class UserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
            
        return self.create_user(email, username, password, **extra_fields)

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class Usera(AbstractBaseUser, PermissionsMixin):  # Ajout de PermissionsMixin
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=255, unique=True)
    role = models.CharField(max_length=50, choices=[
        ('patient', 'Patient'), 
        ('doctor', 'Doctor'), 
        ('pharmacist', 'Pharmacist'),
        ('admin', 'Admin')
    ], default='patient')
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    objects = UserManager()
    
    def __str__(self):
        return self.email

    # Ajout des méthodes nécessaires pour Django Admin
    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

class Profile(models.Model):
    user = models.OneToOneField(Usera, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)

    def __str__(self):
        return f"Profile of {self.user.username}"

class Doctor(models.Model):
    license_number = models.CharField(max_length=50, unique=True)
    specialty = models.CharField(max_length=100)
    profile = models.OneToOneField(
        Profile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='doctor'
    )
    
    def __str__(self):
        return f"{self.license_number} - {self.specialty}"

class Patient(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, related_name='patient')
    date_of_birth = models.DateField(null=True, blank=True)
    medical_history = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Patient {self.profile.user.username}"

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='appointments')
    date = models.DateTimeField()
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']
        unique_together = ['doctor', 'date']

    def __str__(self):
        return f"Appointment #{self.id} - {self.status}"

    def accept(self):
        """ Marquer le rendez-vous comme accepté """
        self.status = 'confirmed'
        self.save()

    def reject(self):
        """ Marquer le rendez-vous comme refusé """
        self.status = 'cancelled'
        self.save()

class MedicalRecord(models.Model):
    patient = models.OneToOneField(
        Patient, 
        on_delete=models.CASCADE, 
        related_name='medical_record'
    )  # Un patient ne peut avoir qu'un seul dossier médical

    file = models.FileField(
        upload_to='medical_records/', 
        null=True, 
        blank=True
    )  # Fichier attaché (ex : PDF, Scan)

    allergies = models.TextField(
        null=True, 
        blank=True
    )  # Allergies connues du patient

    chronic_diseases = models.TextField(
        null=True, 
        blank=True
    )  # Maladies chroniques (diabète, hypertension...)

    medications = models.TextField(
        null=True, 
        blank=True
    )  # Médicaments en cours

    previous_surgeries = models.TextField(
        null=True, 
        blank=True
    )  # Chirurgies antérieures

    blood_type = models.CharField(
        max_length=3, 
        choices=[
            ('A+', 'A+'), ('A-', 'A-'), ('B+', 'B-'),
            ('B-', 'B-'), ('O+', 'O+'), ('O-', 'O-'),
            ('AB+', 'AB+'), ('AB-', 'AB-')
        ], 
        null=True, 
        blank=True
    )  # Groupe sanguin du patient

    emergency_contact = models.CharField(
        max_length=255, 
        null=True, 
        blank=True
    )  # Contact d’urgence

    notes = models.TextField(
        null=True, 
        blank=True
    )  # Notes médicales générales

    date_created = models.DateTimeField(auto_now_add=True)  # Date de création du dossier
    last_updated = models.DateTimeField(auto_now=True)  # Dernière mise à jour

    def __str__(self):
        return f"Medical Record of {self.patient.profile.user.username}"

class Hospital(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    contact_number = models.CharField(max_length=15)
    doctors = models.ManyToManyField(Doctor, related_name='hospitals', blank=True)

    def __str__(self):
        return self.name
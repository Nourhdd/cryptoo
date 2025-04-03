from django.contrib import admin
from .models import Usera, Profile, Doctor, Patient, Appointment, MedicalRecord, Hospital

@admin.register(Usera)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role', 'is_active')
    list_filter = ('role', 'is_active')
    search_fields = ('username', 'email')


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number')
    search_fields = ('user__username', 'phone_number')

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('license_number', 'specialty', 'profile_link')
    search_fields = ('license_number', 'specialty', 'profile__user__username')
    
    def profile_link(self, obj):
        return obj.profile.user.username if obj.profile else None
    profile_link.short_description = 'Username'

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('profile_link', 'date_of_birth')
    search_fields = ('profile__user__username',)
    
    def profile_link(self, obj):
        return obj.profile.user.username
    profile_link.short_description = 'Username'

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient', 'doctor', 'date', 'status')
    list_filter = ('status', 'date')
    search_fields = ('patient__profile__user__username', 'doctor__profile__user__username')

class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient', 'date_created')  # Supprimé 'doctor'
    search_fields = ('patient__profile__user__username',)
    list_filter = ('date_created',)

admin.site.register(MedicalRecord, MedicalRecordAdmin)

@admin.register(Hospital)
class HospitalAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_number')
    filter_horizontal = ('doctors',)
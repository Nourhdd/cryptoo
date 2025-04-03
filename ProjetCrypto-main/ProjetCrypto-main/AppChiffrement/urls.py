from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('accounts/login/', views.login_view, name='login'),  # Redondance pour compatibilité
    path('register/', views.register_choice, name='register_choice'),
    path('register/patient/', views.register_patient, name='register_patient'),
    path('register/doctor/', views.register_doctor, name='register_doctor'),
    path('patient/home/', views.patient_home, name='patient_home'),
    path('appointments/create/', views.create_appointment, name='create_appointment'),
    path('appointments/', views.appointment_list, name='appointment_list'),
    path('medical-record/', views.medical_record_view, name='medical_record'),
    path('doctor/home/', views.doctor_home, name='doctor_home'),
    path('appointment/<int:appointment_id>/<str:action>/', views.update_appointment_status, name='update_appointment_status'),
    path('medical-record/<str:username>/', views.view_medical_record, name='view_medical_record'),
    path('profile/', views.profile_view, name='profile'),
 

 
]
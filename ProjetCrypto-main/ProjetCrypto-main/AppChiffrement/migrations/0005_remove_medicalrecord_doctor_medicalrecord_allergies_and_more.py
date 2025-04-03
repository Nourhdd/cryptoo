# Generated by Django 5.0.3 on 2025-04-03 02:35

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('AppChiffrement', '0004_usera_groups_usera_is_superuser_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='medicalrecord',
            name='doctor',
        ),
        migrations.AddField(
            model_name='medicalrecord',
            name='allergies',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='medicalrecord',
            name='blood_type',
            field=models.CharField(blank=True, choices=[('A+', 'A+'), ('A-', 'A-'), ('B+', 'B-'), ('B-', 'B-'), ('O+', 'O+'), ('O-', 'O-'), ('AB+', 'AB+'), ('AB-', 'AB-')], max_length=3, null=True),
        ),
        migrations.AddField(
            model_name='medicalrecord',
            name='chronic_diseases',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='medicalrecord',
            name='emergency_contact',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='medicalrecord',
            name='last_updated',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='medicalrecord',
            name='medications',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='medicalrecord',
            name='previous_surgeries',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='medicalrecord',
            name='file',
            field=models.FileField(blank=True, null=True, upload_to='medical_records/'),
        ),
        migrations.AlterField(
            model_name='medicalrecord',
            name='patient',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='medical_record', to='AppChiffrement.patient'),
        ),
    ]

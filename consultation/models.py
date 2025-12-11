from django.db import models
from django.contrib.auth.models import User

class Consultation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="consultations")
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone_number = models.CharField(max_length=15)
    
    gender_choices = (('M', 'Male'), ('F', 'Female'))
    gender = models.CharField(max_length=1, choices=gender_choices, blank=True, null=True)
    age = models.IntegerField(blank=True, null=True)
    
    main_concern = models.CharField(max_length=500, blank=True, null=True)
    symptoms = models.TextField()
    duration = models.CharField(max_length=100, blank=True, null=True)
    additional_notes = models.TextField(blank=True, null=True)
    
    appointment_time = models.DateTimeField(blank=True, null=True)
    
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.main_concern or 'No main concern'}"

from django.db import models


class Patient(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=20, unique=True)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["first_name", "last_name"]

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name} ({self.phone})"


class Treatment(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="treatments")
    visit_date = models.DateTimeField(auto_now_add=True)
    complaint = models.TextField(help_text="Patient main complaint or reason for visit")
    diagnosis = models.TextField(blank=True, null=True)
    treatment_plan = models.TextField(help_text="Description of treatment given, medications, advice")
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["-visit_date"]

    def __str__(self) -> str:
        return f"Treatment for {self.patient} on {self.visit_date:%Y-%m-%d %H:%M}"

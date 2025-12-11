from django.contrib import admin

from .models import Patient, Treatment


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "phone", "email", "created_at")
    search_fields = ("first_name", "last_name", "phone", "email")
    list_filter = ("created_at",)


@admin.register(Treatment)
class TreatmentAdmin(admin.ModelAdmin):
    list_display = ("patient", "visit_date", "complaint")
    search_fields = ("patient__first_name", "patient__last_name", "patient__phone", "complaint", "diagnosis")
    list_filter = ("visit_date",)

from rest_framework import serializers

from .models import Patient, Treatment


class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = [
            "id",
            "first_name",
            "last_name",
            "date_of_birth",
            "phone",
            "email",
            "address",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class TreatmentSerializer(serializers.ModelSerializer):
    patient_detail = PatientSerializer(source="patient", read_only=True)

    class Meta:
        model = Treatment
        fields = [
            "id",
            "patient",
            "patient_detail",
            "visit_date",
            "complaint",
            "diagnosis",
            "treatment_plan",
            "notes",
        ]
        read_only_fields = ["id", "visit_date", "patient_detail"]

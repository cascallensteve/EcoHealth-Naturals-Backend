from rest_framework import status, viewsets
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from .models import Patient, Treatment
from .serializers import PatientSerializer, TreatmentSerializer


class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all().order_by("first_name", "last_name")
    serializer_class = PatientSerializer
    permission_classes = [IsAdminUser]

    def create(self, request, *args, **kwargs):
        """Create a patient, or reuse existing if phone already registered.

        Phone number is treated as the unique identifier for a patient.
        If a patient with the same phone exists, it is updated with the
        provided data instead of creating a duplicate record.
        """

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data.get("phone")

        patient, created = Patient.objects.get_or_create(
            phone=phone,
            defaults={
                "first_name": serializer.validated_data.get("first_name", ""),
                "last_name": serializer.validated_data.get("last_name", ""),
                "date_of_birth": serializer.validated_data.get("date_of_birth"),
                "email": serializer.validated_data.get("email"),
                "address": serializer.validated_data.get("address"),
            },
        )

        if not created:
            for field, value in serializer.validated_data.items():
                setattr(patient, field, value)
            patient.save()

        output = self.get_serializer(patient)
        status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        return Response(output.data, status=status_code)


class TreatmentViewSet(viewsets.ModelViewSet):
    queryset = Treatment.objects.select_related("patient").all().order_by("-visit_date")
    serializer_class = TreatmentSerializer
    permission_classes = [IsAdminUser]

    def create(self, request, *args, **kwargs):
        """Create a treatment for a patient.

        If patient data is provided (phone and basic info), the system will
        reuse an existing patient with the same phone, or create a new one
        if none exists. This allows the admin to simply enter patient info
        and treatment details in one request.
        """

        patient_data = request.data.get("patient") or {}
        phone = patient_data.get("phone")

        patient = None
        if phone:
            patient, _created = Patient.objects.get_or_create(
                phone=phone,
                defaults={
                    "first_name": patient_data.get("first_name", ""),
                    "last_name": patient_data.get("last_name", ""),
                    "date_of_birth": patient_data.get("date_of_birth"),
                    "email": patient_data.get("email"),
                    "address": patient_data.get("address"),
                },
            )
            # Optional: update basic info if patient already exists
            for field in [
                "first_name",
                "last_name",
                "date_of_birth",
                "email",
                "address",
            ]:
                if field in patient_data and patient_data[field] is not None:
                    setattr(patient, field, patient_data[field])
            patient.save()

        # If no patient object from nested data, fallback to explicit patient id
        data = request.data.copy()
        if patient is not None:
            data["patient"] = patient.id

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        treatment = serializer.save()
        output = self.get_serializer(treatment)
        return Response(output.data, status=status.HTTP_201_CREATED)

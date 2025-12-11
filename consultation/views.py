from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from .models import Consultation
from .serializers import ConsultationSerializer


# CREATE CONSULTATION (Requires token authentication)
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def create_consultation(request):
    serializer = ConsultationSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response(
            {
                "message": "Consultation submitted successfully",
                "data": serializer.data
            },
            status=status.HTTP_201_CREATED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# LIST USER CONSULTATIONS (Requires token authentication)
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def list_consultations(request):
    consultations = Consultation.objects.filter(user=request.user)
    serializer = ConsultationSerializer(consultations, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


# LIST ALL CONSULTATIONS (Admin only)
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAdminUser])
def list_all_consultations(request):
    consultations = Consultation.objects.all().order_by('-id')
    serializer = ConsultationSerializer(consultations, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


# DELETE CONSULTATION (Admin only)
@api_view(['DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAdminUser])
def delete_consultation(request, pk):
    try:
        consultation = Consultation.objects.get(pk=pk)
    except Consultation.DoesNotExist:
        return Response({"detail": "Consultation not found."}, status=status.HTTP_404_NOT_FOUND)

    consultation.delete()
    return Response({"message": "Consultation deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

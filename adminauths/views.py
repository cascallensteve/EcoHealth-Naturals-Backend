from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from .serializers import AdminSignupSerializer
from .models import AdminProfile
import secrets
import string

# Helper to generate a 6-character alphanumeric verification code
def generate_verification_code(length: int = 6) -> str:
    chars = string.ascii_letters + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))


# --- SIGNUP ---
@api_view(['POST'])
def admin_signup(request):
    serializer = AdminSignupSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        # Generate a short 6-character verification token for email verification
        verification_token = generate_verification_code()
        admin_profile = AdminProfile.objects.get(user=user)
        admin_profile.verification_token = verification_token
        admin_profile.is_verified = False
        admin_profile.save()

        # Send verification code via email
        subject = "Your EcoHealth Naturals admin verification code"
        message = (
            f"Hello {user.username},\n\n"
            f"Your admin verification code is: {verification_token}\n\n"
            "Enter this code in the app to complete your admin email verification."
        )
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )

        # Optionally create an auth token, but login will only work after verification
        token, _ = Token.objects.get_or_create(user=user)
        return Response(
            {
                "message": "Admin created successfully. Verification code sent to email.",
                "token": token.key,
            },
            status=status.HTTP_201_CREATED,
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# --- LOGIN ---
@api_view(['POST'])
def admin_login(request):
    email = request.data.get("email")
    password = request.data.get("password")

    if not email or not password:
        return Response({"error": "Email and password are required"}, status=status.HTTP_400_BAD_REQUEST)

    # Look up user by email, then authenticate using their username
    from django.contrib.auth.models import User

    qs = User.objects.filter(email=email, is_staff=True)

    if not qs.exists():
        return Response({"error": "Invalid admin credentials"}, status=status.HTTP_400_BAD_REQUEST)

    if qs.count() > 1:
        # There are multiple staff users with this email; treat as invalid for security
        return Response({"error": "Email is associated with multiple admin accounts"}, status=status.HTTP_400_BAD_REQUEST)

    user_obj = qs.first()

    user = authenticate(username=user_obj.username, password=password)

    if user is None or not user.is_staff:
        return Response({"error": "Invalid admin credentials"}, status=status.HTTP_400_BAD_REQUEST)

    # Require that the admin has verified their email (is_active True)
    if not user.is_active:
        return Response({"error": "Admin account not verified"}, status=status.HTTP_403_FORBIDDEN)

    token, _ = Token.objects.get_or_create(user=user)
    return Response({
        "message": "Login successful",
        "token": token.key,
    }, status=status.HTTP_200_OK)

# --- LOGOUT ---
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def admin_logout(request):
    request.user.auth_token.delete()
    return Response({"message": "Logged out successfully"}, status=status.HTTP_200_OK)


# --- VERIFY ---
@api_view(['POST'])
def admin_verify(request):
    """Verify admin email using email and verification_token."""
    email = request.data.get("email")
    verification_token = request.data.get("verification_token")

    if not email or not verification_token:
        return Response(
            {"error": "Email and verification_token are required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        admin_profile = AdminProfile.objects.select_related("user").get(
            user__email=email, verification_token=verification_token
        )
    except AdminProfile.DoesNotExist:
        return Response({"error": "Invalid verification details"}, status=status.HTTP_400_BAD_REQUEST)

    # Mark as verified and activate the user
    admin_profile.is_verified = True
    admin_profile.verification_token = None
    admin_profile.save()

    admin_profile.user.is_active = True
    admin_profile.user.save()

    return Response({"message": "Admin email verified successfully"}, status=status.HTTP_200_OK)


# --- RESEND VERIFICATION CODE ---
@api_view(['POST'])
def admin_resend_verification(request):
    """Resend a new verification code to an admin's email."""
    email = request.data.get("email")

    if not email:
        return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        admin_profile = AdminProfile.objects.select_related("user").get(user__email=email)
    except AdminProfile.DoesNotExist:
        return Response({"error": "Admin with this email does not exist"}, status=status.HTTP_400_BAD_REQUEST)

    if admin_profile.is_verified:
        return Response({"message": "Admin is already verified"}, status=status.HTTP_200_OK)

    # Generate a new verification code
    verification_token = generate_verification_code()
    admin_profile.verification_token = verification_token
    admin_profile.save()

    subject = "Your EcoHealth Naturals admin verification code"
    message = (
        f"Hello {admin_profile.user.username},\n\n"
        f"Your new admin verification code is: {verification_token}\n\n"
        "Enter this code in the app to complete your admin email verification."
    )
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [admin_profile.user.email],
        fail_silently=False,
    )

    return Response({"message": "Verification code resent to email"}, status=status.HTTP_200_OK)


# --- LIST ALL USERS (ADMIN ONLY) ---
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAdminUser])
def list_users(request):
    """Return a list of all users (admin-only)."""
    users = User.objects.all().order_by('-date_joined')
    data = [
        {
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "is_staff": u.is_staff,
            "is_active": u.is_active,
            "date_joined": u.date_joined,
        }
        for u in users
    ]
    return Response(data, status=status.HTTP_200_OK)


# --- DELETE USER (ADMIN ONLY) ---
@api_view(['DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAdminUser])
def delete_user(request, pk):
    """Delete a specific user account by ID (admin-only)."""
    try:
        user = User.objects.get(pk=pk)
    except User.DoesNotExist:
        return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

    # Optional: prevent an admin from deleting themselves
    if request.user.id == user.id:
        return Response({"detail": "You cannot delete your own account."}, status=status.HTTP_400_BAD_REQUEST)

    user.delete()
    return Response({"message": "User account deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

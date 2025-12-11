from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.views.decorators.csrf import csrf_exempt
from .serializers import SignupSerializer


@csrf_exempt
@api_view(['POST'])
def signup(request):
    serializer = SignupSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        return Response(
            {
                "message": "User created successfully",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                },
                "token": token.key,
            },
            status=status.HTTP_201_CREATED,
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)





@csrf_exempt
@api_view(['POST'])
def login_view(request):
    """Logs in a user with email and password and returns a token."""
    email = request.data.get('email')
    password = request.data.get('password')

    if not email or not password:
        return Response({"error": "Email and password required"}, status=status.HTTP_400_BAD_REQUEST)

    # There might be multiple users with the same email; try all and authenticate.
    users = User.objects.filter(email=email)

    if not users.exists():
        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

    authenticated_user = None
    for user_obj in users:
        user = authenticate(request, username=user_obj.username, password=password)
        if user is not None:
            authenticated_user = user
            break

    if authenticated_user is not None:
        login(request, authenticated_user)
        token, _ = Token.objects.get_or_create(user=authenticated_user)
        return Response(
            {
                "message": "Login successful",
                "user": {
                    "id": authenticated_user.id,
                    "username": authenticated_user.username,
                    "email": authenticated_user.email,
                },
                "token": token.key,
            },
            status=status.HTTP_200_OK,
        )
    else:
        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)


        
@csrf_exempt
@api_view(['POST'])
def logout_view(request):
    logout(request)
    return Response({"message": "Logged out successfully"}, status=status.HTTP_200_OK)
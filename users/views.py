import os

from google.oauth2 import id_token
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from google.auth.transport import requests as google_requests


from rest_framework_simplejwt.tokens import RefreshToken

from .models import UserProfile
from .serializers import RegisterSerializer, UserSerializer, UserProfileSerializer


GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    user = serializer.save()

    # return tokens
    refresh = RefreshToken.for_user(user)
    return Response({
        "user": UserSerializer(user).data,
        "refresh": str(refresh),
        "access": str(refresh.access_token),
        "detail": "User created. Verification email sent."
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    # using email login
    email = request.data.get('email')
    password = request.data.get('password')
    if not email or not password:
        return Response({"detail": "Email and password are required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(email__iexact=email)
    except User.DoesNotExist:
        return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

    user = authenticate(request, username=user.username, password=password)
    if not user:
        return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

    refresh = RefreshToken.for_user(user)
    return Response({
        "user": UserSerializer(user).data,
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    })

@api_view(['GET', 'PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def me_view(request):
    # GET returns user + profile; PUT/PATCH updates profile (not password)
    user = request.user
    if request.method == "GET":
        return Response(UserSerializer(user).data)

    # update profile fields
    serializer = UserProfileSerializer(user.profile, data=request.data, partial=(request.method=="PATCH"))
    if serializer.is_valid():
        serializer.save()
        return Response({"user": UserSerializer(user).data})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def google_auth(request):
    id_token_str = request.data.get("id_token")
    if not id_token_str:
        return Response({"detail": "id_token is required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        info = id_token.verify_oauth2_token(
            id_token_str,
            google_requests.Request(),
            audience=GOOGLE_CLIENT_ID
        )
    except ValueError:
        return Response({"detail": "Invalid Google token."}, status=status.HTTP_400_BAD_REQUEST)

    email = info.get("email")
    if not email:
        return Response({"detail": "Google account has no email."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(email__iexact=email)
        created = False
    except User.DoesNotExist:
        username = email.split("@")[0]
        counter = 100000000
        while User.objects.filter(username=username).exists():
            counter += 1
            username = f"{username}{counter}"
        user = User.objects.create_user(username=username, email=email)
        user.set_unusable_password()
        user.save()

        profile = UserProfile.objects.create(user=user, name=info.get("name", ""))
        created = True

    refresh = RefreshToken.for_user(user)
    return Response({
        "user": UserSerializer(user).data,
        "refresh": str(refresh),
        "access": str(refresh.access_token),
        "created": created
    })

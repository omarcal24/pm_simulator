from django.urls import path
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from apps.accounts.models import User


@api_view(["GET"])
@permission_classes([IsAuthenticated])
@ensure_csrf_cookie
def me(request):
    """Return current user info."""
    user = request.user
    return Response(
        {
            "id": str(user.id),
            "username": user.username,
            "email": user.email or "",
        }
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    """Session login — requires Django session auth from frontend."""
    from django.contrib.auth import authenticate, login as auth_login

    username = request.data.get("username")
    password = request.data.get("password")
    if not username or not password:
        return Response(
            {"detail": "username and password required"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    user = authenticate(request, username=username, password=password)
    if user is None:
        return Response(
            {"detail": "Invalid credentials"},
            status=status.HTTP_401_UNAUTHORIZED,
        )
    auth_login(request, user)
    return Response(
        {"id": str(user.id), "username": user.username, "email": user.email or ""}
    )


@api_view(["POST"])
def logout(request):
    """Session logout."""
    from django.contrib.auth import logout as auth_logout

    auth_logout(request)
    return Response({"detail": "Logged out"})


urlpatterns = [
    path("me/", me),
    path("auth/login/", login),
    path("auth/logout/", logout),
]

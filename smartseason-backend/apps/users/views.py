"""Auth + user views. Login is rate-limited; admin-only endpoints are guarded."""
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken

from apps.audit.services import record
from apps.core.permissions import IsAdmin
from .models import User
from .serializers import RegisterSerializer, UserSerializer


class RegisterView(generics.CreateAPIView):
    """Public — anyone can sign up. Defaults to field_agent role."""
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
    throttle_scope = "register"

    def perform_create(self, serializer):
        user = serializer.save()
        record(user, "register", entity=f"user:{user.id}", email=user.email)


class LoginView(TokenObtainPairView):
    """JWT login. Throttled. Failed attempts are audited."""
    throttle_scope = "login"

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        email = request.data.get("email", "")
        if response.status_code == 200:
            user = User.objects.filter(email=email).first()
            record(user, "login", entity=f"user:{getattr(user, 'id', None)}")
        else:
            record(None, "login_failed", entity=f"email:{email}")
        return response


class LogoutView(APIView):
    """Blacklist the refresh token so it can't be reused."""
    def post(self, request):
        try:
            RefreshToken(request.data["refresh"]).blacklist()
            record(request.user, "logout", entity=f"user:{request.user.id}")
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            return Response({"detail": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)


class MeView(generics.RetrieveAPIView):
    """Returns the currently-authenticated user (used by the frontend on boot)."""
    serializer_class = UserSerializer
    def get_object(self):
        return self.request.user


class AgentsListView(generics.ListAPIView):
    """Admin-only — list of field agents (used in the assign-agent dropdown)."""
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]
    queryset = User.objects.filter(role=User.ROLE_AGENT, is_active=True).order_by("full_name")

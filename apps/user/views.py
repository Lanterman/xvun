from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from rest_framework import generics, response, status, views
from rest_framework.exceptions import ValidationError, AuthenticationFailed
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema

from . import models, serializers, services, permissions, db_queries
from .celery_tasks import send_reset_password
from config import settings


class SignInView(generics.CreateAPIView):
    """Sign in endpoint"""

    serializer_class = serializers.SignInSerializer
    authentication_classes = []

    @swagger_auto_schema(responses={201: serializers.BaseJWTTokenSerializer}, tags=["auth"], security=[{}])
    def post(self, request, *args, **kwargs):
        error = AuthenticationFailed(detail="Incorrect email or password.", code=status.HTTP_400_BAD_REQUEST)

        user = db_queries.get_user_by_email(request.data["email"])

        if not user:
            raise error

        if not services.validate_password(request.data["password"], user.hashed_password):
            raise error
        
        if not user.is_active:
            raise AuthenticationFailed(detail="Inactivate user.", code=status.HTTP_400_BAD_REQUEST)

        token = services.create_jwttoken(user_id=user.id)
        serializer = serializers.BaseJWTTokenSerializer(token)

        return response.Response(data=serializer.data, status=status.HTTP_201_CREATED)


class SignUpView(generics.CreateAPIView):
    """Sign up endpoint"""

    serializer_class = serializers.SignUpSerializer
    authentication_classes = []

    @swagger_auto_schema(responses={201: serializers.BaseJWTTokenSerializer}, tags=["auth"], security=[{}])
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        token = self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        serializered_token = serializers.BaseJWTTokenSerializer(token)
        return response.Response(serializered_token.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def perform_create(self, serializer):
        user = models.User.objects.create(
            hashed_password=services.create_hashed_password(self.request.data["password1"]), **serializer.data
        )

        return services.create_jwttoken(user_id=user.id)


class SignOutView(views.APIView):
    """Sign out (delete authentication jwt token) endpoint"""

    permission_classes = [IsAuthenticated, permissions.IsAccountOwner]
    
    @swagger_auto_schema(responses={204: '{"detail": "Successfully logged out."}'}, tags=["auth"])
    def delete(self, request, format=None):
        instance = db_queries.get_jwttoken_instance_by_user_id(request.user.id)
        self.perform_delete(instance)
        return response.Response({"detail": "Successfully logged out."}, status=status.HTTP_204_NO_CONTENT)
    
    def perform_delete(self, instance):
        db_queries.logout(instance)


@method_decorator(name="get", decorator=swagger_auto_schema(tags=["profile"]))
@method_decorator(name="put", decorator=swagger_auto_schema(tags=["profile"]))
@method_decorator(name="patch", decorator=swagger_auto_schema(tags=["profile"]))
@method_decorator(name="delete", decorator=swagger_auto_schema(tags=["profile"]))
class ProfileView(generics.RetrieveUpdateDestroyAPIView):
    """User profile endpoint"""

    queryset = models.User.objects.all()
    permission_classes = [IsAuthenticated, permissions.IsMyProfile]
    lookup_field = "username"

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH", "POST"):
            return serializers.UpdateUserInfoSerializer
        elif self.request.method == "GET":
            if self.kwargs and self.kwargs["username"] == self.request.user.username:
                return serializers.MyProfileSerializer
            else:
                return serializers.EnemyProfileSerializer


class RefreshTokenView(generics.CreateAPIView):
    """Refresh authentication JWT tokens endpoint"""

    serializer_class = serializers.RefreshJWTTokenSerializer
    authentication_classes = []
    
    @swagger_auto_schema(responses={
        201: serializers.RefreshJWTTokenSerializer, 
        401: '{"detail": "Refresh token expired."}',
        403: '{"detail": "Invalid refresh token."}', 
        }, 
        tags=["auth"], 
        security=[{}],
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
    
    def create(self, request, *args, **kwargs):
        _token = db_queries.get_jwttoken_instance_by_refresh_token(request.data["refresh_token"])
        
        if _token.created + settings.JWT_SETTINGS["REFRESH_TOKEN_LIFETIME"] < timezone.now():
            raise AuthenticationFailed(_("Refresh token expired."))

        token = self.perform_create(_token.user_id)
        serializer = self.get_serializer(token)
        headers = self.get_success_headers(serializer.data)
        return response.Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, user_id: int):
        return services.create_jwttoken(user_id)


@method_decorator(name="put", decorator=swagger_auto_schema(tags=["profile"]))
class ResetPasswordView(generics.UpdateAPIView):
    """Cahnge a user account password endpoint"""

    queryset = models.User.objects.all()
    permission_classes = []
    serializer_class = serializers.ResetPasswordSerializer
    http_method_names = ["put", "head", "options", "trace"]
    lookup_field = "email"

    def update(self, request, *args, **kwargs):
        user_id_by_secret_key = db_queries.get_user_id_by_secret_key(request.path.split("/")[-2])
        if user_id_by_secret_key is None:
            raise AuthenticationFailed(_("No user with such secret key."))

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        hashed_password = services.create_hashed_password(serializer.data["new_password"])
        self.perform_update(user_id_by_secret_key, hashed_password)
        return response.Response({"new_password": hashed_password}, status=status.HTTP_200_OK)

    def perform_update(self, user_id: int, hashed_password: str):
        db_queries.change_password(user_id, hashed_password)


@method_decorator(name="put", decorator=swagger_auto_schema(tags=["profile"]))
class ChangePasswordView(generics.UpdateAPIView):
    """Cahnge a user account password endpoint"""

    queryset = models.User.objects.all()
    permission_classes = [permissions.IsAccountOwner, IsAuthenticated]
    serializer_class = serializers.ChangePasswordSerializer
    http_method_names = ["put", "head", "options", "trace"]
    lookup_field = "username"

    def update(self, request, *args, **kwargs):
        if not services.validate_password(request.data["old_password"], request.user.hashed_password):
            raise ValidationError(detail={"old_password": "Incorrect old password."}, code=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        hashed_password = services.create_hashed_password(serializer.data["new_password"])
        self.perform_update(hashed_password)
        return response.Response({"new_password": hashed_password}, status=status.HTTP_200_OK)

    def perform_update(self, hashed_password: str):
        db_queries.change_password(self.request.user.id, hashed_password)


class TryToResetPasswordView(generics.CreateAPIView):
    """Try to reset password - endpoint"""

    serializer_class = serializers.TryToResetPasswordSerializer
    authentication_classes = []

    @swagger_auto_schema(tags=["profile"])
    def post(self, request, format=None):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid()

        error = AuthenticationFailed(_("No user with such email."))
        user = db_queries.get_user_by_email(request.data["email"])
        
        if user is None:
            raise error

        secret_key = db_queries.get_secret_key(user.id)

        if secret_key is None:
            raise error

        send_reset_password.delay(user.email, secret_key.key)

        return response.Response({"detail": "Check you email."}, status=status.HTTP_200_OK)

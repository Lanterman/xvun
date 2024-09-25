from rest_framework import exceptions
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from . import models
from .auth import models as auth_models


def get_or_none(email: str) -> models.User | None:
    """If model instance exists, return it, otherwise return None"""

    try:
        query = models.User.objects.get(email=email)
    except models.User.DoesNotExist:
        query = None

    return query


def get_user_by_email(email: str) -> models.User | None:
    """Get user by email""" 

    query = get_or_none(email)
    return query


def get_user_id_by_secret_key(secret_key: str) -> models.User | None:
    """Get the user by the relation's secret_key field"""

    try:
        query = auth_models.SecretKey.objects.get(key=secret_key)
        return query.user_id
    except auth_models.SecretKey.DoesNotExist:
        return None


def change_password(user_id: int, hashed_password: str) -> None:
    """Cahnge user account password"""

    models.User.objects.filter(id=user_id).update(hashed_password=hashed_password)


def logout(instance: auth_models.JWTToken) -> None:
    """Sign out (delete authentication jwt token)"""

    instance.delete()


# action with SecretKey model instance
def get_secret_key(user_id: int) -> auth_models.SecretKey:
    """Get secret key by user id"""

    query = auth_models.SecretKey.objects.filter(user=user_id)
    return None if not query else query[0]


def create_user_secret_key(secret_key: str, user_id: int) -> None:
    """Create user secret key to SecretKey model"""

    auth_models.SecretKey.objects.update_or_create(user_id=user_id, defaults={"key":secret_key, "created": timezone.now()})


# action with JWTToken model instance
def get_jwttoken_instance_by_user_id(user_id: int) -> None:
    """Get authentication a jwt token by a user id"""

    try:
        return auth_models.JWTToken.objects.get(user_id=user_id)
    except auth_models.JWTToken.DoesNotExist:
        raise exceptions.AuthenticationFailed(_('JWTtoken does not exist.'))


def get_jwttoken_instance_by_refresh_token(refresh_token: str) -> auth_models.JWTToken | None:
    """Get a JWTToken model instance or None by refresh token"""

    try:
        return auth_models.JWTToken.objects.get(refresh_token=refresh_token)
    except auth_models.JWTToken.DoesNotExist:
        raise exceptions.AuthenticationFailed(_('Invalid refresh token.'))


def create_jwttoken(access_token: str, refresh_token: str, user_id: int) -> auth_models.JWTToken:
    """Create user token to JWTToken model"""

    instance, _ = auth_models.JWTToken.objects.update_or_create(
        user_id=user_id,
        defaults={"access_token":access_token, "refresh_token":refresh_token, "created": timezone.now()}
    )

    return instance
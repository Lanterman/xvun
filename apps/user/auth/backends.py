from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication, get_authorization_header

from config import settings


class JWTTokenAuthBackend(BaseAuthentication):
    """
    JSON Web token authentication.

    Clients should authenticate by passing the token key in the "Authorization"
    HTTP header, prepended with the string "Bearer ".  For example:

        Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5.eyJ1c2VyX2lkIjoxMjUsInRc3MifQ.CAVyfY41h7Q6xzfR5jEtQGC1bRVWI
    """

    keyword = settings.JWT_SETTINGS["AUTH_HEADER_TYPES"]

    def get_model(self):
        from apps.user.auth.models import JWTToken
        return JWTToken

    def authenticate(self, request):
        auth = get_authorization_header(request).split()

        if not auth or auth[0].lower() != self.keyword.lower().encode():
            return None

        if len(auth) == 1:
            msg = _('Invalid token header. No credentials provided.')
            raise exceptions.AuthenticationFailed(msg)
        
        elif len(auth) > 2:
            msg = _('Invalid token header. Token string should not contain spaces.')
            raise exceptions.AuthenticationFailed(msg)

        try:
            access_token = auth[1].decode()
        except UnicodeError:
            msg = _('Invalid token header. Token string should not contain invalid characters.')
            raise exceptions.AuthenticationFailed(msg)
        
        return self.authenticate_credentials(access_token)

    def authenticate_credentials(self, access_token: str):
        """JWT autentetication"""

        model = self.get_model()
        try:
            token = model.objects.select_related('user').get(access_token=access_token)
        except model.DoesNotExist:
            raise exceptions.AuthenticationFailed(_('Invalid token.'))

        if token.created + settings.JWT_SETTINGS["ACCESS_TOKEN_LIFETIME"] < timezone.now():
            raise exceptions.AuthenticationFailed(_('Token expired.'))

        if not token.user.is_active:
            raise exceptions.AuthenticationFailed(_('User inactive or deleted.'))

        return (token.user, token)

    def authenticate_header(self, request):
        return self.keyword
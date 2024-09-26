import json

from rest_framework.reverse import reverse
from rest_framework.test import APITestCase, APIRequestFactory, APIClient

from apps.user import models, services, auth
from config import settings


class TestIsMyProfilePermission(APITestCase):
    """Testing IsMyProfile class methods"""

    fixtures = ["./config/test/test_data.json"]

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.user_1 = models.User.objects.get(id=1)
        cls.user_2 = models.User.objects.get(id=2)
        cls.token_1 = services.create_jwttoken(cls.user_1.id)
        cls.token_2 = services.create_jwttoken(cls.user_2.id)

        cls.request = APIRequestFactory()
        cls.client = APIClient()
        cls.url = reverse('user-detail', kwargs={"username": cls.user_1.username})
        
        cls.type_token = settings.JWT_SETTINGS["AUTH_HEADER_TYPES"]

    def test_has_object_permission(self):
        """Testing has_object_permission method"""

        self.client.credentials(HTTP_AUTHORIZATION=f'{self.type_token} {self.token_1.access_token}')
        response_get = self.client.get(path=self.url)
        response_patch = self.client.patch(path=self.url, data={"first_name": "string"})
        assert response_get.status_code == 200, response_get.status_code
        assert response_patch.status_code == 200, response_patch.status_code

        self.client.credentials(HTTP_AUTHORIZATION=f'{self.type_token} {self.token_2.access_token}')
        response_get = self.client.get(path=self.url)
        assert response_get.status_code == 200, response_get.status_code

        with self.assertLogs(level="WARNING"):
            response_patch = self.client.patch(path=self.url, data={"first_name": "string"})
        assert response_patch.status_code == 403, response_patch.status_code


class TestResetPasswordViewPermission(APITestCase):
    """Testing ResetPasswordView class methods"""

    fixtures = ["./config/test/test_data.json"]

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.user = models.User.objects.get(id=3)
        cls.token = services.create_jwttoken(cls.user.id)
        cls.secret_key = auth.models.SecretKey.objects.get(id=2)

        cls.request = APIRequestFactory()
        cls.client = APIClient()
        cls.url_1 = reverse("reset-password", kwargs={"email": cls.user.email, 'secret_key': cls.secret_key.key})
        
        cls.type_token = settings.JWT_SETTINGS["AUTH_HEADER_TYPES"]

    def test_has_object_permission(self):
        """Testing has_object_permission method"""

        self.client.credentials(HTTP_AUTHORIZATION=f'{self.type_token} {self.token.access_token}')
        data = {
            "new_password": "karmavdele1",
            "confirm_password": "karmavdele1"
        }

        valid_response_put = self.client.put(path=self.url_1, data=data)
        assert valid_response_put.status_code == 200, valid_response_put.status_code

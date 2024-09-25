from rest_framework.reverse import reverse
from rest_framework.test import APITestCase, APIRequestFactory
from rest_framework.exceptions import AuthenticationFailed

from config import settings
from apps.user import services as user_services, models as user_models
from apps.user.auth import backends, models as auth_models


class TestJWTTokenAuthBackend(APITestCase):
    """Testing JWTTokenAuthBackend class methods"""

    fixtures = ["./config/test/test_data.json"]

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.user = user_models.User.objects.get(id=1)
        cls.token = user_services.create_jwttoken(user_id=1)
        cls.token_to_db = auth_models.JWTToken.objects.get(user_id=3)

        cls.request = APIRequestFactory()
        cls.url = reverse('user-detail', kwargs={"username": cls.user.username})
        cls.instance = backends.JWTTokenAuthBackend()
        
        cls.type_token = settings.JWT_SETTINGS["AUTH_HEADER_TYPES"]
    

    def test_get_model(self):
        """Testing get_model method"""

        model = self.instance.get_model()
        assert "JWTToken" == model.__name__, model.__name__
    
    def test_authenticate(self):
        """Testing authenticate method"""

        request_1 = self.request.get(self.url)
        resposne_1 = self.instance.authenticate(request_1)
        assert None == resposne_1, resposne_1

        request_2 = self.request.get(self.url, headers={"Authorization": f"{self.type_token}"})
        raise_msg = 'Invalid token header. No credentials provided.'
        with self.assertRaisesMessage(AuthenticationFailed, raise_msg):
            self.instance.authenticate(request_2)
        
        request_3 = self.request.get(
            self.url, 
            headers={"Authorization": f"{self.type_token} {self.type_token} {self.token.access_token}"}
        )
        raise_msg = 'Invalid token header. Token string should not contain spaces.'
        with self.assertRaisesMessage(AuthenticationFailed, raise_msg):
            self.instance.authenticate(request_3)
        
        request_4 = self.request.get(
            self.url, 
            headers={"Authorization": f"{self.type_token} {self.token.access_token}1"}
        )
        raise_msg = 'Invalid token.'
        with self.assertRaisesMessage(AuthenticationFailed, raise_msg):
            self.instance.authenticate(request_4)
    

        request_5 = self.request.get(
            self.url, 
            headers={"Authorization": f"{self.type_token} {self.token.access_token}"}
        )
        resposne_5 = self.instance.authenticate(request_5)
        assert tuple == type(resposne_5), resposne_5
        assert 2 == len(resposne_5), resposne_5
        assert "admin" == resposne_5[0].username, resposne_5[0]
        assert "JWTToken" == resposne_5[1].__class__.__name__, resposne_5[1].__class__.__name__
        assert self.token.access_token == resposne_5[1].access_token, resposne_5[1].access_token

    def test_authenticate_credentials(self):
        """Testing authenticate_credentials method"""

        raise_msg = 'Invalid token.'
        with self.assertRaisesMessage(AuthenticationFailed, raise_msg):
            self.instance.authenticate_credentials(f"{self.token}1")

        response_2 = self.instance.authenticate_credentials(self.token_to_db.access_token)
        assert tuple == type(response_2), response_2
        assert 2 == len(response_2), response_2
        assert "user" == response_2[0].username, response_2[0]
        assert "JWTToken" == response_2[1].__class__.__name__, response_2[1].__class__.__name__
        assert self.token_to_db.access_token == response_2[1].access_token, response_2[1].access_token

        raise_msg = 'User inactive or deleted.'
        user_models.User.objects.filter(id=3).update(is_active=False)
        with self.assertRaisesMessage(AuthenticationFailed, raise_msg):
            self.instance.authenticate_credentials(self.token_to_db.access_token)
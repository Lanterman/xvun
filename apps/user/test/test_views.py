import json

from rest_framework.reverse import reverse
from rest_framework.test import APIClient, APITestCase

from apps.user import models, services
from apps.user.auth import models as auth_models


class TestSignInView(APITestCase):
    """Testing the SignInView endpoint methods"""

    fixtures = ["./config/test/test_data.json"]

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.user = models.User.objects.get(id=1)

        cls.client = APIClient()

        cls.path = reverse("sign-in")
    
    def test_get_method(self):
        with self.assertLogs(level="WARNING"):
            response = self.client.get(self.path)
        detail_error = json.loads(response.content)["detail"]
        assert response.status_code == 405, response.status_code
        assert 'Method "GET" not allowed.' == detail_error, detail_error
    
    def test_post_method(self):
        # invalid - no such user
        with self.assertLogs(level="WARNING"):
            invalid_resposne = self.client.post(path=self.path, data={"email": "admin1@mail.ru", "password": "karmavdele"})
        detail_error = json.loads(invalid_resposne.content)["detail"]
        assert invalid_resposne.status_code == 403, invalid_resposne.status_code
        assert "Incorrect email or password." == detail_error, detail_error

        # invalid - invalid password
        with self.assertLogs(level="WARNING"):
            invalid_resposne = self.client.post(path=self.path, data={"email": "admin@mail.ru", "password": "admin1"})
        detail_error = json.loads(invalid_resposne.content)["detail"]
        assert invalid_resposne.status_code == 403, invalid_resposne.status_code
        assert "Incorrect email or password." == detail_error, detail_error

        # invalid - Inactivate user
        with self.assertLogs(level="WARNING"):
            invalid_resposne = self.client.post(path=self.path, data={"email": "no_activate@mail.ru", "password": "karmavdele"})
        detail_error = json.loads(invalid_resposne.content)["detail"]
        assert invalid_resposne.status_code == 403, invalid_resposne.status_code
        assert "Inactivate user." == detail_error, detail_error

        # valid
        valid_resposne = self.client.post(path=self.path, data={"email": "admin@mail.ru", "password": "karmavdele"})
        assert valid_resposne.status_code == 201, valid_resposne.status_code


class TestSignUpView(APITestCase):
    """Testing the SignUpView endpoint methods"""

    fixtures = ["./config/test/test_data.json"]

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.user = models.User.objects.get(id=1)

        cls.client = APIClient()

        cls.path = reverse("sign-up")
    
    def test_get_method(self):
        with self.assertLogs(level="WARNING"):
            response = self.client.get(self.path)
        
        assert response.status_code == 405, response.status_code
    
    def test_post_method(self):
        valid_data = {
            "username": "username", 
            "first_name": "firstname", 
            "last_name": "lastname", 
            "email": "email_123@mail.com", 
            "password1": "password123", 
            "password2": "password123"
        }

        invalid_data = {
            "username": "user", 
            "first_name": "1name", 
            "last_name": "last!", 
            "email": "email_123!@mail.com", 
            "password1": "password", 
            "password2": "pswrd"
        }
        
        valid_resposne = self.client.post(path=self.path, data=valid_data)
        assert valid_resposne.status_code == 201, valid_resposne.status_code

        with self.assertLogs(level="WARNING"):
            invalid_resposne = self.client.post(path=self.path, data=invalid_data)
        
        assert invalid_resposne.status_code == 400, invalid_resposne.status_code


class TestSignOutView(APITestCase):
    """Testing SignOutView class methods"""

    fixtures = ["./config/test/test_data.json"]

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.token = auth_models.JWTToken.objects.get(id=1)

        cls.client = APIClient()

        cls.path = reverse("sign-out")
    
    def test_no_authorization(self):
        with self.assertLogs(level="WARNING"):
            response = self.client.delete(self.path)
        detail_error = json.loads(response.content)["detail"]
        test_detail_error = "Authentication credentials were not provided."
        is_token_exists = auth_models.JWTToken.objects.filter(id=1).exists()
        assert 401 == response.status_code, response.status_code
        assert test_detail_error == detail_error, detail_error
        assert True == is_token_exists, is_token_exists


    def test_get_method(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.access_token)
        with self.assertLogs(level="WARNING"):
            response = self.client.get(self.path)
        detail_error = json.loads(response.content)["detail"]
        test_detail_error = 'Method "GET" not allowed.'
        is_token_exists = auth_models.JWTToken.objects.filter(id=1).exists()
        assert 405 == response.status_code, response.status_code
        assert test_detail_error == detail_error, detail_error
        assert True == is_token_exists, is_token_exists
    
    def test_delete_method(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token.access_token}")
        response = self.client.delete(self.path)
        is_token_exists = auth_models.JWTToken.objects.filter(id=1).exists()
        assert 204 == response.status_code, response.status_code
        assert b"" == response.content, response.content
        assert False == is_token_exists, is_token_exists


class TestProfileView(APITestCase):
    """Testing the ProfileView endpoint methods"""

    fixtures = ["./config/test/test_data.json"]

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.user_1 = models.User.objects.get(id=1)
        cls.user_2 = models.User.objects.get(id=2)
        cls.token = services.create_jwttoken(cls.user_1.id)

        cls.client = APIClient()

        cls.path_1 = reverse("user-detail", kwargs={"username": "admin"})
        cls.path_2 = reverse("user-detail", kwargs={"username": "lanterman"})

        cls.valid_data = {
            "first_name": "firstname", 
            "last_name": "lastname", 
            "email": "email_123@mail.ru", 
        }

        cls.invalid_data = {
            "first_name": "name", 
            "last_name": "name", 
            "email": "email_123!@mail.ru", 
        }
    
    def test_get_method_unauthorization(self):
        with self.assertLogs(level="WARNING"):
            response = self.client.get(self.path_1)
        
        assert response.status_code == 401, response.status_code
    
    def test_get_method_authorization(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.access_token)

        response_1 = self.client.get(self.path_1)
        response_2 = self.client.get(self.path_2)
        
        assert response_1.status_code == 200, response_1.status_code
        assert response_2.status_code == 200, response_2.status_code
    
    def test_post_method_unauthorization(self):
        with self.assertLogs(level="WARNING"):
            response = self.client.post(self.path_1, data=self.valid_data)
        
        assert response.status_code == 401, response.status_code
    
    def test_patch_method_info(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.access_token)

        response_1 = self.client.patch(self.path_1, data=self.valid_data)
        assert response_1.status_code == 200, response_1.status_code

        with self.assertLogs(level="WARNING"):
            response_2 = self.client.patch(self.path_1, data=self.invalid_data)
        assert response_2.status_code == 400, response_2.status_code

        with self.assertLogs(level="WARNING"):
            response_2 = self.client.patch(self.path_2, data=self.valid_data)
        assert response_2.status_code == 403, response_2.status_code


class TestRefreshTokenView(APITestCase):
    """Testing RefreshTokenView class methods"""

    fixtures = ["./config/test/test_data.json"]

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.token_1 = auth_models.JWTToken.objects.get(id=1)
        cls.token_2 = auth_models.JWTToken.objects.get(id=2)

        cls.client = APIClient()

        cls.path = reverse("refresh-tokens")

    def test_get_method(self):
        with self.assertLogs(level="WARNING"):
            response = self.client.get(self.path)
        detail_error = json.loads(response.content)["detail"]
        test_detail_error = 'Method "GET" not allowed.'
        updated_token = auth_models.JWTToken.objects.get(id=1)
        assert 405 == response.status_code, response.status_code
        assert test_detail_error == detail_error, detail_error
        assert self.token_1.access_token == updated_token.access_token, updated_token.access_token
    
    def test_post_method(self):
        # valid request - code 201
        response = self.client.post(self.path, {"refresh_token": self.token_1.refresh_token})
        response_data = json.loads(response.content)
        updated_token = auth_models.JWTToken.objects.get(id=1)
        assert 201 == response.status_code, response.status_code
        assert "access_token" in response_data, response_data
        assert "refresh_token" in response_data, response_data
        assert self.token_1.access_token != updated_token.access_token, updated_token.access_token

        # invalid request - detail: "Refresh token expired."
        with self.assertLogs(level="WARNING"):
            response = self.client.post(self.path, {"refresh_token": self.token_2.refresh_token})
        detail_error = json.loads(response.content)["detail"]
        test_detail_error = "Refresh token expired."
        updated_token = auth_models.JWTToken.objects.get(id=2)
        assert 403 == response.status_code, response.status_code
        assert test_detail_error == detail_error, detail_error
        assert self.token_2.access_token == updated_token.access_token, updated_token.access_token

        # invalid request - detail: "Invalid refresh token."
        with self.assertLogs(level="WARNING"):
            response = self.client.post(self.path, {"refresh_token": "string"})
        detail_error = json.loads(response.content)["detail"]
        test_detail_error = "Invalid refresh token."
        assert 403 == response.status_code, response.status_code
        assert test_detail_error == detail_error, detail_error


class TestChangePasswordView(APITestCase):
    """Testing ChangePasswordView class methods"""

    fixtures = ["./config/test/test_data.json"]

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.user = models.User.objects.get(id=3)
        cls.user_1 = models.User.objects.get(id=1)
        cls.jwt_token = auth_models.JWTToken.objects.get(id=1)

        cls.client = APIClient()

        cls.path = reverse("change-password", kwargs={"username": cls.user.username})
        cls.path_1 = reverse("change-password", kwargs={"username": cls.user_1.username})
        cls.valid_data = {
            "old_password": "karmavdele2",
            "new_password": "karmavdele1",
            "confirm_password": "karmavdele1"
        }
        cls.invalid_data = {
            "old_password": "karmavdel",
            "new_password": "karmavdele1",
            "confirm_password": "karmavdele1"
        }
    
    def test_no_authorization(self):
        with self.assertLogs(level="WARNING"):
            response = self.client.put(self.path, self.valid_data)
        detail_error = json.loads(response.content)["detail"]
        test_detail_error = "Authentication credentials were not provided."
        updated_user = models.User.objects.get(id=3)
        assert 401 == response.status_code, response.status_code
        assert test_detail_error == detail_error, detail_error
        assert self.user.hashed_password == updated_user.hashed_password, updated_user.hashed_password

    def test_get_method(self):
        with self.assertLogs(level="WARNING"):
            response = self.client.get(self.path)
        detail_error = json.loads(response.content)["detail"]
        test_detail_error = 'Method "GET" not allowed.'
        updated_user = models.User.objects.get(id=3)
        assert 405 == response.status_code, response.status_code
        assert test_detail_error == detail_error, detail_error
        assert self.user.hashed_password == updated_user.hashed_password, updated_user.hashed_password
    
    def test_put_method(self):
        # ivalid request - detail: "Incorrect old password."
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.jwt_token.access_token)
        with self.assertLogs(level="WARNING"):
            response = self.client.put(self.path, self.invalid_data)
        detail_error = json.loads(response.content)['old_password']
        test_detail_error = "Incorrect old password."
        updated_user = models.User.objects.get(id=3)
        assert 400 == response.status_code, response.status_code
        assert test_detail_error == detail_error, detail_error
        assert self.user.hashed_password == updated_user.hashed_password, updated_user.hashed_password

        # ivalid request - detail: "This action is only allowed for the account owner"
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.jwt_token.access_token)
        with self.assertLogs(level="WARNING"):
            response = self.client.put(self.path_1, self.valid_data)
        detail_error = json.loads(response.content)['detail']
        test_detail_error = "This action is only allowed for the account owner"
        updated_user = models.User.objects.get(id=3)
        assert 403 == response.status_code, response.status_code
        assert test_detail_error == detail_error, detail_error
        assert self.user.hashed_password == updated_user.hashed_password, updated_user.hashed_password

         # valid request - code 200
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + f"{self.jwt_token.access_token}")
        response = self.client.put(self.path, self.valid_data)
        response_data = json.loads(response.content)
        updated_user = models.User.objects.get(id=3)
        assert 200 == response.status_code, response.status_code
        assert "new_password" in response_data, response_data
        assert self.user.hashed_password != updated_user.hashed_password, updated_user.hashed_password

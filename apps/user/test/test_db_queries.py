from rest_framework.test import APITestCase
from rest_framework.exceptions import AuthenticationFailed

from apps.user import db_queries, models
from apps.user.auth import models as auth_models


class TestGetOrNoneFunction(APITestCase):
    """Testing get_or_none function"""

    fixtures = ["./config/test/test_data.json"]

    def test_existing_user(self):
        response = db_queries.get_or_none("admin@mail.ru")
        self.assertIsNotNone(response, response)
        assert response.__str__() == "admin", response.__str__()
        assert response.is_superuser == True, response.is_superuser
    
    def test_non_existent_user(self):
        response = db_queries.get_or_none("string")
        self.assertIsNone(response, response)


class TestGetUserByEmailFunction(APITestCase):
    """Testing get_user_by_email function"""

    fixtures = ["./config/test/test_data.json"]

    def test_existing_user(self):
        response = db_queries.get_user_by_email("admin@mail.ru")
        self.assertIsNotNone(response, response)
        assert response.__str__() == "admin", response.__str__()
        assert response.is_superuser == True, response.is_superuser
    
    def test_non_existent_user(self):
        response = db_queries.get_user_by_email("admin1@mail.ru")
        self.assertIsNone(response, response)


class TestGetUserIdBySecretKeyFunction(APITestCase):
    """Testing get_user_id_by_secret_key function"""

    fixtures = ["./config/test/test_data.json"]

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.instance = auth_models.SecretKey.objects.get(id=1)

    def test_existing_user_id(self):
        response = db_queries.get_user_id_by_secret_key(self.instance.key)
        self.assertIsNotNone(response, response)
        assert 2 == response, response
    
    def test_non_existent_user_id(self):
        response = db_queries.get_user_id_by_secret_key(f"{self.instance.key}1")
        self.assertIsNone(response, response)


class TestChangePasswordFunction(APITestCase):
    """Testing change_password function"""

    fixtures = ["./config/test/test_data.json"]

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.instance = models.User.objects.get(id=1)

    def test_successfull_user_activate(self):
        hashed_password = 'KtQrvyHOiHFU$b18f34385035abe98c305d63d2121ff72a8bca7385a7d217d1891a1c43d397ae'
        new_hashed_password = 'wqejoweqwenjfnweqeqwemqrk$qweqwneqkeq'
        assert self.instance.hashed_password == hashed_password, self.instance.hashed_password

        response = db_queries.change_password(self.instance.id, new_hashed_password)
        self.assertIsNone(response, response)
        self.instance.refresh_from_db()
        assert self.instance.hashed_password == new_hashed_password, self.instance.hashed_password


class TestLogoutFunction(APITestCase):
    """Testing logout function"""

    fixtures = ["./config/test/test_data.json"]

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.instance = auth_models.JWTToken.objects.get(id=1)

    def test_existing_user_id(self):
        count_instances = auth_models.JWTToken.objects.count()
        assert 2 == count_instances, count_instances

        response = db_queries.logout(self.instance)
        count_instances = auth_models.JWTToken.objects.count()
        self.assertIsNone(response, response)
        assert 1 == count_instances, count_instances


class TestCreateUserSecretKeyFunction(APITestCase):
    """Testing create_user_secret_key function"""

    fixtures = ["./config/test/test_data.json"]

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.instance = auth_models.SecretKey.objects.get(user__id=2)

    def test_update_instance(self):
        secret_key = "35a97667edaa49e839eb47e3409005e66bf2816a4ce59fbf88af7f0a1b38b71f"
        count_instance = auth_models.SecretKey.objects.count()
        assert secret_key == self.instance.key, self.instance.key
        assert 3 == count_instance, count_instance

        new_secret_key = "qwr23j918u3jiuwniqj312jqioqoj131313qwe"
        response = db_queries.create_user_secret_key(new_secret_key, 2)
        count_instance = auth_models.SecretKey.objects.count()
        self.instance.refresh_from_db()
        self.assertIsNone(response, response)
        assert new_secret_key == self.instance.key, self.instance.key
        assert 3 == count_instance, count_instance

    
    def test_create_instance(self):
        secret_key = auth_models.SecretKey.objects.filter(user__id=1).exists()
        self.assertFalse(secret_key,secret_key)

        new_secret_key = "qwr23j918u3jiuwniqj312jqioqoj131313qwe"
        response = db_queries.create_user_secret_key(new_secret_key, 1)
        count_instance = auth_models.SecretKey.objects.count()
        self.instance.refresh_from_db()
        self.assertIsNone(response, response)
        secret_key = auth_models.SecretKey.objects.filter(user__id=1).exists()
        self.assertTrue(secret_key,secret_key)
        assert 4 == count_instance, count_instance


class TestGetJWTTokenInstanceByUserIdFunction(APITestCase):
    """Testing get_jwttoken_instance_by_user_id function"""

    fixtures = ["./config/test/test_data.json"]

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.instance = auth_models.JWTToken.objects.get(id=1)

    def test_existing_token(self):
        response = db_queries.get_jwttoken_instance_by_user_id(3)
        self.assertIsNotNone(response, response)
        assert self.instance == response, response
    
    def test_non_existent_token(self):
        exp_code = 'JWTtoken does not exist.'
        with self.assertRaisesMessage(AuthenticationFailed, exp_code):
            db_queries.get_jwttoken_instance_by_user_id(1)


class TestGetJWTTokenInstanceByRefreshTokenFunction(APITestCase):
    """Testing get_jwttoken_instance_by_refresh_token function"""

    fixtures = ["./config/test/test_data.json"]

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.instance = auth_models.JWTToken.objects.get(id=1)

    def test_existing_token(self):
        response = db_queries.get_jwttoken_instance_by_refresh_token(self.instance.refresh_token)
        self.assertIsNotNone(response, response)
        assert self.instance == response, response
    
    def test_non_existent_token(self):
        exp_code = 'Invalid refresh token.'
        with self.assertRaisesMessage(AuthenticationFailed, exp_code):
            db_queries.get_jwttoken_instance_by_refresh_token(f"{self.instance.refresh_token}w")


class TestCreateJWTTokenFunction(APITestCase):
    """Testing create_jwttoken function"""

    fixtures = ["./config/test/test_data.json"]

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.instance = auth_models.JWTToken.objects.get(user__id=3)

    def test_update_instance(self):
        count_instance = auth_models.JWTToken.objects.count()
        assert 2 == count_instance, count_instance

        response = db_queries.create_jwttoken("access_token", "refresh_token", 3)
        count_instance = auth_models.JWTToken.objects.count()
        self.instance.refresh_from_db()
        self.assertIsNotNone(response, response)
        assert self.instance == response, response
        assert "access_token" == response.access_token, response.access_token
        assert 2 == count_instance, count_instance

    
    def test_create_instance(self):
        secret_key = auth_models.JWTToken.objects.filter(user__id=1).exists()
        self.assertFalse(secret_key,secret_key)

        response = db_queries.create_jwttoken("access_token", "refresh_token", 1)
        count_instance = auth_models.JWTToken.objects.count()
        self.instance.refresh_from_db()
        secret_key = auth_models.JWTToken.objects.filter(user__id=1).exists()
        assert self.instance != response, response
        self.assertIsNotNone(response, response)
        self.assertTrue(secret_key,secret_key)
        assert "access_token" == response.access_token, response.access_token
        assert 3 == count_instance, count_instance

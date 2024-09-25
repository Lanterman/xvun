import re

from rest_framework import serializers, status

from apps.user import models
from apps.user.auth import models as auth_models


class ValidateClass:
    """
    The class containing basic checks. 
    You can inherit from the class but not call it directly.
    """

    @staticmethod
    def validate_first_character(value: str, field_name: str, error_list: list) -> None:
        """Checks if a field contains only characters"""

        if re.match(r'\d|\W', value[0]):
            error_list.append(f"First character of '{field_name}' field can only contain characters!")
    
    @staticmethod
    def validate_only_numbers_contains_and_underscore(value: str, field_name: str, error_list: list) -> None:
        """Check field contains only numbers, letters and underscore"""

        if re.search(r'\W', value):
            error_list.append(f"'{field_name}' field can only numbers, letters and underscore!")

    @staticmethod
    def validate_only_contains(value: str, field_name: str, error_list: list) -> None:
        """Checks if a field contains only characters"""

        if re.search(r'\d|\W', value):
            error_list.append(f"'{field_name}' field can only contain characters!")
    
    @staticmethod
    def validate_min_length(value: str, field_name: str, error_list: list, count: int = 5) -> None:
        """Checks if a field is longer than or equal to the 'count' attribute of characters"""

        if len(value) < count:
            error_list.append(f"'{field_name}' field must be longer than or equal to {count} characters!")
    
    @staticmethod
    def validate_max_length(value: str, field_name: str, error_list: list, count: int = 30) -> None:
        """Checks if a field is less than or equal to the 'count' attribute of characters"""

        if len(value) > count:
            error_list.append(f"'{field_name}' field must be less than or equal to {count} characters!")


class MyProfileSerializer(serializers.ModelSerializer):
    """Profile user serializer"""

    class Meta:
        model = models.User
        fields = ["id", "username", "first_name", "last_name", "email", "created_in"]


class EnemyProfileSerializer(serializers.ModelSerializer):
    """Profile user serializer"""

    class Meta:
        model = models.User
        fields = ["username", "first_name", "last_name", "email", "created_in"]


class UpdateUserInfoSerializer(serializers.ModelSerializer, ValidateClass):
    """Profile user serializer"""

    class Meta:
        model = models.User
        fields = ["first_name", "last_name", "email"]
    
    def validate_first_name(self, value: str) -> str:
        value = value.strip()
        error_list = []

        self.validate_only_contains(value, "First name", error_list)
        self.validate_min_length(value, "First name", error_list)
        self.validate_max_length(value, "First name", error_list)
        
        if error_list:
            raise serializers.ValidationError(error_list, code=status.HTTP_400_BAD_REQUEST)
        
        return value
    
    def validate_last_name(self, value: str) -> str:
        value = value.strip()
        error_list = []

        self.validate_only_contains(value, "Last name", error_list)
        self.validate_min_length(value, "Last name", error_list)
        self.validate_max_length(value, "Last name", error_list)
        
        if error_list:
            raise serializers.ValidationError(error_list, code=status.HTTP_400_BAD_REQUEST)
        
        return value
    
    def validate_email(self, value: str) -> str:
        value = value.strip()
        check_value = value.split("@")[0]
        error_list = []

        self.validate_first_character(value, "Email", error_list)
        self.validate_only_numbers_contains_and_underscore(check_value, "Email", error_list)
        self.validate_min_length(check_value, "Email", error_list)
        self.validate_max_length(check_value, "Email", error_list)

        if error_list:
            raise serializers.ValidationError(error_list, code=status.HTTP_400_BAD_REQUEST)

        return value


class SignInSerializer(serializers.ModelSerializer, ValidateClass):
    """Sign in serializer"""

    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)

    class Meta:
        model = models.User
        fields = ["email", "password"]


class SignUpSerializer(serializers.ModelSerializer, ValidateClass):
    """Sign up serializer"""

    password1 = serializers.CharField(required=True, write_only=True)
    password2 = serializers.CharField(required=True, write_only=True)

    class Meta:
        model = models.User
        fields = ["username", "first_name", "last_name", "email", "password1", "password2"]
    
    def validate_username(self, value: str) -> str:
        value = value.strip()
        error_list = []

        self.validate_first_character(value, "Username", error_list)
        self.validate_only_numbers_contains_and_underscore(value, "Username", error_list)
        self.validate_min_length(value, "Username", error_list)
        self.validate_max_length(value, "Username", error_list)
        
        if error_list:
            raise serializers.ValidationError(error_list, code=status.HTTP_400_BAD_REQUEST)
        
        return value
    
    def validate_first_name(self, value: str) -> str:
        value = value.strip()
        error_list = []

        self.validate_only_contains(value, "First name", error_list)
        self.validate_min_length(value, "First name", error_list)
        self.validate_max_length(value, "First name", error_list)
        
        if error_list:
            raise serializers.ValidationError(error_list, code=status.HTTP_400_BAD_REQUEST)
        
        return value
    
    def validate_last_name(self, value: str) -> str:
        value = value.strip()
        error_list = []

        self.validate_only_contains(value, "Last name", error_list)
        self.validate_min_length(value, "Last name", error_list)
        self.validate_max_length(value, "Last name", error_list)
        
        if error_list:
            raise serializers.ValidationError(error_list, code=status.HTTP_400_BAD_REQUEST)
        
        return value
    
    def validate_email(self, value: str) -> str:
        value = value.strip()
        check_value = value.split("@")[0]
        error_list = []

        self.validate_first_character(value, "Email", error_list)
        self.validate_only_numbers_contains_and_underscore(check_value, "Email", error_list)
        self.validate_min_length(check_value, "Email", error_list)
        self.validate_max_length(check_value, "Email", error_list)
        
        if error_list:
            raise serializers.ValidationError(error_list, code=status.HTTP_400_BAD_REQUEST)
        
        return value
    
    def validate_password1(self, value: str) -> str:
        value = value.strip()
        error_list = []

        self.validate_min_length(value, "Password", error_list, 10)
        self.validate_max_length(value, "Password", error_list, 50)
        
        if error_list:
            raise serializers.ValidationError(error_list, code=status.HTTP_400_BAD_REQUEST)
        
        return value
    
    def validate_password2(self, value: str) -> str:
        password1 = self.initial_data["password1"]

        if password1 != value:
            raise serializers.ValidationError(detail="Password mismatch!", code=status.HTTP_400_BAD_REQUEST)

        return value


class BaseJWTTokenSerializer(serializers.ModelSerializer):
    """Base token serializer"""

    class Meta:
        model = auth_models.JWTToken
        fields = ["access_token", "refresh_token", "created", "user"]


class RefreshJWTTokenSerializer(serializers.ModelSerializer):
    """Base token serializer"""

    class Meta:
        model = auth_models.JWTToken
        fields = ["access_token", "refresh_token", "created", "user"]
        extra_kwargs = {
            "access_token": {"read_only": True},
            "created": {"read_only": True},
            "user": {"read_only": True},
        }


class ChangePasswordSerializer(serializers.ModelSerializer, ValidateClass):
    """Change a user account password"""

    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)

    class Meta:
        model = models.User
        fields = ["old_password", "new_password", "confirm_password"]
        exctra_kwargs = {
            "old_password": {"write_only": True},
            "confirm_password": {"write_only": True},
            }
    
    def validate_new_password(self, value: str) -> str:
        value = value.strip()
        error_list = []
        old_password = self.initial_data["old_password"]

        if old_password == value:
            error_list.append(f"The new password cannot be similar to the old one.")

        self.validate_min_length(value, "New password", error_list, 10)
        self.validate_max_length(value, "New password", error_list, 50)
        
        if error_list:
            raise serializers.ValidationError(error_list, code=status.HTTP_400_BAD_REQUEST)
        
        return value
    
    def validate_confirm_password(self, value: str) -> str:
        new_password = self.initial_data["new_password"]

        if new_password != value:
            raise serializers.ValidationError(detail="Password mismatch!", code=status.HTTP_400_BAD_REQUEST)

        return value


class ResetPasswordSerializer(serializers.ModelSerializer, ValidateClass):
    """Reset a user account password"""

    new_password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)

    class Meta:
        model = models.User
        fields = ["new_password", "confirm_password"]
        exctra_kwargs = {"confirm_password": {"write_only": True}}
    
    def validate_new_password(self, value: str) -> str:
        value = value.strip()
        error_list = []

        self.validate_min_length(value, "New password", error_list, 10)
        self.validate_max_length(value, "New password", error_list, 50)
        
        if error_list:
            raise serializers.ValidationError(error_list, code=status.HTTP_400_BAD_REQUEST)
        
        return value
    
    def validate_confirm_password(self, value: str) -> str:
        new_password = self.initial_data["new_password"]

        if new_password != value:
            raise serializers.ValidationError(detail="Password mismatch!", code=status.HTTP_400_BAD_REQUEST)

        return value


class TryToResetPasswordSerializer(serializers.ModelSerializer):
    """Try to reset a user account password"""

    class Meta:
        model = models.User
        fields = ["email"]

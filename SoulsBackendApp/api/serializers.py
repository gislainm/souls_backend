from typing import Any, Dict

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from ..serializers import UserResponseSerializer


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        return token

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, str]:
        data = super().validate(attrs)
        user_data = UserResponseSerializer(self.user).data
        return {"authToken": data, "user": user_data}
        # return {"access": data["access"], "user": user_data}

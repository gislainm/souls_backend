from django.urls import path

from .views import GenerateOauthCode, VerifyOauthCode

urlpatterns = [
    path("generate", GenerateOauthCode, name="generate_oauth_code"),
    path("verify/<uuid:user_id>", VerifyOauthCode, name="verify_oauth_code"),
]

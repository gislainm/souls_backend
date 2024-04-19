import json

from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from ..emails import send_email_to_group_leader, test_email
from ..models import CustomUser
from ..serializers import UserResponseSerializer, organizationSerializer
from . import forms
from .utils import cache, code
from .utils import token as tokenGenerator

# duration for code validity in minutes
OAUTH_CODE_VALID_FOR = int(settings.OAUTH_CODE_VALID_FOR)


@api_view(["POST"])
def GenerateOauthCode(request):
    code_form = forms.GenerateCodeForm(data=json.loads(request.body))
    if not code_form.is_valid():
        return Response(
            {"error": code_form.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )
    form_data = code_form.cleaned_data
    user_email: str = form_data["email"]
    user = CustomUser.objects.filter(email=user_email).first()
    user_data = UserResponseSerializer(user).data

    if user is None:
        return Response(
            {"error": "No user found with specified email"},
            status=status.HTTP_404_NOT_FOUND,
        )
    if not user.is_group_leader:
        return Response(
            {"error": "User is not a group leader"},
            status=status.HTTP_401_UNAUTHORIZED,
        )
    oauth_code = code.generate_oauth_code(8)
    cache.store_oauth_code(user.email, oauth_code, OAUTH_CODE_VALID_FOR * 60 * 24 * 3)
    user_id = user_data.get("id")
    test_email(
        name=user.name,
        oauth_code=oauth_code,
        record_link="https://www.ignitesouls.com/authorize/%s" % user_id,
    )

    return Response(
        {
            "code": oauth_code,
            "message": "Code generated successfully",
        },
        status=status.HTTP_201_CREATED,
    )


# generate oauth code for testing the automation of send emails to users
def GenerateOauthCodeTesting(group_leader):
    user_email: str = group_leader["email"]
    user = CustomUser.objects.filter(email=user_email).first()
    user_data = UserResponseSerializer(user).data

    if user is None:
        return "No user found with specified email"
    if not user.is_group_leader:
        return "User is not a group leader"
    oauth_code = code.generate_oauth_code(8)
    cache.store_oauth_code(
        user_email, oauth_code, OAUTH_CODE_VALID_FOR * 60 * 24 * 3
    )
    user_id = user_data.get("id")
    # test_email(name=user.name, oauth_code=oauth_code, record_link="www.google.com")
    send_email_to_group_leader(
        name=user.name,
        email=user.email,
        oauth_code=oauth_code,
        record_link="https://www.ignitesouls.com/authorize/%s" % user_id,
    )
    return "Email successfully send to user"


@api_view(["POST"])
def VerifyOauthCode(request, user_id):
    user_data = {"id": user_id, "auth_code": request.data.get("code")}
    verify_form = forms.VerifyCodeForm(data=user_data)
    if not verify_form.is_valid():
        return Response(
            {"error": verify_form.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )
    form_data = verify_form.cleaned_data
    id: str = form_data["id"]
    auth_code: str = form_data["auth_code"]

    user = CustomUser.objects.filter(id=id).first()
    user_small_groups = user.led_groups.all()
    if not user.is_group_leader:
        return Response(
            {"error": "User doesn't have permission"},
            status=status.HTTP_404_NOT_FOUND,
        )

    if not cache.test_oauth_code(user.email, auth_code):
        return Response({"error": "Invalid code"}, status=status.HTTP_401_UNAUTHORIZED)
    else:
        cache.delete_oauth_code(user.email)
    token = tokenGenerator.get_tokens_for_user(user)
    user_small_groups_details = [
        {"id": group.id, "name": group.name} for group in user_small_groups
    ]
    organization = user_small_groups[0].organization
    response = Response(
        {
            "access": token.get("access"),
            "user": UserResponseSerializer(user).data,
            "organization": organizationSerializer(organization).data,
            "groups": user_small_groups_details,
        },
        status=status.HTTP_202_ACCEPTED,
    )
    print(token.get("refresh"))
    response.set_cookie(
        key="refresh",
        value=token.get("refresh"),
        max_age=3 * 24 * 60 * 60,
        httponly=True,
        samesite="None",
        secure=True,
    )
    return response

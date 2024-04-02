from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView

from ..models import CustomUser, Organization
from ..serializers import UserResponseSerializer, organizationSerializer


@api_view(["GET"])
def getRoutes(request):
    routes = ["api section works"]
    return Response(routes)


class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get("refresh")
        if refresh_token:
            try:
                refresh_token = RefreshToken(refresh_token)
                user_id = refresh_token.payload["user_id"]
                user = CustomUser.objects.get(pk=user_id)
                user_data = UserResponseSerializer(user).data
                access_token = str(refresh_token.access_token)
                if user_data.get("is_admin") and user_data.get("is_group_leader"):
                    organization = Organization.objects.get(admin=user_data.get("id"))
                    organization_data = organizationSerializer(organization).data
                    user_small_groups = user.led_groups.all()
                    user_small_groups_details = [
                        {"id": group.id, "name": group.name}
                        for group in user_small_groups
                    ]
                    return Response(
                        {
                            "access": access_token,
                            "user": user_data,
                            "organization": organization_data,
                            "groups": user_small_groups_details,
                        }
                    )
                if user_data.get("is_admin"):
                    organization = Organization.objects.get(admin=user_data.get("id"))
                    organization_data = organizationSerializer(organization).data
                    return Response(
                        {
                            "access": access_token,
                            "user": user_data,
                            "organization": organization_data,
                        }
                    )
                if user_data.get("is_group_leader"):
                    user_small_groups = user.led_groups.all()
                    user_small_groups_details = [
                        {"id": group.id, "name": group.name}
                        for group in user_small_groups
                    ]
                    organization = user_small_groups[0].organization
                    organization_data = organizationSerializer(organization).data
                    return Response(
                        {
                            "access": access_token,
                            "user": user_data,
                            "organization": organization_data,
                            "groups": user_small_groups_details,
                        }
                    )

            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(
                {"error": "Refresh token not found in cookie"},
                status=status.HTTP_400_BAD_REQUEST,
            )

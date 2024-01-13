from rest_framework import status
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken

from .models import CustomUser, Organization
from .serializers import UserSerializer, organizationSerializer, smallGroupSerializer


# create token for user right after registering
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


@api_view(["POST"])
def login(request):
    return Response({})


@api_view(["POST"])
def register(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user_manager = CustomUser._default_manager
        user = user_manager.create_user_admin(**serializer.validated_data)
        token = get_tokens_for_user(user)
        return Response(
            {"authToken": token, "user": UserSerializer(user).data},
            status=status.HTTP_201_CREATED,
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def addOrganization(request):
    if request.method == "POST":
        user = request.user
        if user.is_admin:
            organization_name = request.data.get("name", "")
            if organization_name:
                organization = Organization.objects.create(
                    name=organization_name, admin=user
                )
                return Response(
                    {
                        "organization": organizationSerializer(organization).data,
                        "message": "Organization created successfully",
                    },
                    status=status.HTTP_201_CREATED,
                )
            else:
                return Response(
                    {"error": "Organization name is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            return Response(
                {"error": "You do not have permission to create organizations"},
                status=status.HTTP_403_FORBIDDEN,
            )

    return Response(
        {"error": "Invalid HTTP method"}, status=status.HTTP_400_BAD_REQUEST
    )


@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def addSmallGroup(request, organization_id):
    if request.method == "POST":
        user = request.user
        if user.is_admin:
            try:
                Organization.objects.get(id=organization_id)
                small_group_data = request.data.get("small_group")
                small_group_data["organization"] = organization_id
                small_group_serializer = smallGroupSerializer(data=small_group_data)
                group_leader_serializer = UserSerializer(
                    data=request.data.get("group_leader")
                )
                if group_leader_serializer.is_valid():
                    user_manager = CustomUser._default_manager
                    group_leader = user_manager.create_user_leader(
                        **group_leader_serializer.validated_data
                    )
                else:
                    return Response(
                        {"error": group_leader_serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                if small_group_serializer.is_valid():
                    small_group = small_group_serializer.save()
                    small_group.members.add(group_leader)
                    return Response(
                        {
                            "small_group": smallGroupSerializer(small_group).data,
                            "message": "Small group created successfully",
                        }
                    )
                else:
                    return Response(
                        {"error": small_group_serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            except Organization.DoesNotExist:
                return Response(
                    {"error": "Organization not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        else:
            return Response(
                {"error": "You do not have permission to create small groups"},
                status=status.HTTP_403_FORBIDDEN,
            )
    return Response(
        {"error": "Invalid HTTP method"}, status=status.HTTP_400_BAD_REQUEST
    )

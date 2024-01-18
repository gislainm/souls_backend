from rest_framework import status
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import CustomUser, Organization, SmallGroup
from .oauth.utils import token as tokenGenerator
from .serializers import (
    AttendanceSerializer,
    AttendingUserSerializer,
    UserResponseSerializer,
    UserSerializer,
    organizationSerializer,
    smallGroupSerializer,
)


@api_view(["POST"])
def login(request):
    return Response({})


@api_view(["POST"])
def register(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user_manager = CustomUser._default_manager
        try:
            user = user_manager.create_user_admin(**serializer.validated_data)
            token = tokenGenerator.get_tokens_for_user(user)
            return Response(
                {"authToken": token, "user": UserResponseSerializer(user).data},
                status=status.HTTP_201_CREATED,
            )
        except (ValueError, TypeError) as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
    return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


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
    """
    - This view create a small group in the organization that is already saved in the database.
    - The view also adds a new user in the database, the user is set to the leader of this small-group
    - The leader added with this small group must be a brand new user on the app with no matching email in the database
    """
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
                if (
                    group_leader_serializer.is_valid()
                    and not small_group_serializer.is_valid()
                ):
                    return Response(
                        {"error": small_group_serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                elif (
                    small_group_serializer.is_valid()
                    and not group_leader_serializer.is_valid()
                ):
                    return Response(
                        {"error": group_leader_serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                else:
                    user_manager = CustomUser._default_manager
                    group_leader = user_manager.create_user_leader(
                        **group_leader_serializer.validated_data
                    )
                    small_group = SmallGroup.objects.create(
                        **small_group_serializer.validated_data, leader=group_leader
                    )
                    return Response(
                        {
                            "small_group": smallGroupSerializer(small_group).data,
                            "message": "Small group created successfully",
                        }
                    )
            except Organization.DoesNotExist as e:
                return Response(
                    {"error": "Organization not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            except Exception as e:
                return Response(
                    {"error": str(e)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
        else:
            return Response(
                {"error": "You do not have permission to create small groups"},
                status=status.HTTP_403_FORBIDDEN,
            )
    return Response(
        {"error": "Invalid HTTP method"}, status=status.HTTP_400_BAD_REQUEST
    )


@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def addSmallGroupWithExistingLeader(request, organization_id):
    """
    - This view create a new small-group in the already existing organization, and gives the small-group a leader.
    - The leader given to this small-group has to be an already existing user on the app with the role of small_group_leader
        associated with his/her email
    """
    if request.method == "POST":
        user = request.user
        if user.is_admin:
            try:
                Organization.objects.get(id=organization_id)
                small_group_data = request.data.get("small_group")
                small_group_data["organization"] = organization_id
                small_group_serializer = smallGroupSerializer(data=small_group_data)
                group_leader = CustomUser.objects.filter(
                    id=request.data.get("group_leader").get("id")
                ).first()
                if group_leader is not None and not small_group_serializer.is_valid():
                    return Response(
                        {"error": small_group_serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                elif small_group_serializer.is_valid() and group_leader is None:
                    return Response(
                        {"error": "Group Leader Id is required"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                else:
                    small_group = SmallGroup.objects.create(
                        **small_group_serializer.validated_data, leader=group_leader
                    )
                    return Response(
                        {
                            "small_group": smallGroupSerializer(small_group).data,
                            "message": "Small group created successfully",
                        }
                    )
            except Organization.DoesNotExist as e:
                return Response(
                    {"error": "Organization not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            except Exception as e:
                return Response(
                    {"error": str(e)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
        else:
            return Response(
                {"error": "You do not have permission to create small groups"},
                status=status.HTTP_403_FORBIDDEN,
            )
    return Response(
        {"error": "Invalid HTTP method"}, status=status.HTTP_400_BAD_REQUEST
    )


@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def addSmallGroupMember(request, group_id):
    if request.method == "POST":
        user = request.user
        if user.is_group_leader:
            try:
                small_group = SmallGroup.objects.get(id=group_id)
                user_serializer = AttendingUserSerializer(data=request.data)
                if user_serializer.is_valid():
                    try:
                        new_user = user_serializer.save()
                        small_group.members.add(new_user)
                        return Response(
                            {
                                "small_group": smallGroupSerializer(small_group).data,
                                "message": "User successfully added to the group",
                            },
                            status=status.HTTP_202_ACCEPTED,
                        )
                    except (ValueError, TypeError) as e:
                        return Response(
                            {"error": str(e)},
                            status=status.HTTP_400_BAD_REQUEST,
                        )
                else:
                    return Response(
                        {"error": user_serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            except SmallGroup.DoesNotExist:
                return Response(
                    {"error": "small group not found"},
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


@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def recordAttendance(request, group_id):
    group_leader = request.user
    try:
        group = SmallGroup.objects.get(id=group_id)
    except SmallGroup.DoesNotExist:
        return Response(
            {"error": "Small group requested doesn't exist"},
            status=status.HTTP_404_NOT_FOUND,
        )
    if group_leader.is_group_leader:
        serializer = AttendanceSerializer(data=request.data, context={"group": group})
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "attendance": serializer.data,
                    "message": "Attendance successfully recorded",
                },
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(
                {"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
            )


@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def getOrganizationsGroupLeader(request, organization_id):
    user = request.user
    if user.is_admin:
        try:
            organization = Organization.objects.get(id=organization_id)
            small_groups = organization.small_groups.all()
            leaders = [group.leader for group in small_groups]
            unique_leaders = {leader.email: leader for leader in leaders}.values()
            serializer = UserResponseSerializer(unique_leaders, many=True)
            return Response(
                {"leaders": serializer.data},
            )
        except Organization.DoesNotExist:
            return Response(
                {"error": "Organization requested doesn't exist"},
                status=status.HTTP_404_NOT_FOUND,
            )
    else:
        return Response(
            {"error": "You do not have required permission"},
            status=status.HTTP_403_FORBIDDEN,
        )


@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def getSmallGroups(request, organization_id):
    user = request.user
    if user.is_admin:
        try:
            organization = Organization.objects.get(id=organization_id)
            groups = organization.small_groups.all()
            serializer = smallGroupSerializer(groups, many=True)
            return Response({"groups": serializer.data})
        except Organization.DoesNotExist:
            return Response(
                {"error": "Organization requested doesn't exist"},
                status=status.HTTP_404_NOT_FOUND,
            )
    else:
        return Response(
            {"error": "You do not have required permission"},
            status=status.HTTP_403_FORBIDDEN,
        )
